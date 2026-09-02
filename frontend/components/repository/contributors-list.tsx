import Image from "next/image";

import type { ContributorsSummary } from "@/types/contributors";

export function ContributorsList({ contributors }: { contributors: ContributorsSummary }) {
  return (
    <div className="flex flex-col gap-3 rounded-md border border-border p-5">
      <div className="flex items-center justify-between">
        <h3 className="text-xs text-muted">Contributors</h3>
        <span className="text-xs text-muted">{contributors.total_contributors} total</span>
      </div>

      {contributors.contributors.length === 0 ? (
        <p className="text-sm text-muted">No contributor data available.</p>
      ) : (
        <ul className="flex flex-col gap-2.5">
          {contributors.contributors.slice(0, 8).map((c) => (
            <li key={c.login} className="flex items-center gap-3">
              <Image
                src={c.avatar_url}
                alt=""
                width={24}
                height={24}
                className="rounded-full border border-border"
                unoptimized
              />
              <a
                href={c.html_url}
                target="_blank"
                rel="noreferrer"
                className="flex-1 text-sm text-foreground transition-colors hover:text-accent"
              >
                {c.login}
              </a>
              <div className="h-1.5 w-24 overflow-hidden rounded-full bg-surface-raised">
                <div className="h-full rounded-full bg-accent" style={{ width: `${c.percentage}%` }} />
              </div>
              <span className="w-10 shrink-0 text-right font-mono text-xs text-muted">
                {c.percentage}%
              </span>
            </li>
          ))}
        </ul>
      )}

      <p className="border-t border-border pt-3 text-xs text-muted">{contributors.bus_factor_note}</p>
    </div>
  );
}
