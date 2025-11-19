"""
VaultAI Integration Layer - LLM Client Abstraction
Provider-agnostic interface for LLM interactions using httpx.
"""

import time
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
import httpx

from app.schemas.llm import (
    ChatMessage,
    LLMRequest,
    LLMResponse,
    LLMUsage,
    EmbeddingRequest,
    EmbeddingResponse,
    ProviderConfig,
)
from app.core.logging import get_logger

logger = get_logger(__name__)


class LLMClient(ABC):
    """
    Abstract base class for LLM clients.
    All provider-specific clients must implement this interface.
    """

    def __init__(self, config: ProviderConfig):
        """
        Initialize LLM client with configuration.

        Args:
            config: Provider configuration.
        """
        self.config = config
        self.provider = config.provider
        self.client = httpx.AsyncClient(
            base_url=config.base_url,
            timeout=config.timeout,
        )

    @abstractmethod
    async def chat(
        self,
        messages: List[ChatMessage],
        **params: Any,
    ) -> LLMResponse:
        """
        Send chat completion request.

        Args:
            messages: List of chat messages.
            **params: Additional parameters (temperature, max_tokens, etc.).

        Returns:
            LLM response.
        """
        pass

    @abstractmethod
    async def embed(
        self,
        texts: List[str],
        **params: Any,
    ) -> EmbeddingResponse:
        """
        Generate embeddings for texts.

        Args:
            texts: List of texts to embed.
            **params: Additional parameters.

        Returns:
            Embedding response.
        """
        pass

    async def close(self) -> None:
        """Close HTTP client."""
        await self.client.aclose()

    def _build_headers(self) -> Dict[str, str]:
        """Build common HTTP headers."""
        headers = {
            "Content-Type": "application/json",
        }

        if self.config.api_key:
            headers["Authorization"] = f"Bearer {self.config.api_key}"

        return headers


