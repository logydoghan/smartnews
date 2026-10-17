import Link from "next/link";
import { StoryImage } from "@/components/StoryImage";
import { formatBriefingDate, plural, sectionLabel } from "@/lib/format";
import type { Story } from "@/lib/types";

export function StoryCard({ story: s, showDate = false }: { story: Story; showDate?: boolean }) {
  return (
    <Link href={`/story/${s.slug}`} className="group flex flex-col gap-2.5 border-b border-rule pb-6">
      {s.image_url && (
        <StoryImage
          src={s.image_url}
          alt=""
          sizes="(min-width: 1240px) 400px, (min-width: 640px) 50vw, 100vw"
          className="mb-1.5"
        />
      )}
      <div className="text-xs font-semibold uppercase tracking-wider text-muted">
        {sectionLabel(s)}
        {showDate && ` · ${formatBriefingDate(s.briefing_date)}`}
      </div>
      <div className="font-serif text-[23px] font-semibold leading-tight group-hover:text-accent">{s.title}</div>
      <p className="text-[15px] leading-normal text-body">{s.dek}</p>
      <div className="text-[13px] text-muted">
        {plural(s.angles.length, "angle")} · {plural(s.sources.length, "source")} · {s.agreement_level}
      </div>
    </Link>
  );
}
