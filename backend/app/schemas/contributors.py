from __future__ import annotations

from pydantic import BaseModel


class Contributor(BaseModel):
    login: str
    avatar_url: str
    html_url: str
    contributions: int
    percentage: float


class ContributorsSummary(BaseModel):
    total_contributors: int
    contributors: list[Contributor]
    bus_factor: int
    bus_factor_note: str
