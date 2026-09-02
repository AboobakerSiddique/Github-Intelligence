"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Clock, X } from "lucide-react";

import { clearRecentRepos, getRecentRepos, type RecentRepo } from "@/lib/recent-searches";

export function RecentRepos() {
  const router = useRouter();
  const [repos, setRepos] = useState<RecentRepo[] | null>(null);

  useEffect(() => {
    // Reads a client-only external system (localStorage) on mount — the
    // documented exception to this rule.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setRepos(getRecentRepos());
  }, []);

  if (!repos || repos.length === 0) return null;

  return (
    <div className="flex flex-col gap-2">
      <div className="flex items-center justify-between">
        <span className="flex items-center gap-1.5 text-xs text-muted">
          <Clock className="h-3.5 w-3.5" strokeWidth={2} />
          Recent repositories
        </span>
        <button
          type="button"
          onClick={() => {
            clearRecentRepos();
            setRepos([]);
          }}
          className="flex items-center gap-1 text-xs text-muted transition-colors hover:text-foreground"
        >
          <X className="h-3 w-3" strokeWidth={2} />
          Clear
        </button>
      </div>
      <div className="flex flex-wrap gap-2">
        {repos.map((r) => (
          <button
            key={`${r.owner}/${r.repo}`}
            type="button"
            onClick={() => router.push(`/analyze/${r.owner}/${r.repo}`)}
            className="rounded-md border border-border px-2.5 py-1 font-mono text-xs text-foreground transition-colors hover:border-accent"
          >
            {r.owner}/{r.repo}
          </button>
        ))}
      </div>
    </div>
  );
}
