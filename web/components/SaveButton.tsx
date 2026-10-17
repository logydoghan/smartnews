"use client";

import { useFormStatus } from "react-dom";
import { toggleSave } from "@/lib/actions";

export function SaveButton({ slug, saved }: { slug: string; saved: boolean }) {
  return (
    <form action={toggleSave}>
      <input type="hidden" name="slug" value={slug} />
      <input type="hidden" name="saved" value={String(saved)} />
      <Button saved={saved} />
    </form>
  );
}

function Button({ saved }: { saved: boolean }) {
  const { pending } = useFormStatus();
  // Show the new state right away while the save goes through.
  const shown = pending ? !saved : saved;
  return (
    <button
      type="submit"
      disabled={pending}
      aria-pressed={shown}
      className={`${saveClass} ${shown ? "border-accent bg-accent/10 text-accent" : "border-chip text-ink hover:border-accent hover:text-accent"}`}
    >
      <BookmarkIcon filled={shown} />
      {shown ? "Saved" : "Save story"}
    </button>
  );
}

export const saveClass =
  "inline-flex cursor-pointer items-center gap-2 rounded-lg border px-4 py-2.5 text-sm font-medium transition-colors";

export function BookmarkIcon({ filled }: { filled: boolean }) {
  return (
    <svg aria-hidden="true" viewBox="0 0 24 24" className="size-4" fill={filled ? "currentColor" : "none"} stroke="currentColor" strokeWidth="2">
      <path d="M6 3h12a1 1 0 0 1 1 1v17l-7-4.5L5 21V4a1 1 0 0 1 1-1z" strokeLinejoin="round" />
    </svg>
  );
}
