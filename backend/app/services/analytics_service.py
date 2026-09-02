"""
Analytics service.

Computes a transparent, deterministic Repository Health Score and a set of
engineering metrics from already-fetched repository data. Nothing here
invents data — every number traces back to a real GitHub API response, and
anything that's an estimate is labeled as one.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.schemas.analytics import (
    ActivityEvent,
    EngineeringMetrics,
    HealthFactor,
    HealthScore,
    RepositoryAnalytics,
)

METHODOLOGY = (
    "Score is a weighted average of six factors, each 0-100: activity (25%), "
    "maintenance (15%), issue health (20%), pull request health (15%), "
    "release health (15%), and community engagement (10%). All factors are "
    "derived from data fetched for this repository at analysis time."
)


def _days_since(iso_timestamp: str | None) -> float | None:
    if not iso_timestamp:
        return None
    dt = datetime.fromisoformat(iso_timestamp.replace("Z", "+00:00"))
    return (datetime.now(timezone.utc) - dt).total_seconds() / 86400


def _clamp(value: float, low: int = 0, high: int = 100) -> int:
    return int(max(low, min(high, round(value))))


def _score_activity(pushed_at: str | None) -> HealthFactor:
    days = _days_since(pushed_at)
    if days is None:
        score = 30
        explanation = "No recent push data available."
    elif days <= 7:
        score = 100
        explanation = "Pushed to within the last week."
    elif days <= 30:
        score = 85
        explanation = "Pushed to within the last month."
    elif days <= 90:
        score = 60
        explanation = "Pushed to within the last 3 months."
    elif days <= 365:
        score = 35
        explanation = "Last push was over 3 months ago."
    else:
        score = 10
        explanation = "No pushes in over a year."
    return HealthFactor(name="Activity", score=score, explanation=explanation)


def _score_maintenance(is_archived: bool, open_issues: int, stars: int) -> HealthFactor:
    if is_archived:
        return HealthFactor(name="Maintenance", score=10, explanation="Repository is archived.")
    ratio = open_issues / max(stars, 1)
    if ratio < 0.02:
        score, explanation = 90, "Open issue count is low relative to stars."
    elif ratio < 0.08:
        score, explanation = 70, "Open issue count is moderate relative to stars."
    else:
        score, explanation = 45, "Open issue count is high relative to stars."
    return HealthFactor(name="Maintenance", score=score, explanation=explanation)


def _score_issue_health(issues: list[dict[str, Any]]) -> tuple[HealthFactor, float | None]:
    real_issues = [i for i in issues if "pull_request" not in i]
    if not real_issues:
        return HealthFactor(name="Issue Health", score=60, explanation="No recent issue data available."), None

    closed = [i for i in real_issues if i["state"] == "closed"]
    rate = (len(closed) / len(real_issues)) * 100
    score = _clamp(rate)
    explanation = f"{round(rate)}% of recently tracked issues are closed."
    return HealthFactor(name="Issue Health", score=score, explanation=explanation), round(rate, 1)


def _score_pr_health(pulls: list[dict[str, Any]]) -> tuple[HealthFactor, float | None]:
    closed = [p for p in pulls if p["state"] == "closed"]
    if not closed:
        return HealthFactor(name="Pull Request Health", score=60, explanation="No recently closed pull requests."), None

    merged = [p for p in closed if p.get("merged_at")]
    rate = (len(merged) / len(closed)) * 100
    score = _clamp(rate)
    explanation = f"{round(rate)}% of recently closed pull requests were merged."
    return HealthFactor(name="Pull Request Health", score=score, explanation=explanation), round(rate, 1)


def _score_release_health(releases: list[dict[str, Any]]) -> tuple[HealthFactor, float | None]:
    dated = [r for r in releases if r.get("published_at")]
    if len(dated) < 2:
        note = "No release history" if not dated else "Only one release on record"
        return HealthFactor(name="Release Health", score=40, explanation=f"{note}."), None

    timestamps = sorted(
        datetime.fromisoformat(r["published_at"].replace("Z", "+00:00")) for r in dated
    )
    gaps = [(b - a).total_seconds() / 86400 for a, b in zip(timestamps, timestamps[1:])]
    avg_gap = sum(gaps) / len(gaps)

    if avg_gap <= 30:
        score, explanation = 95, "Releases roughly every month or more often."
    elif avg_gap <= 90:
        score, explanation = 75, "Releases roughly every 1-3 months."
    elif avg_gap <= 180:
        score, explanation = 55, "Releases roughly every 3-6 months."
    else:
        score, explanation = 30, "Releases less than twice a year."
    return HealthFactor(name="Release Health", score=score, explanation=explanation), round(avg_gap, 1)


def _score_community(stars: int, forks: int, contributors_count: int) -> HealthFactor:
    signal = stars + (forks * 2) + (contributors_count * 5)
    if signal >= 5000:
        score, explanation = 95, "Strong community signal (stars, forks, contributors)."
    elif signal >= 500:
        score, explanation = 75, "Solid community signal."
    elif signal >= 50:
        score, explanation = 50, "Modest community signal."
    else:
        score, explanation = 25, "Limited community signal so far."
    return HealthFactor(name="Community Engagement", score=score, explanation=explanation)


def _bus_factor(contributors: list[dict[str, Any]]) -> int | None:
    if not contributors:
        return None
    total = sum(c.get("contributions", 0) for c in contributors)
    if total == 0:
        return None
    ranked = sorted(contributors, key=lambda c: c.get("contributions", 0), reverse=True)
    running = 0
    for i, c in enumerate(ranked, start=1):
        running += c.get("contributions", 0)
        if running / total >= 0.5:
            return i
    return len(ranked)


def compute_health_score(
    *,
    repo: dict[str, Any],
    issues: list[dict[str, Any]],
    pulls: list[dict[str, Any]],
    releases: list[dict[str, Any]],
    contributors: list[dict[str, Any]],
) -> HealthScore:
    factors = [
        _score_activity(repo.get("pushed_at")),
        _score_maintenance(
            repo.get("archived", False), repo.get("open_issues_count", 0), repo.get("stargazers_count", 0)
        ),
        _score_issue_health(issues)[0],
        _score_pr_health(pulls)[0],
        _score_release_health(releases)[0],
        _score_community(
            repo.get("stargazers_count", 0), repo.get("forks_count", 0), len(contributors)
        ),
    ]
    weights = [0.25, 0.15, 0.20, 0.15, 0.15, 0.10]
    overall = _clamp(sum(f.score * w for f, w in zip(factors, weights)))

    if overall >= 80:
        label = "Excellent"
    elif overall >= 60:
        label = "Good"
    elif overall >= 40:
        label = "Fair"
    else:
        label = "Needs attention"

    return HealthScore(overall=overall, label=label, factors=factors, methodology=METHODOLOGY)


def compute_engineering_metrics(
    *,
    issues: list[dict[str, Any]],
    pulls: list[dict[str, Any]],
    releases: list[dict[str, Any]],
    contributors: list[dict[str, Any]],
) -> EngineeringMetrics:
    _, issue_rate = _score_issue_health(issues)
    _, pr_rate = _score_pr_health(pulls)
    _, release_gap = _score_release_health(releases)
    bus_factor = _bus_factor(contributors)

    return EngineeringMetrics(
        issue_resolution_rate=issue_rate,
        pr_merge_rate=pr_rate,
        release_frequency_days=release_gap,
        bus_factor=bus_factor,
        is_estimate=True,
    )


def build_activity_timeline(
    *,
    issues: list[dict[str, Any]],
    pulls: list[dict[str, Any]],
    releases: list[dict[str, Any]],
    limit: int = 15,
) -> list[ActivityEvent]:
    events: list[ActivityEvent] = []

    for p in pulls:
        if p.get("merged_at"):
            events.append(
                ActivityEvent(
                    kind="pull_request_merged",
                    label=f"Pull request merged: {p['title']}",
                    occurred_at=p["merged_at"],
                    url=p.get("html_url"),
                )
            )

    for i in issues:
        if "pull_request" in i:
            continue
        events.append(
            ActivityEvent(
                kind="issue_opened",
                label=f"Issue opened: {i['title']}",
                occurred_at=i["created_at"],
                url=i.get("html_url"),
            )
        )
        if i.get("closed_at"):
            events.append(
                ActivityEvent(
                    kind="issue_closed",
                    label=f"Issue closed: {i['title']}",
                    occurred_at=i["closed_at"],
                    url=i.get("html_url"),
                )
            )

    for r in releases:
        if r.get("published_at"):
            events.append(
                ActivityEvent(
                    kind="release_published",
                    label=f"Release published: {r.get('name') or r['tag_name']}",
                    occurred_at=r["published_at"],
                    url=r.get("html_url"),
                )
            )

    events.sort(key=lambda e: e.occurred_at, reverse=True)
    return events[:limit]


def build_repository_analytics(
    *,
    repo: dict[str, Any],
    issues: list[dict[str, Any]],
    pulls: list[dict[str, Any]],
    releases: list[dict[str, Any]],
    contributors: list[dict[str, Any]],
) -> RepositoryAnalytics:
    return RepositoryAnalytics(
        health=compute_health_score(
            repo=repo, issues=issues, pulls=pulls, releases=releases, contributors=contributors
        ),
        metrics=compute_engineering_metrics(
            issues=issues, pulls=pulls, releases=releases, contributors=contributors
        ),
        activity=build_activity_timeline(issues=issues, pulls=pulls, releases=releases),
    )
