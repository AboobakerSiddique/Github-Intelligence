"use client";

import { useState } from "react";
import { Check, Copy, Download } from "lucide-react";

import { Button } from "@/components/ui/button";
import { buildMarkdownReport, downloadMarkdown } from "@/lib/export-report";
import type { RepositoryOverview } from "@/types/repository";
import type { RepositoryAnalytics } from "@/types/analytics";
import type { AISummary } from "@/types/ai";

export function ShareExport({
  overview,
  analytics,
  aiSummary,
}: {
  overview: RepositoryOverview;
  analytics?: RepositoryAnalytics;
  aiSummary?: AISummary;
}) {
  const [copied, setCopied] = useState(false);

  async function copyLink() {
    await navigator.clipboard.writeText(window.location.href);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  }

  function exportReport() {
    const markdown = buildMarkdownReport({ overview, analytics, aiSummary });
    downloadMarkdown(`${overview.name}-report.md`, markdown);
  }

  return (
    <div className="flex items-center gap-2">
      <Button variant="outline" size="sm" onClick={copyLink}>
        {copied ? (
          <Check className="h-3.5 w-3.5 text-positive" strokeWidth={2} />
        ) : (
          <Copy className="h-3.5 w-3.5" strokeWidth={2} />
        )}
        {copied ? "Copied" : "Copy link"}
      </Button>
      <Button variant="outline" size="sm" onClick={exportReport}>
        <Download className="h-3.5 w-3.5" strokeWidth={2} />
        Export report
      </Button>
    </div>
  );
}
