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
