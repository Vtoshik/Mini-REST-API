const TAB_COLORS = ["bg-accent", "bg-signal", "bg-ink-muted"] as const;

interface IndexTabProps {
  seed: number;
}

export function IndexTab({ seed }: IndexTabProps) {
  const color = TAB_COLORS[seed % TAB_COLORS.length];
  return <span className={`absolute left-0 top-3 bottom-3 w-1.5 rounded-r-sm ${color}`} aria-hidden />;
}
