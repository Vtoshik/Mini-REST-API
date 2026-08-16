import { serverFetch } from "@/lib/serverFetch";
import { User } from "@/lib/types";

export async function getCurrentUser(): Promise<User | null> {
  return serverFetch<User>("/api/v1/me");
}
