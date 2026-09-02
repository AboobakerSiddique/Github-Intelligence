from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class Release(BaseModel):
    tag_name: str
    name: str | None = None
    html_url: str
    is_prerelease: bool
    published_at: datetime | None = None


class ReleasesSummary(BaseModel):
    latest: Release | None
    releases: list[Release]
