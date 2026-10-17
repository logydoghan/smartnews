-- Reader accounts (Supabase Auth, email and password): each reader's saved stories
-- and the comments under each story.
--
-- Saves and comments point at a story by its slug rather than its id. The news agent
-- replaces a whole briefing when it re-runs a morning, and a foreign key would delete
-- every save and comment with it. Slugs start with the briefing date, so they never
-- collide across days; a save whose story is gone simply stops showing.

create table if not exists profiles (
  id           uuid primary key references auth.users (id) on delete cascade,
  display_name text not null check (char_length(display_name) between 1 and 40),
  created_at   timestamptz not null default now()
);

-- Every new account gets a profile, named from the sign-up form (or the email's first part).
create or replace function public.handle_new_user()
returns trigger
language plpgsql
security definer set search_path = ''
as $$
begin
  insert into public.profiles (id, display_name)
  values (
    new.id,
    left(coalesce(nullif(trim(new.raw_user_meta_data ->> 'display_name'), ''), split_part(new.email, '@', 1)), 40)
  );
  return new;
end;
$$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute function public.handle_new_user();

create table if not exists bookmarks (
  user_id    uuid not null references auth.users (id) on delete cascade,
  story_slug text not null,
  created_at timestamptz not null default now(),
  primary key (user_id, story_slug)
);

create table if not exists comments (
  id         uuid primary key default gen_random_uuid(),
  story_slug text not null,
  user_id    uuid not null references profiles (id) on delete cascade,
  body       text not null check (char_length(trim(body)) between 1 and 2000),
  created_at timestamptz not null default now()
);

create index if not exists bookmarks_user_idx on bookmarks (user_id, created_at desc);
create index if not exists comments_story_idx on comments (story_slug, created_at);

alter table profiles  enable row level security;
alter table bookmarks enable row level security;
alter table comments  enable row level security;

-- Names show next to comments, so anyone can read them; each reader edits only their own.
create policy "Public read" on profiles for select using (true);
create policy "Own profile" on profiles for update
  using ((select auth.uid()) = id) with check ((select auth.uid()) = id);

-- Saved stories are private to their reader.
create policy "Own saves" on bookmarks for select using ((select auth.uid()) = user_id);
create policy "Save a story" on bookmarks for insert
  with check ((select auth.uid()) = user_id and exists (select 1 from stories s where s.slug = story_slug));
create policy "Unsave" on bookmarks for delete using ((select auth.uid()) = user_id);

-- Anyone can read comments; signed-in readers comment on real stories and delete their own.
create policy "Public read" on comments for select using (true);
create policy "Comment" on comments for insert
  with check ((select auth.uid()) = user_id and exists (select 1 from stories s where s.slug = story_slug));
create policy "Delete own comment" on comments for delete using ((select auth.uid()) = user_id);
