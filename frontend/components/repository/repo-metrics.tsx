interface MetricProps {
  label: string;
  value: string;
}

function Metric({ label, value }: MetricProps) {
  return (
    <div className="flex flex-col gap-1 border-r border-border px-4 py-3 last:border-r-0">
      <span className="text-xs text-muted">{label}</span>
      <span className="font-mono text-lg text-foreground">{value}</span>
    </div>
  );
}

function formatCount(value: number): string {
  if (value >= 1_000_000) return `${(value / 1_000_000).toFixed(1)}M`;
  if (value >= 1_000) return `${(value / 1_000).toFixed(1)}k`;
  return String(value);
}

interface RepoMetricsProps {
  stars: number;
  forks: number;
  openIssues: number;
  watchers: number;
}

export function RepoMetrics({ stars, forks, openIssues, watchers }: RepoMetricsProps) {
  return (
    <div className="grid grid-cols-2 divide-y divide-border rounded-md border border-border sm:grid-cols-4 sm:divide-y-0">
      <Metric label="Stars" value={formatCount(stars)} />
      <Metric label="Forks" value={formatCount(forks)} />
      <Metric label="Open issues" value={formatCount(openIssues)} />
      <Metric label="Watchers" value={formatCount(watchers)} />
    </div>
  );
}
