"use client";

import { useState } from "react";
import { ChevronDown } from "lucide-react";

import type { HealthScore } from "@/types/analytics";

function scoreColor(score: number): string {
  if (score >= 80) return "text-positive";
  if (score >= 60) return "text-accent";
  if (score >= 40) return "text-foreground";
  return "text-risk";
}

function barColor(score: number): string {
  if (score >= 80) return "bg-positive";
  if (score >= 60) return "bg-accent";
  if (score >= 40) return "bg-muted";
  return "bg-risk";
}

export function HealthScoreCard({ health }: { health: HealthScore }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="flex flex-col gap-4 rounded-md border border-border p-5">
      <div className="flex items-baseline justify-between">
        <div className="flex flex-col gap-1">
          <span className="text-xs text-muted">Repository Health</span>
          <div className="flex items-baseline gap-2">
            <span className={`font-mono text-3xl ${scoreColor(health.overall)}`}>
              {health.overall}
            </span>
            <span className="text-sm text-muted">/ 100</span>
          </div>
          <span className="text-sm text-foreground">{health.label}</span>
        </div>
        <button
          type="button"
          onClick={() => setExpanded((v) => !v)}
          className="flex items-center gap-1 text-xs text-muted transition-colors hover:text-foreground"
        >
          How is this calculated?
          <ChevronDown
            className={`h-3.5 w-3.5 transition-transform ${expanded ? "rotate-180" : ""}`}
            strokeWidth={2}
          />
        </button>
      </div>

      <div className="flex flex-col gap-2.5">
        {health.factors.map((factor) => (
          <div key={factor.name} className="flex items-center gap-3">
            <span className="w-40 shrink-0 text-xs text-muted">{factor.name}</span>
            <div className="h-1.5 flex-1 overflow-hidden rounded-full bg-surface-raised">
              <div
                className={`h-full rounded-full ${barColor(factor.score)}`}
                style={{ width: `${factor.score}%` }}
              />
            </div>
            <span className="w-8 shrink-0 text-right font-mono text-xs text-foreground">
              {factor.score}
            </span>
          </div>
        ))}
      </div>

      {expanded && (
        <p className="border-t border-border pt-3 text-xs leading-relaxed text-muted">
          {health.methodology}
        </p>
      )}
    </div>
  );
}
