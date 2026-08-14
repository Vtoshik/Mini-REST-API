import { cookies } from "next/headers";
import { API_BASE_URL } from "@/lib/api";
import { User } from "@/lib/types";

export async function getCurrentUser(): Promise<User | null> {
  const cookieStore = await cookies();
  const res = await fetch(`${API_BASE_URL}/api/v1/me`, {
    headers: { cookie: cookieStore.toString() },
    cache: "no-store",
  });
  if (!res.ok) return null;
  return res.json();
}
