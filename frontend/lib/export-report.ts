import { API_BASE_URL } from "@/lib/api";
import type { RepositoryOverview } from "@/types/repository";
import type { RepositoryAnalytics } from "@/types/analytics";
import type { AISummary } from "@/types/ai";

export type ExportFormat = "markdown" | "pdf";

/**
 * Downloads a server-rendered report (Markdown or PDF) for the given
 * repository from the backend's /export endpoints. Both formats are built
 * from the same real repository data, so they never drift from each other
 * or from the dashboard the user is looking at.
 */
export async function downloadServerReport(
  owner: string,
  repo: string,
  format: ExportFormat
): Promise<void> {
  const response = await fetch(
    `${API_BASE_URL}/api/repositories/${owner}/${repo}/export/${format}`,
    { headers: { Accept: format === "pdf" ? "application/pdf" : "text/markdown" } }
  );

  if (!response.ok) {
    throw new Error(`Export failed with status ${response.status}`);
  }

  const blob = await response.blob();
  const url = URL.createObjectURL(blob);
  const extension = format === "pdf" ? "pdf" : "md";
  const link = document.createElement("a");
  link.href = url;
  link.download = `${owner}-${repo}-health-report.${extension}`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

/**
 * Builds a Markdown engineering report from already-fetched dashboard
 * data. Kept client-side and dependency-free; a server-rendered PDF export
 * is a natural next step but out of scope for this pass.
 */
export function buildMarkdownReport(params: {
  overview: RepositoryOverview;
  analytics?: RepositoryAnalytics;
  aiSummary?: AISummary;
}): string {
  const { overview, analytics, aiSummary } = params;
  const lines: string[] = [];

  lines.push(`# ${overview.full_name}`);
  lines.push("");
  lines.push(`Generated ${new Date().toLocaleString()}`);
  lines.push("");
  if (overview.description) lines.push(`> ${overview.description}`);
  lines.push("");

  lines.push("## Overview");
  lines.push(`- Stars: ${overview.stars}`);
  lines.push(`- Forks: ${overview.forks}`);
  lines.push(`- Open issues: ${overview.open_issues}`);
  lines.push(`- Primary language: ${overview.primary_language ?? "Unknown"}`);
  lines.push(`- License: ${overview.license_name ?? "None"}`);
  lines.push(`- URL: ${overview.html_url}`);
  lines.push("");

  if (overview.languages.length > 0) {
    lines.push("## Languages");
    for (const lang of overview.languages) {
      lines.push(`- ${lang.name}: ${lang.percentage}%`);
    }
    lines.push("");
  }

  if (analytics) {
    lines.push("## Repository Health");
    lines.push(`**${analytics.health.overall}/100 — ${analytics.health.label}**`);
    lines.push("");
    for (const factor of analytics.health.factors) {
      lines.push(`- ${factor.name}: ${factor.score} — ${factor.explanation}`);
    }
    lines.push("");

    lines.push("## Engineering Metrics (estimates)");
    lines.push(`- Issue resolution rate: ${analytics.metrics.issue_resolution_rate ?? "—"}%`);
    lines.push(`- PR merge rate: ${analytics.metrics.pr_merge_rate ?? "—"}%`);
    lines.push(`- Release frequency: ~${analytics.metrics.release_frequency_days ?? "—"} days`);
    lines.push(`- Bus factor: ${analytics.metrics.bus_factor ?? "—"}`);
    lines.push("");
  }

  if (aiSummary) {
    lines.push("## AI Summary");
    lines.push(aiSummary.summary);
    lines.push("");
    lines.push("### Strengths");
    aiSummary.strengths.forEach((s) => lines.push(`- ${s}`));
    lines.push("");
    lines.push("### Risks");
    aiSummary.risks.forEach((r) => lines.push(`- ${r}`));
    lines.push("");
    lines.push("### Recommendations");
    aiSummary.recommendations.forEach((r) => lines.push(`- ${r}`));
    lines.push("");
    lines.push(`_${aiSummary.based_on} AI interpretation — verify against the source._`);
  }

  return lines.join("\n");
}

export function downloadMarkdown(filename: string, content: string): void {
  const blob = new Blob([content], { type: "text/markdown;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}
