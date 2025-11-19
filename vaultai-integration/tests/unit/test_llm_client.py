"""
Unit tests for LLM Client implementations.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.llm.client import OpenAICompatibleClient, LocalOpenAICompatibleClient
from app.schemas.llm import ChatMessage, ProviderConfig


@pytest.fixture
def provider_config():
    """Create a test provider configuration."""
    return ProviderConfig(
        provider="test",
        base_url="http://localhost:8009",
        model="test-model",
        api_key="test_key",
        timeout=30,
        max_retries=3,
    )


@pytest.fixture
def openai_client(provider_config):
    """Create an OpenAI-compatible client for testing."""
    return OpenAICompatibleClient(provider_config)


@pytest.mark.asyncio
async def test_chat_success(openai_client):
    """Test successful chat completion."""
    # Mock HTTP response
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "model": "test-model",
        "choices": [
            {
                "message": {"content": "Test response"},
                "finish_reason": "stop",
            }
        ],
        "usage": {
            "prompt_tokens": 10,
            "completion_tokens": 5,
            "total_tokens": 15,
        },
    }
    mock_response.raise_for_status = MagicMock()

    # Patch the HTTP client
    with patch.object(openai_client.client, "post", return_value=mock_response) as mock_post:
        messages = [
            ChatMessage(role="system", content="You are a helpful assistant"),
            ChatMessage(role="user", content="Hello"),
        ]

        response = await openai_client.chat(messages)

        # Assertions
        assert response.content == "Test response"
        assert response.model == "test-model"
        assert response.provider == "test"
        assert response.finish_reason == "stop"
        assert response.usage.total_tokens == 15
        assert response.latency_ms > 0

        # Verify HTTP call
        mock_post.assert_called_once()


@pytest.mark.asyncio
async def test_chat_with_parameters(openai_client):
    """Test chat with custom parameters."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "model": "test-model",
        "choices": [{"message": {"content": "Test"}, "finish_reason": "stop"}],
        "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
    }
    mock_response.raise_for_status = MagicMock()

    with patch.object(openai_client.client, "post", return_value=mock_response) as mock_post:
        messages = [ChatMessage(role="user", content="Test")]

        await openai_client.chat(
            messages,
            temperature=0.5,
            max_tokens=100,
            top_p=0.9,
        )

        # Verify parameters were passed
        call_args = mock_post.call_args
        payload = call_args[1]["json"]

        assert payload["temperature"] == 0.5
        assert payload["max_tokens"] == 100
        assert payload["top_p"] == 0.9


@pytest.mark.asyncio
async def test_chat_retry_on_error(openai_client):
    """Test retry logic on HTTP errors."""
    # First two calls fail, third succeeds
    mock_response_error = MagicMock()
    mock_response_error.raise_for_status.side_effect = Exception("HTTP Error")

    mock_response_success = MagicMock()
    mock_response_success.json.return_value = {
        "model": "test-model",
        "choices": [{"message": {"content": "Success"}, "finish_reason": "stop"}],
        "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
    }
    mock_response_success.raise_for_status = MagicMock()

    with patch.object(
        openai_client.client,
        "post",
        side_effect=[mock_response_error, mock_response_error, mock_response_success],
    ):
        messages = [ChatMessage(role="user", content="Test")]

        response = await openai_client.chat(messages)

        # Should succeed after retries
        assert response.content == "Success"


@pytest.mark.asyncio
async def test_embed_success(openai_client):
    """Test successful embedding generation."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "model": "text-embedding-ada-002",
        "data": [
            {"embedding": [0.1, 0.2, 0.3]},
            {"embedding": [0.4, 0.5, 0.6]},
        ],
        "usage": {"prompt_tokens": 10, "total_tokens": 10},
    }
    mock_response.raise_for_status = MagicMock()

    with patch.object(openai_client.client, "post", return_value=mock_response):
        texts = ["Test 1", "Test 2"]

        response = await openai_client.embed(texts)

        # Assertions
        assert len(response.embeddings) == 2
        assert response.embeddings[0] == [0.1, 0.2, 0.3]
        assert response.embeddings[1] == [0.4, 0.5, 0.6]
        assert response.dimension == 3
        assert response.usage.total_tokens == 10


def test_build_headers(openai_client):
    """Test HTTP headers construction."""
    headers = openai_client._build_headers()

    assert "Content-Type" in headers
    assert headers["Content-Type"] == "application/json"
    assert "Authorization" in headers
    assert headers["Authorization"] == "Bearer test_key"


def test_build_headers_no_api_key():
    """Test headers without API key."""
    config = ProviderConfig(
        provider="test",
        base_url="http://localhost:8009",
        model="test-model",
        api_key=None,
        timeout=30,
        max_retries=3,
    )
    client = OpenAICompatibleClient(config)

    headers = client._build_headers()

    assert "Authorization" not in headers


@pytest.mark.asyncio
async def test_local_client_inherits_functionality():
    """Test that LocalOpenAICompatibleClient inherits from OpenAICompatibleClient."""
    config = ProviderConfig(
        provider="local",
        base_url="http://localhost:8009",
        model="llama3-70b",
        timeout=30,
        max_retries=3,
    )

    local_client = LocalOpenAICompatibleClient(config)

    assert isinstance(local_client, OpenAICompatibleClient)
    assert local_client.provider == "local"
    assert local_client.config.model == "llama3-70b"
