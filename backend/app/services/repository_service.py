"""
Repository service.

Owns the logic for turning raw GitHub API responses into the application's
own normalized schemas. API routes should never touch raw GitHub JSON —
they call into this service and get back Pydantic models.
"""
from __future__ import annotations

import asyncio
from typing import Any

from app.clients.github_client import GitHubClient
from app.schemas.contributors import Contributor, ContributorsSummary
from app.schemas.issues import Issue, IssueAuthor, IssuesSummary
from app.schemas.pulls import PullAuthor, PullRequest, PullsSummary
from app.schemas.releases import Release, ReleasesSummary
from app.schemas.repository import (
    LanguageBreakdown,
    RepositoryOverview,
    RepositoryOwner,
)
from app.utils.cache import cache, cache_key
from app.utils.logger import get_logger

logger = get_logger(__name__)

RAW_REPO_TTL = 120


def _build_languages(raw_languages: dict[str, int]) -> list[LanguageBreakdown]:
    total_bytes = sum(raw_languages.values())
    if total_bytes == 0:
        return []

    breakdown = [
        LanguageBreakdown(
            name=name,
            bytes=count,
            percentage=round((count / total_bytes) * 100, 1),
        )
        for name, count in raw_languages.items()
    ]
    return sorted(breakdown, key=lambda lang: lang.bytes, reverse=True)


def _build_owner(raw_owner: dict[str, Any]) -> RepositoryOwner:
    return RepositoryOwner(
        login=raw_owner["login"],
        avatar_url=raw_owner["avatar_url"],
        html_url=raw_owner["html_url"],
        type=raw_owner["type"],
    )


async def get_repository_overview(
    client: GitHubClient, owner: str, repo: str
) -> RepositoryOverview:
    """Fetch and normalize a repository's core metadata + language breakdown."""
    raw_repo, raw_languages = await asyncio.gather(
        client.get_repository(owner, repo),
        client.get_languages(owner, repo),
    )
    return _build_overview(raw_repo, raw_languages)


async def get_repository_overview_from_raw(data: dict[str, Any]) -> RepositoryOverview:
    """Builds a RepositoryOverview from an already-fetched raw data bundle (see gather_raw_repository_data)."""
    return _build_overview(data["repo"], data["languages"])


def _build_overview(raw_repo: dict[str, Any], raw_languages: dict[str, int]) -> RepositoryOverview:
    license_info = raw_repo.get("license") or {}

    return RepositoryOverview(
        owner=_build_owner(raw_repo["owner"]),
        name=raw_repo["name"],
        full_name=raw_repo["full_name"],
        description=raw_repo.get("description"),
        html_url=raw_repo["html_url"],
        homepage=raw_repo.get("homepage") or None,
        stars=raw_repo.get("stargazers_count", 0),
        forks=raw_repo.get("forks_count", 0),
        watchers=raw_repo.get("subscribers_count", raw_repo.get("watchers_count", 0)),
        open_issues=raw_repo.get("open_issues_count", 0),
        default_branch=raw_repo.get("default_branch", "main"),
        primary_language=raw_repo.get("language"),
        topics=raw_repo.get("topics", []) or [],
        is_archived=raw_repo.get("archived", False),
        is_fork=raw_repo.get("fork", False),
        license_name=license_info.get("name"),
        created_at=raw_repo["created_at"],
        updated_at=raw_repo["updated_at"],
        pushed_at=raw_repo.get("pushed_at"),
        languages=_build_languages(raw_languages),
    )


async def get_repository_languages(
    client: GitHubClient, owner: str, repo: str
) -> list[LanguageBreakdown]:
    raw_languages = await client.get_languages(owner, repo)
    return _build_languages(raw_languages)


def _build_issues_summary(raw_issues: list[dict[str, Any]]) -> tuple[IssuesSummary, list[dict[str, Any]]]:
    real_issues = [i for i in raw_issues if "pull_request" not in i]
    issues = [
        Issue(
            number=i["number"],
            title=i["title"],
            state=i["state"],
            author=IssueAuthor(login=i["user"]["login"], avatar_url=i["user"]["avatar_url"]),
            labels=[label["name"] if isinstance(label, dict) else label for label in i.get("labels", [])],
            comments=i.get("comments", 0),
            html_url=i["html_url"],
            created_at=i["created_at"],
            closed_at=i.get("closed_at"),
        )
        for i in real_issues
    ]
    open_count = sum(1 for i in issues if i.state == "open")
    closed_count = sum(1 for i in issues if i.state == "closed")
    summary = IssuesSummary(
        open_count=open_count,
        closed_count=closed_count,
        total_count=len(issues),
        issues=issues[:30],
    )
    return summary, real_issues


