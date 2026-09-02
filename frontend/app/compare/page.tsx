"use client";

import { useState, type FormEvent } from "react";
import { ArrowLeftRight, Loader2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import { SiteFooter } from "@/components/layout/site-footer";
import { SiteHeader } from "@/components/layout/site-header";
import { CompareView } from "@/components/repository/compare-view";
import { apiPost } from "@/lib/api";
import { parseRepositoryInput } from "@/lib/repository";
import type { CompareResponse } from "@/types/compare";
import { ApiError } from "@/types/repository";

type State =
  | { status: "idle" }
  | { status: "loading" }
  | { status: "error"; message: string }
  | { status: "success"; data: CompareResponse };

export default function ComparePage() {
  const [repoA, setRepoA] = useState("");
  const [repoB, setRepoB] = useState("");
  const [state, setState] = useState<State>({ status: "idle" });

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();

    const parsedA = parseRepositoryInput(repoA);
    const parsedB = parseRepositoryInput(repoB);
    if (!parsedA || !parsedB) {
      setState({ status: "error", message: "Enter two valid repositories to compare." });
      return;
    }

    setState({ status: "loading" });
    try {
      const data = await apiPost<CompareResponse>("/api/compare", {
        repositories: [`${parsedA.owner}/${parsedA.repo}`, `${parsedB.owner}/${parsedB.repo}`],
      });
      setState({ status: "success", data });
    } catch (error) {
      const message =
        error instanceof ApiError ? (error.detail ?? error.message) : "Something went wrong.";
      setState({ status: "error", message });
    }
  }

  return (
    <>
      <SiteHeader />
      <main className="flex-1">
        <div className="mx-auto flex w-full max-w-3xl flex-col gap-8 px-6 py-16">
          <div className="flex flex-col gap-2">
            <h1 className="flex items-center gap-2 font-mono text-2xl text-foreground">
              <ArrowLeftRight className="h-5 w-5 text-accent" strokeWidth={2} />
              Compare repositories
            </h1>
            <p className="text-sm text-muted">
              See health, activity, and community signals side by side.
            </p>
          </div>

          <form onSubmit={handleSubmit} className="flex flex-col gap-3 sm:flex-row sm:items-center">
            <input
              value={repoA}
              onChange={(e) => setRepoA(e.target.value)}
              placeholder="owner/repository"
              className="flex-1 rounded-md border border-border bg-surface px-3 py-2 font-mono text-sm text-foreground placeholder:text-muted focus:outline-none focus:ring-2 focus:ring-accent"
            />
            <span className="shrink-0 text-center text-xs text-muted">vs</span>
            <input
              value={repoB}
              onChange={(e) => setRepoB(e.target.value)}
              placeholder="owner/repository"
              className="flex-1 rounded-md border border-border bg-surface px-3 py-2 font-mono text-sm text-foreground placeholder:text-muted focus:outline-none focus:ring-2 focus:ring-accent"
            />
            <Button type="submit" disabled={state.status === "loading"} className="shrink-0">
              {state.status === "loading" ? (
                <Loader2 className="h-4 w-4 animate-spin" strokeWidth={2} />
              ) : (
                "Compare"
              )}
            </Button>
          </form>

          {state.status === "error" && <p className="text-sm text-risk">{state.message}</p>}

          {state.status === "success" && <CompareView entries={state.data.entries} />}
        </div>
      </main>
      <SiteFooter />
    </>
  );
}
