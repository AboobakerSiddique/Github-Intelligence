"use client";

import { useEffect, useRef, useState } from "react";
import { Check, ChevronDown, Copy, Download, FileText, Loader2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import { downloadServerReport } from "@/lib/export-report";
import type { RepositoryOverview } from "@/types/repository";
import type { RepositoryAnalytics } from "@/types/analytics";
import type { AISummary } from "@/types/ai";

export function ShareExport({
  overview,
}: {
  overview: RepositoryOverview;
  analytics?: RepositoryAnalytics;
  aiSummary?: AISummary;
}) {
  const [copied, setCopied] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);
  const [exporting, setExporting] = useState<"markdown" | "pdf" | null>(null);
  const [error, setError] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setMenuOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  async function copyLink() {
    await navigator.clipboard.writeText(window.location.href);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  }

  async function handleExport(format: "markdown" | "pdf") {
    setMenuOpen(false);
    setExporting(format);
    setError(false);
    try {
      await downloadServerReport(overview.owner.login, overview.name, format);
    } catch {
      setError(true);
      setTimeout(() => setError(false), 2500);
    } finally {
      setExporting(null);
    }
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

      <div className="relative" ref={menuRef}>
        <Button
          variant="outline"
          size="sm"
          onClick={() => setMenuOpen((open) => !open)}
          disabled={exporting !== null}
        >
          {exporting ? (
            <Loader2 className="h-3.5 w-3.5 animate-spin" strokeWidth={2} />
          ) : (
            <Download className="h-3.5 w-3.5" strokeWidth={2} />
          )}
          {error ? "Export failed" : exporting ? "Exporting…" : "Export report"}
          <ChevronDown className="h-3.5 w-3.5" strokeWidth={2} />
        </Button>

        {menuOpen && (
          <div className="absolute right-0 top-full z-10 mt-1 w-40 overflow-hidden rounded-md border border-border bg-surface shadow-lg">
            <button
              type="button"
              onClick={() => handleExport("markdown")}
              className="flex w-full items-center gap-2 px-3 py-2 text-left text-xs text-foreground transition-colors hover:bg-surface-raised"
            >
              <FileText className="h-3.5 w-3.5" strokeWidth={2} />
              Markdown (.md)
            </button>
            <button
              type="button"
              onClick={() => handleExport("pdf")}
              className="flex w-full items-center gap-2 px-3 py-2 text-left text-xs text-foreground transition-colors hover:bg-surface-raised"
            >
              <FileText className="h-3.5 w-3.5" strokeWidth={2} />
              PDF (.pdf)
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
