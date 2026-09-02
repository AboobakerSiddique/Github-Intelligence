"use client";

import { useEffect, useState } from "react";

import { apiGet } from "@/lib/api";
import { ApiError } from "@/types/repository";

export type ResourceState<T> =
  | { status: "loading" }
  | { status: "error"; error: ApiError }
  | { status: "success"; data: T };

/**
 * Fetches a repository-scoped resource (issues, pulls, contributors,
 * releases, analytics, ...). Each caller supplies the path; the component
 * that renders this should be keyed by `${owner}/${repo}` upstream so
 * state resets cleanly when the repository changes (see analyze page).
 */
export function useRepositoryResource<T>(path: string): ResourceState<T> {
  const [state, setState] = useState<ResourceState<T>>({ status: "loading" });

  useEffect(() => {
    let cancelled = false;

    apiGet<T>(path)
      .then((data) => {
        if (!cancelled) setState({ status: "success", data });
      })
      .catch((error: unknown) => {
        if (cancelled) return;
        const apiError =
          error instanceof ApiError
            ? error
            : new ApiError(0, {
                error: "network_error",
                message: "Couldn't reach the server",
                detail: "Check your connection and try again.",
              });
        setState({ status: "error", error: apiError });
      });

    return () => {
      cancelled = true;
    };
  }, [path]);

  return state;
}
