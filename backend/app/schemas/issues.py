from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class IssueAuthor(BaseModel):
    login: str
    avatar_url: str


class Issue(BaseModel):
    number: int
    title: str
    state: str  # "open" | "closed"
    author: IssueAuthor
    labels: list[str]
    comments: int
    html_url: str
    created_at: datetime
    closed_at: datetime | None = None


class IssuesSummary(BaseModel):
    open_count: int
    closed_count: int
    total_count: int
    issues: list[Issue]
