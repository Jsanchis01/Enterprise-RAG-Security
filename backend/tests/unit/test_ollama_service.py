"""
test_ollama_service.py – Unit tests for OllamaService (Phase 5)

Tests:
11. Successful mocked generation
12. Timeout / connection error handling
13. Model and endpoint configuration is respected
"""

import httpx
import pytest
from unittest.mock import patch, MagicMock
from app.services.ollama_service import (
    OllamaService,
    OllamaServiceError,
    GenerationResult,
)


def test_successful_mocked_generation():
    """Test 11: Generation succeeds when Ollama returns a valid response payload."""
    svc = OllamaService(base_url="http://mock-ollama:11434", model="qwen3:4b")

    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "response": "The annual meal allowance is $50 per day.",
        "prompt_eval_count": 45,
        "eval_count": 18,
        "total_duration": 450_000_000,  # 450 ms in nanoseconds
    }

    with patch("httpx.post", return_value=mock_response) as mock_post:
        res = svc.generate("What is the meal allowance?")

        assert isinstance(res, GenerationResult)
        assert res.answer == "The annual meal allowance is $50 per day."
        assert res.model == "qwen3:4b"
        assert res.prompt_tokens == 45
        assert res.completion_tokens == 18
        assert res.total_duration_ms == 450.0

        # Verify POST payload sent to Ollama
        mock_post.assert_called_once()
        call_kwargs = mock_post.call_args[1]
        assert call_kwargs["json"]["model"] == "qwen3:4b"
        assert call_kwargs["json"]["options"]["temperature"] == 0.1
        assert call_kwargs["json"]["options"]["seed"] == 42


def test_ollama_timeout_error_handling():
    """Test 12a: TimeoutException is caught and wrapped into OllamaServiceError."""
    svc = OllamaService(timeout=5.0)

    with patch("httpx.post", side_effect=httpx.TimeoutException("Request timed out")):
        with pytest.raises(OllamaServiceError) as exc_info:
            svc.generate("Test prompt")
        assert "timed out after 5.0s" in str(exc_info.value)


def test_ollama_connection_error_handling():
    """Test 12b: ConnectError is caught and wrapped into OllamaServiceError."""
    svc = OllamaService(base_url="http://invalid-host:11434")

    with patch("httpx.post", side_effect=httpx.ConnectError("Connection refused")):
        with pytest.raises(OllamaServiceError) as exc_info:
            svc.generate("Test prompt")
        assert "Cannot connect to Ollama" in str(exc_info.value)


def test_ollama_non_200_status_code():
    """Test 12c: HTTP non-200 responses raise OllamaServiceError."""
    svc = OllamaService()

    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 500
    mock_response.text = "Internal Server Error in Ollama engine"

    with patch("httpx.post", return_value=mock_response):
        with pytest.raises(OllamaServiceError) as exc_info:
            svc.generate("Test prompt")
        assert "Ollama returned HTTP 500" in str(exc_info.value)


def test_ollama_empty_response_handling():
    """Test 12d: Empty response text from Ollama raises OllamaServiceError."""
    svc = OllamaService()

    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {"response": ""}

    with patch("httpx.post", return_value=mock_response):
        with pytest.raises(OllamaServiceError) as exc_info:
            svc.generate("Test prompt")
        assert "empty response" in str(exc_info.value).lower()


def test_configuration_respected():
    """Test 13: Custom base_url, model, temperature, and num_ctx configurations are applied."""
    custom_url = "http://custom-host:8080"
    custom_model = "custom-llm:7b"
    custom_temp = 0.7
    custom_ctx = 4096

    svc = OllamaService(
        base_url=custom_url,
        model=custom_model,
        temperature=custom_temp,
        num_ctx=custom_ctx,
        timeout=30.0,
    )

    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {"response": "Custom answer"}

    with patch("httpx.post", return_value=mock_response) as mock_post:
        res = svc.generate("Prompt")

        assert res.model == custom_model
        assert res.answer == "Custom answer"

        call_args, call_kwargs = mock_post.call_args
        assert call_args[0] == "http://custom-host:8080/api/generate"
        assert call_kwargs["json"]["model"] == custom_model
        assert call_kwargs["json"]["options"]["temperature"] == custom_temp
        assert call_kwargs["json"]["options"]["num_ctx"] == custom_ctx
        assert call_kwargs["timeout"] == 30.0
