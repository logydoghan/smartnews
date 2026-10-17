import type { EmailOtpType } from "@supabase/supabase-js";
import { NextResponse, type NextRequest } from "next/server";
import { safeNext } from "@/lib/auth";
import { readerClient } from "@/lib/supabase-server";

// The link in Supabase's confirmation email lands here and starts the reader's session.
// It handles both link styles Supabase can send: a one-time `code`, or a `token_hash`.
export async function GET(request: NextRequest) {
  const params = request.nextUrl.searchParams;
  const next = safeNext(params.get("next"));
  const code = params.get("code");
  const tokenHash = params.get("token_hash");
  const type = params.get("type") as EmailOtpType | null;

  const db = await readerClient();
  if (db) {
    const { error } = code
      ? await db.auth.exchangeCodeForSession(code)
      : tokenHash && type
        ? await db.auth.verifyOtp({ token_hash: tokenHash, type })
        : { error: new Error("missing code") };
    if (!error) return NextResponse.redirect(new URL(next, request.url));
  }
  return NextResponse.redirect(new URL("/login?error=link", request.url));
}
