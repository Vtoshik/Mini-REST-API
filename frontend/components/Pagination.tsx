import Link from "next/link";
import { Pagination as PaginationInfo } from "@/lib/types";

export function Pagination({
  pagination,
  basePath,
}: {
  pagination: PaginationInfo;
  basePath: string;
}) {
  const { page, total_pages } = pagination;

  if (total_pages <= 1) return null;

  const hrefFor = (targetPage: number) =>
    targetPage <= 1 ? basePath : `${basePath}?page=${targetPage}`;

  return (
    <nav
      aria-label="Pagination"
      className="flex items-center justify-between border-t border-rule pt-4"
    >
      {page > 1 ? (
        <Link
          href={hrefFor(page - 1)}
          className="font-display text-xs uppercase tracking-[0.15em] text-ink transition-colors hover:text-accent"
        >
          ← Previous
        </Link>
      ) : (
        <span className="font-display text-xs uppercase tracking-[0.15em] text-ink-muted/50">
          ← Previous
        </span>
      )}

      <p className="font-display text-xs uppercase tracking-[0.15em] text-ink-muted">
        Page {page} of {total_pages}
      </p>

      {page < total_pages ? (
        <Link
          href={hrefFor(page + 1)}
          className="font-display text-xs uppercase tracking-[0.15em] text-ink transition-colors hover:text-accent"
        >
          Next →
        </Link>
      ) : (
        <span className="font-display text-xs uppercase tracking-[0.15em] text-ink-muted/50">
          Next →
        </span>
      )}
    </nav>
  );
}
