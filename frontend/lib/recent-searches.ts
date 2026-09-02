"use client";

const STORAGE_KEY = "gh-intelligence:recent-repos";
const MAX_ENTRIES = 8;

export interface RecentRepo {
  owner: string;
  repo: string;
  visitedAt: string;
}

function safeParse(raw: string | null): RecentRepo[] {
  if (!raw) return [];
  try {
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

export function getRecentRepos(): RecentRepo[] {
  if (typeof window === "undefined") return [];
  return safeParse(window.localStorage.getItem(STORAGE_KEY));
}

export function addRecentRepo(owner: string, repo: string): void {
  if (typeof window === "undefined") return;
  const existing = getRecentRepos().filter(
    (r) => !(r.owner.toLowerCase() === owner.toLowerCase() && r.repo.toLowerCase() === repo.toLowerCase())
  );
  const updated = [{ owner, repo, visitedAt: new Date().toISOString() }, ...existing].slice(
    0,
    MAX_ENTRIES
  );
  window.localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
}

export function clearRecentRepos(): void {
  if (typeof window === "undefined") return;
  window.localStorage.removeItem(STORAGE_KEY);
}
