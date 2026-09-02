import { ExternalLink } from "lucide-react";

import type { RepositoryOverview } from "@/types/repository";

export function RepoHeader({ repo }: { repo: RepositoryOverview }) {
  return (
    <div className="flex flex-col gap-3">
      <div className="flex items-start justify-between gap-4">
        <div className="flex flex-col gap-1">
          <h1 className="font-mono text-2xl text-foreground">{repo.name}</h1>
          <a
            href={repo.owner.html_url}
            target="_blank"
            rel="noreferrer"
            className="text-sm text-muted transition-colors hover:text-foreground"
          >
            {repo.full_name}
          </a>
        </div>
        <a
          href={repo.html_url}
          target="_blank"
          rel="noreferrer"
          className="flex shrink-0 items-center gap-1.5 rounded-md border border-border px-3 py-1.5 text-xs text-foreground transition-colors hover:bg-surface-raised"
        >
          Open on GitHub
          <ExternalLink className="h-3.5 w-3.5" strokeWidth={2} />
        </a>
      </div>

      {repo.description && (
        <p className="max-w-xl text-sm text-muted">{repo.description}</p>
      )}

      {repo.topics.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {repo.topics.map((topic) => (
            <span
              key={topic}
              className="rounded-md border border-border px-2 py-1 font-mono text-xs text-muted"
            >
              {topic}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}
