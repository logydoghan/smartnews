import type { Source } from "@/lib/types";

const SEGMENTS = [
  { key: "left", label: "Left", color: "bg-lean-left" },
  { key: "center", label: "Center", color: "bg-lean-center" },
  { key: "right", label: "Right", color: "bg-lean-right" },
] as const;

/** How the story's sources split by editorial leaning. Unlabeled sources are left out. */
export function LeanBar({ sources }: { sources: Source[] }) {
  const counts = SEGMENTS.map((s) => ({ ...s, count: sources.filter((src) => src.leaning === s.key).length }));
  const total = counts.reduce((sum, s) => sum + s.count, 0);
  if (total === 0) return null;
  const description = counts.map((s) => `${s.count} ${s.label.toLowerCase()}`).join(", ");

  return (
    <div className="flex flex-col gap-2.5">
      <div className="text-sm font-semibold">Where the coverage comes from</div>
      <div role="img" aria-label={`Sources by leaning: ${description}`} className="flex h-3.5 gap-0.5 overflow-hidden rounded-full">
        {counts.map((s) =>
          s.count > 0 ? <div key={s.key} className={s.color} style={{ flexGrow: s.count }} /> : null,
        )}
      </div>
      <div className="flex justify-between text-[13px] text-muted">
        {counts.map((s) => (
          <span key={s.key}>
            {s.label} · {s.count}
          </span>
        ))}
      </div>
    </div>
  );
}
