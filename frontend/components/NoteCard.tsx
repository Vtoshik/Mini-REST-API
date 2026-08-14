import { Note } from "@/lib/types";
import { IndexTab } from "@/components/IndexTab";

function formatStamp(dateStr?: string) {
  if (!dateStr) return "—";
  const d = new Date(dateStr);
  return d
    .toLocaleDateString("en-US", { year: "2-digit", month: "2-digit", day: "2-digit" })
    .replace(/\//g, ".");
}

export function NoteCard({ note }: { note: Note }) {
  return (
    <article className="relative overflow-hidden rounded-sm border border-rule bg-paper-card pl-6 pr-4 py-4 shadow-[2px_2px_0_var(--rule)]">
      <IndexTab seed={note.id} />
      <div className="flex items-baseline justify-between gap-3">
        <h3 className="truncate font-display text-base font-bold tracking-tight text-ink">
          {note.pinned && <span className="mr-1.5 text-accent" aria-label="Pinned">●</span>}
          {note.title}
        </h3>
        <span className="shrink-0 font-display text-xs text-ink-muted">
          #{String(note.id).padStart(3, "0")} · {formatStamp(note.created_at)}
        </span>
      </div>
      {note.category && (
        <span className="mt-1.5 inline-block rounded-sm border border-rule bg-paper px-1.5 py-0.5 font-display text-[10px] uppercase tracking-wide text-ink-muted">
          {note.category}
        </span>
      )}
      {note.content && (
        <p className="mt-2 line-clamp-3 text-sm text-ink-muted">{note.content}</p>
      )}
    </article>
  );
}
