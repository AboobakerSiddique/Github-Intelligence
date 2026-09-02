from datetime import datetime, timedelta, timezone

from app.services.analytics_service import (
    build_activity_timeline,
    build_repository_analytics,
    compute_engineering_metrics,
    compute_health_score,
)

NOW = datetime.now(timezone.utc)


def _iso(days_ago: float) -> str:
    return (NOW - timedelta(days=days_ago)).isoformat().replace("+00:00", "Z")


ACTIVE_REPO = {
    "pushed_at": _iso(1),
    "archived": False,
    "open_issues_count": 5,
    "stargazers_count": 1000,
    "forks_count": 100,
}

HEALTHY_ISSUES = [
    {"state": "closed", "title": f"Fixed bug {i}", "created_at": _iso(20 + i)} for i in range(8)
] + [{"state": "open", "title": f"Open issue {i}", "created_at": _iso(2 + i)} for i in range(2)]

HEALTHY_PULLS = [
    {"state": "closed", "merged_at": _iso(5), "title": f"Merged PR {i}"} for i in range(9)
] + [{"state": "closed", "merged_at": None, "title": "Closed without merge"}]

HEALTHY_RELEASES = [
    {"published_at": _iso(10), "tag_name": "v3.0.0"},
    {"published_at": _iso(40), "tag_name": "v2.0.0"},
    {"published_at": _iso(70), "tag_name": "v1.0.0"},
]

CONTRIBUTORS = [{"login": "a", "contributions": 100}, {"login": "b", "contributions": 20}]


def test_health_score_is_deterministic():
    score_1 = compute_health_score(
        repo=ACTIVE_REPO,
        issues=HEALTHY_ISSUES,
        pulls=HEALTHY_PULLS,
        releases=HEALTHY_RELEASES,
        contributors=CONTRIBUTORS,
    )
    score_2 = compute_health_score(
        repo=ACTIVE_REPO,
        issues=HEALTHY_ISSUES,
        pulls=HEALTHY_PULLS,
        releases=HEALTHY_RELEASES,
        contributors=CONTRIBUTORS,
    )
    assert score_1.overall == score_2.overall
    assert 0 <= score_1.overall <= 100
    assert len(score_1.factors) == 6


def test_healthy_repository_scores_well():
    score = compute_health_score(
        repo=ACTIVE_REPO,
        issues=HEALTHY_ISSUES,
        pulls=HEALTHY_PULLS,
        releases=HEALTHY_RELEASES,
        contributors=CONTRIBUTORS,
    )
    assert score.overall >= 60
    assert score.label in ("Good", "Excellent")


def test_archived_repository_scores_poorly_on_maintenance():
    archived_repo = {**ACTIVE_REPO, "archived": True, "pushed_at": _iso(900)}
    score = compute_health_score(
        repo=archived_repo, issues=[], pulls=[], releases=[], contributors=[]
    )
    maintenance = next(f for f in score.factors if f.name == "Maintenance")
    assert maintenance.score <= 20
    assert score.overall < 60


def test_engineering_metrics_computed_from_data():
    metrics = compute_engineering_metrics(
        issues=HEALTHY_ISSUES, pulls=HEALTHY_PULLS, releases=HEALTHY_RELEASES, contributors=CONTRIBUTORS
    )
    assert metrics.issue_resolution_rate == 80.0
    assert metrics.pr_merge_rate == 90.0
    assert metrics.bus_factor == 1  # top contributor alone accounts for >50%
    assert metrics.is_estimate is True


def test_engineering_metrics_handle_empty_data():
    metrics = compute_engineering_metrics(issues=[], pulls=[], releases=[], contributors=[])
    assert metrics.issue_resolution_rate is None
    assert metrics.pr_merge_rate is None
    assert metrics.bus_factor is None


def test_activity_timeline_sorted_and_limited():
    issues = [
        {"title": "Old issue", "created_at": _iso(50), "html_url": "u1"},
        {"title": "New issue", "created_at": _iso(1), "html_url": "u2"},
    ]
    releases = [{"tag_name": "v1", "published_at": _iso(10), "html_url": "u3"}]
    timeline = build_activity_timeline(issues=issues, pulls=[], releases=releases, limit=2)

    assert len(timeline) == 2
    # Most recent first.
    assert timeline[0].occurred_at >= timeline[1].occurred_at


def test_build_repository_analytics_shapes_full_response():
    analytics = build_repository_analytics(
        repo=ACTIVE_REPO,
        issues=HEALTHY_ISSUES,
        pulls=HEALTHY_PULLS,
        releases=HEALTHY_RELEASES,
        contributors=CONTRIBUTORS,
    )
    assert analytics.health.overall > 0
    assert analytics.metrics.bus_factor == 1
    assert isinstance(analytics.activity, list)
