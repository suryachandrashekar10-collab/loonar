-- Migration 003: pgvector extension + semantic search RPC
-- Run this in Supabase SQL Editor after migrations 001 and 002.
-- ─────────────────────────────────────────────────────────────

-- 1. Enable pgvector extension (must be done once per project)
create extension if not exists vector;

-- 2. Add Supabase full-text search index on content_library
create index if not exists content_library_fts
  on content_library
  using gin(to_tsvector('english', chunk_text));

-- 3. Add full-text search index on requirements
create index if not exists requirements_fts
  on requirements
  using gin(to_tsvector('english', text));

-- 4. IVFFlat indexes for cosine similarity (already in 001, but guard with IF NOT EXISTS)
create index if not exists document_chunks_embedding_idx
  on document_chunks
  using ivfflat (embedding vector_cosine_ops)
  with (lists = 100);

create index if not exists content_library_embedding_idx
  on content_library
  using ivfflat (embedding vector_cosine_ops)
  with (lists = 100);

create index if not exists requirements_embedding_idx
  on requirements
  using ivfflat (embedding vector_cosine_ops)
  with (lists = 100);

-- 5. match_documents — semantic search across document chunks
-- Used by /library/search for past proposal retrieval.
create or replace function match_documents(
  query_embedding  vector(1536),
  match_threshold  float     default 0.5,
  match_count      int       default 10
)
returns table (
  id            uuid,
  document_id   uuid,
  chunk_text    text,
  filename      text,
  doc_type      text,
  page_start    int,
  page_end      int,
  tags          text[],
  similarity    float
)
language sql stable
as $$
  select
    cl.id,
    cl.document_id,
    cl.chunk_text,
    cl.filename,
    cl.doc_type,
    cl.page_start,
    cl.page_end,
    cl.tags,
    1 - (cl.embedding <=> query_embedding) as similarity
  from content_library cl
  where cl.embedding is not null
    and 1 - (cl.embedding <=> query_embedding) > match_threshold
  order by cl.embedding <=> query_embedding
  limit match_count;
$$;

-- 6. match_requirements — semantic search within a project's requirements
-- Used to find similar requirements across projects for deviation templates.
create or replace function match_requirements(
  query_embedding  vector(1536),
  project_id_filter uuid      default null,
  match_threshold  float      default 0.6,
  match_count      int        default 10
)
returns table (
  id            uuid,
  project_id    uuid,
  req_id        text,
  clause        text,
  category      text,
  text          text,
  risk_level    text,
  confidence    float,
  page_number   int,
  similarity    float
)
language sql stable
as $$
  select
    r.id,
    r.project_id,
    r.req_id,
    r.clause,
    r.category,
    r.text,
    r.risk_level,
    r.confidence,
    r.page_number,
    1 - (r.embedding <=> query_embedding) as similarity
  from requirements r
  where r.embedding is not null
    and (project_id_filter is null or r.project_id = project_id_filter)
    and 1 - (r.embedding <=> query_embedding) > match_threshold
  order by r.embedding <=> query_embedding
  limit match_count;
$$;

-- 7. match_chunks — semantic search within document chunks (for citation lookup)
create or replace function match_chunks(
  query_embedding  vector(1536),
  document_id_filter uuid     default null,
  match_threshold  float      default 0.5,
  match_count      int        default 5
)
returns table (
  id            uuid,
  document_id   uuid,
  chunk_index   int,
  text          text,
  page_start    int,
  page_end      int,
  similarity    float
)
language sql stable
as $$
  select
    dc.id,
    dc.document_id,
    dc.chunk_index,
    dc.text,
    dc.page_start,
    dc.page_end,
    1 - (dc.embedding <=> query_embedding) as similarity
  from document_chunks dc
  where dc.embedding is not null
    and (document_id_filter is null or dc.document_id = document_id_filter)
    and 1 - (dc.embedding <=> query_embedding) > match_threshold
  order by dc.embedding <=> query_embedding
  limit match_count;
$$;

-- 8. Grant execute to service role and anon (Supabase RLS applies on top)
grant execute on function match_documents    to service_role, anon, authenticated;
grant execute on function match_requirements to service_role, anon, authenticated;
grant execute on function match_chunks       to service_role, anon, authenticated;

-- 9. Helper view: projects with deviation counts (used by dashboard)
create or replace view project_summary as
select
  p.id,
  p.name,
  p.customer,
  p.rfq_ref,
  p.value_eur,
  p.deadline,
  p.status,
  p.created_at,
  count(distinct r.id)  filter (where r.id is not null)                       as requirement_count,
  count(distinct r.id)  filter (where r.risk_level = 'high')                  as high_risk_count,
  count(distinct d.id)  filter (where d.id is not null)                       as deviation_count,
  count(distinct d.id)  filter (where d.status = 'pending')                   as pending_deviations,
  count(distinct c.id)  filter (where c.id is not null)                       as contradiction_count,
  count(distinct aj.id) filter (where aj.status not in ('done', 'failed'))    as active_jobs
from projects p
left join requirements   r  on r.project_id = p.id
left join deviations     d  on d.project_id = p.id
left join contradictions c  on c.project_id = p.id
left join analysis_jobs  aj on aj.project_id = p.id
group by p.id;

grant select on project_summary to service_role, anon, authenticated;
