from __future__ import annotations

from pydantic import BaseModel, Field


class AISummary(BaseModel):
    summary: str
    strengths: list[str]
    risks: list[str]
    recommendations: list[str]
    source: str = "ai_interpretation"
    based_on: str = "Based on GitHub data fetched for this analysis."


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=500)


class AskResponse(BaseModel):
    question: str
    answer: str
    source: str = "ai_interpretation"
