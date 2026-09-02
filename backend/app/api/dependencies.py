from fastapi import Request

from app.clients.gemini_client import GeminiClient
from app.clients.github_client import GitHubClient


def get_github_client(request: Request) -> GitHubClient:
    """Returns the shared, app-lifetime GitHubClient (single connection pool)."""
    return request.app.state.github_client


def get_gemini_client(request: Request) -> GeminiClient:
    """Returns the shared, app-lifetime GeminiClient (single connection pool)."""
    return request.app.state.gemini_client
