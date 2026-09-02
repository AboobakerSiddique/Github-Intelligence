import { ExternalLink } from "lucide-react";

import type { IssuesSummary } from "@/types/issues";

function timeAgo(iso: string): string {
  const days = Math.floor((Date.now() - new Date(iso).getTime()) / 86_400_000);
  if (days <= 0) return "today";
  if (days === 1) return "1 day ago";
  if (days < 30) return `${days} days ago`;
  const months = Math.floor(days / 30);
  return months === 1 ? "1 month ago" : `${months} months ago`;
}

export function IssuesList({ issues }: { issues: IssuesSummary }) {
  return (
    <div className="flex flex-col gap-3 rounded-md border border-border p-5">
      <div className="flex items-center gap-4">
        <h3 className="text-xs text-muted">Issues</h3>
        <span className="text-xs text-muted">
          <span className="text-foreground">{issues.open_count}</span> open
        </span>
        <span className="text-xs text-muted">
          <span className="text-foreground">{issues.closed_count}</span> closed
        </span>
      </div>

      {issues.issues.length === 0 ? (
        <p className="text-sm text-muted">No issues found.</p>
      ) : (
        <ul className="flex flex-col divide-y divide-border">
          {issues.issues.slice(0, 8).map((issue) => (
            <li key={issue.number} className="flex items-start justify-between gap-3 py-2.5">
              <div className="flex flex-col gap-1">
                <a
                  href={issue.html_url}
                  target="_blank"
                  rel="noreferrer"
                  className="flex items-center gap-1.5 text-sm text-foreground transition-colors hover:text-accent"
                >
                  {issue.title}
                  <ExternalLink className="h-3 w-3 shrink-0 text-muted" strokeWidth={2} />
                </a>
                <span className="text-xs text-muted">
                  #{issue.number} opened {timeAgo(issue.created_at)} by {issue.author.login}
                </span>
              </div>
              <span
                className={`shrink-0 rounded-md px-2 py-0.5 text-[10px] ${
                  issue.state === "open"
                    ? "bg-positive-soft text-positive"
                    : "bg-surface-raised text-muted"
                }`}
              >
                {issue.state}
              </span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
