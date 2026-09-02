"use client";

import { useRepositoryResource, type ResourceState } from "@/hooks/use-repository-resource";
import type { RepositoryOverview } from "@/types/repository";

export function useRepositoryOverview(owner: string, repo: string): ResourceState<RepositoryOverview> {
  return useRepositoryResource<RepositoryOverview>(`/api/repositories/${owner}/${repo}`);
}
