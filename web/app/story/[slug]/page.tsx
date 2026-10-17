import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { Suspense } from "react";
import { AngleCompare } from "@/components/AngleCompare";
import { LeanBar } from "@/components/LeanBar";
import { StoryComments, StorySave } from "@/components/StoryAccountParts";
import { StoryImage } from "@/components/StoryImage";
import { SiteFooter, SiteHeader } from "@/components/SiteHeader";
import { getLatestBriefing, getStory } from "@/lib/data";
import { formatBriefingDate, plural, sectionLabel } from "@/lib/format";

// Before the first briefing exists there are no stories, but Cache Components needs at
// least one param to build. The placeholder renders as a 404; real stories render on request.
const NO_STORIES_YET = "no-stories-yet";

export async function generateStaticParams() {
  const briefing = await getLatestBriefing();
  const params = (briefing?.stories ?? []).map((s) => ({ slug: s.slug }));
  return params.length > 0 ? params : [{ slug: NO_STORIES_YET }];
}

export async function generateMetadata({ params }: PageProps<"/story/[slug]">): Promise<Metadata> {
  const story = await getStory((await params).slug);
  return story ? { title: story.title, description: story.dek } : {};
}

export default function StoryPage(props: PageProps<"/story/[slug]">) {
  return (
    <>
      <SiteHeader>
        <Link href="/" className="py-2.5 text-sm font-medium text-accent hover:text-accent-strong">
          Back to today&apos;s briefing
        </Link>
      </SiteHeader>
      <main className="mx-auto w-full max-w-[1240px] px-6 pt-10 pb-20">
        <Suspense fallback={<p className="text-muted">Loading story…</p>}>
          <StoryContent params={props.params} />
        </Suspense>
      </main>
      <SiteFooter />
    </>
  );
}

async function StoryContent({ params }: Pick<PageProps<"/story/[slug]">, "params">) {
  const story = await getStory((await params).slug);
  if (!story) notFound();
  const countries = new Set(story.sources.map((s) => s.country).filter(Boolean));

  return (
    <div className="flex flex-col gap-12">
      <section className="flex max-w-[820px] flex-col gap-4">
        <div className="text-[13px] font-semibold uppercase tracking-wider text-muted">
          {sectionLabel(story)} · {formatBriefingDate(story.briefing_date)}
        </div>
        <h1 className="font-serif text-[34px] leading-[1.1] font-bold tracking-tight md:text-5xl">{story.title}</h1>
        <p className="text-lg leading-relaxed text-body">{story.dek}</p>
        <div className="text-sm text-muted">
          {plural(story.sources.length, "source")} from {plural(countries.size, "country", "countries")} ·{" "}
          {plural(story.angles.length, "angle")} · analysis written by AI
        </div>
        <Suspense>
          <StorySave slug={story.slug} />
        </Suspense>
        {story.image_url && (
          <figure className="mt-2 flex flex-col gap-2">
            <StoryImage src={story.image_url} alt={story.image_alt ?? ""} sizes="(min-width: 860px) 820px, 100vw" eager />
            <figcaption className="text-[13px] text-muted">
              Illustration made by AI to suggest the subject. It does not show the real event.
            </figcaption>
          </figure>
        )}
      </section>

      <section aria-labelledby="facts" className="grid grid-cols-[repeat(auto-fit,minmax(min(320px,100%),1fr))] gap-8">
        <div className="flex flex-col gap-3.5">
          <h2 id="facts" className="font-serif text-[26px] font-semibold">
            What happened
          </h2>
          <ul className="flex list-disc flex-col gap-2.5 pl-5 text-[17px] leading-relaxed text-body">
            {story.facts.map((fact) => (
              <li key={fact.text}>
                {fact.text}{" "}
                {fact.refs.map((ref) => (
                  <a key={ref} href={`#source-${ref}`} className="mr-1 text-accent hover:text-accent-strong">
                    [{ref}]
                  </a>
                ))}
              </li>
            ))}
          </ul>
        </div>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div className="flex flex-col gap-2.5 rounded-xl bg-soft p-5.5">
            <h3 className="text-[15px] font-semibold">Most coverage agrees</h3>
            <p className="text-[15px] leading-normal text-body">{story.agree}</p>
          </div>
          <div className="flex flex-col gap-2.5 rounded-xl bg-soft p-5.5">
            <h3 className="text-[15px] font-semibold">Coverage disagrees on</h3>
            <p className="text-[15px] leading-normal text-body">{story.disagree}</p>
          </div>
          <div className="pt-1 sm:col-span-2">
            <LeanBar sources={story.sources} />
          </div>
        </div>
      </section>

      {story.angles.length > 0 && <AngleCompare angles={story.angles} />}

      <section id="sources" aria-labelledby="sources-heading" className="flex max-w-[820px] flex-col gap-3">
        <h2 id="sources-heading" className="font-serif text-[26px] font-semibold">
          Sources
        </h2>
        <ol className="flex list-decimal flex-col gap-2 pl-6 text-[15px] leading-normal text-body">
          {story.sources.map((src) => (
            <li key={src.ref} id={`source-${src.ref}`} className="scroll-mt-6">
              <a href={src.url} target="_blank" rel="noopener noreferrer" className="text-accent hover:text-accent-strong">
                {src.outlet}: {src.title}
              </a>
              {src.country && <span className="text-muted"> · {src.country}</span>}
            </li>
          ))}
        </ol>
        <p className="mt-2 text-[13px] leading-relaxed text-muted">
          Each angle is a summary written by AI from the sources it cites. It describes how that side sees the
          story; it is not this site&apos;s opinion.
        </p>
      </section>

      <section id="comments" aria-labelledby="comments-heading" className="flex max-w-[820px] scroll-mt-6 flex-col gap-4">
        <h2 id="comments-heading" className="font-serif text-[26px] font-semibold">
          Comments
        </h2>
        <Suspense fallback={<p className="text-muted">Loading comments…</p>}>
          <StoryComments slug={story.slug} />
        </Suspense>
      </section>
    </div>
  );
}
