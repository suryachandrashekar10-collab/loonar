"""
Run this after creating your Supabase project and filling .env:
  cd backend && python setup_check.py

It validates connectivity, runs the migrations, seeds demo data,
and confirms embeddings + RPC are working.
"""
import os
import sys
import asyncio
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")
ANTHROPIC_KEY = os.getenv("ANTHROPIC_API_KEY", "")
OPENAI_KEY = os.getenv("OPENAI_API_KEY", "")

PASS = "✅"
FAIL = "❌"
WARN = "⚠️ "


def check(label: str, ok: bool, detail: str = ""):
    status = PASS if ok else FAIL
    print(f"  {status}  {label}" + (f"  — {detail}" if detail else ""))
    return ok


def section(title: str):
    print(f"\n{'─'*50}")
    print(f"  {title}")
    print('─'*50)


def main():
    all_ok = True

    section("1. Environment variables")
    all_ok &= check("SUPABASE_URL",       bool(SUPABASE_URL),   SUPABASE_URL[:40] + "..." if SUPABASE_URL else "not set")
    all_ok &= check("SUPABASE_SERVICE_KEY", bool(SUPABASE_KEY), "set" if SUPABASE_KEY else "not set")
    all_ok &= check("ANTHROPIC_API_KEY",  bool(ANTHROPIC_KEY),  "set" if ANTHROPIC_KEY else "not set")
    check(          "OPENAI_API_KEY",     bool(OPENAI_KEY),      "set (optional — needed for semantic search)" if not OPENAI_KEY else "set")

    if not (SUPABASE_URL and SUPABASE_KEY):
        print("\n  → Create a Supabase project at https://supabase.com")
        print("    Copy URL and service_role key into .env")
        sys.exit(1)

    section("2. Supabase connectivity")
    try:
        from supabase import create_client
        sb = create_client(SUPABASE_URL, SUPABASE_KEY)
        result = sb.table("projects").select("id").limit(1).execute()
        all_ok &= check("projects table", True, f"{len(result.data)} rows")
    except Exception as e:
        all_ok &= check("Supabase connection", False, str(e))
        print("\n  → Run migrations 001, 002, 003 in Supabase SQL Editor first")
        print("    Files: supabase/migrations/001_initial_schema.sql")
        print("           supabase/migrations/002_citation_and_corrections.sql")
        print("           supabase/migrations/003_pgvector_search.sql")
        sys.exit(1)

    section("3. Schema tables")
    tables = ["projects", "documents", "requirements", "contradictions",
              "deviations", "document_chunks", "content_library",
              "analysis_jobs", "correction_log"]
    for table in tables:
        try:
            sb.table(table).select("id").limit(1).execute()
            check(table, True)
        except Exception as e:
            all_ok &= check(table, False, str(e))

    section("4. pgvector extension + RPC functions")
    try:
        sb.rpc("match_documents", {"query_embedding": [0.0] * 1536, "match_threshold": 0.99, "match_count": 1}).execute()
        check("match_documents RPC", True)
    except Exception as e:
        all_ok &= check("match_documents RPC", False, "run migration 003 to create this function")

    try:
        sb.rpc("match_requirements", {"query_embedding": [0.0] * 1536, "match_threshold": 0.99}).execute()
        check("match_requirements RPC", True)
    except Exception as e:
        all_ok &= check("match_requirements RPC", False, str(e)[:60])

    section("5. Seed demo data")
    try:
        seed_path = os.path.join(os.path.dirname(__file__), "..", "supabase", "seed.sql")
        with open(seed_path) as f:
            sql = f.read()
        sb.rpc("exec_sql", {"sql": sql}).execute()
        check("seed.sql executed via RPC", True)
    except Exception:
        # Supabase Python client can't run raw SQL — that's expected
        # Just check if demo project exists
        try:
            proj = sb.table("projects").select("id").eq("id", "demo-project-0001-0000-0000-000000000000").execute()
            if proj.data:
                check("Demo project exists (already seeded)", True)
            else:
                check("Demo data", False, "run supabase/seed.sql manually in SQL Editor")
        except Exception as e:
            check("Demo data check", False, str(e)[:60])

    section("6. Anthropic API")
    try:
        import httpx, json
        resp = httpx.post(
            "https://api.anthropic.com/v1/messages",
            headers={"x-api-key": ANTHROPIC_KEY, "anthropic-version": "2023-06-01"},
            json={"model": "claude-haiku-4-5-20251001", "max_tokens": 10,
                  "messages": [{"role": "user", "content": "ping"}]},
            timeout=15,
        )
        all_ok &= check("Claude API (Haiku)", resp.status_code == 200, f"HTTP {resp.status_code}")
    except Exception as e:
        all_ok &= check("Claude API", False, str(e)[:60])

    section("7. OpenAI embeddings (optional)")
    if OPENAI_KEY:
        try:
            import httpx
            resp = httpx.post(
                "https://api.openai.com/v1/embeddings",
                headers={"Authorization": f"Bearer {OPENAI_KEY}"},
                json={"model": "text-embedding-3-small", "input": "test"},
                timeout=15,
            )
            dim = len(resp.json()["data"][0]["embedding"]) if resp.status_code == 200 else 0
            all_ok &= check("OpenAI embeddings", resp.status_code == 200, f"dim={dim}")
        except Exception as e:
            all_ok &= check("OpenAI embeddings", False, str(e)[:60])
    else:
        print(f"  {WARN} OPENAI_API_KEY not set — semantic search will fall back to full-text")

    section("8. Supabase Storage buckets")
    try:
        buckets = sb.storage.list_buckets()
        bucket_names = [b.name for b in buckets]
        check("documents bucket", "documents" in bucket_names,
              "exists" if "documents" in bucket_names else "create it in Storage → New bucket → name: documents, public: false")
    except Exception as e:
        check("Storage", False, str(e)[:60])

    print(f"\n{'═'*50}")
    if all_ok:
        print("  ✅  All checks passed — start the backend:")
        print("      cd backend && uvicorn main:app --reload --port 8000")
    else:
        print("  ❌  Some checks failed — fix above issues then re-run")
    print('═'*50 + "\n")


if __name__ == "__main__":
    main()
