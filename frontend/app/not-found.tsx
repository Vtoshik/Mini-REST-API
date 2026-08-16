import Link from "next/link";

export default function NotFound() {
  return (
    <main className="mx-auto flex w-full max-w-3xl flex-1 flex-col items-center justify-center gap-4 px-6 py-16 text-center">
      <p className="font-display text-xs uppercase tracking-[0.2em] text-signal">
        Drawer empty
      </p>
      <h1 className="font-display text-3xl font-bold tracking-tight text-ink">
        404 — not found
      </h1>
      <p className="max-w-md text-ink-muted">
        There&apos;s nothing filed at this address. It may have been moved or removed.
      </p>
      <Link
        href="/"
        className="mt-2 rounded-sm bg-accent px-4 py-2 font-display text-sm font-medium text-paper-card transition-colors hover:bg-accent-hover"
      >
        Back to start
      </Link>
    </main>
  );
}
