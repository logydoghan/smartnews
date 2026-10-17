import { createClient, type SupabaseClient } from "@supabase/supabase-js";
import { cacheLife } from "next/cache";
import { SAMPLE_BRIEFING } from "./sample";
import type { Angle, Briefing, Source, Story } from "./types";

// Without Supabase settings the site serves sample stories, so it runs out of the box.
function supabase(): SupabaseClient | null {
  const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const key = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;
  return url && key ? createClient(url, key, { auth: { persistSession: false } }) : null;
}

type StoryRow = Omit<Story, "sources" | "angles"> & {
  story_sources: Source[];
  angles: Angle[];
};

const STORY_COLUMNS =
  "briefing_date, rank, slug, title, topic, region, dek, why_it_matters, agree, disagree, agreement_level, facts, " +
  "story_sources (ref, url, title, outlet, country, leaning, published_at), " +
  "angles (position, key, label, stance, body, refs)";

function toStory({ story_sources, angles, ...rest }: StoryRow): Story {
  return {
    ...rest,
    sources: [...story_sources].sort((a, b) => a.ref - b.ref),
    angles: [...angles].sort((a, b) => a.position - b.position),
  };
}

export async function getLatestBriefing(): Promise<Briefing | null> {
  "use cache";
  // The agents publish once each morning; re-check within the hour.
  cacheLife("hours");

  const db = supabase();
  if (!db) return SAMPLE_BRIEFING;

  const { data: briefing, error } = await db
    .from("briefings")
    .select("date, article_count, outlet_count")
    .order("date", { ascending: false })
    .limit(1)
    .maybeSingle();
  if (error) throw new Error(`Could not load the latest briefing: ${error.message}`);
  if (!briefing) return null;

  const { data: rows, error: storiesError } = await db
    .from("stories")
    .select(STORY_COLUMNS)
    .eq("briefing_date", briefing.date)
    .order("rank");
  if (storiesError) throw new Error(`Could not load stories: ${storiesError.message}`);

  return { ...briefing, stories: (rows as unknown as StoryRow[]).map(toStory) };
}

export async function getStory(slug: string): Promise<Story | null> {
  "use cache";
  cacheLife("hours");

  const db = supabase();
  if (!db) return SAMPLE_BRIEFING.stories.find((s) => s.slug === slug) ?? null;

  const { data, error } = await db.from("stories").select(STORY_COLUMNS).eq("slug", slug).maybeSingle();
  if (error) throw new Error(`Could not load story: ${error.message}`);
  return data ? toStory(data as unknown as StoryRow) : null;
}
