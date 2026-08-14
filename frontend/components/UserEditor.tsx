"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { apiFetch, ApiError } from "@/lib/api";
import { User, UserStatus } from "@/lib/types";
import { FormField } from "@/components/FormField";

export function UserEditor({ user }: { user: User }) {
  const router = useRouter();
  const [username, setUsername] = useState(user.username);
  const [email, setEmail] = useState(user.email);
  const [status, setStatus] = useState<UserStatus>(user.status);
  const [password, setPassword] = useState("");
  const [formError, setFormError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [confirmingDelete, setConfirmingDelete] = useState(false);

  async function handleSave() {
    setFormError(null);
    setSaving(true);
    try {
      const body: Record<string, string> = { username, email, status };
      if (password) body.password = password;
      await apiFetch(`/api/v1/admin/users/${user.id}`, { method: "PUT", body });
      setPassword("");
      router.refresh();
    } catch (err) {
      setFormError(err instanceof ApiError ? err.message : "Something went wrong. Try again.");
    } finally {
      setSaving(false);
    }
  }

  async function handleDelete() {
    setDeleting(true);
    try {
      await apiFetch(`/api/v1/admin/users/${user.id}`, { method: "DELETE" });
      router.push("/admin");
      router.refresh();
    } catch (err) {
      setFormError(err instanceof ApiError ? err.message : "Couldn't delete this account.");
      setDeleting(false);
    }
  }

  return (
    <div className="mt-8 flex flex-col gap-5">
      <FormField id="username" label="Username" value={username} onChange={setUsername} />
      <FormField id="email" label="Email" type="email" value={email} onChange={setEmail} />

      <div className="flex flex-col gap-1.5">
        <label htmlFor="status" className="font-display text-xs uppercase tracking-[0.15em] text-ink-muted">
          Access level
        </label>
        <select
          id="status"
          value={status}
          onChange={(e) => setStatus(e.target.value as UserStatus)}
          className="border-0 border-b-2 border-rule bg-transparent px-0.5 py-2 text-ink outline-none transition-colors focus:border-accent"
        >
          <option value="user">user</option>
          <option value="admin">admin</option>
        </select>
      </div>

      <FormField
        id="password"
        label="New password (leave blank to keep current)"
        type="password"
        value={password}
        onChange={setPassword}
        autoComplete="new-password"
      />

      {formError && (
        <p role="alert" className="rounded-sm border border-signal bg-signal/10 px-3 py-2 text-sm text-signal">
          {formError}
        </p>
      )}

      <div className="mt-2 flex items-center gap-3">
        <button
          type="button"
          onClick={handleSave}
          disabled={saving}
          className="rounded-sm bg-accent px-4 py-2 font-display text-sm font-medium text-paper-card transition-colors hover:bg-accent-hover disabled:opacity-60"
        >
          {saving ? "Saving…" : "Save changes"}
        </button>
        <Link
          href="/admin"
          className="rounded-sm border border-ink px-4 py-2 font-display text-sm font-medium text-ink transition-colors hover:border-accent hover:text-accent"
        >
          Back
        </Link>

        <div className="ml-auto">
          {confirmingDelete ? (
            <div className="flex items-center gap-2">
              <span className="text-sm text-ink-muted">Delete for good?</span>
              <button
                type="button"
                onClick={handleDelete}
                disabled={deleting}
                className="rounded-sm bg-signal px-3 py-1.5 font-display text-xs font-medium text-paper-card transition-colors hover:bg-signal-hover disabled:opacity-60"
              >
                {deleting ? "Deleting…" : "Confirm"}
              </button>
              <button
                type="button"
                onClick={() => setConfirmingDelete(false)}
                className="font-display text-xs text-ink-muted hover:text-ink"
              >
                Cancel
              </button>
            </div>
          ) : (
            <button
              type="button"
              onClick={() => setConfirmingDelete(true)}
              className="font-display text-xs font-medium text-signal hover:text-signal-hover"
            >
              Delete account
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
