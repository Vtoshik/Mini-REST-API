import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { TextAreaField } from "@/components/TextAreaField";

describe("TextAreaField", () => {
  it("renders the label and current value", () => {
    render(<TextAreaField id="content" label="Content" value="hello" onChange={() => {}} />);
    expect(screen.getByLabelText("Content")).toHaveValue("hello");
  });

  it("calls onChange as the user types", async () => {
    const user = userEvent.setup();
    const onChange = vi.fn();
    render(<TextAreaField id="content" label="Content" value="" onChange={onChange} />);

    await user.type(screen.getByLabelText("Content"), "hi");

    expect(onChange).toHaveBeenCalledWith("h");
    expect(onChange).toHaveBeenCalledWith("i");
  });

  it("defaults to 6 rows and respects a custom rows prop", () => {
    const { rerender } = render(<TextAreaField id="content" label="Content" value="" onChange={() => {}} />);
    expect(screen.getByLabelText("Content")).toHaveAttribute("rows", "6");

    rerender(<TextAreaField id="content" label="Content" value="" onChange={() => {}} rows={10} />);
    expect(screen.getByLabelText("Content")).toHaveAttribute("rows", "10");
  });

  it("shows an error message when provided", () => {
    render(<TextAreaField id="content" label="Content" value="" onChange={() => {}} error="Too long" />);
    expect(screen.getByText("Too long")).toBeInTheDocument();
  });
});
