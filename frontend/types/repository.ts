export interface RepositoryOwner {
  login: string;
  avatar_url: string;
  html_url: string;
  type: string;
}

export interface LanguageBreakdown {
  name: string;
  bytes: number;
  percentage: number;
}

export interface RepositoryOverview {
  owner: RepositoryOwner;
  name: string;
  full_name: string;
  description: string | null;
  html_url: string;
  homepage: string | null;

  stars: number;
  forks: number;
  watchers: number;
  open_issues: number;

  default_branch: string;
  primary_language: string | null;
  topics: string[];

  is_archived: boolean;
  is_fork: boolean;
  license_name: string | null;

  created_at: string;
  updated_at: string;
  pushed_at: string | null;

  languages: LanguageBreakdown[];
}

export interface ApiErrorBody {
  error: string;
  message: string;
  detail?: string;
}

export class ApiError extends Error {
  status: number;
  code: string;
  detail?: string;

  constructor(status: number, body: ApiErrorBody) {
    super(body.message);
    this.status = status;
    this.code = body.error;
    this.detail = body.detail;
  }
}
