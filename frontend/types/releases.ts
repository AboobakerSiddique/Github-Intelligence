export interface Release {
  tag_name: string;
  name: string | null;
  html_url: string;
  is_prerelease: boolean;
  published_at: string | null;
}

export interface ReleasesSummary {
  latest: Release | null;
  releases: Release[];
}
