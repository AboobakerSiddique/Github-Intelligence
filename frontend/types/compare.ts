import type { RepositoryOverview } from "@/types/repository";

export interface RepositoryComparisonEntry {
  overview: RepositoryOverview;
  health_score: number;
  open_issues: number;
  contributors_count: number;
}

export interface CompareResponse {
  entries: RepositoryComparisonEntry[];
}