class OpenAICompatibleClient(LLMClient):
    """
    Client for OpenAI-compatible APIs.
    Works with OpenAI, local LLMs exposing OpenAI API, and similar services.
    """

    async def chat(
        self,
        messages: List[ChatMessage],
        **params: Any,
    ) -> LLMResponse:
        """
        Send chat completion request to OpenAI-compatible endpoint.

        Args:
            messages: Chat messages.
            **params: Additional parameters.

        Returns:
            LLM response.
        """
        start_time = time.time()

        # Build request payload
        payload = {
            "model": params.get("model") or self.config.model,
            "messages": [msg.model_dump() for msg in messages],
        }

        # Add optional parameters
        if "temperature" in params:
            payload["temperature"] = params["temperature"]
        if "max_tokens" in params:
            payload["max_tokens"] = params["max_tokens"]
        if "top_p" in params:
            payload["top_p"] = params["top_p"]
        if "frequency_penalty" in params:
            payload["frequency_penalty"] = params["frequency_penalty"]
        if "presence_penalty" in params:
            payload["presence_penalty"] = params["presence_penalty"]
        if "stop" in params:
            payload["stop"] = params["stop"]
        if "stream" in params:
            payload["stream"] = params["stream"]

        # Send request with retries
        last_error = None
        for attempt in range(self.config.max_retries):
            try:
                logger.debug(f"Sending chat request to {self.provider} (attempt {attempt + 1})")

                response = await self.client.post(
                    "/v1/chat/completions",
                    headers=self._build_headers(),
                    json=payload,
                )
                response.raise_for_status()

                data = response.json()
                latency_ms = (time.time() - start_time) * 1000

                # Parse response
                choice = data["choices"][0]
                usage_data = data.get("usage", {})

                return LLMResponse(
                    content=choice["message"]["content"],
                    model=data["model"],
                    provider=self.provider,
                    usage=LLMUsage(
                        prompt_tokens=usage_data.get("prompt_tokens", 0),
                        completion_tokens=usage_data.get("completion_tokens", 0),
                        total_tokens=usage_data.get("total_tokens", 0),
                    ) if usage_data else None,
                    finish_reason=choice.get("finish_reason"),
                    latency_ms=latency_ms,
                )

            except httpx.HTTPStatusError as e:
                last_error = e
                logger.warning(f"HTTP error on attempt {attempt + 1}: {e}")
                if attempt < self.config.max_retries - 1:
                    await self._wait_before_retry(attempt)
            except httpx.RequestError as e:
                last_error = e
                logger.warning(f"Request error on attempt {attempt + 1}: {e}")
                if attempt < self.config.max_retries - 1:
                    await self._wait_before_retry(attempt)
            except Exception as e:
                last_error = e
                logger.error(f"Unexpected error on attempt {attempt + 1}: {e}")
                if attempt < self.config.max_retries - 1:
                    await self._wait_before_retry(attempt)

        # All retries failed
        logger.error(f"All {self.config.max_retries} attempts failed for chat request")
        raise Exception(f"LLM request failed after {self.config.max_retries} attempts: {last_error}")

    async def embed(
        self,
        texts: List[str],
        **params: Any,
    ) -> EmbeddingResponse:
        """
        Generate embeddings using OpenAI-compatible endpoint.

        Args:
            texts: Texts to embed.
            **params: Additional parameters.

        Returns:
            Embedding response.
        """
        payload = {
            "model": params.get("model") or self.config.extra.get("embedding_model", "text-embedding-ada-002"),
            "input": texts,
        }

        last_error = None
        for attempt in range(self.config.max_retries):
            try:
                logger.debug(f"Sending embedding request to {self.provider} (attempt {attempt + 1})")

                response = await self.client.post(
                    "/v1/embeddings",
                    headers=self._build_headers(),
                    json=payload,
                )
                response.raise_for_status()

                data = response.json()
                usage_data = data.get("usage", {})

                # Extract embeddings
                embeddings = [item["embedding"] for item in data["data"]]
                dimension = len(embeddings[0]) if embeddings else 0

                return EmbeddingResponse(
                    embeddings=embeddings,
                    model=data["model"],
                    dimension=dimension,
                    usage=LLMUsage(
                        prompt_tokens=usage_data.get("prompt_tokens", 0),
                        completion_tokens=0,
                        total_tokens=usage_data.get("total_tokens", 0),
                    ) if usage_data else None,
                )

            except Exception as e:
                last_error = e
                logger.warning(f"Embedding error on attempt {attempt + 1}: {e}")
                if attempt < self.config.max_retries - 1:
                    await self._wait_before_retry(attempt)

        logger.error(f"All {self.config.max_retries} attempts failed for embedding request")
        raise Exception(f"Embedding request failed after {self.config.max_retries} attempts: {last_error}")

    async def _wait_before_retry(self, attempt: int) -> None:
        """
        Exponential backoff before retry.

        Args:
            attempt: Current attempt number (0-indexed).
        """
        import asyncio
        wait_time = 2 ** attempt  # 1s, 2s, 4s, ...
        logger.debug(f"Waiting {wait_time}s before retry")
        await asyncio.sleep(wait_time)


class LocalOpenAICompatibleClient(OpenAICompatibleClient):
    """
    Client for local private LLMs exposing OpenAI-compatible API.
    Examples: vLLM, Ollama, LM Studio, text-generation-webui.
    """

    pass  # Inherits all functionality from OpenAICompatibleClient