def _build_pulls_summary(raw_pulls: list[dict[str, Any]]) -> PullsSummary:
    pulls = [
        PullRequest(
            number=p["number"],
            title=p["title"],
            state=p["state"],
            is_merged=bool(p.get("merged_at")),
            author=PullAuthor(login=p["user"]["login"], avatar_url=p["user"]["avatar_url"]),
            html_url=p["html_url"],
            created_at=p["created_at"],
            closed_at=p.get("closed_at"),
            merged_at=p.get("merged_at"),
        )
        for p in raw_pulls
    ]
    open_count = sum(1 for p in pulls if p.state == "open")
    merged_count = sum(1 for p in pulls if p.is_merged)
    closed_count = sum(1 for p in pulls if p.state == "closed" and not p.is_merged)
    return PullsSummary(
        open_count=open_count,
        merged_count=merged_count,
        closed_count=closed_count,
        total_count=len(pulls),
        pull_requests=pulls[:30],
    )


def _build_contributors_summary(raw_contributors: list[dict[str, Any]]) -> ContributorsSummary:
    total = sum(c.get("contributions", 0) for c in raw_contributors)
    contributors = [
        Contributor(
            login=c["login"],
            avatar_url=c["avatar_url"],
            html_url=c["html_url"],
            contributions=c.get("contributions", 0),
            percentage=round((c.get("contributions", 0) / total) * 100, 1) if total else 0.0,
        )
        for c in raw_contributors
    ]
    contributors.sort(key=lambda c: c.contributions, reverse=True)

    running = 0
    bus_factor = len(contributors)
    for i, c in enumerate(contributors, start=1):
        running += c.contributions
        if total and running / total >= 0.5:
            bus_factor = i
            break

    note = (
        f"The top {bus_factor} contributor{'s' if bus_factor != 1 else ''} account for "
        "at least half of all tracked contributions."
        if total
        else "Not enough contribution data to estimate."
    )

    return ContributorsSummary(
        total_contributors=len(contributors),
        contributors=contributors[:20],
        bus_factor=bus_factor,
        bus_factor_note=note,
    )


def _build_releases_summary(raw_releases: list[dict[str, Any]]) -> ReleasesSummary:
    releases = [
        Release(
            tag_name=r["tag_name"],
            name=r.get("name"),
            html_url=r["html_url"],
            is_prerelease=r.get("prerelease", False),
            published_at=r.get("published_at"),
        )
        for r in raw_releases
    ]
    return ReleasesSummary(latest=releases[0] if releases else None, releases=releases)


async def get_issues_summary(client: GitHubClient, owner: str, repo: str) -> IssuesSummary:
    raw_issues = await client.get_issues(owner, repo)
    summary, _ = _build_issues_summary(raw_issues)
    return summary


async def get_pulls_summary(client: GitHubClient, owner: str, repo: str) -> PullsSummary:
    raw_pulls = await client.get_pulls(owner, repo)
    return _build_pulls_summary(raw_pulls)


async def get_contributors_summary(client: GitHubClient, owner: str, repo: str) -> ContributorsSummary:
    raw_contributors = await client.get_contributors(owner, repo)
    return _build_contributors_summary(raw_contributors)


async def get_releases_summary(client: GitHubClient, owner: str, repo: str) -> ReleasesSummary:
    raw_releases = await client.get_releases(owner, repo)
    return _build_releases_summary(raw_releases)


async def gather_raw_repository_data(
    client: GitHubClient, owner: str, repo: str
) -> dict[str, Any]:
    """
    Fetches (and caches) the full raw dataset for a repository in one shot —
    used by analytics, AI, and comparison, which all need the same underlying
    data. Cached briefly to avoid duplicate GitHub calls across endpoints
    hit back-to-back for the same repository.
    """
    key = cache_key("raw_repo_data", owner, repo)
    cached = cache.get(key)
    if cached is not None:
        return cached

    raw_repo, raw_languages, raw_issues, raw_pulls, raw_releases, raw_contributors = await asyncio.gather(
        client.get_repository(owner, repo),
        client.get_languages(owner, repo),
        client.get_issues(owner, repo),
        client.get_pulls(owner, repo),
        client.get_releases(owner, repo),
        client.get_contributors(owner, repo),
    )

    data = {
        "repo": raw_repo,
        "languages": raw_languages,
        "issues": raw_issues,
        "pulls": raw_pulls,
        "releases": raw_releases,
        "contributors": raw_contributors,
    }
    cache.set(key, data, ttl_seconds=RAW_REPO_TTL)
    return data
