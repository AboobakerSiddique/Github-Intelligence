import httpx
import pytest
import respx

from app.clients.exceptions import (
    RateLimitExceededError,
    RepositoryNotFoundError,
)
from app.clients.github_client import GitHubClient


@pytest.mark.asyncio
@respx.mock
async def test_get_repository_returns_json():
    respx.get("https://api.github.com/repos/octocat/hello-world").mock(
        return_value=httpx.Response(200, json={"name": "hello-world", "id": 1})
    )

    async with GitHubClient() as client:
        result = await client.get_repository("octocat", "hello-world")

    assert result == {"name": "hello-world", "id": 1}


@pytest.mark.asyncio
@respx.mock
async def test_get_repository_raises_not_found_on_404():
    respx.get("https://api.github.com/repos/octocat/missing").mock(
        return_value=httpx.Response(404, json={"message": "Not Found"})
    )

    async with GitHubClient() as client:
        with pytest.raises(RepositoryNotFoundError):
            await client.get_repository("octocat", "missing")


@pytest.mark.asyncio
@respx.mock
async def test_get_repository_raises_rate_limit_error():
    respx.get("https://api.github.com/repos/octocat/hello-world").mock(
        return_value=httpx.Response(
            403,
            json={"message": "API rate limit exceeded"},
            headers={"x-ratelimit-remaining": "0", "x-ratelimit-reset": "1700000000"},
        )
    )

    async with GitHubClient() as client:
        with pytest.raises(RateLimitExceededError) as exc_info:
            await client.get_repository("octocat", "hello-world")

    assert exc_info.value.reset_at == 1700000000


@pytest.mark.asyncio
@respx.mock
async def test_get_repository_retries_on_502_then_succeeds():
    route = respx.get("https://api.github.com/repos/octocat/hello-world")
    route.side_effect = [
        httpx.Response(502),
        httpx.Response(200, json={"name": "hello-world"}),
    ]

    async with GitHubClient() as client:
        result = await client.get_repository("octocat", "hello-world")

    assert result == {"name": "hello-world"}
    assert route.call_count == 2


@pytest.mark.asyncio
@respx.mock
async def test_get_languages_returns_byte_counts():
    respx.get("https://api.github.com/repos/octocat/hello-world/languages").mock(
        return_value=httpx.Response(200, json={"Python": 1000, "TypeScript": 500})
    )

    async with GitHubClient() as client:
        result = await client.get_languages("octocat", "hello-world")

    assert result == {"Python": 1000, "TypeScript": 500}


@pytest.mark.asyncio
@respx.mock
async def test_get_contributors_paginates_until_short_page():
    base = "https://api.github.com/repos/octocat/hello-world/contributors"
    respx.get(base, params={"page": "1", "per_page": "30", "anon": "false"}).mock(
        return_value=httpx.Response(200, json=[{"login": f"user{i}"} for i in range(30)])
    )
    respx.get(base, params={"page": "2", "per_page": "30", "anon": "false"}).mock(
        return_value=httpx.Response(200, json=[{"login": "user30"}])
    )

    async with GitHubClient() as client:
        result = await client.get_contributors("octocat", "hello-world", max_pages=3)

    assert len(result) == 31
