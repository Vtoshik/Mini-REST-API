import Link from "next/link";
import { getCurrentUser } from "@/lib/session";
import { serverFetch } from "@/lib/serverFetch";
import { Note } from "@/lib/types";
import { NoteCard } from "@/components/NoteCard";
import { LogoutButton } from "@/components/LogoutButton";

export default async function NotesPage() {
  const [user, notes] = await Promise.all([
    getCurrentUser(),
    serverFetch<Note[]>("/api/v1/notes"),
  ]);

  return (
    <main className="mx-auto flex w-full max-w-3xl flex-1 flex-col gap-8 px-6 py-16">
      <header className="flex items-start justify-between border-b border-rule pb-6">
        <div>
          <p className="font-display text-xs uppercase tracking-[0.2em] text-ink-muted">
            Drawer 01 — Notes
          </p>
          <h1 className="mt-2 font-display text-3xl font-bold tracking-tight text-ink">
            {user ? `${user.username}'s notes` : "Notes"}
          </h1>
        </div>
        <div className="flex items-center gap-3">
          {user?.status === "admin" && (
            <Link
              href="/admin"
              className="rounded-sm border border-ink px-3 py-1.5 font-display text-xs font-medium text-ink transition-colors hover:border-accent hover:text-accent"
            >
              Admin
            </Link>
          )}
          <LogoutButton />
        </div>
      </header>

      <div className="flex items-center justify-between">
        <p className="text-sm text-ink-muted">
          {notes?.length ? `${notes.length} ${notes.length === 1 ? "entry" : "entries"} in the drawer` : "The drawer is empty"}
        </p>
        <Link
          href="/notes/new"
          className="rounded-sm bg-accent px-4 py-2 font-display text-sm font-medium text-paper-card transition-colors hover:bg-accent-hover"
        >
          New note
        </Link>
      </div>

      {notes && notes.length > 0 ? (
        <section aria-label="Notes" className="grid gap-4 sm:grid-cols-2">
          {notes.map((note) => (
            <Link key={note.id} href={`/notes/${note.id}`} className="block">
              <NoteCard note={note} />
            </Link>
          ))}
        </section>
      ) : (
        <div className="rounded-sm border border-dashed border-rule px-6 py-12 text-center">
          <p className="font-display text-sm text-ink-muted">No notes yet.</p>
          <p className="mt-1 text-sm text-ink-muted">
            Write down the first thing worth keeping track of.
          </p>
        </div>
      )}
    </main>
  );
}
