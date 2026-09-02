import { ExternalLink } from "lucide-react";

import type { PullsSummary } from "@/types/pulls";

function stateLabel(state: string, isMerged: boolean): string {
  if (isMerged) return "merged";
  return state;
}

function stateClasses(state: string, isMerged: boolean): string {
  if (isMerged) return "bg-accent/15 text-accent";
  if (state === "open") return "bg-positive-soft text-positive";
  return "bg-surface-raised text-muted";
}

export function PullsList({ pulls }: { pulls: PullsSummary }) {
  return (
    <div className="flex flex-col gap-3 rounded-md border border-border p-5">
      <div className="flex items-center gap-4">
        <h3 className="text-xs text-muted">Pull Requests</h3>
        <span className="text-xs text-muted">
          <span className="text-foreground">{pulls.open_count}</span> open
        </span>
        <span className="text-xs text-muted">
          <span className="text-foreground">{pulls.merged_count}</span> merged
        </span>
        <span className="text-xs text-muted">
          <span className="text-foreground">{pulls.closed_count}</span> closed
        </span>
      </div>

      {pulls.pull_requests.length === 0 ? (
        <p className="text-sm text-muted">No pull requests found.</p>
      ) : (
        <ul className="flex flex-col divide-y divide-border">
          {pulls.pull_requests.slice(0, 8).map((pr) => (
            <li key={pr.number} className="flex items-start justify-between gap-3 py-2.5">
              <div className="flex flex-col gap-1">
                <a
                  href={pr.html_url}
                  target="_blank"
                  rel="noreferrer"
                  className="flex items-center gap-1.5 text-sm text-foreground transition-colors hover:text-accent"
                >
                  {pr.title}
                  <ExternalLink className="h-3 w-3 shrink-0 text-muted" strokeWidth={2} />
                </a>
                <span className="text-xs text-muted">
                  #{pr.number} by {pr.author.login}
                </span>
              </div>
              <span
                className={`shrink-0 rounded-md px-2 py-0.5 text-[10px] ${stateClasses(pr.state, pr.is_merged)}`}
              >
                {stateLabel(pr.state, pr.is_merged)}
              </span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
