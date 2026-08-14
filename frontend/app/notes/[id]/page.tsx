import { notFound } from "next/navigation";
import { serverFetch } from "@/lib/serverFetch";
import { Note } from "@/lib/types";
import { NoteEditor } from "@/components/NoteEditor";

export default async function NoteDetailPage({ params }: PageProps<"/notes/[id]">) {
  const { id } = await params;
  const note = await serverFetch<Note>(`/api/v1/notes/${id}`);

  if (!note) notFound();

  return (
    <main className="mx-auto flex w-full max-w-lg flex-1 flex-col px-6 py-16">
      <p className="font-display text-xs uppercase tracking-[0.2em] text-ink-muted">
        Drawer 01 — Notes — #{String(note.id).padStart(3, "0")}
      </p>
      <NoteEditor note={note} />
    </main>
  );
}
