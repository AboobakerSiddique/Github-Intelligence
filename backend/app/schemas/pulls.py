from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class PullAuthor(BaseModel):
    login: str
    avatar_url: str


class PullRequest(BaseModel):
    number: int
    title: str
    state: str  # "open" | "closed"
    is_merged: bool
    author: PullAuthor
    html_url: str
    created_at: datetime
    closed_at: datetime | None = None
    merged_at: datetime | None = None


class PullsSummary(BaseModel):
    open_count: int
    merged_count: int
    closed_count: int
    total_count: int
    pull_requests: list[PullRequest]
