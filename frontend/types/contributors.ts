export interface Contributor {
  login: string;
  avatar_url: string;
  html_url: string;
  contributions: number;
  percentage: number;
}

export interface ContributorsSummary {
  total_contributors: number;
  contributors: Contributor[];
  bus_factor: number;
  bus_factor_note: string;
}
