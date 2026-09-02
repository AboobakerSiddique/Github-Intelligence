from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.api.dependencies import get_github_client
from app.api.error_handling import ERROR_RESPONSES, handle_github_errors
from app.clients.github_client import GitHubClient
from app.schemas.contributors import ContributorsSummary
from app.schemas.issues import IssuesSummary
from app.schemas.pulls import PullsSummary
from app.schemas.releases import ReleasesSummary
from app.schemas.repository import RepositoryLanguagesResponse, RepositoryOverview
from app.services import repository_service

router = APIRouter(prefix="/api/repositories", tags=["repositories"])


@router.get(
    "/{owner}/{repo}",
    response_model=RepositoryOverview,
    responses=ERROR_RESPONSES,
    summary="Get repository overview",
    description="Fetches and normalizes core repository metadata and language breakdown.",
)
async def get_repository(owner: str, repo: str, client: GitHubClient = Depends(get_github_client)):
    return await handle_github_errors(repository_service.get_repository_overview(client, owner, repo))


@router.get(
    "/{owner}/{repo}/languages",
    response_model=RepositoryLanguagesResponse,
    responses=ERROR_RESPONSES,
    summary="Get repository language breakdown",
    description="Returns the repository's languages as percentages of total code bytes.",
)
async def get_languages(owner: str, repo: str, client: GitHubClient = Depends(get_github_client)):
    languages = await handle_github_errors(
        repository_service.get_repository_languages(client, owner, repo)
    )
    if isinstance(languages, JSONResponse):
        return languages
    return RepositoryLanguagesResponse(languages=languages)


@router.get(
    "/{owner}/{repo}/issues",
    response_model=IssuesSummary,
    responses=ERROR_RESPONSES,
    summary="Get repository issues",
    description="Returns open/closed counts and a list of recent issues (pull requests excluded).",
)
async def get_issues(owner: str, repo: str, client: GitHubClient = Depends(get_github_client)):
    return await handle_github_errors(repository_service.get_issues_summary(client, owner, repo))


@router.get(
    "/{owner}/{repo}/pulls",
    response_model=PullsSummary,
    responses=ERROR_RESPONSES,
    summary="Get repository pull requests",
    description="Returns open/merged/closed counts and a list of recent pull requests.",
)
async def get_pulls(owner: str, repo: str, client: GitHubClient = Depends(get_github_client)):
    return await handle_github_errors(repository_service.get_pulls_summary(client, owner, repo))


@router.get(
    "/{owner}/{repo}/contributors",
    response_model=ContributorsSummary,
    responses=ERROR_RESPONSES,
    summary="Get repository contributors",
    description="Returns top contributors by contribution count, with an approximate bus factor.",
)
async def get_contributors(owner: str, repo: str, client: GitHubClient = Depends(get_github_client)):
    return await handle_github_errors(repository_service.get_contributors_summary(client, owner, repo))


@router.get(
    "/{owner}/{repo}/releases",
    response_model=ReleasesSummary,
    responses=ERROR_RESPONSES,
    summary="Get repository releases",
    description="Returns the latest release and recent release history.",
)
async def get_releases(owner: str, repo: str, client: GitHubClient = Depends(get_github_client)):
    return await handle_github_errors(repository_service.get_releases_summary(client, owner, repo))
