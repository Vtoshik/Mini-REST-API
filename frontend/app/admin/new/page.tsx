"use client";

import { useState, FormEvent } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { apiFetch, ApiError } from "@/lib/api";
import { FormField } from "@/components/FormField";

const PASSWORD_PATTERN = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&_])[A-Za-z\d@$!%*?&_]{8,}$/;

function validate(username: string, email: string, password: string) {
  const errors: { username?: string; email?: string; password?: string } = {};
  if (username.length < 3 || username.length > 20) {
    errors.username = "3-20 characters";
  }
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    errors.email = "Enter a valid email address";
  }
  if (!PASSWORD_PATTERN.test(password)) {
    errors.password = "8+ chars with upper, lower, digit, and one of @$!%*?&_";
  }
  return errors;
}

export default function NewUserPage() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fieldErrors, setFieldErrors] = useState<ReturnType<typeof validate>>({});
  const [formError, setFormError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setFormError(null);
    const errors = validate(username, email, password);
    setFieldErrors(errors);
    if (Object.keys(errors).length > 0) return;

    setSubmitting(true);
    try {
      await apiFetch("/api/v1/admin/users", { method: "POST", body: { username, email, password } });
      router.push("/admin");
      router.refresh();
    } catch (err) {
      setFormError(err instanceof ApiError ? err.message : "Something went wrong. Try again.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="mx-auto flex w-full max-w-sm flex-1 flex-col justify-center px-6 py-16">
      <p className="font-display text-xs uppercase tracking-[0.2em] text-ink-muted">
        Drawer 00 — Accounts
      </p>
      <h1 className="mt-2 font-display text-2xl font-bold tracking-tight text-ink">
        New user
      </h1>
      <p className="mt-2 text-sm text-ink-muted">
        New accounts start with regular user access. Promote to admin from the account page after creating it.
      </p>

      <form onSubmit={handleSubmit} noValidate className="mt-8 flex flex-col gap-5">
        <FormField id="username" label="Username" value={username} onChange={setUsername} error={fieldErrors.username} autoComplete="off" />
        <FormField id="email" label="Email" type="email" value={email} onChange={setEmail} error={fieldErrors.email} autoComplete="off" />
        <FormField
          id="password"
          label="Password"
          type="password"
          value={password}
          onChange={setPassword}
          error={fieldErrors.password}
          autoComplete="new-password"
        />

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
            {submitting ? "Creating…" : "Create user"}
          </button>
          <Link
            href="/admin"
            className="rounded-sm border border-ink px-4 py-2 font-display text-sm font-medium text-ink transition-colors hover:border-signal hover:text-signal"
          >
            Cancel
          </Link>
        </div>
      </form>
    </main>
  );
}
