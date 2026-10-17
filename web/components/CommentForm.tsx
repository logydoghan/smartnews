"use client";

import { useActionState } from "react";
import { addComment, type FormState } from "@/lib/actions";

type Attempt = (FormState & { n: number }) | null;

export function CommentForm({ slug, name }: { slug: string; name: string }) {
  // `n` counts posts, so the textarea remounts with the reader's text after every failed one.
  const [state, action, pending] = useActionState(
    async (prev: Attempt, form: FormData): Promise<Attempt> => ({ ...(await addComment(prev, form)), n: (prev?.n ?? 0) + 1 }),
    null,
  );

  return (
    <form action={action} className="flex flex-col gap-3">
      <input type="hidden" name="slug" value={slug} />
      <label className="flex flex-col gap-1.5 text-sm font-medium">
        Comment as {name}
        <textarea
          name="body"
          required
          maxLength={2000}
          rows={4}
          // React clears the form after each post; on an error, put the text back.
          key={state?.n ?? 0}
          defaultValue={state?.error ? state.values?.body : undefined}
          className="w-full rounded-lg border border-chip px-3.5 py-3 text-[15px] font-normal leading-relaxed outline-none focus:border-accent focus:ring-2 focus:ring-accent/20"
        />
      </label>
      {state?.error && (
        <p role="alert" className="text-sm text-red-700">
          {state.error}
        </p>
      )}
      <button
        type="submit"
        disabled={pending}
        className="self-start rounded-lg bg-accent px-5 py-3 text-[15px] font-semibold text-white hover:bg-accent-strong disabled:opacity-60"
      >
        {pending ? "Posting…" : "Post comment"}
      </button>
    </form>
  );
}
