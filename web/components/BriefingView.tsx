"use client";

import Link from "next/link";
import { useState } from "react";
import { StoryCard } from "@/components/StoryCard";
import { StoryImage } from "@/components/StoryImage";
import { plural, sectionLabel } from "@/lib/format";
import { CATEGORIES, type Category, type Story } from "@/lib/types";

const chip = "rounded-full px-3.5 py-2.5 text-sm";

export function BriefingView({ stories }: { stories: Story[] }) {
  const [category, setCategory] = useState<Category | null>(null);
  const shown = category ? stories.filter((s) => s.category === category) : stories;
  const [lead, ...rest] = shown;

  return (
    <>
      <nav aria-label="Sections" className="flex flex-wrap gap-1 pb-6">
        {[null, ...CATEGORIES].map((c) => {
          const active = c === category;
          return (
            <button
              key={c ?? "all"}
              type="button"
              aria-pressed={active}
              onClick={() => setCategory(c)}
              className={`${chip} ${active ? "bg-ink font-medium text-white" : "text-muted hover:bg-soft hover:text-ink"}`}
            >
              {c ?? "All"}
            </button>
          );
        })}
      </nav>

      {lead ? (
        <LeadStory story={lead} />
      ) : (
        <p className="py-10 text-muted">No {category} stories in today&apos;s briefing.</p>
      )}

      {rest.length > 0 && (
        <section aria-label="More stories" className="grid grid-cols-[repeat(auto-fill,minmax(280px,1fr))] gap-8 pt-8">
          {rest.map((s) => (
            <StoryCard key={s.slug} story={s} />
          ))}
        </section>
      )}
    </>
  );
}

function LeadStory({ story }: { story: Story }) {
  const href = `/story/${story.slug}`;
  return (
    <article className="grid grid-cols-[repeat(auto-fit,minmax(320px,1fr))] gap-10 border-t-[3px] border-b border-t-ink border-b-rule pt-8 pb-10">
      <div className="flex flex-col gap-4">
        {story.image_url && (
          <Link href={href} tabIndex={-1} aria-hidden="true" className="mb-2">
            <StoryImage
              src={story.image_url}
              alt=""
              sizes="(min-width: 1240px) 600px, (min-width: 768px) 50vw, 100vw"
              eager
            />
          </Link>
        )}
        <div className="text-[13px] font-semibold uppercase tracking-wider text-muted">Top story · {sectionLabel(story)}</div>
        <h2 className="font-serif text-[40px] leading-[1.12] font-bold tracking-tight">
          <Link href={href} className="hover:text-accent">
            {story.title}
          </Link>
        </h2>
        <p className="text-lg leading-relaxed text-body">{story.dek}</p>
        <div className="flex flex-wrap gap-2">
          {story.angles.map((a) => (
            <span key={a.key} className="rounded-full border border-chip px-3 py-1.5 text-[13px]">
              {a.label}
            </span>
          ))}
        </div>
        <Link
          href={href}
          className="mt-2 self-start rounded-lg bg-accent px-5.5 py-3.5 text-[15px] font-semibold text-white hover:bg-accent-strong"
        >
          Compare {plural(story.angles.length, "angle")}
        </Link>
      </div>
      <div className="flex flex-col gap-3.5 self-start rounded-xl bg-soft p-7">
        <div className="text-[13px] font-semibold uppercase tracking-wider text-muted">How the angles differ</div>
        {story.angles.slice(0, 3).map((a) => (
          <div key={a.key} className="flex flex-col gap-1">
            <div className="font-semibold">{a.label}</div>
            <div className="text-[15px] leading-normal text-body">{a.stance}</div>
          </div>
        ))}
        <div className="border-t border-rule pt-2 text-[13px] text-muted">
          Agreement level: <strong className="text-ink">{story.agreement_level}</strong> ·{" "}
          {plural(story.sources.length, "source")}
        </div>
      </div>
    </article>
  );
}
