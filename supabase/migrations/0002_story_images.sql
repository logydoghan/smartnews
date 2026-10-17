-- Image agent: one AI illustration per story. Files live in a public Storage bucket
-- that anyone can read; only the agents (with the secret key) can upload.

alter table stories add column if not exists image_url text;
alter table stories add column if not exists image_alt text;

insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values ('story-images', 'story-images', true, 5242880, array['image/webp', 'image/png', 'image/jpeg'])
on conflict (id) do nothing;
