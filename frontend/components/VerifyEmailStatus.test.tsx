import { describe, it, expect, beforeEach, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";

vi.mock("@/lib/api", async () => {
  const actual = await vi.importActual<typeof import("@/lib/api")>("@/lib/api");
  return { ...actual, apiFetch: vi.fn() };
});

import { apiFetch } from "@/lib/api";
import { VerifyEmailStatus } from "@/components/VerifyEmailStatus";

describe("VerifyEmailStatus", () => {
  beforeEach(() => {
    vi.mocked(apiFetch).mockReset();
  });

  it("shows a verifying message while the request is in flight", () => {
    vi.mocked(apiFetch).mockReturnValue(new Promise(() => {}));
    render(<VerifyEmailStatus token="abc" />);
    expect(screen.getByText("Verifying…")).toBeInTheDocument();
  });

  it("shows success and a sign-in link once verified", async () => {
    vi.mocked(apiFetch).mockResolvedValue({ message: "Email verified" });
    render(<VerifyEmailStatus token="abc" />);

    await waitFor(() => expect(screen.getByText(/Email verified/)).toBeInTheDocument());
    expect(screen.getByRole("link", { name: "Go to sign in" })).toHaveAttribute("href", "/login");
  });

  it("shows an error message when verification fails", async () => {
    const { ApiError } = await import("@/lib/api");
    vi.mocked(apiFetch).mockRejectedValue(
      new ApiError(400, "This verification link is invalid or has expired", {})
    );
    render(<VerifyEmailStatus token="bad-token" />);

    await waitFor(() =>
      expect(screen.getByText("This verification link is invalid or has expired")).toBeInTheDocument()
    );
  });
});
