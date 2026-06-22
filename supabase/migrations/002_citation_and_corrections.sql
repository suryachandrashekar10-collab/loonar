-- Citation fields on requirements
alter table requirements
  add column if not exists source_chunk_id  uuid,
  add column if not exists confidence        numeric check (confidence between 0 and 1),
  add column if not exists paragraph_index   int,
  add column if not exists bounding_box      jsonb,      -- {x, y, w, h} from OCR
  add column if not exists verified          boolean default false,
  add column if not exists verified_by       text,
  add column if not exists verified_at       timestamptz;

-- Job tracking for async processing
create table if not exists analysis_jobs (
  id            uuid primary key default gen_random_uuid(),
  project_id    uuid references projects(id) on delete cascade,
  document_id   uuid references documents(id),
  status        text default 'queued' check (status in ('queued','ingesting','extracting','detecting','done','failed')),
  progress      jsonb default '{"pages_processed":0,"pages_total":0,"requirements_found":0,"contradictions_found":0}'::jsonb,
  error         text,
  started_at    timestamptz,
  completed_at  timestamptz,
  created_at    timestamptz default now()
);

-- Human correction flywheel — every override is gold
create table if not exists correction_log (
  id                    uuid primary key default gen_random_uuid(),
  requirement_id        uuid references requirements(id) on delete cascade,
  project_id            uuid references projects(id),
  engineer_name         text,
  field_changed         text not null,   -- 'risk_level', 'category', 'text', 'deviation_flag'
  original_value        text,
  corrected_value       text,
  reason                text,
  bid_outcome           text,            -- filled in post-award: 'won','lost','claim'
  created_at            timestamptz default now()
);

-- Chunks table — stores raw text chunks with page/para metadata
create table if not exists document_chunks (
  id              uuid primary key default gen_random_uuid(),
  document_id     uuid references documents(id) on delete cascade,
  chunk_index     int not null,
  text            text not null,
  page_start      int,
  page_end        int,
  paragraph_start int,
  embedding       vector(1536),
  created_at      timestamptz default now()
);

create index if not exists idx_chunks_document     on document_chunks (document_id);
create index if not exists idx_chunks_embedding    on document_chunks using ivfflat (embedding vector_cosine_ops) with (lists = 100);
create index if not exists idx_jobs_project_status on analysis_jobs (project_id, status);
create index if not exists idx_corrections_req     on correction_log (requirement_id);
create index if not exists idx_corrections_project on correction_log (project_id);
