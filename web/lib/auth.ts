import "server-only";
import { readerClient } from "./supabase-server";

export interface Reader {
  id: string;
  name: string;
}

/** The signed-in reader, or null. Reads the session cookie, so call it inside a Suspense boundary. */
export async function getReader(): Promise<Reader | null> {
  const db = await readerClient();
  if (!db) return null;
  // getClaims verifies the session token rather than trusting the cookie as-is.
  const { data } = await db.auth.getClaims();
  const claims = data?.claims;
  if (!claims?.sub) return null;
  const meta = (claims.user_metadata ?? {}) as { display_name?: string };
  const email = typeof claims.email === "string" ? claims.email : "";
  return { id: claims.sub, name: meta.display_name?.trim() || email.split("@")[0] || "Reader" };
}

/** Only same-site paths, so a crafted link can't send a reader elsewhere after logging in. */
export function safeNext(next: unknown): string {
  // "//host" and "/\host" both leave the site in a browser.
  return typeof next === "string" && /^\/(?![/\\])/.test(next) ? next : "/";
}
