export interface IssueAuthor {
  login: string;
  avatar_url: string;
}

export interface Issue {
  number: number;
  title: string;
  state: "open" | "closed";
  author: IssueAuthor;
  labels: string[];
  comments: number;
  html_url: string;
  created_at: string;
  closed_at: string | null;
}

export interface IssuesSummary {
  open_count: number;
  closed_count: number;
  total_count: number;
  issues: Issue[];
}
