"""
Shared error handling for routes that call into GitHub-backed services.

Centralizing this means every router returns the exact same error shape —
no stack traces, no internals, just a friendly, consistent body.
"""
from __future__ import annotations

from typing import Awaitable, TypeVar

from fastapi.responses import JSONResponse

from app.clients.exceptions import (
    GitHubTimeoutError,
    GitHubUpstreamError,
    RateLimitExceededError,
    RepositoryNotFoundError,
)
from app.schemas.errors import ErrorResponse
from app.utils.logger import get_logger

logger = get_logger(__name__)

T = TypeVar("T")

ERROR_RESPONSES = {
    404: {"model": ErrorResponse, "description": "Repository not found"},
    429: {"model": ErrorResponse, "description": "GitHub API rate limit reached"},
    502: {"model": ErrorResponse, "description": "GitHub API failure"},
    504: {"model": ErrorResponse, "description": "GitHub API timeout"},
}


async def handle_github_errors(coro: Awaitable[T]) -> T | JSONResponse:
    """Runs a service call and maps GitHub client errors to friendly HTTP responses."""
    try:
        return await coro
    except RepositoryNotFoundError as exc:
        return not_found(exc.owner, exc.repo)
    except RateLimitExceededError as exc:
        return rate_limited(exc.reset_at)
    except GitHubTimeoutError:
        return timeout()
    except GitHubUpstreamError as exc:
        return upstream_failure(exc)


def not_found(owner: str, repo: str) -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content=ErrorResponse(
            error="repository_not_found",
            message="Repository not found",
            detail=f"We couldn't find {owner}/{repo}. Check the repository URL and try again.",
        ).model_dump(),
    )


def rate_limited(reset_at: int | None) -> JSONResponse:
    return JSONResponse(
        status_code=429,
        content=ErrorResponse(
            error="rate_limit_exceeded",
            message="GitHub API limit reached",
            detail="We've temporarily reached GitHub's API limit. Please try again later.",
        ).model_dump()
        | ({"reset_at": reset_at} if reset_at else {}),
    )


def timeout() -> JSONResponse:
    return JSONResponse(
        status_code=504,
        content=ErrorResponse(
            error="github_timeout",
            message="GitHub took too long to respond",
            detail="Please try again in a moment.",
        ).model_dump(),
    )


def upstream_failure(exc: GitHubUpstreamError) -> JSONResponse:
    logger.error("Unhandled GitHub upstream error | status=%s", exc.status_code)
    return JSONResponse(
        status_code=502,
        content=ErrorResponse(
            error="github_upstream_error",
            message="GitHub API is currently unavailable",
            detail="Please try again later.",
        ).model_dump(),
    )
