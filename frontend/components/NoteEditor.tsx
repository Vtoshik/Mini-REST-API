"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { apiFetch, ApiError } from "@/lib/api";
import { Note } from "@/lib/types";
import { FormField } from "@/components/FormField";
import { TextAreaField } from "@/components/TextAreaField";

const TITLE_PATTERN = /^\S.*\S$/;

function validateTitle(title: string): string | undefined {
  if (title.length === 0) return "Required";
  if (title.length > 20) return "20 characters max";
  if (!TITLE_PATTERN.test(title)) return "Can't be only whitespace";
  return undefined;
}

export function NoteEditor({ note }: { note: Note }) {
  const router = useRouter();
  const [title, setTitle] = useState(note.title);
  const [content, setContent] = useState(note.content ?? "");
  const [titleError, setTitleError] = useState<string | undefined>();
  const [formError, setFormError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [confirmingDelete, setConfirmingDelete] = useState(false);

  async function handleSave() {
    setFormError(null);
    const error = validateTitle(title);
    setTitleError(error);
    if (error) return;

    setSaving(true);
    try {
      await apiFetch(`/api/v1/notes/${note.id}`, { method: "PATCH", body: { title, content } });
      router.refresh();
    } catch (err) {
      setFormError(err instanceof ApiError ? err.message : "Something went wrong. Try again.");
    } finally {
      setSaving(false);
    }
  }

  async function handleDelete() {
    setDeleting(true);
    try {
      await apiFetch(`/api/v1/notes/${note.id}`, { method: "DELETE" });
      router.push("/notes");
      router.refresh();
    } catch (err) {
      setFormError(err instanceof ApiError ? err.message : "Couldn't delete this note.");
      setDeleting(false);
    }
  }

  return (
    <div className="mt-8 flex flex-col gap-5">
      <FormField id="title" label="Title (20 chars max)" value={title} onChange={setTitle} error={titleError} />
      <TextAreaField id="content" label="Content" value={content} onChange={setContent} />

      {formError && (
        <p role="alert" className="rounded-sm border border-signal bg-signal/10 px-3 py-2 text-sm text-signal">
          {formError}
        </p>
      )}

      <div className="mt-2 flex items-center gap-3">
        <button
          type="button"
          onClick={handleSave}
          disabled={saving}
          className="rounded-sm bg-accent px-4 py-2 font-display text-sm font-medium text-paper-card transition-colors hover:bg-accent-hover disabled:opacity-60"
        >
          {saving ? "Saving…" : "Save changes"}
        </button>
        <Link
          href="/notes"
          className="rounded-sm border border-ink px-4 py-2 font-display text-sm font-medium text-ink transition-colors hover:border-accent hover:text-accent"
        >
          Back
        </Link>

        <div className="ml-auto">
          {confirmingDelete ? (
            <div className="flex items-center gap-2">
              <span className="text-sm text-ink-muted">Delete for good?</span>
              <button
                type="button"
                onClick={handleDelete}
                disabled={deleting}
                className="rounded-sm bg-signal px-3 py-1.5 font-display text-xs font-medium text-paper-card transition-colors hover:bg-signal-hover disabled:opacity-60"
              >
                {deleting ? "Deleting…" : "Confirm"}
              </button>
              <button
                type="button"
                onClick={() => setConfirmingDelete(false)}
                className="font-display text-xs text-ink-muted hover:text-ink"
              >
                Cancel
              </button>
            </div>
          ) : (
            <button
              type="button"
              onClick={() => setConfirmingDelete(true)}
              className="font-display text-xs font-medium text-signal hover:text-signal-hover"
            >
              Delete note
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