class AzureOpenAIClient(LLMClient):
    """
    Client for Azure OpenAI Service.
    Handles Azure-specific URL structure and API versioning.
    """

    async def chat(
        self,
        messages: List[ChatMessage],
        **params: Any,
    ) -> LLMResponse:
        """
        Send chat request to Azure OpenAI.

        Args:
            messages: Chat messages.
            **params: Additional parameters.

        Returns:
            LLM response.
        """
        start_time = time.time()

        # Azure uses deployment name instead of model
        deployment = params.get("model") or self.config.model
        api_version = self.config.extra.get("api_version", "2024-02-01")

        # Build Azure-specific endpoint
        endpoint = f"/openai/deployments/{deployment}/chat/completions?api-version={api_version}"

        payload = {
            "messages": [msg.model_dump() for msg in messages],
        }

        # Add optional parameters
        if "temperature" in params:
            payload["temperature"] = params["temperature"]
        if "max_tokens" in params:
            payload["max_tokens"] = params["max_tokens"]
        if "top_p" in params:
            payload["top_p"] = params["top_p"]
        if "frequency_penalty" in params:
            payload["frequency_penalty"] = params["frequency_penalty"]
        if "presence_penalty" in params:
            payload["presence_penalty"] = params["presence_penalty"]
        if "stop" in params:
            payload["stop"] = params["stop"]

        # Azure uses api-key header instead of Bearer token
        headers = {
            "Content-Type": "application/json",
            "api-key": self.config.api_key or "",
        }

        last_error = None
        for attempt in range(self.config.max_retries):
            try:
                logger.debug(f"Sending chat request to Azure OpenAI (attempt {attempt + 1})")

                response = await self.client.post(
                    endpoint,
                    headers=headers,
                    json=payload,
                )
                response.raise_for_status()

                data = response.json()
                latency_ms = (time.time() - start_time) * 1000

                choice = data["choices"][0]
                usage_data = data.get("usage", {})

                return LLMResponse(
                    content=choice["message"]["content"],
                    model=deployment,
                    provider=self.provider,
                    usage=LLMUsage(
                        prompt_tokens=usage_data.get("prompt_tokens", 0),
                        completion_tokens=usage_data.get("completion_tokens", 0),
                        total_tokens=usage_data.get("total_tokens", 0),
                    ) if usage_data else None,
                    finish_reason=choice.get("finish_reason"),
                    latency_ms=latency_ms,
                )

            except Exception as e:
                last_error = e
                logger.warning(f"Azure OpenAI error on attempt {attempt + 1}: {e}")
                if attempt < self.config.max_retries - 1:
                    await self._wait_before_retry(attempt)

        logger.error(f"All {self.config.max_retries} attempts failed for Azure chat request")
        raise Exception(f"Azure chat request failed after {self.config.max_retries} attempts: {last_error}")

    async def embed(
        self,
        texts: List[str],
        **params: Any,
    ) -> EmbeddingResponse:
        """
        Generate embeddings using Azure OpenAI.

        Args:
            texts: Texts to embed.
            **params: Additional parameters.

        Returns:
            Embedding response.
        """
        deployment = params.get("model") or self.config.extra.get("embedding_model", "text-embedding-ada-002")
        api_version = self.config.extra.get("api_version", "2024-02-01")

        endpoint = f"/openai/deployments/{deployment}/embeddings?api-version={api_version}"

        payload = {
            "input": texts,
        }

        headers = {
            "Content-Type": "application/json",
            "api-key": self.config.api_key or "",
        }

        last_error = None
        for attempt in range(self.config.max_retries):
            try:
                response = await self.client.post(
                    endpoint,
                    headers=headers,
                    json=payload,
                )
                response.raise_for_status()

                data = response.json()
                usage_data = data.get("usage", {})

                embeddings = [item["embedding"] for item in data["data"]]
                dimension = len(embeddings[0]) if embeddings else 0

                return EmbeddingResponse(
                    embeddings=embeddings,
                    model=deployment,
                    dimension=dimension,
                    usage=LLMUsage(
                        prompt_tokens=usage_data.get("prompt_tokens", 0),
                        completion_tokens=0,
                        total_tokens=usage_data.get("total_tokens", 0),
                    ) if usage_data else None,
                )

            except Exception as e:
                last_error = e
                if attempt < self.config.max_retries - 1:
                    await self._wait_before_retry(attempt)

        raise Exception(f"Azure embedding request failed: {last_error}")

    async def _wait_before_retry(self, attempt: int) -> None:
        """Exponential backoff."""
        import asyncio
        wait_time = 2 ** attempt
        await asyncio.sleep(wait_time)
