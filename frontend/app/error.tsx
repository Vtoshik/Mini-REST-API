"use client";

import { useEffect } from "react";
import Link from "next/link";

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <main className="mx-auto flex w-full max-w-3xl flex-1 flex-col items-center justify-center gap-4 px-6 py-16 text-center">
      <p className="font-display text-xs uppercase tracking-[0.2em] text-signal">
        Something tore
      </p>
      <h1 className="font-display text-3xl font-bold tracking-tight text-ink">
        This page hit an error
      </h1>
      <p className="max-w-md text-ink-muted">
        Something went wrong loading this page. You can try again, or head back to
        the start.
      </p>
      <div className="mt-2 flex gap-3">
        <button
          onClick={reset}
          className="rounded-sm bg-accent px-4 py-2 font-display text-sm font-medium text-paper-card transition-colors hover:bg-accent-hover"
        >
          Try again
        </button>
        <Link
          href="/"
          className="rounded-sm border border-ink px-4 py-2 font-display text-sm font-medium text-ink transition-colors hover:border-accent hover:text-accent"
        >
          Back to start
        </Link>
      </div>
    </main>
  );
}
