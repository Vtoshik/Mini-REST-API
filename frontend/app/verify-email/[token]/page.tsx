import { VerifyEmailStatus } from "@/components/VerifyEmailStatus";

export default async function VerifyEmailPage({ params }: PageProps<"/verify-email/[token]">) {
  const { token } = await params;

  return (
    <main className="mx-auto flex w-full max-w-sm flex-1 flex-col justify-center px-6 py-16">
      <p className="font-display text-xs uppercase tracking-[0.2em] text-ink-muted">
        Drawer 02 — Account
      </p>
      <h1 className="mt-2 font-display text-2xl font-bold tracking-tight text-ink">
        Verify your email
      </h1>
      <VerifyEmailStatus token={token} />
    </main>
  );
}
