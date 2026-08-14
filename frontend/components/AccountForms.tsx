"use client";

import { useState, FormEvent } from "react";
import { useRouter } from "next/navigation";
import { apiFetch, ApiError } from "@/lib/api";
import { User } from "@/lib/types";
import { FormField } from "@/components/FormField";

function ProfileForm({ user }: { user: User }) {
  const router = useRouter();
  const [username, setUsername] = useState(user.username);
  const [email, setEmail] = useState(user.email);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [saving, setSaving] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setSuccess(false);
    setSaving(true);
    try {
      await apiFetch("/api/v1/me", { method: "PUT", body: { username, email } });
      setSuccess(true);
      router.refresh();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Something went wrong. Try again.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} noValidate className="flex flex-col gap-5">
      <FormField id="username" label="Username" value={username} onChange={setUsername} autoComplete="username" />
      <FormField id="email" label="Email" type="email" value={email} onChange={setEmail} autoComplete="email" />

      {error && (
        <p role="alert" className="rounded-sm border border-signal bg-signal/10 px-3 py-2 text-sm text-signal">
          {error}
        </p>
      )}
      {success && <p className="text-sm text-accent">Profile updated.</p>}

      <button
        type="submit"
        disabled={saving}
        className="self-start rounded-sm bg-accent px-4 py-2 font-display text-sm font-medium text-paper-card transition-colors hover:bg-accent-hover disabled:opacity-60"
      >
        {saving ? "Saving…" : "Save profile"}
      </button>
    </form>
  );
}

function PasswordForm() {
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [saving, setSaving] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setSuccess(false);
    setSaving(true);
    try {
      await apiFetch("/api/v1/me/password", {
        method: "POST",
        body: { current_password: currentPassword, new_password: newPassword },
      });
      setCurrentPassword("");
      setNewPassword("");
      setSuccess(true);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Something went wrong. Try again.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} noValidate className="flex flex-col gap-5">
      <FormField
        id="current_password"
        label="Current password"
        type="password"
        value={currentPassword}
        onChange={setCurrentPassword}
        autoComplete="current-password"
      />
      <FormField
        id="new_password"
        label="New password"
        type="password"
        value={newPassword}
        onChange={setNewPassword}
        autoComplete="new-password"
      />

      {error && (
        <p role="alert" className="rounded-sm border border-signal bg-signal/10 px-3 py-2 text-sm text-signal">
          {error}
        </p>
      )}
      {success && <p className="text-sm text-accent">Password updated.</p>}

      <button
        type="submit"
        disabled={saving}
        className="self-start rounded-sm bg-accent px-4 py-2 font-display text-sm font-medium text-paper-card transition-colors hover:bg-accent-hover disabled:opacity-60"
      >
        {saving ? "Updating…" : "Update password"}
      </button>
    </form>
  );
}

export function AccountForms({ user }: { user: User }) {
  return (
    <div className="mt-8 flex flex-col gap-10">
      <section className="flex flex-col gap-4">
        <h2 className="font-display text-sm font-bold uppercase tracking-wide text-ink">Profile</h2>
        <ProfileForm user={user} />
      </section>

      <section className="flex flex-col gap-4 border-t border-rule pt-8">
        <h2 className="font-display text-sm font-bold uppercase tracking-wide text-ink">Password</h2>
        <PasswordForm />
      </section>
    </div>
  );
}
