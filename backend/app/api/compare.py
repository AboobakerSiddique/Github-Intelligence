import asyncio

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.api.dependencies import get_github_client
from app.api.error_handling import handle_github_errors
from app.clients.exceptions import GitHubClientError
from app.clients.github_client import GitHubClient
from app.schemas.compare import CompareRequest, CompareResponse, RepositoryComparisonEntry
from app.schemas.errors import ErrorResponse
from app.services import analytics_service, repository_service

router = APIRouter(prefix="/api", tags=["compare"])


def _split(ref: str) -> tuple[str, str]:
    owner, _, repo = ref.partition("/")
    return owner, repo


@router.post(
    "/compare",
    response_model=CompareResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid repository reference"},
        404: {"model": ErrorResponse, "description": "One or more repositories not found"},
    },
    summary="Compare two repositories",
    description="Fetches and normalizes data for two repositories side by side, including health scores.",
)
async def compare_repositories(
    body: CompareRequest, client: GitHubClient = Depends(get_github_client)
):
    refs = [_split(ref) for ref in body.repositories]
    if any(not owner or not repo for owner, repo in refs):
        return JSONResponse(
            status_code=400,
            content=ErrorResponse(
                error="invalid_repository",
                message="Invalid repository reference",
                detail="Each repository must be in owner/repository format.",
            ).model_dump(),
        )

    try:
        raw_data_list = await asyncio.gather(
            *[repository_service.gather_raw_repository_data(client, owner, repo) for owner, repo in refs]
        )
    except GitHubClientError:
        return await handle_github_errors(_raise_first_error(client, refs))

    entries = []
    for data in raw_data_list:
        overview = await repository_service.get_repository_overview_from_raw(data)
        health = analytics_service.compute_health_score(
            repo=data["repo"],
            issues=data["issues"],
            pulls=data["pulls"],
            releases=data["releases"],
            contributors=data["contributors"],
        )
        entries.append(
            RepositoryComparisonEntry(
                overview=overview,
                health_score=health.overall,
                open_issues=data["repo"].get("open_issues_count", 0),
                contributors_count=len(data["contributors"]),
            )
        )

    return CompareResponse(entries=entries)


async def _raise_first_error(client: GitHubClient, refs: list[tuple[str, str]]):
    # Re-fetch sequentially so the first failing repository's specific
    # error (404 vs rate-limit vs upstream) surfaces to handle_github_errors.
    for owner, repo in refs:
        await repository_service.gather_raw_repository_data(client, owner, repo)
