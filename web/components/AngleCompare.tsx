"use client";

import { useState } from "react";
import { plural } from "@/lib/format";
import type { Angle } from "@/lib/types";

type Mode = "side" | "one";

/**
 * The angles on one story. Wide screens default to side by side with a toggle;
 * phones always show one angle at a time with tabs.
 */
export function AngleCompare({ angles }: { angles: Angle[] }) {
  const [mode, setMode] = useState<Mode>("side");
  const [active, setActive] = useState(0);
  const current = angles[Math.min(active, angles.length - 1)];

  return (
    <section aria-labelledby="angles" className="flex flex-col gap-5">
      <div className="flex flex-wrap items-baseline justify-between gap-3 border-t-[3px] border-ink pt-5">
        <h2 id="angles" className="font-serif text-[32px] font-semibold">
          {angles.length === 1 ? "One angle" : `${angles.length} angles`} on this story
        </h2>
        <div className="hidden gap-1 rounded-full bg-soft p-1 md:flex">
          {(
            [
              ["side", "Side by side"],
              ["one", "One at a time"],
            ] as const
          ).map(([value, label]) => (
            <button
              key={value}
              type="button"
              aria-pressed={mode === value}
              onClick={() => setMode(value)}
              className={`min-h-10 rounded-full px-4 text-sm ${mode === value ? "bg-ink font-medium text-white" : "text-body"}`}
            >
              {label}
            </button>
          ))}
        </div>
      </div>

      <div className={mode === "side" ? "hidden gap-5 md:grid md:grid-cols-[repeat(auto-fit,minmax(220px,1fr))]" : "hidden"}>
        {angles.map((a) => (
          <AngleCard key={a.key} angle={a} />
        ))}
      </div>

      <div className={mode === "one" ? "flex flex-col gap-4" : "flex flex-col gap-4 md:hidden"}>
        <div role="tablist" aria-label="Angles" className="flex gap-2 overflow-x-auto">
          {angles.map((a, i) => (
            <button
              key={a.key}
              type="button"
              role="tab"
              aria-selected={i === active}
              onClick={() => setActive(i)}
              className={`min-h-11 flex-none rounded-full px-4 text-sm ${
                i === active ? "bg-ink font-medium text-white" : "border border-chip bg-white text-ink"
              }`}
            >
              {a.label}
            </button>
          ))}
        </div>
        {current && <AngleCard angle={current} note={`${active + 1} of ${angles.length}`} />}
      </div>
    </section>
  );
}

function AngleCard({ angle, note }: { angle: Angle; note?: string }) {
  return (
    <article className="flex flex-col gap-3.5 rounded-xl border border-rule bg-white p-6">
      <div className="flex items-center justify-between gap-2">
        <h3 className="text-[13px] font-semibold uppercase tracking-wider text-muted">{angle.label}</h3>
        <span className="text-xs text-muted">{note ?? plural(angle.refs.length, "source")}</span>
      </div>
      <p className="font-serif text-[21px] leading-snug font-semibold">{angle.stance}</p>
      <p className="text-[15px] leading-relaxed text-body">{angle.body}</p>
      <div className="mt-auto border-t border-rule pt-3 text-[13px] text-muted">
        Cited:{" "}
        {angle.refs.map((ref) => (
          <a key={ref} href={`#source-${ref}`} className="mr-1 text-accent hover:text-accent-strong">
            [{ref}]
          </a>
        ))}
      </div>
    </article>
  );
}
