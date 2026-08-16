import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { UsersList } from "@/components/UsersList";
import { User } from "@/lib/types";

function user(overrides: Partial<User>): User {
  return { id: 1, username: "demo", email: "demo@example.com", status: "user", ...overrides };
}

describe("UsersList", () => {
  it("shows an empty state with no users", () => {
    render(<UsersList users={[]} />);
    expect(screen.getByText("No accounts on file.")).toBeInTheDocument();
  });

  it("renders every user when there is no filter", () => {
    const users = [user({ id: 1, username: "alice" }), user({ id: 2, username: "bob" })];
    render(<UsersList users={users} />);
    expect(screen.getByText("alice")).toBeInTheDocument();
    expect(screen.getByText("bob")).toBeInTheDocument();
    expect(screen.getByText("2 of 2 accounts")).toBeInTheDocument();
  });

  it("filters by username", async () => {
    const events = userEvent.setup();
    const users = [user({ id: 1, username: "alice" }), user({ id: 2, username: "bob" })];
    render(<UsersList users={users} />);

    await events.type(screen.getByLabelText("Search"), "ali");

    expect(screen.getByText("alice")).toBeInTheDocument();
    expect(screen.queryByText("bob")).not.toBeInTheDocument();
  });

  it("filters by email", async () => {
    const events = userEvent.setup();
    const users = [
      user({ id: 1, username: "alice", email: "alice@example.com" }),
      user({ id: 2, username: "bob", email: "bob@work.com" }),
    ];
    render(<UsersList users={users} />);

    await events.type(screen.getByLabelText("Search"), "work.com");

    expect(screen.getByText("bob")).toBeInTheDocument();
    expect(screen.queryByText("alice")).not.toBeInTheDocument();
  });

  it("filters by status", async () => {
    const events = userEvent.setup();
    const users = [
      user({ id: 1, username: "alice", status: "admin" }),
      user({ id: 2, username: "bob", status: "user" }),
    ];
    render(<UsersList users={users} />);

    await events.type(screen.getByLabelText("Search"), "admin");

    expect(screen.getByText("alice")).toBeInTheDocument();
    expect(screen.queryByText("bob")).not.toBeInTheDocument();
  });

  it("shows a no-match message with the query when nothing matches", async () => {
    const events = userEvent.setup();
    render(<UsersList users={[user({ id: 1, username: "alice" })]} />);

    await events.type(screen.getByLabelText("Search"), "nonexistent");

    expect(screen.getByText('No accounts match "nonexistent".')).toBeInTheDocument();
  });
});
