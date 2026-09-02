"use client";

import { useEffect, useState } from "react";

import { apiGet } from "@/lib/api";

interface HealthResponse {
  status: string;
  environment: string;
  version: string;
}

type Status = "checking" | "online" | "offline";

export function BackendStatus() {
  const [status, setStatus] = useState<Status>("checking");
  const [detail, setDetail] = useState<HealthResponse | null>(null);

  useEffect(() => {
    let cancelled = false;

    apiGet<HealthResponse>("/api/health")
      .then((data) => {
        if (cancelled) return;
        setStatus("online");
        setDetail(data);
      })
      .catch(() => {
        if (cancelled) return;
        setStatus("offline");
      });

    return () => {
      cancelled = true;
    };
  }, []);

  const dotColor =
    status === "online"
      ? "bg-positive"
      : status === "offline"
        ? "bg-risk"
        : "bg-muted";

  const label =
    status === "checking"
      ? "Checking API…"
      : status === "online"
        ? `API online — v${detail?.version}`
        : "API offline";

  return (
    <div className="flex items-center gap-2 text-xs text-muted">
      <span className={`h-1.5 w-1.5 rounded-full ${dotColor}`} aria-hidden />
      <span className="font-mono">{label}</span>
    </div>
  );
}
