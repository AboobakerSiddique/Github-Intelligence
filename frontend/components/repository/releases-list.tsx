import { ExternalLink, Tag } from "lucide-react";

import type { ReleasesSummary } from "@/types/releases";

function formatDate(iso: string | null): string {
  if (!iso) return "Unpublished";
  return new Date(iso).toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" });
}

export function ReleasesList({ releases }: { releases: ReleasesSummary }) {
  return (
    <div className="flex flex-col gap-3 rounded-md border border-border p-5">
      <h3 className="text-xs text-muted">Releases</h3>

      {releases.releases.length === 0 ? (
        <p className="text-sm text-muted">No releases published yet.</p>
      ) : (
        <ul className="flex flex-col divide-y divide-border">
          {releases.releases.slice(0, 6).map((release) => (
            <li key={release.tag_name} className="flex items-center justify-between gap-3 py-2.5">
              <div className="flex items-center gap-2">
                <Tag className="h-3.5 w-3.5 shrink-0 text-muted" strokeWidth={2} />
                <a
                  href={release.html_url}
                  target="_blank"
                  rel="noreferrer"
                  className="flex items-center gap-1.5 font-mono text-sm text-foreground transition-colors hover:text-accent"
                >
                  {release.name || release.tag_name}
                  <ExternalLink className="h-3 w-3 shrink-0 text-muted" strokeWidth={2} />
                </a>
                {release.is_prerelease && (
                  <span className="rounded-md bg-surface-raised px-1.5 py-0.5 text-[10px] text-muted">
                    pre-release
                  </span>
                )}
              </div>
              <span className="shrink-0 text-xs text-muted">{formatDate(release.published_at)}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
