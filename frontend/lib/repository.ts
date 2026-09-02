/**
 * Parses a GitHub repository reference from either a full URL
 * (https://github.com/owner/repo) or a shorthand (owner/repo).
 * Returns null for anything that isn't a plausible owner/repo pair.
 */
const GITHUB_SEGMENT = /^[A-Za-z0-9._-]+$/;

export interface ParsedRepository {
  owner: string;
  repo: string;
}

export function parseRepositoryInput(raw: string): ParsedRepository | null {
  const value = raw.trim();
  if (!value) return null;

  let owner: string | undefined;
  let repo: string | undefined;

  if (/^https?:\/\//i.test(value)) {
    try {
      const url = new URL(value);
      if (!/(^|\.)github\.com$/i.test(url.hostname)) return null;
      const segments = url.pathname.split("/").filter(Boolean);
      [owner, repo] = segments;
    } catch {
      return null;
    }
  } else {
    const segments = value.split("/").filter(Boolean);
    [owner, repo] = segments;
  }

  if (!owner || !repo) return null;

  repo = repo.replace(/\.git$/i, "");

  if (!GITHUB_SEGMENT.test(owner) || !GITHUB_SEGMENT.test(repo)) return null;

  return { owner, repo };
}
