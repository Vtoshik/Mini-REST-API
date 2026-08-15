import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { FormField } from "@/components/FormField";

describe("FormField", () => {
  it("renders the label and current value", () => {
    render(<FormField id="email" label="Email" value="a@example.com" onChange={() => {}} />);
    expect(screen.getByLabelText("Email")).toHaveValue("a@example.com");
  });

  it("calls onChange with the new value as the user types", async () => {
    const user = userEvent.setup();
    const onChange = vi.fn();
    render(<FormField id="email" label="Email" value="" onChange={onChange} />);

    await user.type(screen.getByLabelText("Email"), "hi");

    expect(onChange).toHaveBeenCalledWith("h");
    expect(onChange).toHaveBeenCalledWith("i");
  });

  it("shows an error message and marks the field invalid", () => {
    render(<FormField id="email" label="Email" value="" onChange={() => {}} error="Required" />);
    expect(screen.getByText("Required")).toBeInTheDocument();
    expect(screen.getByLabelText("Email")).toHaveAttribute("aria-invalid", "true");
  });

  it("does not mark the field invalid without an error", () => {
    render(<FormField id="email" label="Email" value="" onChange={() => {}} />);
    expect(screen.getByLabelText("Email")).toHaveAttribute("aria-invalid", "false");
  });
});
