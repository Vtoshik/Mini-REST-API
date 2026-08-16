import { describe, it, expect, beforeEach, vi } from "vitest";

function jsonResponse(body: unknown, init: { status?: number; ok?: boolean } = {}) {
  const status = init.status ?? 200;
  return {
    ok: init.ok ?? (status >= 200 && status < 300),
    status,
    statusText: "",
    headers: { get: () => "application/json" },
    json: async () => body,
  } as unknown as Response;
}

describe("apiFetch", () => {
  beforeEach(() => {
    vi.resetModules();
    vi.stubGlobal("fetch", vi.fn());
  });

  it("does not fetch a CSRF token for GET requests", async () => {
    const { apiFetch } = await import("@/lib/api");
    (fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce(jsonResponse({ ok: true }));

    await apiFetch("/api/v1/notes");

    expect(fetch).toHaveBeenCalledTimes(1);
    const [, options] = (fetch as ReturnType<typeof vi.fn>).mock.calls[0];
    expect(options.headers["X-CSRF-Token"]).toBeUndefined();
    expect(options.credentials).toBe("include");
  });

  it("fetches a CSRF token before an unsafe request and caches it", async () => {
    const { apiFetch } = await import("@/lib/api");
    const fetchMock = fetch as ReturnType<typeof vi.fn>;
    fetchMock
      .mockResolvedValueOnce(jsonResponse({ csrf_token: "tok-1" }))
      .mockResolvedValueOnce(jsonResponse({ message: "Note created" }, { status: 201 }))
      .mockResolvedValueOnce(jsonResponse({ message: "Note updated" }));

    await apiFetch("/api/v1/notes", { method: "POST", body: { title: "x" } });
    expect(fetchMock).toHaveBeenCalledTimes(2);
    expect(fetchMock.mock.calls[0][0]).toContain("/api/v1/csrf-token");
    expect(fetchMock.mock.calls[1][1].headers["X-CSRF-Token"]).toBe("tok-1");

    // second unsafe call reuses the cached token, no extra csrf-token fetch
    await apiFetch("/api/v1/notes/1", { method: "PATCH", body: { title: "y" } });
    expect(fetchMock).toHaveBeenCalledTimes(3);
    expect(fetchMock.mock.calls[2][1].headers["X-CSRF-Token"]).toBe("tok-1");
  });

  it("throws an ApiError with the server message on non-ok responses", async () => {
    const { apiFetch, ApiError } = await import("@/lib/api");
    (fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce(
      jsonResponse({ message: "Invalid credentials" }, { status: 401 })
    );

    await expect(apiFetch("/api/v1/me")).rejects.toMatchObject(
      new ApiError(401, "Invalid credentials", { message: "Invalid credentials" })
    );
  });

  it("falls back to statusText when the error body has no message", async () => {
    const { apiFetch } = await import("@/lib/api");
    (fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
      ok: false,
      status: 500,
      statusText: "Internal Server Error",
      headers: { get: () => null },
      json: async () => null,
    } as unknown as Response);

    await expect(apiFetch("/api/v1/me")).rejects.toThrow("Internal Server Error");
  });

  it("returns null-bodied data for non-JSON successful responses", async () => {
    const { apiFetch } = await import("@/lib/api");
    const fetchMock = fetch as ReturnType<typeof vi.fn>;
    fetchMock
      .mockResolvedValueOnce(jsonResponse({ csrf_token: "tok-1" }))
      .mockResolvedValueOnce({
        ok: true,
        status: 204,
        statusText: "",
        headers: { get: () => null },
        json: async () => ({}),
      } as unknown as Response);

    const result = await apiFetch("/api/v1/logout", { method: "POST" });
    expect(result).toBeNull();
  });

  it("sends the request body as JSON", async () => {
    const { apiFetch } = await import("@/lib/api");
    const fetchMock = fetch as ReturnType<typeof vi.fn>;
    fetchMock
      .mockResolvedValueOnce(jsonResponse({ csrf_token: "tok-1" }))
      .mockResolvedValueOnce(jsonResponse({ message: "ok" }));

    await apiFetch("/api/v1/notes", { method: "POST", body: { title: "hello" } });
    const [, options] = fetchMock.mock.calls[1];
    expect(options.body).toBe(JSON.stringify({ title: "hello" }));
  });
});
