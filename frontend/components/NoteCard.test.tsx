import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { NoteCard } from "@/components/NoteCard";
import { Note } from "@/lib/types";

function note(overrides: Partial<Note>): Note {
  return {
    id: 7,
    title: "Groceries",
    content: null,
    pinned: false,
    category: null,
    created_at: "2026-03-05T00:00:00Z",
    ...overrides,
  };
}

describe("NoteCard", () => {
  it("renders the title and zero-padded id", () => {
    render(<NoteCard note={note({})} />);
    expect(screen.getByText("Groceries")).toBeInTheDocument();
    expect(screen.getByText(/#007/)).toBeInTheDocument();
  });

  it("shows a pin marker only when pinned", () => {
    const { rerender } = render(<NoteCard note={note({ pinned: false })} />);
    expect(screen.queryByLabelText("Pinned")).not.toBeInTheDocument();

    rerender(<NoteCard note={note({ pinned: true })} />);
    expect(screen.getByLabelText("Pinned")).toBeInTheDocument();
  });

  it("renders the category badge only when a category is set", () => {
    const { rerender } = render(<NoteCard note={note({ category: null })} />);
    expect(screen.queryByText("Work")).not.toBeInTheDocument();

    rerender(<NoteCard note={note({ category: "Work" })} />);
    expect(screen.getByText("Work")).toBeInTheDocument();
  });

  it("renders content only when present", () => {
    const { rerender } = render(<NoteCard note={note({ content: null })} />);
    expect(screen.queryByText("Milk and eggs")).not.toBeInTheDocument();

    rerender(<NoteCard note={note({ content: "Milk and eggs" })} />);
    expect(screen.getByText("Milk and eggs")).toBeInTheDocument();
  });

  it("shows a placeholder dash when created_at is missing", () => {
    const noDate = note({});
    delete noDate.created_at;
    render(<NoteCard note={noDate} />);
    expect(screen.getByText(/—/)).toBeInTheDocument();
  });
});
