from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.api.dependencies import get_github_client
from app.api.error_handling import ERROR_RESPONSES, handle_github_errors
from app.clients.github_client import GitHubClient
from app.schemas.analytics import RepositoryAnalytics
from app.services import analytics_service, repository_service

router = APIRouter(prefix="/api/repositories", tags=["analytics"])


@router.get(
    "/{owner}/{repo}/analytics",
    response_model=RepositoryAnalytics,
    responses=ERROR_RESPONSES,
    summary="Get repository health score, engineering metrics, and activity timeline",
    description=(
        "Computes a deterministic Repository Health Score plus engineering "
        "metrics (issue resolution rate, PR merge rate, release frequency, "
        "bus factor) and a recent activity timeline, all from real GitHub data."
    ),
)
async def get_analytics(owner: str, repo: str, client: GitHubClient = Depends(get_github_client)):
    data = await handle_github_errors(
        repository_service.gather_raw_repository_data(client, owner, repo)
    )
    if isinstance(data, JSONResponse):
        return data

    return analytics_service.build_repository_analytics(
        repo=data["repo"],
        issues=data["issues"],
        pulls=data["pulls"],
        releases=data["releases"],
        contributors=data["contributors"],
    )
