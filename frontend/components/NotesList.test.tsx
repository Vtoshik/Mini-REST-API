import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { NotesList } from "@/components/NotesList";
import { Note } from "@/lib/types";

function note(overrides: Partial<Note>): Note {
  return {
    id: 1,
    title: "Untitled",
    content: null,
    pinned: false,
    category: null,
    created_at: "2026-01-01T00:00:00Z",
    ...overrides,
  };
}

describe("NotesList", () => {
  it("shows an empty state with no notes", () => {
    render(<NotesList notes={[]} />);
    expect(screen.getByText("No notes yet.")).toBeInTheDocument();
  });

  it("renders every note when there is no filter", () => {
    const notes = [note({ id: 1, title: "Groceries" }), note({ id: 2, title: "Taxes" })];
    render(<NotesList notes={notes} />);
    expect(screen.getByText("Groceries")).toBeInTheDocument();
    expect(screen.getByText("Taxes")).toBeInTheDocument();
    expect(screen.getByText("2 of 2 entries")).toBeInTheDocument();
  });

  it("filters by title and content search text", async () => {
    const user = userEvent.setup();
    const notes = [
      note({ id: 1, title: "Groceries", content: "milk and eggs" }),
      note({ id: 2, title: "Taxes", content: "file by april" }),
    ];
    render(<NotesList notes={notes} />);

    await user.type(screen.getByLabelText("Search"), "milk");

    expect(screen.getByText("Groceries")).toBeInTheDocument();
    expect(screen.queryByText("Taxes")).not.toBeInTheDocument();
    expect(screen.getByText("1 of 2 entries")).toBeInTheDocument();
  });

  it("filters by category", async () => {
    const user = userEvent.setup();
    const notes = [
      note({ id: 1, title: "Groceries", category: "Home" }),
      note({ id: 2, title: "Taxes", category: "Finance" }),
    ];
    render(<NotesList notes={notes} />);

    await user.selectOptions(screen.getByLabelText("Category"), "Finance");

    expect(screen.getByText("Taxes")).toBeInTheDocument();
    expect(screen.queryByText("Groceries")).not.toBeInTheDocument();
  });

  it("shows a no-match message when filters exclude everything", async () => {
    const user = userEvent.setup();
    render(<NotesList notes={[note({ id: 1, title: "Groceries" })]} />);

    await user.type(screen.getByLabelText("Search"), "nonexistent");

    expect(screen.getByText("No notes match the current filters.")).toBeInTheDocument();
  });

  it("sorts pinned notes first", () => {
    const notes = [
      note({ id: 1, title: "Unpinned", pinned: false, created_at: "2026-01-02T00:00:00Z" }),
      note({ id: 2, title: "Pinned", pinned: true, created_at: "2026-01-01T00:00:00Z" }),
    ];
    render(<NotesList notes={notes} />);

    const titles = screen.getAllByRole("heading", { level: 3 }).map((el) => el.textContent);
    expect(titles[0]).toContain("Pinned");
  });
});
