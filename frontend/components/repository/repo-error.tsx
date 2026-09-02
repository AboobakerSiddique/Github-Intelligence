import { AlertTriangle } from "lucide-react";

import type { ApiError } from "@/types/repository";

export function RepoError({ error, owner, repo }: { error: ApiError; owner: string; repo: string }) {
  const heading =
    error.code === "repository_not_found"
      ? "Repository not found"
      : error.code === "rate_limit_exceeded"
        ? "GitHub API limit reached"
        : error.code === "network_error"
          ? "Couldn't reach the server"
          : "Something went wrong";

  const body =
    error.detail ??
    (error.code === "repository_not_found"
      ? `We couldn't find ${owner}/${repo}. Check the repository URL and try again.`
      : "Please try again in a moment.");

  return (
    <div className="flex flex-col items-start gap-3 rounded-md border border-border px-5 py-6">
      <AlertTriangle className="h-5 w-5 text-risk" strokeWidth={2} />
      <div className="flex flex-col gap-1">
        <h2 className="font-mono text-base text-foreground">{heading}</h2>
        <p className="max-w-md text-sm text-muted">{body}</p>
      </div>
    </div>
  );
}
