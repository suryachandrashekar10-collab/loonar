"""
Embedding generation and pgvector storage.
Uses OpenAI text-embedding-3-small (best price/performance for retrieval).
Falls back gracefully if no key configured.
"""
import os
from typing import Optional
import httpx

OPENAI_EMBED_URL = "https://api.openai.com/v1/embeddings"
EMBED_MODEL = "text-embedding-3-small"
EMBED_DIM = 1536


async def embed_text(text: str, openai_key: str) -> Optional[list[float]]:
    """Generate a 1536-dim embedding vector for text."""
    if not openai_key or not text.strip():
        return None
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.post(
                OPENAI_EMBED_URL,
                headers={"Authorization": f"Bearer {openai_key}"},
                json={"model": EMBED_MODEL, "input": text[:8191]},
            )
            r.raise_for_status()
            return r.json()["data"][0]["embedding"]
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
        texts = [c["text"][:8191] for c in batch]

        try:
            async with httpx.AsyncClient(timeout=60) as client:
                r = await client.post(
                    OPENAI_EMBED_URL,
                    headers={"Authorization": f"Bearer {openai_key}"},
                    json={"model": EMBED_MODEL, "input": texts},
                )
                r.raise_for_status()
                embeddings = [item["embedding"] for item in r.json()["data"]]

            for chunk, embedding in zip(batch, embeddings):
                if chunk.get("db_id"):
                    supabase.table("document_chunks").update(
                        {"embedding": embedding}
                    ).eq("id", chunk["db_id"]).execute()

        except Exception:
            pass  # embeddings are enhancement, not critical path


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
            # pgvector RPC — requires match_documents function in Supabase
            result = supabase.rpc("match_documents", {
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
