"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { apiFetch, ApiError } from "@/lib/api";

type Status = "verifying" | "success" | "error";

export function VerifyEmailStatus({ token }: { token: string }) {
  const [status, setStatus] = useState<Status>("verifying");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    apiFetch("/api/v1/verify-email", { method: "POST", body: { token } })
      .then(() => {
        if (!cancelled) setStatus("success");
      })
      .catch((err) => {
        if (cancelled) return;
        setError(err instanceof ApiError ? err.message : "Something went wrong. Try again.");
        setStatus("error");
      });
    return () => {
      cancelled = true;
    };
  }, [token]);

  if (status === "verifying") {
    return <p className="mt-8 text-sm text-ink-muted">Verifying…</p>;
  }

  if (status === "success") {
    return (
      <div className="mt-8 flex flex-col gap-3">
        <p className="text-sm text-accent">Email verified. You can sign in now.</p>
        <Link
          href="/login"
          className="self-start rounded-sm bg-accent px-4 py-2 font-display text-sm font-medium text-paper-card transition-colors hover:bg-accent-hover"
        >
          Go to sign in
        </Link>
      </div>
    );
  }

  return (
    <p role="alert" className="mt-8 rounded-sm border border-signal bg-signal/10 px-3 py-2 text-sm text-signal">
      {error}
    </p>
  );
}
