export default function Loading() {
  return (
    <main className="mx-auto flex w-full max-w-3xl flex-1 flex-col items-center justify-center gap-4 px-6 py-16">
      <div className="h-8 w-8 animate-spin rounded-full border-2 border-rule border-t-accent" />
      <p className="font-display text-xs uppercase tracking-[0.2em] text-ink-muted">
        Loading
      </p>
    </main>
  );
}
