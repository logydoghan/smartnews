-- SmartNews schema: one briefing per morning, its top stories, each story's
-- sources and the angles the analysis agent wrote from them.

create table if not exists briefings (
  date          date primary key,
  article_count integer not null,
  outlet_count  integer not null,
  created_at    timestamptz not null default now()
);

create table if not exists stories (
  id              uuid primary key default gen_random_uuid(),
  briefing_date   date not null references briefings (date) on delete cascade,
  rank            integer not null,
  slug            text not null unique,
  title           text not null,
  topic           text not null,
  region          text not null,
  dek             text not null,
  why_it_matters  text not null,
  agree           text not null,
  disagree        text not null,
  agreement_level text not null check (agreement_level in ('broad agreement', 'mixed', 'views split')),
  facts           jsonb not null default '[]'::jsonb, -- [{ "text": str, "refs": [int] }]
  created_at      timestamptz not null default now(),
  unique (briefing_date, rank)
);

-- `ref` is the source's number within its story, as cited by facts and angles.
create table if not exists story_sources (
  story_id     uuid not null references stories (id) on delete cascade,
  ref          integer not null,
  url          text not null,
  title        text not null,
  outlet       text not null,
  country      text not null default '',
  leaning      text check (leaning in ('left', 'center', 'right')),
  published_at timestamptz,
  primary key (story_id, ref)
);

create table if not exists angles (
  story_id uuid not null references stories (id) on delete cascade,
  position integer not null,
  key      text not null,
  label    text not null,
  stance   text not null,
  body     text not null,
  refs     integer[] not null default '{}',
  primary key (story_id, key)
);

create index if not exists stories_briefing_idx on stories (briefing_date, rank);

-- The website reads with the public anon key; only the agents (service connection) write.
alter table briefings     enable row level security;
alter table stories       enable row level security;
alter table story_sources enable row level security;
alter table angles        enable row level security;

create policy "Public read" on briefings     for select using (true);
create policy "Public read" on stories       for select using (true);
create policy "Public read" on story_sources for select using (true);
create policy "Public read" on angles        for select using (true);
