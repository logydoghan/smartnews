import Link from "next/link";
import { BookmarkIcon, SaveButton, saveClass } from "@/components/SaveButton";
import { CommentForm } from "@/components/CommentForm";
import { deleteComment } from "@/lib/actions";
import { getReader } from "@/lib/auth";
import { formatCommentTime, plural } from "@/lib/format";
import { getComments, isSaved } from "@/lib/reader-data";
import { accountsEnabled } from "@/lib/supabase-server";

// The parts of a story page that depend on who is reading. Each reads the session,
// so the story page renders them inside Suspense boundaries.

export async function StorySave({ slug }: { slug: string }) {
  if (!accountsEnabled) return null;
  const reader = await getReader();
  if (!reader) {
    return (
      <Link href={`/login?next=${encodeURIComponent(`/story/${slug}`)}`} className={`${saveClass} self-start border-chip hover:border-accent hover:text-accent`}>
        <BookmarkIcon filled={false} />
        Save story
      </Link>
    );
  }
  return <SaveButton slug={slug} saved={await isSaved(reader, slug)} />;
}

export async function StoryComments({ slug }: { slug: string }) {
  if (!accountsEnabled) {
    return <p className="text-[15px] text-muted">Comments turn on once the site is connected to its database.</p>;
  }
  const [reader, comments] = await Promise.all([getReader(), getComments(slug)]);
  const here = encodeURIComponent(`/story/${slug}#comments`);

  return (
    <div className="flex flex-col gap-6">
      <p className="text-sm text-muted">{comments.length === 0 ? "No comments yet." : plural(comments.length, "comment")}</p>
      {comments.length > 0 && (
        <ul className="flex flex-col divide-y divide-rule border-y border-rule">
          {comments.map((c) => (
            <li key={c.id} className="flex flex-col gap-1.5 py-4">
              <div className="flex flex-wrap items-baseline gap-x-3 text-sm">
                <span className="font-semibold">{c.author}</span>
                <time dateTime={c.created_at} className="text-muted">
                  {formatCommentTime(c.created_at)}
                </time>
                {reader?.id === c.user_id && (
                  <form action={deleteComment} className="ml-auto">
                    <input type="hidden" name="id" value={c.id} />
                    <button type="submit" className="cursor-pointer text-muted hover:text-red-700">
                      Delete
                    </button>
                  </form>
                )}
              </div>
              <p className="whitespace-pre-line text-[15px] leading-relaxed text-body">{c.body}</p>
            </li>
          ))}
        </ul>
      )}
      {reader ? (
        <CommentForm slug={slug} name={reader.name} />
      ) : (
        <p className="text-[15px] text-body">
          <Link href={`/login?next=${here}`} className="font-medium text-accent hover:text-accent-strong">
            Log in
          </Link>{" "}
          or{" "}
          <Link href={`/signup?next=${here}`} className="font-medium text-accent hover:text-accent-strong">
            sign up
          </Link>{" "}
          to comment.
        </p>
      )}
    </div>
  );
}
