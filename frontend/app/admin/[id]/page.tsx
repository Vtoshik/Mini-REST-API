import { notFound } from "next/navigation";
import { serverFetch } from "@/lib/serverFetch";
import { User } from "@/lib/types";
import { UserEditor } from "@/components/UserEditor";

export default async function AdminUserDetailPage({ params }: PageProps<"/admin/[id]">) {
  const { id } = await params;
  const user = await serverFetch<User>(`/api/v1/admin/users/${id}`);

  if (!user) notFound();

  return (
    <main className="mx-auto flex w-full max-w-sm flex-1 flex-col px-6 py-16">
      <p className="font-display text-xs uppercase tracking-[0.2em] text-ink-muted">
        Drawer 00 — Accounts — #{String(user.id).padStart(3, "0")}
      </p>
      <UserEditor user={user} />
    </main>
  );
}
