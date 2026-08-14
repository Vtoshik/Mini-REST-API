import Link from "next/link";
import { NoteCard } from "@/components/NoteCard";

const SAMPLE_NOTES = [
  { id: 12, title: "Deploy checklist", content: "Rotate JWT secret, confirm CORS origins, tag release.", category: "work", pinned: true, created_at: "2026-08-01" },
  { id: 7, title: "Reading list", content: "Designing Data-Intensive Applications, ch. 5–7.", category: null, pinned: false, created_at: "2026-07-22" },
  { id: 3, title: "Standup notes", content: "Migration 006 blocked on index rebuild timing.", category: "work", pinned: false, created_at: "2026-07-14" },
];

export default function Home() {
  return (
    <main className="mx-auto flex w-full max-w-3xl flex-1 flex-col gap-10 px-6 py-16">
      <header className="border-b border-rule pb-6">
        <p className="font-display text-xs uppercase tracking-[0.2em] text-ink-muted">
          Drawer 01 — Notes
        </p>
        <h1 className="mt-2 font-display text-4xl font-bold tracking-tight text-ink">
          Ledger
        </h1>
        <p className="mt-3 max-w-md text-sm text-ink-muted">
          A note-taking app for people who think in records, not paragraphs.
          Every entry gets a stamp, a tab, and a place in the drawer.
        </p>
        <div className="mt-6 flex gap-3">
          <Link
            href="/login"
            className="rounded-sm bg-accent px-4 py-2 font-display text-sm font-medium text-paper-card transition-colors hover:bg-accent-hover"
          >
            Log in
          </Link>
          <Link
            href="/register"
            className="rounded-sm border border-ink px-4 py-2 font-display text-sm font-medium text-ink transition-colors hover:border-accent hover:text-accent"
          >
            Create account
          </Link>
        </div>
      </header>

      <section aria-label="Sample notes" className="grid gap-4 sm:grid-cols-2">
        {SAMPLE_NOTES.map((note) => (
          <NoteCard key={note.id} note={note} />
        ))}
      </section>
    </main>
  );
}
