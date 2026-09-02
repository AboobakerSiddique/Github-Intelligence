from __future__ import annotations

from pydantic import BaseModel, Field


class HealthFactor(BaseModel):
    name: str
    score: int = Field(..., ge=0, le=100)
    explanation: str


class HealthScore(BaseModel):
    overall: int = Field(..., ge=0, le=100)
    label: str  # "Excellent" | "Good" | "Fair" | "Needs attention"
    factors: list[HealthFactor]
    methodology: str


class EngineeringMetrics(BaseModel):
    issue_resolution_rate: float | None = Field(
        None, description="Percentage of issues closed, of those created. Estimate."
    )
    pr_merge_rate: float | None = Field(
        None, description="Percentage of pull requests merged, of those closed. Estimate."
    )
    release_frequency_days: float | None = Field(
        None, description="Average days between recent releases. Estimate."
    )
    bus_factor: int | None = Field(
        None, description="Approximate number of contributors responsible for the majority of commits."
    )
    is_estimate: bool = True


class ActivityEvent(BaseModel):
    kind: str  # "pull_request_merged" | "issue_opened" | "release_published" | "issue_closed"
    label: str
    occurred_at: str
    url: str | None = None


class RepositoryAnalytics(BaseModel):
    health: HealthScore
    metrics: EngineeringMetrics
    activity: list[ActivityEvent]
