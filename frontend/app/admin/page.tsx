import Link from "next/link";
import { getCurrentUser } from "@/lib/session";
import { serverFetch } from "@/lib/serverFetch";
import { User } from "@/lib/types";
import { UserRow } from "@/components/UserRow";
import { LogoutButton } from "@/components/LogoutButton";

export default async function AdminPage() {
  const [user, users] = await Promise.all([
    getCurrentUser(),
    serverFetch<User[]>("/api/v1/admin/users"),
  ]);

  return (
    <main className="mx-auto flex w-full max-w-3xl flex-1 flex-col gap-8 px-6 py-16">
      <header className="flex items-start justify-between border-b border-rule pb-6">
        <div>
          <p className="font-display text-xs uppercase tracking-[0.2em] text-ink-muted">
            Drawer 00 — Accounts
          </p>
          <h1 className="mt-2 font-display text-3xl font-bold tracking-tight text-ink">
            Users
          </h1>
        </div>
        <div className="flex items-center gap-3">
          <Link
            href="/notes"
            className="rounded-sm border border-ink px-3 py-1.5 font-display text-xs font-medium text-ink transition-colors hover:border-accent hover:text-accent"
          >
            My notes
          </Link>
          <LogoutButton />
        </div>
      </header>

      <div className="flex items-center justify-between">
        <p className="text-sm text-ink-muted">
          Signed in as <span className="font-display text-ink">{user?.username}</span>
        </p>
        <Link
          href="/admin/new"
          className="rounded-sm bg-accent px-4 py-2 font-display text-sm font-medium text-paper-card transition-colors hover:bg-accent-hover"
        >
          New user
        </Link>
      </div>

      {users && users.length > 0 ? (
        <div className="border-t border-rule">
          {users.map((u) => (
            <UserRow key={u.id} user={u} />
          ))}
        </div>
      ) : (
        <div className="rounded-sm border border-dashed border-rule px-6 py-12 text-center">
          <p className="font-display text-sm text-ink-muted">No accounts on file.</p>
        </div>
      )}
    </main>
  );
}
