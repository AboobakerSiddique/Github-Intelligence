import { GitMerge, GitPullRequestClosed, Tag, CircleDot } from "lucide-react";

import type { ActivityEvent } from "@/types/analytics";

const ICONS: Record<string, typeof GitMerge> = {
  pull_request_merged: GitMerge,
  issue_opened: CircleDot,
  issue_closed: GitPullRequestClosed,
  release_published: Tag,
};

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" });
}

export function ActivityTimeline({ events }: { events: ActivityEvent[] }) {
  if (events.length === 0) {
    return (
      <div className="rounded-md border border-border p-5">
        <h3 className="mb-2 text-xs text-muted">Activity</h3>
        <p className="text-sm text-muted">No recent activity found.</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-3 rounded-md border border-border p-5">
      <h3 className="text-xs text-muted">Activity</h3>
      <ul className="flex flex-col gap-3">
        {events.map((event, i) => {
          const Icon = ICONS[event.kind] ?? CircleDot;
          return (
            <li key={`${event.kind}-${event.occurred_at}-${i}`} className="flex items-start gap-3">
              <Icon className="mt-0.5 h-3.5 w-3.5 shrink-0 text-muted" strokeWidth={2} />
              <div className="flex flex-1 flex-col gap-0.5">
                {event.url ? (
                  <a
                    href={event.url}
                    target="_blank"
                    rel="noreferrer"
                    className="text-sm text-foreground transition-colors hover:text-accent"
                  >
                    {event.label}
                  </a>
                ) : (
                  <span className="text-sm text-foreground">{event.label}</span>
                )}
                <span className="text-xs text-muted">{formatDate(event.occurred_at)}</span>
              </div>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
