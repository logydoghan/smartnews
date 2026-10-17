import { Suspense } from "react";
import { AuthForm } from "@/components/AuthForm";
import { SiteFooter, SiteHeader } from "@/components/SiteHeader";
import { safeNext } from "@/lib/auth";
import { accountsEnabled } from "@/lib/supabase-server";

export function AuthPage({
  mode,
  title,
  intro,
  searchParams,
}: {
  mode: "login" | "signup";
  title: string;
  intro: string;
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}) {
  return (
    <>
      <SiteHeader />
      <main className="mx-auto w-full max-w-[440px] px-6 pt-14 pb-20">
        <h1 className="font-serif text-[36px] font-semibold tracking-tight">{title}</h1>
        <p className="mt-2 mb-8 text-[15px] leading-relaxed text-body">{intro}</p>
        {!accountsEnabled && (
          <p className="mb-6 rounded-lg bg-soft px-4 py-3 text-sm text-body">
            Accounts turn on once the site is connected to its Supabase database.
          </p>
        )}
        <Suspense>
          <Form mode={mode} searchParams={searchParams} />
        </Suspense>
      </main>
      <SiteFooter />
    </>
  );
}

async function Form({ mode, searchParams }: { mode: "login" | "signup"; searchParams: Promise<Record<string, string | string[] | undefined>> }) {
  const { next, error } = await searchParams;
  return (
    <>
      {error === "link" && (
        <p role="alert" className="mb-6 text-sm text-red-700">
          That sign-in link didn&apos;t work or has expired. Log in, or sign up again to get a new one.
        </p>
      )}
      <AuthForm mode={mode} next={safeNext(next)} />
    </>
  );
}
