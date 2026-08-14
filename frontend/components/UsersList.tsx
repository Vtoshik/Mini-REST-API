"use client";

import { useMemo, useState } from "react";
import { User } from "@/lib/types";
import { UserRow } from "@/components/UserRow";
import { FormField } from "@/components/FormField";

export function UsersList({ users }: { users: User[] }) {
  const [query, setQuery] = useState("");

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return users;
    return users.filter(
      (u) =>
        u.username.toLowerCase().includes(q) ||
        u.email.toLowerCase().includes(q) ||
        u.status.toLowerCase().includes(q)
    );
  }, [users, query]);

  if (users.length === 0) {
    return (
      <div className="rounded-sm border border-dashed border-rule px-6 py-12 text-center">
        <p className="font-display text-sm text-ink-muted">No accounts on file.</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-6">
      <div className="max-w-xs">
        <FormField id="users-search" label="Search" value={query} onChange={setQuery} />
      </div>

      <p className="text-sm text-ink-muted">
        {filtered.length} of {users.length} {users.length === 1 ? "account" : "accounts"}
      </p>

      {filtered.length > 0 ? (
        <div className="border-t border-rule">
          {filtered.map((u) => (
            <UserRow key={u.id} user={u} />
          ))}
        </div>
      ) : (
        <p className="text-sm text-ink-muted">No accounts match &quot;{query}&quot;.</p>
      )}
    </div>
  );
}
