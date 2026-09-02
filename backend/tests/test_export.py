from app.schemas.ai import AISummary
from app.schemas.repository import RepositoryOverview, RepositoryOwner
from app.services import analytics_service, export_service, pdf_service
from tests.test_analytics import (
    ACTIVE_REPO,
    CONTRIBUTORS,
    HEALTHY_ISSUES,
    HEALTHY_PULLS,
    HEALTHY_RELEASES,
)

OVERVIEW = RepositoryOverview(
    owner=RepositoryOwner(
        login="octocat",
        avatar_url="https://example.com/avatar.png",
        html_url="https://github.com/octocat",
        type="User",
    ),
    name="hello-world",
    full_name="octocat/hello-world",
    description="A test repository.",
    html_url="https://github.com/octocat/hello-world",
    stars=1000,
    forks=100,
    watchers=1000,
    open_issues=5,
    default_branch="main",
    is_archived=False,
    is_fork=False,
    created_at="2020-01-01T00:00:00Z",
    updated_at="2026-01-01T00:00:00Z",
)

ANALYTICS = analytics_service.build_repository_analytics(
    repo=ACTIVE_REPO,
    issues=HEALTHY_ISSUES,
    pulls=HEALTHY_PULLS,
    releases=HEALTHY_RELEASES,
    contributors=CONTRIBUTORS,
)

AI_SUMMARY = AISummary(
    summary="This repository is actively maintained.",
    strengths=["Fast issue resolution"],
    risks=["Low bus factor"],
    recommendations=["Add more maintainers"],
)


def test_markdown_report_includes_core_sections():
    markdown = export_service.build_markdown_report(OVERVIEW, ANALYTICS)

    assert "# Repository Health Report — octocat/hello-world" in markdown
    assert "## Health Score" in markdown
    assert "## Engineering Metrics" in markdown
    assert "## Recent Activity" in markdown
    assert str(ANALYTICS.health.overall) in markdown


def test_markdown_report_includes_ai_summary_when_provided():
    markdown = export_service.build_markdown_report(OVERVIEW, ANALYTICS, AI_SUMMARY)

    assert "## AI Summary" in markdown
    assert "This repository is actively maintained." in markdown
    assert "Fast issue resolution" in markdown
    assert "Add more maintainers" in markdown


def test_markdown_report_omits_ai_section_when_absent():
    markdown = export_service.build_markdown_report(OVERVIEW, ANALYTICS, ai_summary=None)

    assert "## AI Summary" not in markdown


def test_pdf_report_generates_valid_pdf_bytes():
    pdf_bytes = pdf_service.build_pdf_report(OVERVIEW, ANALYTICS, AI_SUMMARY)

    assert isinstance(pdf_bytes, bytes)
    assert pdf_bytes.startswith(b"%PDF-")
    assert len(pdf_bytes) > 500  # sanity check it's not an empty/broken document


def test_pdf_report_generates_without_ai_summary():
    pdf_bytes = pdf_service.build_pdf_report(OVERVIEW, ANALYTICS, ai_summary=None)

    assert pdf_bytes.startswith(b"%PDF-")
