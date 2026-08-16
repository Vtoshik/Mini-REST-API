import { cookies } from "next/headers";
import { API_BASE_URL } from "@/lib/api";

// Server-side code (Server Components, this file) runs inside the Next.js
// server process, which in Docker Compose is a different container from
// Flask — "localhost" there means the frontend container itself, not the
// backend. API_INTERNAL_URL lets Compose point server-side calls at the
// backend's service name (e.g. http://backend:5000) while the browser still
// uses NEXT_PUBLIC_API_URL (e.g. http://localhost:5000). Outside Docker,
// leave API_INTERNAL_URL unset and this just falls back to the public URL.
const SERVER_API_BASE_URL = process.env.API_INTERNAL_URL ?? API_BASE_URL;

export async function serverFetch<T>(path: string): Promise<T | null> {
  const cookieStore = await cookies();
  const res = await fetch(`${SERVER_API_BASE_URL}${path}`, {
    headers: { cookie: cookieStore.toString() },
    cache: "no-store",
  });
  if (!res.ok) return null;
  return res.json();
}
