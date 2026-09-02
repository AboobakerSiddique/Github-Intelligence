"use client";

import { useRouter } from "next/navigation";
import { useState, type FormEvent } from "react";
import { ArrowRight, Link2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import { parseRepositoryInput } from "@/lib/repository";
import { addRecentRepo } from "@/lib/recent-searches";

const EXAMPLE_REPOS = ["vercel/next.js", "fastapi/fastapi", "facebook/react"];

export function RepoInput() {
  const router = useRouter();
  const [value, setValue] = useState("");
  const [error, setError] = useState<string | null>(null);

  function analyze(input: string) {
    const parsed = parseRepositoryInput(input);
    if (!parsed) {
      setError("Enter a valid GitHub URL or owner/repository.");
      return;
    }
    setError(null);
    addRecentRepo(parsed.owner, parsed.repo);
    router.push(`/analyze/${parsed.owner}/${parsed.repo}`);
  }

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    analyze(value);
  }

  return (
    <div className="flex flex-col gap-3">
      <form
        onSubmit={handleSubmit}
        className="flex items-center gap-2 rounded-md border border-border bg-surface px-3 py-2 focus-within:ring-2 focus-within:ring-accent"
      >
        <Link2 className="h-4 w-4 shrink-0 text-muted" strokeWidth={2} />
        <label htmlFor="repo-input" className="sr-only">
          GitHub repository URL or owner/repository
        </label>
        <input
          id="repo-input"
          name="repository"
          type="text"
          value={value}
          onChange={(event) => setValue(event.target.value)}
          placeholder="owner/repository"
          className="flex-1 bg-transparent font-mono text-sm text-foreground placeholder:text-muted focus:outline-none"
          autoComplete="off"
          spellCheck={false}
        />
        <Button type="submit" size="sm" className="shrink-0">
          Analyze
          <ArrowRight className="h-3.5 w-3.5" strokeWidth={2} />
        </Button>
      </form>

      {error ? (
        <p role="alert" className="text-xs text-risk">
          {error}
        </p>
      ) : (
        <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-muted">
          <span>Try:</span>
          {EXAMPLE_REPOS.map((example) => (
            <button
              key={example}
              type="button"
              onClick={() => {
                setValue(example);
                analyze(example);
              }}
              className="font-mono text-accent transition-colors hover:underline"
            >
              {example}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
