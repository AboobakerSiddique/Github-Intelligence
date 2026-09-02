from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse, PlainTextResponse, Response

from app.api.dependencies import get_gemini_client, get_github_client
from app.api.error_handling import ERROR_RESPONSES, handle_github_errors
from app.clients.gemini_client import AIUnavailableError, GeminiClient
from app.clients.github_client import GitHubClient
from app.services import ai_service, analytics_service, export_service, pdf_service, repository_service

router = APIRouter(prefix="/api/repositories", tags=["export"])


async def _gather_export_data(owner: str, repo: str, include_ai: bool, client, gemini):
    """Shared fetch + compute step for both markdown and PDF export."""
    data = await handle_github_errors(
        repository_service.gather_raw_repository_data(client, owner, repo)
    )
    if isinstance(data, JSONResponse):
        return data, None, None, None

    overview = await handle_github_errors(repository_service.get_repository_overview(client, owner, repo))
    if isinstance(overview, JSONResponse):
        return overview, None, None, None

    analytics = analytics_service.build_repository_analytics(
        repo=data["repo"],
        issues=data["issues"],
        pulls=data["pulls"],
        releases=data["releases"],
        contributors=data["contributors"],
    )

    ai_summary = None
    if include_ai:
        try:
            ai_summary = await ai_service.generate_summary(gemini, data)
        except AIUnavailableError:
            ai_summary = None  # export still succeeds without AI section

    return None, overview, analytics, ai_summary


@router.get(
    "/{owner}/{repo}/export/markdown",
    responses=ERROR_RESPONSES,
    summary="Export the repository analysis as a Markdown report",
    description=(
        "Fetches repository data, computes health/analytics, optionally "
        "includes an AI summary, and returns a formatted Markdown report."
    ),
)
async def export_markdown(
    owner: str,
    repo: str,
    include_ai: bool = True,
    client: GitHubClient = Depends(get_github_client),
    gemini: GeminiClient = Depends(get_gemini_client),
):
    error, overview, analytics, ai_summary = await _gather_export_data(owner, repo, include_ai, client, gemini)
    if error is not None:
        return error

    markdown = export_service.build_markdown_report(overview, analytics, ai_summary)

    filename = f"{owner}-{repo}-health-report.md"
    return PlainTextResponse(
        content=markdown,
        media_type="text/markdown",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get(
    "/{owner}/{repo}/export/pdf",
    responses=ERROR_RESPONSES,
    summary="Export the repository analysis as a PDF report",
    description=(
        "Fetches repository data, computes health/analytics, optionally "
        "includes an AI summary, and returns a formatted PDF report."
    ),
)
async def export_pdf(
    owner: str,
    repo: str,
    include_ai: bool = True,
    client: GitHubClient = Depends(get_github_client),
    gemini: GeminiClient = Depends(get_gemini_client),
):
    error, overview, analytics, ai_summary = await _gather_export_data(owner, repo, include_ai, client, gemini)
    if error is not None:
        return error

    pdf_bytes = pdf_service.build_pdf_report(overview, analytics, ai_summary)

    filename = f"{owner}-{repo}-health-report.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
