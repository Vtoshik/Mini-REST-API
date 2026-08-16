"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import { Note } from "@/lib/types";
import { NoteCard } from "@/components/NoteCard";
import { FormField } from "@/components/FormField";

const ALL_CATEGORIES = "__all__";

export function NotesList({ notes }: { notes: Note[] }) {
  const [query, setQuery] = useState("");
  const [category, setCategory] = useState(ALL_CATEGORIES);

  const categories = useMemo(
    () => Array.from(new Set(notes.map((n) => n.category).filter((c): c is string => Boolean(c)))).sort(),
    [notes]
  );

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    const matches = notes.filter((note) => {
      const matchesQuery =
        !q || note.title.toLowerCase().includes(q) || (note.content ?? "").toLowerCase().includes(q);
      const matchesCategory = category === ALL_CATEGORIES || note.category === category;
      return matchesQuery && matchesCategory;
    });
    return [...matches].sort((a, b) => {
      if (a.pinned !== b.pinned) return a.pinned ? -1 : 1;
      return (b.created_at ?? "").localeCompare(a.created_at ?? "");
    });
  }, [notes, query, category]);

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
      <div className="flex flex-wrap items-end gap-4">
        <div className="max-w-xs flex-1">
          <FormField id="notes-search" label="Search" value={query} onChange={setQuery} />
        </div>
        {categories.length > 0 && (
          <div className="flex flex-col gap-1.5">
            <label htmlFor="notes-category" className="font-display text-xs uppercase tracking-[0.15em] text-ink-muted">
              Category
            </label>
            <select
              id="notes-category"
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="border-0 border-b-2 border-rule bg-transparent px-0.5 py-2 text-ink outline-none transition-colors focus:border-accent"
            >
              <option value={ALL_CATEGORIES}>All</option>
              {categories.map((c) => (
                <option key={c} value={c}>
                  {c}
                </option>
              ))}
            </select>
          </div>
        )}
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
        <p className="text-sm text-ink-muted">No notes match the current filters.</p>
      )}
    </div>
  );
}
