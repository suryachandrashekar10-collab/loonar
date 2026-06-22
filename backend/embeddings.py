"""
Embedding generation and pgvector storage.
Uses OpenAI text-embedding-3-small (best price/performance for retrieval).
Falls back gracefully if no key configured.
"""
import os
from typing import Optional
import httpx

GOOGLE_EMBED_URL = "https://generativelanguage.googleapis.com/v1beta/models/text-embedding-004:embedContent"
EMBED_DIM = 768  # text-embedding-004 outputs 768 dims


async def embed_text(text: str, openai_key: str) -> Optional[list[float]]:
    """Generate embedding via Google text-embedding-004 (free, same key as Gemini).
    openai_key param is reused as the Gemini/Google API key."""
    if not openai_key or not text.strip():
        return None
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.post(
                GOOGLE_EMBED_URL,
                headers={"content-type": "application/json", "X-goog-api-key": openai_key},
                json={"model": "models/text-embedding-004", "content": {"parts": [{"text": text[:8191]}]}},
            )
            r.raise_for_status()
            return r.json()["embedding"]["values"]
    except Exception:
        return None


async def embed_and_store_chunks(
    supabase,
    openai_key: str,
    chunks: list[dict],
    document_id: str,
    batch_size: int = 20,
):
    """
    Generate embeddings for document chunks and update rows in document_chunks table.
    chunks: list of dicts with 'db_id' and 'text' fields.
    """
    if not openai_key or not supabase:
        return

    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        try:
            # Google embedding API is per-request (no batch endpoint), so embed sequentially
            for chunk in batch:
                embedding = await embed_text(chunk["text"], openai_key)
                if embedding and chunk.get("db_id"):
                    supabase.table("document_chunks").update(
                        {"embedding": embedding}
                    ).eq("id", chunk["db_id"]).execute()
        except Exception:
            pass


async def semantic_search(
    supabase,
    openai_key: str,
    query: str,
    limit: int = 10,
    table: str = "content_library",
    text_column: str = "chunk_text",
    embedding_column: str = "embedding",
) -> list[dict]:
    """
    Run pgvector cosine similarity search.
    Falls back to full-text search if embeddings unavailable.
    """
    query_embedding = await embed_text(query, openai_key)

    if query_embedding and supabase:
        try:
            # pgvector cosine similarity — requires migration 003
            rpc_name = "match_documents" if table == "content_library" else "match_chunks"
            result = supabase.rpc(rpc_name, {
                "query_embedding": query_embedding,
                "match_threshold": 0.5,
                "match_count": limit,
            }).execute()
            if result.data:
                return result.data
        except Exception:
            pass

    # Fallback: full-text search
    if supabase:
        try:
            terms = " | ".join(w for w in query.split() if len(w) > 2)
            result = supabase.table(table).select("*").text_search(
                text_column, terms
            ).limit(limit).execute()
            return result.data or []
        except Exception:
            pass

    return []
