import Link from "next/link";
import { serverFetch } from "@/lib/serverFetch";
import { Note } from "@/lib/types";
import { TrashList } from "@/components/TrashList";

export default async function TrashPage() {
  const notes = await serverFetch<Note[]>("/api/v1/notes/trash");

  return (
    <main className="mx-auto flex w-full max-w-3xl flex-1 flex-col gap-8 px-6 py-16">
      <header className="flex items-start justify-between border-b border-rule pb-6">
        <div>
          <p className="font-display text-xs uppercase tracking-[0.2em] text-ink-muted">
            Drawer 01 — Notes
          </p>
          <h1 className="mt-2 font-display text-3xl font-bold tracking-tight text-ink">Trash</h1>
        </div>
        <Link
          href="/notes"
          className="rounded-sm border border-ink px-3 py-1.5 font-display text-xs font-medium text-ink transition-colors hover:border-accent hover:text-accent"
        >
          Back to notes
        </Link>
      </header>

      <p className="text-sm text-ink-muted">
        Trashed notes stay here until you restore or permanently delete them.
      </p>

      <TrashList notes={notes ?? []} />
    </main>
  );
}
