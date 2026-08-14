"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { apiFetch, ApiError } from "@/lib/api";
import { Note } from "@/lib/types";

function formatStamp(dateStr?: string | null) {
  if (!dateStr) return "—";
  return new Date(dateStr)
    .toLocaleDateString("en-US", { year: "2-digit", month: "2-digit", day: "2-digit" })
    .replace(/\//g, ".");
}

function TrashRow({ note }: { note: Note }) {
  const router = useRouter();
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [confirmingDelete, setConfirmingDelete] = useState(false);

  async function handleRestore() {
    setError(null);
    setPending(true);
    try {
      await apiFetch(`/api/v1/notes/${note.id}/restore`, { method: "POST" });
      router.refresh();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Couldn't restore this note.");
      setPending(false);
    }
  }

  async function handlePermanentDelete() {
    setError(null);
    setPending(true);
    try {
      await apiFetch(`/api/v1/notes/${note.id}/permanent`, { method: "DELETE" });
      router.refresh();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Couldn't delete this note.");
      setPending(false);
    }
  }

  return (
    <div className="flex flex-col gap-1.5 border-b border-rule px-3 py-3">
      <div className="flex items-center justify-between gap-3">
        <div className="min-w-0">
          <p className="truncate font-display font-medium text-ink">{note.title}</p>
          <p className="font-display text-xs text-ink-muted">Trashed {formatStamp(note.deleted_at)}</p>
        </div>
        <div className="flex shrink-0 items-center gap-3">
          <button
            type="button"
            onClick={handleRestore}
            disabled={pending}
            className="font-display text-xs font-medium text-accent hover:text-accent-hover disabled:opacity-60"
          >
            Restore
          </button>
          {confirmingDelete ? (
            <>
              <button
                type="button"
                onClick={handlePermanentDelete}
                disabled={pending}
                className="rounded-sm bg-signal px-2 py-1 font-display text-xs font-medium text-paper-card transition-colors hover:bg-signal-hover disabled:opacity-60"
              >
                Confirm
              </button>
              <button
                type="button"
                onClick={() => setConfirmingDelete(false)}
                className="font-display text-xs text-ink-muted hover:text-ink"
              >
                Cancel
              </button>
            </>
          ) : (
            <button
              type="button"
              onClick={() => setConfirmingDelete(true)}
              className="font-display text-xs font-medium text-signal hover:text-signal-hover"
            >
              Delete forever
            </button>
          )}
        </div>
      </div>
      {error && <p className="text-xs text-signal">{error}</p>}
    </div>
  );
}

export function TrashList({ notes }: { notes: Note[] }) {
  if (notes.length === 0) {
    return (
      <div className="rounded-sm border border-dashed border-rule px-6 py-12 text-center">
        <p className="font-display text-sm text-ink-muted">Trash is empty.</p>
      </div>
    );
  }

  return (
    <div className="border-t border-rule">
      {notes.map((note) => (
        <TrashRow key={note.id} note={note} />
      ))}
    </div>
  );
}
