import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { UserRow } from "@/components/UserRow";
import { User } from "@/lib/types";

function user(overrides: Partial<User>): User {
  return { id: 3, username: "alice", email: "alice@example.com", status: "user", ...overrides };
}

describe("UserRow", () => {
  it("links to the admin detail page for that user", () => {
    render(<UserRow user={user({})} />);
    expect(screen.getByRole("link")).toHaveAttribute("href", "/admin/3");
  });

  it("renders username, email, and status", () => {
    render(<UserRow user={user({ status: "admin" })} />);
    expect(screen.getByText("alice")).toBeInTheDocument();
    expect(screen.getByText("alice@example.com")).toBeInTheDocument();
    expect(screen.getByText("admin")).toBeInTheDocument();
  });

  it("shows a placeholder dash when created_at is missing", () => {
    render(<UserRow user={user({})} />);
    expect(screen.getByText("—")).toBeInTheDocument();
  });
});
