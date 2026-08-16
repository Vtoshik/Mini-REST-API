import { NextRequest, NextResponse } from "next/server";

// See the comment in lib/serverFetch.ts: this runs server-side too, so it
// needs the internal (container-to-container) URL in Docker Compose, not
// the browser-facing one.
const API_BASE_URL =
  process.env.API_INTERNAL_URL ?? process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:5000";

export async function proxy(request: NextRequest) {
  const res = await fetch(`${API_BASE_URL}/api/v1/me`, {
    headers: { cookie: request.headers.get("cookie") ?? "" },
  });

  if (!res.ok) {
    const loginUrl = new URL("/login", request.url);
    loginUrl.searchParams.set("next", request.nextUrl.pathname);
    return NextResponse.redirect(loginUrl);
  }

  if (request.nextUrl.pathname.startsWith("/admin")) {
    const user = await res.json();
    if (user.status !== "admin") {
      return NextResponse.redirect(new URL("/notes", request.url));
    }
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/notes/:path*", "/admin/:path*", "/account/:path*"],
};
