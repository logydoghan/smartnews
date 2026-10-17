import type { Metadata } from "next";
import Link from "next/link";
import { redirect } from "next/navigation";
import { Suspense } from "react";
import { SiteFooter, SiteHeader } from "@/components/SiteHeader";
import { StoryCard } from "@/components/StoryCard";
import { getReader } from "@/lib/auth";
import { getSavedStories } from "@/lib/reader-data";
import { accountsEnabled } from "@/lib/supabase-server";

export const metadata: Metadata = { title: "Saved stories" };

export default function SavedPage() {
  return (
    <>
      <SiteHeader />
      <main className="mx-auto w-full max-w-[1240px] px-6 pt-10 pb-20">
        <div className="text-[13px] font-semibold uppercase tracking-widest text-accent">Your reading list</div>
        <h1 className="mt-1.5 mb-8 font-serif text-[44px] font-semibold tracking-tight">Saved stories</h1>
        <Suspense fallback={<p className="text-muted">Loading your saved stories…</p>}>
          <SavedList />
        </Suspense>
      </main>
      <SiteFooter />
    </>
  );
}

async function SavedList() {
  if (!accountsEnabled) {
    return <p className="text-lg text-muted">Saving stories turns on once the site is connected to its database.</p>;
  }
  const reader = await getReader();
  if (!reader) redirect("/login?next=/saved");
  const stories = await getSavedStories(reader);

  if (stories.length === 0) {
    return (
      <p className="text-lg text-muted">
        Nothing saved yet. Open any story from{" "}
        <Link href="/" className="text-accent hover:text-accent-strong">
          today&apos;s briefing
        </Link>{" "}
        and press Save story to keep it here.
      </p>
    );
  }
  return (
    <section aria-label="Saved stories" className="grid grid-cols-[repeat(auto-fill,minmax(280px,1fr))] gap-8">
      {stories.map((s) => (
        <StoryCard key={s.slug} story={s} showDate />
      ))}
    </section>
  );
}
