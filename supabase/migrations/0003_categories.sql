-- The home page groups stories by section (Politics, Finance, ...) instead of world region.

alter table stories add column if not exists category text not null default 'Politics'
  check (category in ('Politics', 'Finance', 'Technology', 'Health', 'Entertainment', 'Sports'));
alter table stories alter column category drop default;
alter table stories drop column if exists region;
