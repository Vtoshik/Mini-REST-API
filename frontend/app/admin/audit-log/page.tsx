import Link from "next/link";
import { serverFetch } from "@/lib/serverFetch";
import { AuditLogEntry, Paginated } from "@/lib/types";
import { Pagination } from "@/components/Pagination";

const ACTION_LABELS: Record<string, string> = {
  user_created: "created user",
  user_updated: "updated user",
  user_deleted: "deleted user",
  password_reset_issued: "issued a password reset for",
};

function formatStamp(dateStr: string) {
  return new Date(dateStr).toLocaleString("en-US", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export default async function AuditLogPage({ searchParams }: PageProps<"/admin/audit-log">) {
  const { page } = await searchParams;
  const pageParam = Array.isArray(page) ? page[0] : page;
  const log = await serverFetch<Paginated<AuditLogEntry>>(
    `/api/v1/admin/audit-log?page=${pageParam ?? 1}`
  );
  const entries = log?.data ?? [];

  return (
    <main className="mx-auto flex w-full max-w-3xl flex-1 flex-col gap-8 px-6 py-16">
      <header className="flex items-start justify-between border-b border-rule pb-6">
        <div>
          <p className="font-display text-xs uppercase tracking-[0.2em] text-ink-muted">
            Drawer 00 — Accounts
          </p>
          <h1 className="mt-2 font-display text-3xl font-bold tracking-tight text-ink">
            Audit log
          </h1>
        </div>
        <Link
          href="/admin"
          className="rounded-sm border border-ink px-3 py-1.5 font-display text-xs font-medium text-ink transition-colors hover:border-accent hover:text-accent"
        >
          Back to users
        </Link>
      </header>

      <p className="text-sm text-ink-muted">
        A record of admin actions on user accounts: creations, edits, deletions, and
        password resets issued.
      </p>

      {entries.length === 0 ? (
        <div className="rounded-sm border border-dashed border-rule px-6 py-12 text-center">
          <p className="font-display text-sm text-ink-muted">Nothing logged yet.</p>
        </div>
      ) : (
        <div className="border-t border-rule">
          {entries.map((entry) => (
            <div
              key={entry.id}
              className="grid grid-cols-[auto_1fr_auto] items-center gap-4 border-b border-rule px-3 py-3 text-sm"
            >
              <span className="font-display font-medium text-ink">{entry.actor_username}</span>
              <span className="truncate text-ink-muted">
                {ACTION_LABELS[entry.action] ?? entry.action}
                {entry.details ? ` — ${entry.details}` : ""}
              </span>
              <span className="font-display text-xs text-ink-muted">
                {formatStamp(entry.created_at)}
              </span>
            </div>
          ))}
        </div>
      )}

      {log && <Pagination pagination={log.pagination} basePath="/admin/audit-log" />}
    </main>
  );
}
