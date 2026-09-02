from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class LanguageBreakdown(BaseModel):
    """A single language's share of the repository, by bytes of code."""

    name: str
    bytes: int
    percentage: float = Field(..., description="Rounded percentage of total bytes, 0-100.")


class RepositoryOwner(BaseModel):
    login: str
    avatar_url: str
    html_url: str
    type: str


class RepositoryOverview(BaseModel):
    """Normalized repository metadata — the application's own shape, not GitHub's raw response."""

    owner: RepositoryOwner
    name: str
    full_name: str
    description: str | None = None
    html_url: str
    homepage: str | None = None

    stars: int
    forks: int
    watchers: int
    open_issues: int

    default_branch: str
    primary_language: str | None = None
    topics: list[str] = Field(default_factory=list)

    is_archived: bool
    is_fork: bool
    license_name: str | None = None

    created_at: datetime
    updated_at: datetime
    pushed_at: datetime | None = None

    languages: list[LanguageBreakdown] = Field(default_factory=list)


class RepositoryLanguagesResponse(BaseModel):
    languages: list[LanguageBreakdown]
