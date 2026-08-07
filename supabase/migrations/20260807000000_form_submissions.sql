-- Klear Path Home — form submission storage
--
-- Two tables back every public form on the site:
--   help_requests        — the /get-help document-replacement intake
--   contact_submissions  — contact, volunteer, get-involved, and newsletter forms
--
-- Both are write-only to the public (anon) role: anyone can INSERT, nobody can
-- SELECT, UPDATE, or DELETE with the publishable key. Staff read the rows through
-- the Supabase dashboard or a service-role key, neither of which is exposed to the
-- browser. Length limits are enforced in the database so a malformed or abusive
-- payload is rejected at the source rather than in client-side validation only.

create extension if not exists "pgcrypto";

-- ---------------------------------------------------------------------------
-- help_requests
-- ---------------------------------------------------------------------------

create table if not exists public.help_requests (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),

  name text not null check (char_length(name) between 1 and 120),
  phone text check (char_length(phone) <= 40),
  email text check (char_length(email) <= 254),
  county text check (char_length(county) <= 120),

  documents text[] not null default '{}',
  documents_other text check (char_length(documents_other) <= 200),
  deadline text check (char_length(deadline) <= 200),
  veteran boolean not null default false,
  notes text check (char_length(notes) <= 4000),

  source text not null default 'get-help' check (char_length(source) <= 60),
  status text not null default 'new'
    check (status in ('new', 'contacted', 'in_progress', 'fulfilled', 'closed')),
  handled_at timestamptz,

  -- At least one way to reach the person back, and at least one document asked for.
  constraint help_requests_contact_required check (
    coalesce(nullif(btrim(phone), ''), nullif(btrim(email), '')) is not null
  ),
  constraint help_requests_documents_required check (
    array_length(documents, 1) >= 1
  )
);

comment on table public.help_requests is
  'Document-replacement requests submitted from /get-help. Write-only to anon.';

create index if not exists help_requests_created_at_idx
  on public.help_requests (created_at desc);
create index if not exists help_requests_status_idx
  on public.help_requests (status) where status <> 'closed';

-- ---------------------------------------------------------------------------
-- contact_submissions
-- ---------------------------------------------------------------------------

create table if not exists public.contact_submissions (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),

  form text not null
    check (form in ('contact', 'volunteer', 'get-involved', 'newsletter')),

  name text check (char_length(name) <= 120),
  email text check (char_length(email) <= 254),
  phone text check (char_length(phone) <= 40),
  organization text check (char_length(organization) <= 200),

  inquiry_type text check (char_length(inquiry_type) <= 60),
  subject text check (char_length(subject) <= 200),
  message text check (char_length(message) <= 4000),

  interests text[] not null default '{}',
  availability text check (char_length(availability) <= 200),

  status text not null default 'new'
    check (status in ('new', 'contacted', 'in_progress', 'fulfilled', 'closed')),
  handled_at timestamptz,

  -- Every submission needs at least one reply channel.
  constraint contact_submissions_contact_required check (
    coalesce(nullif(btrim(email), ''), nullif(btrim(phone), '')) is not null
  )
);

comment on table public.contact_submissions is
  'Contact, volunteer, get-involved, and newsletter submissions. Write-only to anon.';

create index if not exists contact_submissions_created_at_idx
  on public.contact_submissions (created_at desc);
create index if not exists contact_submissions_form_idx
  on public.contact_submissions (form, created_at desc);

-- ---------------------------------------------------------------------------
-- Row level security — insert only, for everyone
-- ---------------------------------------------------------------------------

alter table public.help_requests enable row level security;
alter table public.contact_submissions enable row level security;

drop policy if exists "Anyone may submit a help request" on public.help_requests;
create policy "Anyone may submit a help request"
  on public.help_requests
  for insert
  to anon, authenticated
  with check (true);

drop policy if exists "Anyone may submit a contact form" on public.contact_submissions;
create policy "Anyone may submit a contact form"
  on public.contact_submissions
  for insert
  to anon, authenticated
  with check (true);

-- No SELECT/UPDATE/DELETE policies exist, so RLS denies those to anon and
-- authenticated even though the grants below would otherwise permit them.
-- Revoke table grants as a second layer, so a future permissive policy added by
-- mistake still cannot leak rows.

revoke all on public.help_requests from anon, authenticated;
revoke all on public.contact_submissions from anon, authenticated;

grant insert on public.help_requests to anon, authenticated;
grant insert on public.contact_submissions to anon, authenticated;
