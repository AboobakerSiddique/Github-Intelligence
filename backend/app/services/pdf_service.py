"""
PDF export service.

Renders the same repository analysis used by export_service.build_markdown_report
into a formatted PDF using reportlab (pure Python, no system dependencies —
safe to run on Render's standard Python runtime).
"""
from __future__ import annotations

import io
from datetime import datetime, timezone

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    ListFlowable,
    ListItem,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from app.schemas.ai import AISummary
from app.schemas.analytics import RepositoryAnalytics
from app.schemas.repository import RepositoryOverview

_STYLES = getSampleStyleSheet()
_TITLE = ParagraphStyle("ReportTitle", parent=_STYLES["Title"], fontSize=18, spaceAfter=6)
_H2 = ParagraphStyle("ReportH2", parent=_STYLES["Heading2"], spaceBefore=16, spaceAfter=8)
_BODY = _STYLES["BodyText"]
_META = ParagraphStyle("Meta", parent=_STYLES["Normal"], textColor=colors.grey, fontSize=9)
_SCORE = ParagraphStyle("Score", parent=_STYLES["Heading1"], fontSize=22, spaceAfter=4)


def build_pdf_report(
    repo: RepositoryOverview,
    analytics: RepositoryAnalytics,
    ai_summary: AISummary | None = None,
) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
        title=f"{repo.full_name} — Health Report",
    )
    story = []

    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    story.append(Paragraph(f"Repository Health Report — {repo.full_name}", _TITLE))
    story.append(Paragraph(f"Generated {generated_at} by GitHub Repository Intelligence", _META))
    if repo.description:
        story.append(Spacer(1, 8))
        story.append(Paragraph(repo.description, _BODY))
    story.append(Spacer(1, 4))
    story.append(Paragraph(repo.html_url, _META))

    story.append(Paragraph("Health Score", _H2))
    story.append(Paragraph(f"{analytics.health.overall}/100 — {analytics.health.label}", _SCORE))
    story.append(Paragraph(analytics.health.methodology, _META))
    story.append(Spacer(1, 8))

    factor_rows = [["Factor", "Score", "Notes"]]
    for factor in analytics.health.factors:
        factor_rows.append([factor.name, f"{factor.score}/100", Paragraph(factor.explanation, _BODY)])
    factor_table = Table(factor_rows, colWidths=[1.3 * inch, 0.8 * inch, 4 * inch])
    factor_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f2937")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d1d5db")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f9fafb")]),
            ]
        )
    )
    story.append(factor_table)

    story.append(Paragraph("Engineering Metrics", _H2))
    metrics = analytics.metrics
    metric_rows = [
        ["Metric", "Value"],
        ["Issue resolution rate",
         f"{metrics.issue_resolution_rate}%" if metrics.issue_resolution_rate is not None else "N/A"],
        ["PR merge rate",
         f"{metrics.pr_merge_rate}%" if metrics.pr_merge_rate is not None else "N/A"],
        ["Release frequency",
         f"{metrics.release_frequency_days} days" if metrics.release_frequency_days is not None else "N/A"],
        ["Bus factor",
         str(metrics.bus_factor) if metrics.bus_factor is not None else "N/A"],
    ]
    metric_table = Table(metric_rows, colWidths=[2.5 * inch, 2 * inch])
    metric_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f2937")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d1d5db")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f9fafb")]),
            ]
        )
    )
    story.append(metric_table)
    if metrics.is_estimate:
        story.append(Spacer(1, 4))
        story.append(Paragraph("Metrics above are estimates derived from sampled GitHub data.", _META))

    if ai_summary:
        story.append(Paragraph("AI Summary", _H2))
        story.append(Paragraph(ai_summary.summary, _BODY))
        if ai_summary.strengths:
            story.append(Paragraph("Strengths", ParagraphStyle("h3", parent=_STYLES["Heading3"])))
            story.append(
                ListFlowable(
                    [ListItem(Paragraph(item, _BODY)) for item in ai_summary.strengths],
                    bulletType="bullet",
                )
            )
        if ai_summary.risks:
            story.append(Paragraph("Risks", ParagraphStyle("h3", parent=_STYLES["Heading3"])))
            story.append(
                ListFlowable(
                    [ListItem(Paragraph(item, _BODY)) for item in ai_summary.risks],
                    bulletType="bullet",
                )
            )
        if ai_summary.recommendations:
            story.append(Paragraph("Recommendations", ParagraphStyle("h3", parent=_STYLES["Heading3"])))
            story.append(
                ListFlowable(
                    [ListItem(Paragraph(item, _BODY)) for item in ai_summary.recommendations],
                    bulletType="bullet",
                )
            )

    story.append(Paragraph("Recent Activity", _H2))
    if analytics.activity:
        for event in analytics.activity[:15]:
            text = f"<b>{event.occurred_at}</b> — {event.kind}: {event.label}"
            story.append(Paragraph(text, _BODY))
    else:
        story.append(Paragraph("No recent activity found.", _BODY))

    story.append(Spacer(1, 16))
    story.append(Paragraph("Report generated by GitHub Repository Intelligence", _META))

    doc.build(story)
    return buffer.getvalue()
