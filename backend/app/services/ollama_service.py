"""
ollama_service.py – Phase 5: Ollama LLM Integration

Provides synchronous text generation using the Ollama REST API.

Configuration is read from the application Settings (config.py):
  - OLLAMA_BASE_URL  (default: http://localhost:11434)
  - OLLAMA_MODEL     (default: qwen3:4b)
  - LLM_TEMPERATURE  (default: 0.1)
  - LLM_NUM_CTX      (default: 2048)

Uses httpx (already a project dependency) with configurable timeouts.
Raises OllamaServiceError for connection failures, timeouts, and non-2xx responses.
All errors are translated to structured exceptions rather than propagated raw.

EXPERIMENTAL PARITY NOTE:
Both baseline and policy-aware pipelines must use the same Ollama model,
temperature, and generation configuration.  This service is the single shared
Ollama integration point for both pipelines.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import httpx

from app.core.config import get_settings

settings = get_settings()

# Default timeout for Ollama generation requests (seconds)
_DEFAULT_TIMEOUT = 120.0


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class OllamaServiceError(Exception):
    """Raised when Ollama is unreachable, times out, or returns an error response."""


# ---------------------------------------------------------------------------
# Result
# ---------------------------------------------------------------------------

@dataclass
class GenerationResult:
    """
    Result of a single Ollama generation call.

    Fields:
        answer:       The generated text response.
        model:        The model that was used.
        prompt_tokens:    Approximate token count for the prompt (from Ollama metadata).
        completion_tokens: Approximate token count for the completion.
        total_duration_ms: Total generation time reported by Ollama in milliseconds.
    """
    answer: str
    model: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_duration_ms: float = 0.0


# ---------------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------------

class OllamaService:
    """
    Thin httpx-based client for the Ollama /api/generate endpoint.

    Designed to be independently testable: inject a mock httpx.Client
    or override base_url/model in tests.

    Both baseline and policy-aware pipelines use the same instance/configuration.
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        num_ctx: Optional[int] = None,
        timeout: float = _DEFAULT_TIMEOUT,
    ) -> None:
        self.base_url = (base_url or settings.OLLAMA_BASE_URL).rstrip("/")
        self.model = model or settings.OLLAMA_MODEL
        self.temperature = temperature if temperature is not None else settings.LLM_TEMPERATURE
        self.num_ctx = num_ctx if num_ctx is not None else settings.LLM_NUM_CTX
        self.timeout = timeout

    def generate(self, prompt: str) -> GenerationResult:
        """
        Sends a prompt to Ollama and returns the generated text.

        Args:
            prompt: The fully assembled prompt string (including system + context + query).

        Returns:
            GenerationResult with the answer and generation metadata.

        Raises:
            OllamaServiceError: On connection error, timeout, or non-2xx response.
        """
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": self.temperature,
                "num_ctx": self.num_ctx,
                "seed": 42,
            },
        }

        try:
            response = httpx.post(url, json=payload, timeout=self.timeout)
        except httpx.ConnectError as exc:
            raise OllamaServiceError(
                f"Cannot connect to Ollama at '{self.base_url}'. "
                f"Ensure Ollama is running. Detail: {exc}"
            ) from exc
        except httpx.TimeoutException as exc:
            raise OllamaServiceError(
                f"Ollama request timed out after {self.timeout}s. "
                f"Model: '{self.model}'. Detail: {exc}"
            ) from exc
        except httpx.RequestError as exc:
            raise OllamaServiceError(
                f"HTTP request to Ollama failed. Detail: {exc}"
            ) from exc

        if response.status_code != 200:
            raise OllamaServiceError(
                f"Ollama returned HTTP {response.status_code}: {response.text[:200]}"
            )

        try:
            data = response.json()
        except Exception as exc:
            raise OllamaServiceError(
                f"Failed to parse Ollama JSON response: {exc}"
            ) from exc

        answer = data.get("response", "").strip()
        if not answer:
            raise OllamaServiceError("Ollama returned an empty response.")

        # Extract usage/timing metadata (may not be present in all versions)
        prompt_eval_count = data.get("prompt_eval_count", 0)
        eval_count = data.get("eval_count", 0)
        total_duration_ns = data.get("total_duration", 0)
        total_duration_ms = total_duration_ns / 1_000_000 if total_duration_ns else 0.0

        return GenerationResult(
            answer=answer,
            model=self.model,
            prompt_tokens=prompt_eval_count,
            completion_tokens=eval_count,
            total_duration_ms=total_duration_ms,
        )
