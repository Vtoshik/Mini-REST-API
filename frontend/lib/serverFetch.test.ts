import { describe, it, expect, beforeEach, vi } from "vitest";

const toStringMock = vi.fn(() => "access_token_cookie=abc123");

vi.mock("next/headers", () => ({
  cookies: vi.fn(async () => ({ toString: toStringMock })),
}));

describe("serverFetch", () => {
  beforeEach(() => {
    vi.resetModules();
    vi.unstubAllEnvs();
    vi.stubGlobal("fetch", vi.fn());
  });

  it("forwards the cookie header from the incoming request", async () => {
    (fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ id: 1, username: "demo" }),
    });
    const { serverFetch } = await import("@/lib/serverFetch");

    const result = await serverFetch("/api/v1/me");

    expect(result).toEqual({ id: 1, username: "demo" });
    const [, options] = (fetch as ReturnType<typeof vi.fn>).mock.calls[0];
    expect(options.headers.cookie).toBe("access_token_cookie=abc123");
    expect(options.cache).toBe("no-store");
  });

  it("returns null when the response is not ok", async () => {
    (fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({ ok: false, json: async () => ({}) });
    const { serverFetch } = await import("@/lib/serverFetch");

    const result = await serverFetch("/api/v1/me");
    expect(result).toBeNull();
  });

  it("uses API_INTERNAL_URL when set, for server-side (Docker-network) calls", async () => {
    vi.stubEnv("API_INTERNAL_URL", "http://backend:5000");
    (fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({ ok: true, json: async () => ({}) });
    const { serverFetch } = await import("@/lib/serverFetch");

    await serverFetch("/api/v1/me");
    const [url] = (fetch as ReturnType<typeof vi.fn>).mock.calls[0];
    expect(url).toBe("http://backend:5000/api/v1/me");
  });

  it("falls back to NEXT_PUBLIC_API_URL when API_INTERNAL_URL is unset", async () => {
    vi.stubEnv("NEXT_PUBLIC_API_URL", "http://localhost:5000");
    (fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({ ok: true, json: async () => ({}) });
    const { serverFetch } = await import("@/lib/serverFetch");

    await serverFetch("/api/v1/me");
    const [url] = (fetch as ReturnType<typeof vi.fn>).mock.calls[0];
    expect(url).toBe("http://localhost:5000/api/v1/me");
  });
});
