"use server";

import { refresh } from "next/cache";
import { headers } from "next/headers";
import { redirect } from "next/navigation";
import { getReader, safeNext } from "./auth";
import { readerClient } from "./supabase-server";

/** `values` hands back what the reader typed, since React clears a form after each submit. */
export type FormState = { error?: string; message?: string; values?: Record<string, string> } | null;

const NOT_SET_UP = "Accounts turn on once the site is connected to its database.";

export async function signUp(_prev: FormState, form: FormData): Promise<FormState> {
  const db = await readerClient();
  if (!db) return { error: NOT_SET_UP };
  const name = String(form.get("name") ?? "").trim();
  const email = String(form.get("email") ?? "").trim();
  const password = String(form.get("password") ?? "");
  const next = safeNext(form.get("next"));
  const values = { name, email };
  if (!name || name.length > 40) return { error: "Choose a display name of up to 40 characters.", values };
  if (password.length < 8) return { error: "Use a password of at least 8 characters.", values };

  const h = await headers();
  const origin = h.get("origin") ?? `https://${h.get("host")}`;
  const { data, error } = await db.auth.signUp({
    email,
    password,
    options: {
      data: { display_name: name },
      emailRedirectTo: `${origin}/auth/confirm?next=${encodeURIComponent(next)}`,
    },
  });
  if (error) return { error: error.message, values };
  // With email confirmation on (Supabase's default), there is no session until the link is clicked.
  if (!data.session) return { message: `Almost done. We sent a link to ${email}; open it to finish signing up.` };
  redirect(next);
}

export async function logIn(_prev: FormState, form: FormData): Promise<FormState> {
  const db = await readerClient();
  if (!db) return { error: NOT_SET_UP };
  const email = String(form.get("email") ?? "").trim();
  const { error } = await db.auth.signInWithPassword({ email, password: String(form.get("password") ?? "") });
  if (error) {
    const message = error.message === "Invalid login credentials" ? "Wrong email or password." : error.message;
    return { error: message, values: { email } };
  }
  redirect(safeNext(form.get("next")));
}

export async function logOut() {
  const db = await readerClient();
  await db?.auth.signOut();
  redirect("/");
}

/** Saves the story for the signed-in reader, or removes it if it was already saved. */
export async function toggleSave(form: FormData) {
  const slug = String(form.get("slug") ?? "");
  const db = await readerClient();
  const reader = await getReader();
  if (!db || !reader) redirect(`/login?next=${encodeURIComponent(`/story/${slug}`)}`);

  if (form.get("saved") === "true") {
    await db.from("bookmarks").delete().eq("user_id", reader.id).eq("story_slug", slug);
  } else {
    // The primary key makes a double click harmless.
    await db.from("bookmarks").upsert({ user_id: reader.id, story_slug: slug }, { ignoreDuplicates: true });
  }
  refresh();
}

export async function addComment(_prev: FormState, form: FormData): Promise<FormState> {
  const slug = String(form.get("slug") ?? "");
  const body = String(form.get("body") ?? "").trim();
  const db = await readerClient();
  const reader = await getReader();
  if (!db || !reader) return { error: "Log in to comment.", values: { body } };
  if (!body) return { error: "Write something first." };
  if (body.length > 2000) return { error: "Comments can be up to 2,000 characters.", values: { body } };

  const { error } = await db.from("comments").insert({ story_slug: slug, user_id: reader.id, body });
  if (error) return { error: "Your comment couldn't be posted. Please try again.", values: { body } };
  refresh();
  return { message: "posted" };
}

export async function deleteComment(form: FormData) {
  const db = await readerClient();
  const reader = await getReader();
  if (!db || !reader) return;
  // Row-level security also limits deletes to the comment's author.
  await db.from("comments").delete().eq("id", String(form.get("id") ?? "")).eq("user_id", reader.id);
  refresh();
}
