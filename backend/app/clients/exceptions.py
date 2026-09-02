"""
Exceptions raised by the GitHub client.

These are intentionally generic (not tied to httpx or FastAPI) so services
and API routes can catch them without depending on transport details.
"""
from __future__ import annotations


class GitHubClientError(Exception):
    """Base class for all GitHub client errors."""


class RepositoryNotFoundError(GitHubClientError):
    """Raised when GitHub returns 404 for a repository lookup."""

    def __init__(self, owner: str, repo: str):
        self.owner = owner
        self.repo = repo
        super().__init__(f"Repository not found: {owner}/{repo}")


class RateLimitExceededError(GitHubClientError):
    """Raised when GitHub returns 403/429 due to rate limiting."""

    def __init__(self, reset_at: int | None = None):
        self.reset_at = reset_at
        super().__init__("GitHub API rate limit exceeded")


class GitHubTimeoutError(GitHubClientError):
    """Raised when a request to GitHub times out."""


class GitHubUpstreamError(GitHubClientError):
    """Raised for unexpected GitHub API failures (5xx, malformed responses)."""

    def __init__(self, status_code: int, message: str = ""):
        self.status_code = status_code
        super().__init__(f"GitHub API error ({status_code}): {message}")
