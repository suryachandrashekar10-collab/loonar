-- Enable pgvector for semantic search
create extension if not exists vector;

-- Projects (one per customer RFQ engagement)
create table projects (
  id          uuid primary key default gen_random_uuid(),
  name        text not null,
  customer    text not null,
  rfq_ref     text,
  value_eur   numeric,
  deadline    date,
  status      text default 'active' check (status in ('active', 'no-bid', 'submitted', 'won', 'lost')),
  created_at  timestamptz default now()
);

-- Uploaded documents per project
create table documents (
  id          uuid primary key default gen_random_uuid(),
  project_id  uuid references projects(id) on delete cascade,
  filename    text not null,
  doc_type    text,           -- 'rfq', 'spec', 'addendum', 'past_proposal', 'manual'
  storage_path text not null, -- Supabase Storage path
  page_count  int,
  version     int default 1,
  created_at  timestamptz default now()
);

-- Extracted requirements (from RFQ analysis)
create table requirements (
  id          uuid primary key default gen_random_uuid(),
  project_id  uuid references projects(id) on delete cascade,
  document_id uuid references documents(id) on delete cascade,
  req_id      text not null,  -- e.g. REQ-001
  clause      text,
  category    text,           -- 'Material', 'Testing', 'Standards', 'Dimensional', 'Inspection'
  text        text not null,
  risk_level  text check (risk_level in ('high', 'medium', 'low')),
  page_number int,
  embedding   vector(1536),   -- for semantic similarity search
  created_at  timestamptz default now()
);

-- Cross-document contradictions detected
create table contradictions (
  id          uuid primary key default gen_random_uuid(),
  project_id  uuid references projects(id) on delete cascade,
  req_id_a    uuid references requirements(id),
  req_id_b    uuid references requirements(id),
  description text not null,
  severity    text check (severity in ('critical', 'high', 'medium', 'low')),
  resolved    boolean default false,
  created_at  timestamptz default now()
);

-- Deviation register
create table deviations (
  id                  uuid primary key default gen_random_uuid(),
  project_id          uuid references projects(id) on delete cascade,
  requirement_id      uuid references requirements(id),
  dev_id              text not null,  -- e.g. DEV-001
  clause              text,
  doc_ref             text,
  customer_spec       text not null,
  proposed_deviation  text not null,
  justification       text,
  commercial_impact   text,
  status              text default 'pending' check (status in ('pending', 'accepted', 'rejected', 'clarification')),
  created_at          timestamptz default now()
);

-- Content library (past proposals, manuals, supplier quotes)
create table content_library (
  id          uuid primary key default gen_random_uuid(),
  document_id uuid references documents(id) on delete cascade,
  title       text not null,
  doc_type    text,
  tags        text[],
  chunk_index int,            -- chunk number within doc
  chunk_text  text not null,
  embedding   vector(1536),
  created_at  timestamptz default now()
);

-- Addendum change log
create table addendum_changes (
  id                        uuid primary key default gen_random_uuid(),
  project_id                uuid references projects(id) on delete cascade,
  original_doc_id           uuid references documents(id),
  addendum_doc_id           uuid references documents(id),
  change_id                 text,
  section_ref               text,
  change_type               text,  -- 'material', 'testing', 'commercial', 'dimensional'
  severity                  text check (severity in ('critical', 'high', 'medium', 'low')),
  text_before               text,
  text_after                text,
  affected_deviation_ids    uuid[],
  affected_proposal_sections text[],
  action_required           text,
  created_at                timestamptz default now()
);

-- Bid/no-bid assessments
create table bid_assessments (
  id          uuid primary key default gen_random_uuid(),
  project_id  uuid references projects(id) on delete cascade,
  scores      jsonb not null,   -- {technical: 82, delivery: 55, margin: 70, ...}
  total_score numeric,
  verdict     text check (verdict in ('bid', 'conditional', 'no-bid')),
  key_risks   text[],
  created_at  timestamptz default now()
);

-- Indexes for performance
create index if not exists idx_requirements_project    on requirements (project_id);
create index if not exists idx_requirements_embedding  on requirements using ivfflat (embedding vector_cosine_ops) with (lists = 100);
create index if not exists idx_library_embedding       on content_library using ivfflat (embedding vector_cosine_ops) with (lists = 100);
create index if not exists idx_deviations_project      on deviations (project_id, status);
create index if not exists idx_addendum_project        on addendum_changes (project_id);
