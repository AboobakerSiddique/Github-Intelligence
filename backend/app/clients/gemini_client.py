"""
Gemini API client.

Talks to Google's Generative Language API over plain httpx (no SDK
dependency). Only this module holds the Gemini request/response shape —
callers pass a prompt string and get text back.
"""
from __future__ import annotations

import httpx

from app.config import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

GEMINI_API_BASE = "https://generativelanguage.googleapis.com/v1beta"
DEFAULT_MODEL = "gemini-3.5-flash"
REQUEST_TIMEOUT_SECONDS = 20.0


class AIUnavailableError(Exception):
    """Raised when the AI service can't be reached or isn't configured."""


class GeminiClient:
    def __init__(self, client: httpx.AsyncClient | None = None):
        self._owns_client = client is None
        self._client = client or httpx.AsyncClient(timeout=REQUEST_TIMEOUT_SECONDS)

    async def aclose(self) -> None:
        if self._owns_client:
            await self._client.aclose()

    async def generate(self, prompt: str, *, model: str = DEFAULT_MODEL) -> str:
        settings = get_settings()
        if not settings.gemini_api_key:
            raise AIUnavailableError("GEMINI_API_KEY is not configured on the server.")

        url = f"{GEMINI_API_BASE}/models/{model}:generateContent"
        try:
            response = await self._client.post(
                url,
                params={"key": settings.gemini_api_key},
                json={"contents": [{"parts": [{"text": prompt}]}]},
            )
        except httpx.HTTPError as exc:
            logger.warning("Gemini request failed: %s", exc)
            raise AIUnavailableError("Could not reach the AI service.") from exc

        if response.status_code >= 400:
            logger.warning("Gemini API error | status=%s", response.status_code)
            raise AIUnavailableError("The AI service returned an error.")

        try:
            data = response.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError, ValueError) as exc:
            raise AIUnavailableError("The AI service returned an unexpected response.") from exc
