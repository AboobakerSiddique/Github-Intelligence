"use client";

import { use, useEffect, useState } from "react";
import Link from "next/link";
import { ArrowLeft } from "lucide-react";

import { SiteFooter } from "@/components/layout/site-footer";
import { SiteHeader } from "@/components/layout/site-header";
import { LanguageBar } from "@/components/charts/language-bar";
import { RepoDashboardSkeleton } from "@/components/repository/repo-dashboard-skeleton";
import { RepoError } from "@/components/repository/repo-error";
import { RepoHeader } from "@/components/repository/repo-header";
import { RepoMetrics } from "@/components/repository/repo-metrics";
import { HealthScoreCard } from "@/components/repository/health-score";
import { EngineeringMetricsCard } from "@/components/repository/engineering-metrics";
import { IssuesList } from "@/components/repository/issues-list";
import { PullsList } from "@/components/repository/pulls-list";
import { ContributorsList } from "@/components/repository/contributors-list";
import { ReleasesList } from "@/components/repository/releases-list";
import { ActivityTimeline } from "@/components/repository/activity-timeline";
import { ShareExport } from "@/components/repository/share-export";
import { AIPanel } from "@/components/ai/ai-panel";
import { useRepositoryOverview } from "@/hooks/use-repository-overview";
import { useRepositoryResource } from "@/hooks/use-repository-resource";
import { addRecentRepo } from "@/lib/recent-searches";
import type { RepositoryAnalytics } from "@/types/analytics";
import type { IssuesSummary } from "@/types/issues";
import type { PullsSummary } from "@/types/pulls";
import type { ContributorsSummary } from "@/types/contributors";
import type { ReleasesSummary } from "@/types/releases";

const TABS = [
  { id: "overview", label: "Overview" },
  { id: "issues", label: "Issues" },
  { id: "pulls", label: "Pull Requests" },
  { id: "contributors", label: "Contributors" },
  { id: "releases", label: "Releases" },
  { id: "ai", label: "AI Insights" },
] as const;

type TabId = (typeof TABS)[number]["id"];

export default function AnalyzePage({
  params,
}: {
  params: Promise<{ owner: string; repo: string }>;
}) {
  const { owner, repo } = use(params);

  return (
    <>
      <SiteHeader />
      <main className="flex-1">
        <div className="mx-auto flex w-full max-w-4xl flex-col gap-4 px-6 py-16">
          <Link
            href="/"
            className="flex w-fit items-center gap-1.5 text-xs text-muted transition-colors hover:text-foreground"
          >
            <ArrowLeft className="h-3.5 w-3.5" strokeWidth={2} />
            Back
          </Link>

          <RepoDashboard key={`${owner}/${repo}`} owner={owner} repo={repo} />
        </div>
      </main>
      <SiteFooter />
    </>
  );
}

