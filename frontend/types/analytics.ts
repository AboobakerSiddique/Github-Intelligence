export interface HealthFactor {
  name: string;
  score: number;
  explanation: string;
}

export interface HealthScore {
  overall: number;
  label: string;
  factors: HealthFactor[];
  methodology: string;
}

export interface EngineeringMetrics {
  issue_resolution_rate: number | null;
  pr_merge_rate: number | null;
  release_frequency_days: number | null;
  bus_factor: number | null;
  is_estimate: boolean;
}

export interface ActivityEvent {
  kind: string;
  label: string;
  occurred_at: string;
  url: string | null;
}

export interface RepositoryAnalytics {
  health: HealthScore;
  metrics: EngineeringMetrics;
  activity: ActivityEvent[];
}
