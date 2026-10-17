import "server-only";
import type { Reader } from "./auth";
import { STORY_COLUMNS, toStory, type StoryRow } from "./data";
import { readerClient } from "./supabase-server";
import type { Story } from "./types";

// These read per reader at request time, so they stay out of the shared story cache.

export interface StoryComment {
  id: string;
  body: string;
  created_at: string;
  user_id: string;
  author: string;
}

export async function isSaved(reader: Reader, slug: string): Promise<boolean> {
  const db = await readerClient();
  if (!db) return false;
  const { data } = await db.from("bookmarks").select("story_slug").eq("user_id", reader.id).eq("story_slug", slug).maybeSingle();
  return Boolean(data);
}

/** The reader's saved stories, newest save first. Stories the news agent has since replaced drop out. */
export async function getSavedStories(reader: Reader): Promise<Story[]> {
  const db = await readerClient();
  if (!db) return [];
  const { data: saves, error } = await db
    .from("bookmarks")
    .select("story_slug")
    .eq("user_id", reader.id)
    .order("created_at", { ascending: false });
  if (error) throw new Error(`Could not load saved stories: ${error.message}`);
  const slugs = saves.map((s) => s.story_slug as string);
  if (slugs.length === 0) return [];

  const { data: rows, error: storiesError } = await db.from("stories").select(STORY_COLUMNS).in("slug", slugs);
  if (storiesError) throw new Error(`Could not load saved stories: ${storiesError.message}`);
  const bySlug = new Map((rows as unknown as StoryRow[]).map((r) => [r.slug, toStory(r)]));
  return slugs.flatMap((slug) => bySlug.get(slug) ?? []);
}

export async function getComments(slug: string): Promise<StoryComment[]> {
  const db = await readerClient();
  if (!db) return [];
  const { data, error } = await db
    .from("comments")
    .select("id, body, created_at, user_id, profiles (display_name)")
    .eq("story_slug", slug)
    .order("created_at");
  if (error) throw new Error(`Could not load comments: ${error.message}`);
  type Row = Omit<StoryComment, "author"> & { profiles: { display_name: string } | null };
  return (data as unknown as Row[]).map(({ profiles, ...c }) => ({ ...c, author: profiles?.display_name ?? "Reader" }));
}
