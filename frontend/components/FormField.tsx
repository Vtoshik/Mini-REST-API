interface FormFieldProps {
  id: string;
  label: string;
  type?: string;
  value: string;
  onChange: (value: string) => void;
  error?: string;
  autoComplete?: string;
}

export function FormField({
  id,
  label,
  type = "text",
  value,
  onChange,
  error,
  autoComplete,
}: FormFieldProps) {
  return (
    <div className="flex flex-col gap-1.5">
      <label htmlFor={id} className="font-display text-xs uppercase tracking-[0.15em] text-ink-muted">
        {label}
      </label>
      <input
        id={id}
        name={id}
        type={type}
        value={value}
        autoComplete={autoComplete}
        onChange={(e) => onChange(e.target.value)}
        aria-invalid={Boolean(error)}
        aria-describedby={error ? `${id}-error` : undefined}
        className="border-0 border-b-2 border-rule bg-transparent px-0.5 py-2 text-ink outline-none transition-colors focus:border-accent"
      />
      {error && (
        <p id={`${id}-error`} className="text-xs text-signal">
          {error}
        </p>
      )}
    </div>
  );
}
