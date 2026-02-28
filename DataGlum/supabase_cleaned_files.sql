create extension if not exists pgcrypto;

create table if not exists public.cleaned_files (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  original_filename text not null,
  cleaned_filename text not null,
  original_rows int,
  cleaned_rows int,
  rows_removed int,
  fixes_count int default 0,
  created_at timestamptz not null default now()
);

alter table public.cleaned_files enable row level security;

drop policy if exists "read own cleaned files" on public.cleaned_files;
create policy "read own cleaned files"
on public.cleaned_files for select
using (auth.uid() = user_id);

drop policy if exists "insert own cleaned files" on public.cleaned_files;
create policy "insert own cleaned files"
on public.cleaned_files for insert
with check (auth.uid() = user_id);

create index if not exists cleaned_files_user_created_idx
on public.cleaned_files (user_id, created_at desc);
