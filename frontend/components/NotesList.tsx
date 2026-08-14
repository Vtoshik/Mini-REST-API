"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import { Note } from "@/lib/types";
import { NoteCard } from "@/components/NoteCard";
import { FormField } from "@/components/FormField";

export function NotesList({ notes }: { notes: Note[] }) {
  const [query, setQuery] = useState("");

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return notes;
    return notes.filter(
      (note) => note.title.toLowerCase().includes(q) || (note.content ?? "").toLowerCase().includes(q)
    );
  }, [notes, query]);

  if (notes.length === 0) {
    return (
      <div className="rounded-sm border border-dashed border-rule px-6 py-12 text-center">
        <p className="font-display text-sm text-ink-muted">No notes yet.</p>
        <p className="mt-1 text-sm text-ink-muted">Write down the first thing worth keeping track of.</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-6">
      <div className="max-w-xs">
        <FormField id="notes-search" label="Search" value={query} onChange={setQuery} />
      </div>

      <p className="text-sm text-ink-muted">
        {filtered.length} of {notes.length} {notes.length === 1 ? "entry" : "entries"}
      </p>

      {filtered.length > 0 ? (
        <section aria-label="Notes" className="grid gap-4 sm:grid-cols-2">
          {filtered.map((note) => (
            <Link key={note.id} href={`/notes/${note.id}`} className="block">
              <NoteCard note={note} />
            </Link>
          ))}
        </section>
      ) : (
        <p className="text-sm text-ink-muted">No notes match &quot;{query}&quot;.</p>
      )}
    </div>
  );
}
