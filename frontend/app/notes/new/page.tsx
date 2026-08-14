"use client";

import { useState, FormEvent } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { apiFetch, ApiError } from "@/lib/api";
import { FormField } from "@/components/FormField";
import { TextAreaField } from "@/components/TextAreaField";

// Mirrors the backend's exact rule (schemas.py NoteCreateSchema): titles need
// two non-space characters at minimum, so a single character is rejected too.
const TITLE_PATTERN = /^\S.*\S$/;

function validateTitle(title: string): string | undefined {
  if (title.length === 0) return "Required";
  if (title.length > 20) return "20 characters max";
  if (!TITLE_PATTERN.test(title)) return "Can't be only whitespace";
  return undefined;
}

export default function NewNotePage() {
  const router = useRouter();
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [titleError, setTitleError] = useState<string | undefined>();
  const [formError, setFormError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setFormError(null);
    const error = validateTitle(title);
    setTitleError(error);
    if (error) return;

    setSubmitting(true);
    try {
      await apiFetch("/api/v1/notes", { method: "POST", body: { title, content } });
      router.push("/notes");
      router.refresh();
    } catch (err) {
      setFormError(err instanceof ApiError ? err.message : "Something went wrong. Try again.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="mx-auto flex w-full max-w-lg flex-1 flex-col px-6 py-16">
      <p className="font-display text-xs uppercase tracking-[0.2em] text-ink-muted">
        Drawer 01 — Notes
      </p>
      <h1 className="mt-2 font-display text-2xl font-bold tracking-tight text-ink">
        New note
      </h1>

      <form onSubmit={handleSubmit} noValidate className="mt-8 flex flex-col gap-5">
        <FormField id="title" label="Title (20 chars max)" value={title} onChange={setTitle} error={titleError} />
        <TextAreaField id="content" label="Content" value={content} onChange={setContent} />

        {formError && (
          <p role="alert" className="rounded-sm border border-signal bg-signal/10 px-3 py-2 text-sm text-signal">
            {formError}
          </p>
        )}

        <div className="mt-2 flex gap-3">
          <button
            type="submit"
            disabled={submitting}
            className="rounded-sm bg-accent px-4 py-2 font-display text-sm font-medium text-paper-card transition-colors hover:bg-accent-hover disabled:opacity-60"
          >
            {submitting ? "Saving…" : "Save note"}
          </button>
          <Link
            href="/notes"
            className="rounded-sm border border-ink px-4 py-2 font-display text-sm font-medium text-ink transition-colors hover:border-signal hover:text-signal"
          >
            Cancel
          </Link>
        </div>
      </form>
    </main>
  );
}
