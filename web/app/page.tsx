import { BriefingView } from "@/components/BriefingView";
import { SiteFooter, SiteHeader } from "@/components/SiteHeader";
import { getLatestBriefing } from "@/lib/data";
import { formatBriefingDate, plural } from "@/lib/format";

export default async function Home() {
  const briefing = await getLatestBriefing();

  return (
    <>
      <SiteHeader />
      <main className="mx-auto w-full max-w-[1240px] px-6 pt-10 pb-20">
        {briefing?.sample && (
          <p className="mb-8 rounded-lg bg-soft px-4 py-3 text-sm text-body">
            Showing sample stories. Connect the Supabase database to see the real morning briefing.
          </p>
        )}
        {briefing ? (
          <>
            <div className="flex flex-wrap items-baseline justify-between gap-3 pb-4">
              <div>
                <div className="text-[13px] font-semibold uppercase tracking-widest text-accent">Morning briefing</div>
                <h1 className="mt-1.5 font-serif text-[44px] font-semibold tracking-tight">
                  {formatBriefingDate(briefing.date)}
                </h1>
              </div>
              <div className="text-sm text-muted">
                {plural(briefing.stories.length, "story", "stories")} · gathered from{" "}
                {plural(briefing.outlet_count, "outlet")}
              </div>
            </div>
            <BriefingView stories={briefing.stories} />
          </>
        ) : (
          <p className="text-lg text-muted">The first morning briefing hasn&apos;t been published yet.</p>
        )}
      </main>
      <SiteFooter />
    </>
  );
}
