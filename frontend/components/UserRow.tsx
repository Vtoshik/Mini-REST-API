import Link from "next/link";
import { User } from "@/lib/types";

function formatStamp(dateStr?: string) {
  if (!dateStr) return "—";
  return new Date(dateStr)
    .toLocaleDateString("en-US", { year: "2-digit", month: "2-digit", day: "2-digit" })
    .replace(/\//g, ".");
}

export function UserRow({ user }: { user: User }) {
  return (
    <Link
      href={`/admin/${user.id}`}
      className="grid grid-cols-[auto_1fr_1fr_auto_auto] items-center gap-4 border-b border-rule px-3 py-3 text-sm transition-colors hover:bg-paper-card"
    >
      <span
        className={`h-2 w-2 rounded-full ${user.status === "admin" ? "bg-accent" : "bg-ink-muted"}`}
        aria-hidden
      />
      <span className="truncate font-display font-medium text-ink">{user.username}</span>
      <span className="truncate text-ink-muted">{user.email}</span>
      <span className="font-display text-xs uppercase tracking-wide text-ink-muted">
        {user.status}
      </span>
      <span className="font-display text-xs text-ink-muted">{formatStamp(user.created_at)}</span>
    </Link>
  );
}
