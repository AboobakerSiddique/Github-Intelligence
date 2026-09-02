"""
AI service.

Builds structured, factual repository context and hands it to Gemini as
the analysis layer — the model is instructed to reason over the supplied
data only, never to invent repository facts it wasn't given.
"""
from __future__ import annotations

import json
from typing import Any

from app.clients.gemini_client import AIUnavailableError, GeminiClient
from app.schemas.ai import AISummary
from app.utils.logger import get_logger

logger = get_logger(__name__)


def _build_context(data: dict[str, Any]) -> str:
    repo = data["repo"]
    languages = data["languages"]
    issues = [i for i in data["issues"] if "pull_request" not in i]
    pulls = data["pulls"]
    releases = data["releases"]
    contributors = data["contributors"]

    context = {
        "name": repo.get("full_name"),
        "description": repo.get("description"),
        "primary_language": repo.get("language"),
        "languages": languages,
        "topics": repo.get("topics", []),
        "stars": repo.get("stargazers_count"),
        "forks": repo.get("forks_count"),
        "open_issues": repo.get("open_issues_count"),
        "is_archived": repo.get("archived"),
        "license": (repo.get("license") or {}).get("name"),
        "created_at": repo.get("created_at"),
        "pushed_at": repo.get("pushed_at"),
        "open_issue_titles": [i["title"] for i in issues if i["state"] == "open"][:10],
        "recent_closed_issue_titles": [i["title"] for i in issues if i["state"] == "closed"][:10],
        "recent_pr_titles": [p["title"] for p in pulls[:10]],
        "recent_release_tags": [r.get("tag_name") for r in releases[:5]],
        "top_contributors": [c["login"] for c in contributors[:10]],
        "contributor_count": len(contributors),
    }
    return json.dumps(context, indent=2, default=str)


SUMMARY_INSTRUCTIONS = """You are an engineering analyst reviewing a GitHub repository. \
You are given real, factual data about the repository below. Base your analysis ONLY on \
this data — do not invent facts, contributors, or events that aren't present.

Repository data:
{context}

Respond with ONLY a JSON object (no markdown fences, no preamble) matching this shape:
{{
  "summary": "2-4 sentence plain-language summary of what this repository is and its current state",
  "strengths": ["short bullet", "short bullet"],
  "risks": ["short bullet", "short bullet"],
  "recommendations": ["short bullet", "short bullet"]
}}
Keep each bullet under 20 words. Use 2-4 bullets per list."""

ASK_INSTRUCTIONS = """You are an assistant answering questions about a specific GitHub repository. \
You are given real, factual data about the repository below. Answer ONLY using this data. \
If the data doesn't contain the answer, say so plainly instead of guessing.

Repository data:
{context}

Question: {question}

Answer in 2-5 sentences, plain language, no markdown headers."""


async def generate_summary(gemini: GeminiClient, data: dict[str, Any]) -> AISummary:
    context = _build_context(data)
    prompt = SUMMARY_INSTRUCTIONS.format(context=context)

    raw_text = await gemini.generate(prompt)
    cleaned = raw_text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()

    try:
        parsed = json.loads(cleaned)
        return AISummary(
            summary=parsed["summary"],
            strengths=parsed.get("strengths", []),
            risks=parsed.get("risks", []),
            recommendations=parsed.get("recommendations", []),
        )
    except (json.JSONDecodeError, KeyError) as exc:
        logger.warning("Failed to parse AI summary JSON: %s", exc)
        raise AIUnavailableError("The AI returned an unexpected response format.") from exc


async def answer_question(gemini: GeminiClient, data: dict[str, Any], question: str) -> str:
    context = _build_context(data)
    prompt = ASK_INSTRUCTIONS.format(context=context, question=question)
    return (await gemini.generate(prompt)).strip()
