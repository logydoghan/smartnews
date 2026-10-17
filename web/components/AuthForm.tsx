"use client";

import Link from "next/link";
import { useActionState } from "react";
import { logIn, signUp, type FormState } from "@/lib/actions";

type Attempt = (FormState & { n: number }) | null;

const input =
  "w-full rounded-lg border border-chip px-3.5 py-3 text-[15px] outline-none focus:border-accent focus:ring-2 focus:ring-accent/20";

export function AuthForm({ mode, next }: { mode: "login" | "signup"; next: string }) {
  // `n` counts attempts, so the fields remount with what the reader typed after each failed one.
  const [state, action, pending] = useActionState(
    async (prev: Attempt, form: FormData): Promise<Attempt> => ({
      ...(await (mode === "login" ? logIn : signUp)(prev, form)),
      n: (prev?.n ?? 0) + 1,
    }),
    null,
  );
  const typed = state?.values ?? {};
  const signup = mode === "signup";
  const nextQuery = next === "/" ? "" : `?next=${encodeURIComponent(next)}`;

  if (state?.message) {
    return <p className="rounded-lg bg-soft px-4 py-3 text-[15px] leading-relaxed text-body">{state.message}</p>;
  }

  return (
    <form key={state?.n ?? 0} action={action} className="flex flex-col gap-4">
      <input type="hidden" name="next" value={next} />
      {signup && (
        <label className="flex flex-col gap-1.5 text-sm font-medium">
          Display name
          <input name="name" defaultValue={typed.name} required maxLength={40} autoComplete="nickname" className={input} />
          <span className="text-[13px] font-normal text-muted">Shown next to your comments.</span>
        </label>
      )}
      <label className="flex flex-col gap-1.5 text-sm font-medium">
        Email
        <input name="email" type="email" defaultValue={typed.email} required autoComplete="email" className={input} />
      </label>
      <label className="flex flex-col gap-1.5 text-sm font-medium">
        Password
        <input
          name="password"
          type="password"
          required
          minLength={signup ? 8 : undefined}
          autoComplete={signup ? "new-password" : "current-password"}
          className={input}
        />
        {signup && <span className="text-[13px] font-normal text-muted">At least 8 characters.</span>}
      </label>
      {state?.error && (
        <p role="alert" className="text-sm text-red-700">
          {state.error}
        </p>
      )}
      <button
        type="submit"
        disabled={pending}
        className="mt-1 rounded-lg bg-accent px-5 py-3.5 text-[15px] font-semibold text-white hover:bg-accent-strong disabled:opacity-60"
      >
        {pending ? "One moment…" : signup ? "Create account" : "Log in"}
      </button>
      <p className="text-sm text-muted">
        {signup ? "Already have an account? " : "New to SmartNews? "}
        <Link href={`${signup ? "/login" : "/signup"}${nextQuery}`} className="font-medium text-accent hover:text-accent-strong">
          {signup ? "Log in" : "Sign up"}
        </Link>
      </p>
    </form>
  );
}
