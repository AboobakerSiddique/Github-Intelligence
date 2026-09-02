"""
GitHub REST API client.

This is the only module in the application allowed to talk to
`api.github.com`. It returns raw (but validated-shape) JSON dictionaries —
normalization into application schemas happens in `services/`.
"""
from __future__ import annotations

import asyncio
from typing import Any

import httpx

from app.clients.exceptions import (
    GitHubTimeoutError,
    GitHubUpstreamError,
    RateLimitExceededError,
    RepositoryNotFoundError,
)
from app.config import get_settings
from app.utils.cache import cache, cache_key
from app.utils.logger import get_logger

logger = get_logger(__name__)

GITHUB_API_BASE = "https://api.github.com"
REQUEST_TIMEOUT_SECONDS = 10.0
MAX_RETRIES = 2
RETRYABLE_STATUS_CODES = {502, 503, 504}


class GitHubClient:
    """Thin async wrapper around the GitHub REST API."""

    def __init__(self, client: httpx.AsyncClient | None = None):
        settings = get_settings()
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "github-intelligence-app",
        }
        if settings.github_token:
            headers["Authorization"] = f"Bearer {settings.github_token}"

        self._owns_client = client is None
        self._client = client or httpx.AsyncClient(
            base_url=GITHUB_API_BASE,
            headers=headers,
            timeout=REQUEST_TIMEOUT_SECONDS,
        )

    async def aclose(self) -> None:
        if self._owns_client:
            await self._client.aclose()

    async def __aenter__(self) -> "GitHubClient":
        return self

    async def __aexit__(self, *exc_info: object) -> None:
        await self.aclose()

    # -- Public API ---------------------------------------------------

    async def get_repository(self, owner: str, repo: str) -> dict[str, Any]:
        """Fetch repository metadata (name, description, stars, topics, etc.)."""
        return await self._request("GET", f"/repos/{owner}/{repo}", owner, repo)

    async def get_languages(self, owner: str, repo: str) -> dict[str, int]:
        """Fetch language byte-counts, e.g. {"Python": 102934, "TypeScript": 40213}."""
        return await self._request("GET", f"/repos/{owner}/{repo}/languages", owner, repo)

    async def get_contributors(
        self, owner: str, repo: str, max_pages: int = 3, per_page: int = 30
    ) -> list[dict[str, Any]]:
        """Fetch top contributors, paginated up to `max_pages`."""
        return await self._paginate(
            f"/repos/{owner}/{repo}/contributors",
            owner,
            repo,
            max_pages=max_pages,
            per_page=per_page,
            params={"anon": "false"},
        )

    async def get_issues(
        self, owner: str, repo: str, state: str = "all", max_pages: int = 2, per_page: int = 30
    ) -> list[dict[str, Any]]:
        """Fetch issues (GitHub includes PRs here too — callers should filter via `pull_request`)."""
        return await self._paginate(
            f"/repos/{owner}/{repo}/issues",
            owner,
            repo,
            max_pages=max_pages,
            per_page=per_page,
            params={"state": state, "sort": "created", "direction": "desc"},
        )

    async def get_pulls(
        self, owner: str, repo: str, state: str = "all", max_pages: int = 2, per_page: int = 30
    ) -> list[dict[str, Any]]:
        return await self._paginate(
            f"/repos/{owner}/{repo}/pulls",
            owner,
            repo,
            max_pages=max_pages,
            per_page=per_page,
            params={"state": state, "sort": "created", "direction": "desc"},
        )

    async def get_releases(
        self, owner: str, repo: str, max_pages: int = 1, per_page: int = 10
    ) -> list[dict[str, Any]]:
        return await self._paginate(
            f"/repos/{owner}/{repo}/releases",
            owner,
            repo,
            max_pages=max_pages,
            per_page=per_page,
        )

    # -- Internals ------------------------------------------------------

    async def _paginate(
        self,
        path: str,
        owner: str,
        repo: str,
        max_pages: int,
        per_page: int,
        params: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        for page in range(1, max_pages + 1):
            page_params = {"per_page": per_page, "page": page, **(params or {})}
            batch = await self._request("GET", path, owner, repo, params=page_params)
            if not isinstance(batch, list) or not batch:
                break
            results.extend(batch)
            if len(batch) < per_page:
                break
        return results

    async def _request(
        self,
        method: str,
        path: str,
        owner: str,
        repo: str,
        params: dict[str, Any] | None = None,
    ) -> Any:
        cache_ttl = get_settings().cache_ttl_seconds
        key = cache_key("gh", method, path, str(sorted((params or {}).items())))

        if method == "GET" and cache_ttl > 0:
            cached = cache.get(key)
            if cached is not None:
                logger.info("Cache hit | %s %s", method, path)
                return cached

        last_error: Exception | None = None

        for attempt in range(MAX_RETRIES + 1):
            try:
                response = await self._client.request(method, path, params=params)
            except httpx.TimeoutException as exc:
                logger.warning("GitHub request timed out: %s %s", method, path)
                last_error = GitHubTimeoutError(f"Timed out requesting {path}")
                await self._backoff(attempt)
                continue
            except httpx.HTTPError as exc:
                logger.warning("GitHub request network error: %s %s (%s)", method, path, exc)
                last_error = GitHubUpstreamError(0, str(exc))
                await self._backoff(attempt)
                continue

            logger.info(
                "GitHub API request | %s %s | status=%s | attempt=%s",
                method,
                path,
                response.status_code,
                attempt + 1,
            )

            if response.status_code == 404:
                raise RepositoryNotFoundError(owner, repo)

            if response.status_code in (403, 429) and self._is_rate_limited(response):
                reset_at = self._rate_limit_reset(response)
                logger.warning("GitHub rate limit hit | resets_at=%s", reset_at)
                raise RateLimitExceededError(reset_at=reset_at)

            if response.status_code in RETRYABLE_STATUS_CODES and attempt < MAX_RETRIES:
                last_error = GitHubUpstreamError(response.status_code)
                await self._backoff(attempt)
                continue

            if response.status_code >= 400:
                raise GitHubUpstreamError(response.status_code, response.text[:200])

            try:
                result = response.json()
            except ValueError as exc:
                raise GitHubUpstreamError(response.status_code, "Malformed JSON response") from exc

            if method == "GET" and cache_ttl > 0:
                cache.set(key, result, ttl_seconds=cache_ttl)
            return result

        # Exhausted retries without a successful response.
        raise last_error or GitHubUpstreamError(0, "Unknown GitHub client failure")

    @staticmethod
    def _is_rate_limited(response: httpx.Response) -> bool:
        remaining = response.headers.get("x-ratelimit-remaining")
        return remaining == "0" or response.status_code == 429

    @staticmethod
    def _rate_limit_reset(response: httpx.Response) -> int | None:
        reset_header = response.headers.get("x-ratelimit-reset")
        return int(reset_header) if reset_header and reset_header.isdigit() else None

    @staticmethod
    async def _backoff(attempt: int) -> None:
        await asyncio.sleep(min(0.5 * (2**attempt), 2.0))