function RepoDashboard({ owner, repo }: { owner: string; repo: string }) {
  const overviewState = useRepositoryOverview(owner, repo);
  const analyticsState = useRepositoryResource<RepositoryAnalytics>(
    `/api/repositories/${owner}/${repo}/analytics`
  );
  const [tab, setTab] = useState<TabId>("overview");

  useEffect(() => {
    if (overviewState.status === "success") {
      addRecentRepo(owner, repo);
    }
  }, [overviewState.status, owner, repo]);

  if (overviewState.status === "loading") return <RepoDashboardSkeleton />;

  if (overviewState.status === "error") {
    return <RepoError error={overviewState.error} owner={owner} repo={repo} />;
  }

  const overview = overviewState.data;
  const health = analyticsState.status === "success" ? analyticsState.data.health : undefined;

  return (
    <div className="flex flex-col gap-8">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <RepoHeader repo={overview} />
        <ShareExport
          overview={overview}
          analytics={analyticsState.status === "success" ? analyticsState.data : undefined}
        />
      </div>

      <RepoMetrics
        stars={overview.stars}
        forks={overview.forks}
        openIssues={overview.open_issues}
        watchers={overview.watchers}
      />

      {health && (
        <div className="flex items-center gap-2 text-xs text-muted">
          <span className="h-1.5 w-1.5 rounded-full bg-positive" aria-hidden />
          Health score: <span className="font-mono text-foreground">{health.overall}/100</span>
        </div>
      )}

      <nav className="flex flex-wrap gap-1 border-b border-border">
        {TABS.map((t) => (
          <button
            key={t.id}
            type="button"
            onClick={() => setTab(t.id)}
            className={`border-b-2 px-3 py-2 text-sm transition-colors ${
              tab === t.id
                ? "border-accent text-foreground"
                : "border-transparent text-muted hover:text-foreground"
            }`}
          >
            {t.label}
          </button>
        ))}
      </nav>

      <div className="flex flex-col gap-6">
        {tab === "overview" && (
          <>
            <div className="flex flex-col gap-2">
              <h2 className="text-xs text-muted">Languages</h2>
              <LanguageBar languages={overview.languages} />
            </div>
            {analyticsState.status === "loading" && (
              <p className="text-sm text-muted">Computing health score…</p>
            )}
            {analyticsState.status === "error" && (
              <p className="text-sm text-risk">
                {analyticsState.error.detail ?? "Couldn't load analytics right now."}
              </p>
            )}
            {analyticsState.status === "success" && (
              <>
                <HealthScoreCard health={analyticsState.data.health} />
                <EngineeringMetricsCard metrics={analyticsState.data.metrics} />
                <ActivityTimeline events={analyticsState.data.activity} />
              </>
            )}
          </>
        )}

        {tab === "issues" && <IssuesTab owner={owner} repo={repo} />}
        {tab === "pulls" && <PullsTab owner={owner} repo={repo} />}
        {tab === "contributors" && <ContributorsTab owner={owner} repo={repo} />}
        {tab === "releases" && <ReleasesTab owner={owner} repo={repo} />}
        {tab === "ai" && <AIPanel owner={owner} repo={repo} />}
      </div>
    </div>
  );
}

function IssuesTab({ owner, repo }: { owner: string; repo: string }) {
  const state = useRepositoryResource<IssuesSummary>(`/api/repositories/${owner}/${repo}/issues`);
  if (state.status === "loading") return <SectionSkeleton />;
  if (state.status === "error") return <SectionError message={state.error.detail} />;
  return <IssuesList issues={state.data} />;
}

function PullsTab({ owner, repo }: { owner: string; repo: string }) {
  const state = useRepositoryResource<PullsSummary>(`/api/repositories/${owner}/${repo}/pulls`);
  if (state.status === "loading") return <SectionSkeleton />;
  if (state.status === "error") return <SectionError message={state.error.detail} />;
  return <PullsList pulls={state.data} />;
}

function ContributorsTab({ owner, repo }: { owner: string; repo: string }) {
  const state = useRepositoryResource<ContributorsSummary>(
    `/api/repositories/${owner}/${repo}/contributors`
  );
  if (state.status === "loading") return <SectionSkeleton />;
  if (state.status === "error") return <SectionError message={state.error.detail} />;
  return <ContributorsList contributors={state.data} />;
}

function ReleasesTab({ owner, repo }: { owner: string; repo: string }) {
  const state = useRepositoryResource<ReleasesSummary>(`/api/repositories/${owner}/${repo}/releases`);
  if (state.status === "loading") return <SectionSkeleton />;
  if (state.status === "error") return <SectionError message={state.error.detail} />;
  return <ReleasesList releases={state.data} />;
}

function SectionSkeleton() {
  return (
    <div className="flex flex-col gap-2 rounded-md border border-border p-5">
      <div className="h-4 w-32 animate-pulse rounded-md bg-surface-raised" />
      <div className="h-4 w-full animate-pulse rounded-md bg-surface-raised" />
      <div className="h-4 w-2/3 animate-pulse rounded-md bg-surface-raised" />
    </div>
  );
}

function SectionError({ message }: { message?: string }) {
  return (
    <div className="rounded-md border border-border p-5">
      <p className="text-sm text-risk">{message ?? "Couldn't load this section right now."}</p>
    </div>
  );
}
