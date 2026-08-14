import { cookies } from "next/headers";
import { API_BASE_URL } from "@/lib/api";

export async function serverFetch<T>(path: string): Promise<T | null> {
  const cookieStore = await cookies();
  const res = await fetch(`${API_BASE_URL}${path}`, {
    headers: { cookie: cookieStore.toString() },
    cache: "no-store",
  });
  if (!res.ok) return null;
  return res.json();
}
