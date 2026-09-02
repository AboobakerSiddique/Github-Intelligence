import pytest

from app.clients.gemini_client import AIUnavailableError, GeminiClient
from app.services import ai_service

RAW_DATA = {
    "repo": {
        "full_name": "octocat/hello-world",
        "description": "A demo repo",
        "language": "Python",
        "topics": ["demo"],
        "stargazers_count": 10,
        "forks_count": 2,
        "open_issues_count": 1,
        "archived": False,
        "license": {"name": "MIT License"},
        "created_at": "2020-01-01T00:00:00Z",
        "pushed_at": "2024-01-01T00:00:00Z",
    },
    "languages": {"Python": 1000},
    "issues": [{"title": "Bug", "state": "open"}],
    "pulls": [{"title": "Add feature"}],
    "releases": [{"tag_name": "v1.0.0"}],
    "contributors": [{"login": "octocat"}],
}


class FakeGemini(GeminiClient):
    def __init__(self, response_text: str):
        self._response_text = response_text

    async def generate(self, prompt: str, *, model: str = "gemini-2.0-flash") -> str:
        self.last_prompt = prompt
        return self._response_text


@pytest.mark.asyncio
async def test_generate_summary_parses_valid_json():
    fake = FakeGemini(
        '{"summary": "A demo repo.", "strengths": ["Simple"], '
        '"risks": ["Small"], "recommendations": ["Add tests"]}'
    )
    summary = await ai_service.generate_summary(fake, RAW_DATA)

    assert summary.summary == "A demo repo."
    assert summary.strengths == ["Simple"]
    assert "octocat/hello-world" in fake.last_prompt


@pytest.mark.asyncio
async def test_generate_summary_strips_markdown_fences():
    fake = FakeGemini('```json\n{"summary": "ok", "strengths": [], "risks": [], "recommendations": []}\n```')
    summary = await ai_service.generate_summary(fake, RAW_DATA)
    assert summary.summary == "ok"


@pytest.mark.asyncio
async def test_generate_summary_raises_on_malformed_json():
    fake = FakeGemini("not json at all")
    with pytest.raises(AIUnavailableError):
        await ai_service.generate_summary(fake, RAW_DATA)


@pytest.mark.asyncio
async def test_answer_question_includes_question_in_prompt():
    fake = FakeGemini("This repo uses Python.")
    answer = await ai_service.answer_question(fake, RAW_DATA, "What language is this?")

    assert answer == "This repo uses Python."
    assert "What language is this?" in fake.last_prompt
    assert "octocat/hello-world" in fake.last_prompt
