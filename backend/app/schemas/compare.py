from __future__ import annotations

from pydantic import BaseModel, Field

from app.schemas.repository import RepositoryOverview


class CompareRequest(BaseModel):
    repositories: list[str] = Field(
        ..., min_length=2, max_length=2, description="Two 'owner/repo' strings to compare."
    )


class RepositoryComparisonEntry(BaseModel):
    overview: RepositoryOverview
    health_score: int
    open_issues: int
    contributors_count: int


class CompareResponse(BaseModel):
    entries: list[RepositoryComparisonEntry]
