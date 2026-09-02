from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.api.dependencies import get_gemini_client, get_github_client
from app.api.error_handling import ERROR_RESPONSES, handle_github_errors
from app.clients.gemini_client import AIUnavailableError, GeminiClient
from app.clients.github_client import GitHubClient
from app.schemas.ai import AISummary, AskRequest, AskResponse
from app.schemas.errors import ErrorResponse
from app.services import ai_service, repository_service
from app.utils.logger import get_logger

router = APIRouter(prefix="/api/repositories", tags=["ai"])
logger = get_logger(__name__)

AI_ERROR_RESPONSES = {
    **ERROR_RESPONSES,
    503: {"model": ErrorResponse, "description": "AI service unavailable"},
}


def _ai_unavailable(detail: str) -> JSONResponse:
    return JSONResponse(
        status_code=503,
        content=ErrorResponse(
            error="ai_unavailable",
            message="AI insights are temporarily unavailable",
            detail=detail,
        ).model_dump(),
    )


@router.post(
    "/{owner}/{repo}/ai/summary",
    response_model=AISummary,
    responses=AI_ERROR_RESPONSES,
    summary="Generate an AI engineering summary",
    description=(
        "Uses Gemini to interpret real repository data (never invented) "
        "into a plain-language summary, strengths, risks, and recommendations."
    ),
)
async def post_ai_summary(
    owner: str,
    repo: str,
    client: GitHubClient = Depends(get_github_client),
    gemini: GeminiClient = Depends(get_gemini_client),
):
    data = await handle_github_errors(
        repository_service.gather_raw_repository_data(client, owner, repo)
    )
    if isinstance(data, JSONResponse):
        return data

    try:
        return await ai_service.generate_summary(gemini, data)
    except AIUnavailableError as exc:
        return _ai_unavailable(str(exc))


@router.post(
    "/{owner}/{repo}/ai/ask",
    response_model=AskResponse,
    responses=AI_ERROR_RESPONSES,
    summary="Ask this repository a question",
    description="Answers a free-form question about the repository using only fetched GitHub data.",
)
async def post_ai_ask(
    owner: str,
    repo: str,
    body: AskRequest,
    client: GitHubClient = Depends(get_github_client),
    gemini: GeminiClient = Depends(get_gemini_client),
):
    data = await handle_github_errors(
        repository_service.gather_raw_repository_data(client, owner, repo)
    )
    if isinstance(data, JSONResponse):
        return data

    try:
        answer = await ai_service.answer_question(gemini, data, body.question)
        return AskResponse(question=body.question, answer=answer)
    except AIUnavailableError as exc:
        return _ai_unavailable(str(exc))
