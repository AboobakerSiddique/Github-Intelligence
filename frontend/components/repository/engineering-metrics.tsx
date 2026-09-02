import type { EngineeringMetrics } from "@/types/analytics";

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex flex-col gap-1">
      <span className="text-xs text-muted">{label}</span>
      <span className="font-mono text-base text-foreground">{value}</span>
    </div>
  );
}

export function EngineeringMetricsCard({ metrics }: { metrics: EngineeringMetrics }) {
  return (
    <div className="flex flex-col gap-3 rounded-md border border-border p-5">
      <div className="flex items-center justify-between">
        <h3 className="text-xs text-muted">Engineering Metrics</h3>
        {metrics.is_estimate && (
          <span className="rounded-md bg-surface-raised px-2 py-0.5 text-[10px] text-muted">
            Estimate
          </span>
        )}
      </div>
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        <Stat
          label="Issue resolution"
          value={metrics.issue_resolution_rate != null ? `${metrics.issue_resolution_rate}%` : "—"}
        />
        <Stat
          label="PR merge rate"
          value={metrics.pr_merge_rate != null ? `${metrics.pr_merge_rate}%` : "—"}
        />
        <Stat
          label="Release cadence"
          value={
            metrics.release_frequency_days != null
              ? `~${Math.round(metrics.release_frequency_days)}d`
              : "—"
          }
        />
        <Stat label="Bus factor" value={metrics.bus_factor != null ? String(metrics.bus_factor) : "—"} />
      </div>
    </div>
  );
}
