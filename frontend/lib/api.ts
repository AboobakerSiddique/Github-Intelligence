import { ApiError, type ApiErrorBody } from "@/types/repository";

/**
 * Base URL for the FastAPI backend. Never put secrets here — this file is
 * bundled into client code. GITHUB_TOKEN and GEMINI_API_KEY live only on
 * the backend.
 */
export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export async function apiGet<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: { Accept: "application/json", ...init?.headers },
  });

  if (!response.ok) {
    let body: ApiErrorBody;
    try {
      body = (await response.json()) as ApiErrorBody;
    } catch {
      body = { error: "unknown_error", message: "Something went wrong." };
    }
    throw new ApiError(response.status, body);
  }

  return response.json() as Promise<T>;
}

export async function apiPost<T>(
  path: string,
  body?: unknown,
  init?: RequestInit
): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: "POST",
    ...init,
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
      ...init?.headers,
    },
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });

  if (!response.ok) {
    let errorBody: ApiErrorBody;
    try {
      errorBody = (await response.json()) as ApiErrorBody;
    } catch {
      errorBody = { error: "unknown_error", message: "Something went wrong." };
    }
    throw new ApiError(response.status, errorBody);
  }

  return response.json() as Promise<T>;
}
