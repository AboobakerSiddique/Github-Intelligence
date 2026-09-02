"use client";

import { useState, type FormEvent } from "react";
import { Sparkles, Send, Loader2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import { apiPost } from "@/lib/api";
import type { AskResponse, AISummary } from "@/types/ai";
import { ApiError } from "@/types/repository";

const QUICK_QUESTIONS = [
  "Summarize this repository",
  "What technologies does it use?",
  "How active is development?",
  "What should be improved?",
  "What would a recruiter notice?",
  "Explain the project architecture",
];

interface AskState {
  status: "idle" | "loading" | "error" | "success";
  answer?: AskResponse;
  error?: string;
}

export function AIPanel({ owner, repo }: { owner: string; repo: string }) {
  const [summary, setSummary] = useState<
    { status: "idle" } | { status: "loading" } | { status: "error"; message: string } | { status: "success"; data: AISummary }
  >({ status: "idle" });
  const [question, setQuestion] = useState("");
  const [ask, setAsk] = useState<AskState>({ status: "idle" });

  async function loadSummary() {
    setSummary({ status: "loading" });
    try {
      const data = await apiPost<AISummary>(`/api/repositories/${owner}/${repo}/ai/summary`);
      setSummary({ status: "success", data });
    } catch (error) {
      const message =
        error instanceof ApiError
          ? (error.detail ?? error.message)
          : "Couldn't generate an AI summary right now.";
      setSummary({ status: "error", message });
    }
  }

  async function askQuestion(q: string) {
    if (!q.trim()) return;
    setAsk({ status: "loading" });
    setQuestion(q);
    try {
      const data = await apiPost<AskResponse>(`/api/repositories/${owner}/${repo}/ai/ask`, {
        question: q,
      });
      setAsk({ status: "success", answer: data });
    } catch (error) {
      const message =
        error instanceof ApiError
          ? (error.detail ?? error.message)
          : "Couldn't reach the AI service right now.";
      setAsk({ status: "error", error: message });
    }
  }

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    askQuestion(question);
  }

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-col gap-3 rounded-md border border-border p-5">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Sparkles className="h-4 w-4 text-accent" strokeWidth={2} />
            <h3 className="text-xs text-muted">AI Engineering Review</h3>
          </div>
          {summary.status !== "loading" && (
            <Button variant="outline" size="sm" onClick={loadSummary}>
              {summary.status === "success" ? "Regenerate" : "Generate"}
            </Button>
          )}
        </div>

        {summary.status === "idle" && (
          <p className="text-sm text-muted">
            Generate an AI-interpreted summary, strengths, risks, and recommendations from this
            repository&apos;s real data.
          </p>
        )}

        {summary.status === "loading" && (
          <div className="flex items-center gap-2 py-4 text-sm text-muted">
            <Loader2 className="h-4 w-4 animate-spin" strokeWidth={2} />
            Analyzing repository data…
          </div>
        )}

        {summary.status === "error" && <p className="text-sm text-risk">{summary.message}</p>}

        {summary.status === "success" && (
          <div className="flex flex-col gap-4">
            <p className="text-sm leading-relaxed text-foreground">{summary.data.summary}</p>
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
              <ReviewList title="Strengths" items={summary.data.strengths} tone="positive" />
              <ReviewList title="Risks" items={summary.data.risks} tone="risk" />
              <ReviewList title="Recommendations" items={summary.data.recommendations} tone="neutral" />
            </div>
            <p className="border-t border-border pt-3 text-xs text-muted">
              {summary.data.based_on} AI interpretation — not a substitute for reading the code.
            </p>
          </div>
        )}
      </div>

      <div className="flex flex-col gap-3 rounded-md border border-border p-5">
        <h3 className="text-xs text-muted">Ask this repository</h3>

        <form onSubmit={handleSubmit} className="flex items-center gap-2">
          <input
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="What technologies does this project use?"
            className="flex-1 rounded-md border border-border bg-surface px-3 py-2 text-sm text-foreground placeholder:text-muted focus:outline-none focus:ring-2 focus:ring-accent"
          />
          <Button type="submit" size="sm" disabled={ask.status === "loading"}>
            {ask.status === "loading" ? (
              <Loader2 className="h-3.5 w-3.5 animate-spin" strokeWidth={2} />
            ) : (
              <Send className="h-3.5 w-3.5" strokeWidth={2} />
            )}
          </Button>
        </form>

        <div className="flex flex-wrap gap-2">
          {QUICK_QUESTIONS.map((q) => (
            <button
              key={q}
              type="button"
              onClick={() => askQuestion(q)}
              className="rounded-md border border-border px-2.5 py-1 text-xs text-muted transition-colors hover:border-accent hover:text-foreground"
            >
              {q}
            </button>
          ))}
        </div>

        {ask.status === "error" && <p className="text-sm text-risk">{ask.error}</p>}

        {ask.status === "success" && ask.answer && (
          <div className="flex flex-col gap-1 rounded-md bg-surface-raised p-3">
            <span className="text-xs text-muted">{ask.answer.question}</span>
            <p className="text-sm leading-relaxed text-foreground">{ask.answer.answer}</p>
          </div>
        )}
      </div>
    </div>
  );
}

function ReviewList({
  title,
  items,
  tone,
}: {
  title: string;
  items: string[];
  tone: "positive" | "risk" | "neutral";
}) {
  const dotColor = tone === "positive" ? "bg-positive" : tone === "risk" ? "bg-risk" : "bg-accent";
  return (
    <div className="flex flex-col gap-1.5">
      <span className="text-xs text-muted">{title}</span>
      <ul className="flex flex-col gap-1.5">
        {items.map((item, i) => (
          <li key={i} className="flex items-start gap-2 text-xs text-foreground">
            <span className={`mt-1 h-1.5 w-1.5 shrink-0 rounded-full ${dotColor}`} aria-hidden />
            {item}
          </li>
        ))}
      </ul>
    </div>
  );
}
