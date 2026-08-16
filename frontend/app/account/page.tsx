import { getCurrentUser } from "@/lib/session";
import { AccountForms } from "@/components/AccountForms";

export default async function AccountPage() {
  const user = await getCurrentUser();

  return (
    <main className="mx-auto flex w-full max-w-md flex-1 flex-col px-6 py-16">
      <p className="font-display text-xs uppercase tracking-[0.2em] text-ink-muted">
        Drawer 02 — Account
      </p>
      <h1 className="mt-2 font-display text-2xl font-bold tracking-tight text-ink">
        Your account
      </h1>
      {user && <AccountForms user={user} />}
    </main>
  );
}
