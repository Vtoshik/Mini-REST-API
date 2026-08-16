import Link from "next/link";
import { getCurrentUser } from "@/lib/session";
import { serverFetch } from "@/lib/serverFetch";
import { User, Paginated } from "@/lib/types";
import { UsersList } from "@/components/UsersList";
import { LogoutButton } from "@/components/LogoutButton";
import { Pagination } from "@/components/Pagination";

export default async function AdminPage({ searchParams }: PageProps<"/admin">) {
  const { page } = await searchParams;
  const pageParam = Array.isArray(page) ? page[0] : page;
  const [user, users] = await Promise.all([
    getCurrentUser(),
    serverFetch<Paginated<User>>(`/api/v1/admin/users?page=${pageParam ?? 1}`),
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
        <div className="flex items-center gap-3">
          <Link
            href="/admin/audit-log"
            className="rounded-sm border border-ink px-3 py-1.5 font-display text-xs font-medium text-ink transition-colors hover:border-accent hover:text-accent"
          >
            Audit log
          </Link>
          <Link
            href="/admin/new"
            className="rounded-sm bg-accent px-4 py-2 font-display text-sm font-medium text-paper-card transition-colors hover:bg-accent-hover"
          >
            New user
          </Link>
        </div>
      </div>

      <UsersList users={users?.data ?? []} />
      {users && <Pagination pagination={users.pagination} basePath="/admin" />}
    </main>
  );
}
