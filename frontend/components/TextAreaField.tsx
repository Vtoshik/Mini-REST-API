interface TextAreaFieldProps {
  id: string;
  label: string;
  value: string;
  onChange: (value: string) => void;
  error?: string;
  rows?: number;
}

export function TextAreaField({ id, label, value, onChange, error, rows = 6 }: TextAreaFieldProps) {
  return (
    <div className="flex flex-col gap-1.5">
      <label htmlFor={id} className="font-display text-xs uppercase tracking-[0.15em] text-ink-muted">
        {label}
      </label>
      <textarea
        id={id}
        name={id}
        rows={rows}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        aria-invalid={Boolean(error)}
        aria-describedby={error ? `${id}-error` : undefined}
        className="resize-y rounded-sm border border-rule bg-paper-card px-3 py-2 text-sm text-ink outline-none transition-colors focus:border-2 focus:border-accent"
      />
      {error && (
        <p id={`${id}-error`} className="text-xs text-signal">
          {error}
        </p>
      )}
    </div>
  );
}
