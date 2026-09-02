export interface PullAuthor {
  login: string;
  avatar_url: string;
}

export interface PullRequest {
  number: number;
  title: string;
  state: "open" | "closed";
  is_merged: boolean;
  author: PullAuthor;
  html_url: string;
  created_at: string;
  closed_at: string | null;
  merged_at: string | null;
}

export interface PullsSummary {
  open_count: number;
  merged_count: number;
  closed_count: number;
  total_count: number;
  pull_requests: PullRequest[];
}
