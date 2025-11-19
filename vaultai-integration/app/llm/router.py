"""
VaultAI Integration Layer - LLM Router
Routes requests to appropriate LLM provider based on configuration and task type.
"""

from typing import Dict, Optional, List
from app.llm.client import (
    LLMClient,
    LocalOpenAICompatibleClient,
    OpenAICompatibleClient,
    AzureOpenAIClient,
)
from app.schemas.llm import (
    ChatMessage,
    LLMRequest,
    LLMResponse,
    EmbeddingRequest,
    EmbeddingResponse,
    ProviderConfig,
)
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class LLMRouter:
    """
    Routes LLM requests to appropriate providers.

    Supports:
    - Default provider for general tasks
    - Task-specific provider overrides (e.g., local for sensitive data)
    - Fallback to alternative providers on failure
    """

    def __init__(self):
        """Initialize router with configured providers."""
        self.providers: Dict[str, LLMClient] = {}
        self.default_provider = settings.LLM_DEFAULT_PROVIDER
        self._initialize_providers()

    def _initialize_providers(self) -> None:
        """Initialize all configured LLM providers."""
        # Initialize local provider
        if settings.LLM_LOCAL_BASE_URL:
            try:
                self.providers["local"] = LocalOpenAICompatibleClient(
                    ProviderConfig(
                        provider="local",
                        base_url=settings.LLM_LOCAL_BASE_URL,
                        model=settings.LLM_LOCAL_MODEL,
                        api_key=settings.LLM_LOCAL_API_KEY,
                        timeout=settings.LLM_TIMEOUT_SECONDS,
                        max_retries=settings.LLM_MAX_RETRIES,
                        extra={"embedding_model": settings.EMBEDDINGS_MODEL},
                    )
                )
                logger.info(f"Initialized local LLM provider: {settings.LLM_LOCAL_BASE_URL}")
            except Exception as e:
                logger.error(f"Failed to initialize local provider: {e}")

        # Initialize OpenAI-compatible provider
        if settings.LLM_OPENAI_BASE_URL and settings.LLM_OPENAI_API_KEY:
            try:
                self.providers["openai_compatible"] = OpenAICompatibleClient(
                    ProviderConfig(
                        provider="openai_compatible",
                        base_url=settings.LLM_OPENAI_BASE_URL,
                        model=settings.LLM_OPENAI_MODEL,
                        api_key=settings.LLM_OPENAI_API_KEY,
                        timeout=settings.LLM_TIMEOUT_SECONDS,
                        max_retries=settings.LLM_MAX_RETRIES,
                        extra={"embedding_model": settings.EMBEDDINGS_MODEL},
                    )
                )
                logger.info("Initialized OpenAI-compatible provider")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI provider: {e}")

        # Initialize Azure provider
        if settings.LLM_AZURE_BASE_URL and settings.LLM_AZURE_API_KEY:
            try:
                self.providers["azure"] = AzureOpenAIClient(
                    ProviderConfig(
                        provider="azure",
                        base_url=settings.LLM_AZURE_BASE_URL,
                        model=settings.LLM_AZURE_MODEL or "gpt-4",
                        api_key=settings.LLM_AZURE_API_KEY,
                        timeout=settings.LLM_TIMEOUT_SECONDS,
                        max_retries=settings.LLM_MAX_RETRIES,
                        extra={
                            "api_version": settings.LLM_AZURE_API_VERSION,
                            "embedding_model": settings.EMBEDDINGS_MODEL,
                        },
                    )
                )
                logger.info("Initialized Azure OpenAI provider")
            except Exception as e:
                logger.error(f"Failed to initialize Azure provider: {e}")

        if not self.providers:
            logger.error("No LLM providers initialized! Check configuration.")

    def provider_for_task(self, task_type: str) -> str:
        """
        Select provider based on task type.

        Task-specific routing logic:
        - exit_ready_*: Prefer local for confidential business data
        - facilitator_*: Prefer local for negotiation context
        - crm_matching: Can use cloud for general matching
        - analytics_*: Can use cloud for insights

        Args:
            task_type: Type of task (e.g., "exit_ready_teaser", "analytics_report").

        Returns:
            Provider name.
        """
        # Task-specific routing rules
        if task_type.startswith("exit_ready_"):
            # Confidential business data - prefer local
            return "local" if "local" in self.providers else self.default_provider

        if task_type.startswith("facilitator_"):
            # Negotiation context - prefer local
            return "local" if "local" in self.providers else self.default_provider

        if task_type.startswith("crm_"):
            # General CRM tasks - can use cloud
            return self.default_provider

        if task_type.startswith("analytics_"):
            # Analytics - can use cloud
            return self.default_provider

        # Default
        return self.default_provider

    async def chat(
        self,
        request: LLMRequest,
        task_type: Optional[str] = None,
        provider_override: Optional[str] = None,
    ) -> LLMResponse:
        """
        Route chat request to appropriate provider.

        Args:
            request: LLM request.
            task_type: Optional task type for routing.
            provider_override: Optional provider to use instead of default routing.

        Returns:
            LLM response.

        Raises:
            Exception: If all providers fail or no providers available.
        """
        # Determine provider
        provider_name = provider_override or (
            self.provider_for_task(task_type) if task_type else self.default_provider
        )

        if provider_name not in self.providers:
            logger.warning(f"Provider {provider_name} not available, using default")
            provider_name = self.default_provider

        if provider_name not in self.providers:
            raise Exception("No LLM providers available")

        # Get client
        client = self.providers[provider_name]

        logger.info(f"Routing chat request to {provider_name} for task: {task_type or 'general'}")

        # Prepare parameters
        params = {
            "model": request.model,
            "temperature": request.temperature or settings.LLM_TEMPERATURE,
            "max_tokens": request.max_tokens or settings.LLM_MAX_TOKENS,
        }

        # Add optional parameters
        if request.top_p is not None:
            params["top_p"] = request.top_p
        if request.frequency_penalty is not None:
            params["frequency_penalty"] = request.frequency_penalty
        if request.presence_penalty is not None:
            params["presence_penalty"] = request.presence_penalty
        if request.stop is not None:
            params["stop"] = request.stop
        if request.stream:
            params["stream"] = request.stream

        # Send request
        try:
            response = await client.chat(request.messages, **params)
            logger.info(
                f"Chat completed: {response.usage.total_tokens if response.usage else 'N/A'} tokens, "
                f"{response.latency_ms:.0f}ms"
            )
            return response
        except Exception as e:
            logger.error(f"Chat request failed on {provider_name}: {e}")
            raise

    async def embed(
        self,
        request: EmbeddingRequest,
        provider_override: Optional[str] = None,
    ) -> EmbeddingResponse:
        """
        Route embedding request to appropriate provider.

        Args:
            request: Embedding request.
            provider_override: Optional provider override.

        Returns:
            Embedding response.
        """
        provider_name = provider_override or settings.EMBEDDINGS_PROVIDER

        if provider_name not in self.providers:
            logger.warning(f"Embedding provider {provider_name} not available, using default")
            provider_name = self.default_provider

        if provider_name not in self.providers:
            raise Exception("No embedding providers available")

        client = self.providers[provider_name]

        logger.info(f"Routing embedding request to {provider_name} for {len(request.texts)} texts")

        params = {
            "model": request.model or settings.EMBEDDINGS_MODEL,
        }

        try:
            response = await client.embed(request.texts, **params)
            logger.info(f"Embeddings generated: {len(response.embeddings)} vectors of dimension {response.dimension}")
            return response
        except Exception as e:
            logger.error(f"Embedding request failed on {provider_name}: {e}")
            raise

    async def close_all(self) -> None:
        """Close all provider clients."""
        for provider_name, client in self.providers.items():
            try:
                await client.close()
                logger.info(f"Closed {provider_name} client")
            except Exception as e:
                logger.error(f"Error closing {provider_name} client: {e}")


# Global router instance
llm_router = LLMRouter()
