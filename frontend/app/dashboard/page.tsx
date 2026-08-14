import { getCurrentUser } from "@/lib/session";
import { LogoutButton } from "@/components/LogoutButton";

export default async function DashboardPage() {
  const user = await getCurrentUser();

  return (
    <main className="mx-auto flex w-full max-w-3xl flex-1 flex-col gap-8 px-6 py-16">
      <header className="flex items-start justify-between border-b border-rule pb-6">
        <div>
          <p className="font-display text-xs uppercase tracking-[0.2em] text-ink-muted">
            Drawer 01 — Notes
          </p>
          <h1 className="mt-2 font-display text-3xl font-bold tracking-tight text-ink">
            {user ? `${user.username}'s notes` : "Notes"}
          </h1>
        </div>
        <LogoutButton />
      </header>

      <p className="text-sm text-ink-muted">
        Signed in as <span className="font-display text-ink">{user?.username}</span>
        {user?.status === "admin" && (
          <span className="ml-2 rounded-sm border border-accent px-1.5 py-0.5 font-display text-xs text-accent">
            admin
          </span>
        )}
        . The note ledger itself is next up — this is the confirmed-working shell.
      </p>
    </main>
  );
}
