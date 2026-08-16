"use client";

import { useState, FormEvent } from "react";
import Link from "next/link";
import { apiFetch, ApiError } from "@/lib/api";
import { FormField } from "@/components/FormField";

interface RegisterResponse {
  user_id: number;
  verify_token: string;
  verify_path: string;
}

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

export default function RegisterPage() {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fieldErrors, setFieldErrors] = useState<ReturnType<typeof validate>>({});
  const [formError, setFormError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [verifyLink, setVerifyLink] = useState<string | null>(null);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setFormError(null);
    const errors = validate(username, email, password);
    setFieldErrors(errors);
    if (Object.keys(errors).length > 0) return;

    setSubmitting(true);
    try {
      const data = await apiFetch<RegisterResponse>("/api/v1/register", {
        method: "POST",
        body: { username, email, password },
      });
      setVerifyLink(`${window.location.origin}${data.verify_path}`);
    } catch (err) {
      setFormError(err instanceof ApiError ? err.message : "Something went wrong. Try again.");
    } finally {
      setSubmitting(false);
    }
  }

  if (verifyLink) {
    return (
      <main className="mx-auto flex w-full max-w-sm flex-1 flex-col justify-center px-6 py-16">
        <p className="font-display text-xs uppercase tracking-[0.2em] text-ink-muted">
          Drawer 01 — Notes
        </p>
        <h1 className="mt-2 font-display text-2xl font-bold tracking-tight text-ink">
          Check your email
        </h1>
        <p className="mt-4 text-sm text-ink-muted">
          Account created. There&apos;s no email service configured yet, so here&apos;s the
          verification link directly — you&apos;ll need it before you can sign in.
        </p>
        <Link
          href={verifyLink}
          className="mt-4 truncate rounded-sm border border-rule bg-paper-card px-3 py-2 text-xs text-accent underline-offset-2 hover:underline"
        >
          {verifyLink}
        </Link>
      </main>
    );
  }

  return (
    <main className="mx-auto flex w-full max-w-sm flex-1 flex-col justify-center px-6 py-16">
      <p className="font-display text-xs uppercase tracking-[0.2em] text-ink-muted">
        Drawer 01 — Notes
      </p>
      <h1 className="mt-2 font-display text-2xl font-bold tracking-tight text-ink">
        Create account
      </h1>

      <form onSubmit={handleSubmit} noValidate className="mt-8 flex flex-col gap-5">
        <FormField id="username" label="Username" value={username} onChange={setUsername} error={fieldErrors.username} autoComplete="username" />
        <FormField id="email" label="Email" type="email" value={email} onChange={setEmail} error={fieldErrors.email} autoComplete="email" />
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

        <button
          type="submit"
          disabled={submitting}
          className="mt-2 rounded-sm bg-accent px-4 py-2 font-display text-sm font-medium text-paper-card transition-colors hover:bg-accent-hover disabled:opacity-60"
        >
          {submitting ? "Creating account…" : "Create account"}
        </button>
      </form>

      <p className="mt-6 text-sm text-ink-muted">
        Already have an account?{" "}
        <Link href="/login" className="text-accent underline-offset-2 hover:underline">
          Sign in
        </Link>
      </p>
    </main>
  );
}
