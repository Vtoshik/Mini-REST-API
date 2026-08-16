export type UserStatus = "user" | "admin";

export interface User {
  id: number;
  username: string;
  email: string;
  status: UserStatus;
  created_at?: string;
}

export interface Note {
  id: number;
  title: string;
  content: string | null;
  category?: string | null;
  pinned: boolean;
  created_at?: string;
  deleted_at?: string | null;
}

export interface AuditLogEntry {
  id: number;
  actor_username: string;
  action: string;
  target_type: string;
  target_id: number | null;
  details: string | null;
  created_at: string;
}

export interface Pagination {
  page: number;
  per_page: number;
  total: number;
  total_pages: number;
}

export interface Paginated<T> {
  data: T[];
  pagination: Pagination;
}
