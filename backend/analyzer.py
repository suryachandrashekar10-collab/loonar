"""
Core RFQ analysis engine — runs in background after upload.
Writes progress to analysis_jobs table (Supabase Realtime pushes to frontend).
"""
import asyncio
import json
import re
import uuid
from typing import Any
import httpx
import yaml
from pathlib import Path

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.3-70b-versatile"  # best free model on Groq
ONTOLOGY_PATH = Path(__file__).parent.parent / "ontology" / "valves.yaml"


def load_ontology() -> str:
    """Load ontology YAML and format as a compact context string for Claude."""
    try:
        data = yaml.safe_load(ONTOLOGY_PATH.read_text())
        lines = ["# Industrial Standards Ontology (Valves)"]
        lines.append("## Material Equivalences")
        for group, aliases in data.get("material_equivalences", {}).items():
            lines.append(f"- {group}: {' | '.join(aliases)}")
        lines.append("\n## Sour Service")
        ss = data.get("sour_service_standards", {})
        lines.append(f"- Primary: {ss.get('primary')} = {' = '.join(ss.get('equivalent', []))}")
        lines.append(f"- Triggers: {', '.join(ss.get('triggers', []))}")
        lines.append("\n## Pressure Classes (ascending)")
        pc = data.get("pressure_classes", {})
        lines.append(f"- {' < '.join(pc.get('ascending_order', []))}")
        lines.append(f"- Note: {pc.get('note', '')}")
        lines.append("\n## Common Deviation Patterns")
        for p in data.get("common_deviation_patterns", []):
            lines.append(f"- If '{p['trigger']}': {p['pattern']} [risk: {p['risk']}]")
        return "\n".join(lines)
    except Exception:
        return ""


ONTOLOGY_CONTEXT = load_ontology()


async def _groq(api_key: str, prompt: str, max_tokens: int = 4096) -> str:
    async with httpx.AsyncClient(timeout=120) as client:
        r = await client.post(
            GROQ_URL,
            headers={"Authorization": f"Bearer {api_key}", "content-type": "application/json"},
            json={
                "model": GROQ_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens,
                "temperature": 0.1,
            },
        )
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]


def _parse_json_block(text: str) -> Any:
    """Extract JSON from Claude response, handling markdown code fences."""
    match = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    raw = match.group(1) if match else text
    return json.loads(raw.strip())


async def _update_job(supabase, job_id: str, **fields):
    supabase.table("analysis_jobs").update(fields).eq("id", job_id).execute()


async def run_analysis(
    supabase,
    api_key: str,   # Gemini API key
    openai_key: str,
    job_id: str,
    project_id: str,
    document_id: str,
    pages: list[dict],
    chunks: list[dict],
    filename: str,
):
    """
    Full analysis pipeline for one document.
    Progress written to analysis_jobs so Supabase Realtime streams it to frontend.
    """
    try:
        # ── Step 1: Store chunks (already extracted by pdf_parser) ───────────
        await _update_job(supabase, job_id, status="ingesting",
                          progress={"stage": f"Indexing {len(pages)} pages into {len(chunks)} chunks...",
                                    "pages_processed": 0, "pages_total": len(pages),
                                    "requirements_found": 0, "contradictions_found": 0})

        for i, chunk in enumerate(chunks):
            chunk_row = {
                "id": str(uuid.uuid4()),
                "document_id": document_id,
                "chunk_index": i,
                "text": chunk["text"],
                "page_start": chunk["page_start"],
                "page_end": chunk["page_end"],
                "paragraph_start": i,
            }
            result = supabase.table("document_chunks").insert(chunk_row).execute()
            chunk["db_id"] = result.data[0]["id"]

        total_pages = pages[-1]["page_number"] if pages else len(chunks)

        # Kick off embedding in background (non-blocking for extraction pipeline)
        from embeddings import embed_and_store_chunks
        if openai_key:
            asyncio.create_task(embed_and_store_chunks(supabase, openai_key, chunks, document_id))

        # ── Step 2: Extract requirements per chunk ────────────────────────────
        await _update_job(supabase, job_id, status="extracting",
                          progress={"stage": "Extracting requirements...",
                                    "pages_processed": 0, "pages_total": total_pages,
                                    "requirements_found": 0, "contradictions_found": 0})

        all_requirements = []
        req_counter = 1

        for i, chunk in enumerate(chunks):
            prompt = f"""You are an expert industrial proposal engineer specializing in valves, pumps, and pressure equipment.

## Standards Ontology Context
{ONTOLOGY_CONTEXT}

## Task
Extract ALL technical and commercial requirements from this RFQ document chunk.
For each requirement output a JSON object with these exact fields:
- req_id: string (format "REQ-{'{'}NNN{'}'}", sequential)
- clause: string (section/clause reference if visible, else "")
- category: one of ["Material", "Testing", "Standards", "Dimensional", "Inspection", "Commercial", "Documentation", "Safety"]
- text: string (verbatim or near-verbatim requirement text)
- risk_level: one of ["high", "medium", "low"]
  - high = missed deviation costs >€50k or creates legal liability
  - medium = missed deviation costs €5k-€50k or affects delivery
  - low = minor, easily addressed
- confidence: float 0.0-1.0 (how confident you are this is a real requirement)
- deviation_likely: boolean (true if standard product likely cannot comply)
- deviation_hint: string (brief note on likely deviation, or "" if compliant)

Return ONLY a JSON array. No explanation, no markdown prose outside the code block.

## Document chunk (pages {chunk['page_start']}-{chunk['page_end']} of {total_pages}):
{chunk['text']}
"""
            try:
                response = await _groq(api_key, prompt, 2048)
                reqs = _parse_json_block(response)
                if isinstance(reqs, list):
                    for req in reqs:
                        if req.get("confidence", 0) < 0.4:
                            continue
                        req_id = f"REQ-{req_counter:03d}"
                        req_counter += 1
                        row = {
                            "id": str(uuid.uuid4()),
                            "project_id": project_id,
                            "document_id": document_id,
                            "source_chunk_id": chunk["db_id"],
                            "req_id": req_id,
                            "clause": req.get("clause", ""),
                            "category": req.get("category", "Other"),
                            "text": req.get("text", ""),
                            "risk_level": req.get("risk_level", "low"),
                            "confidence": req.get("confidence", 0.8),
                            "page_number": chunk["page_start"],
                            "paragraph_index": i,
                            "verified": False,
                        }
                        supabase.table("requirements").insert(row).execute()
                        all_requirements.append({**row, "deviation_likely": req.get("deviation_likely"),
                                                 "deviation_hint": req.get("deviation_hint", "")})
            except Exception:
                pass  # skip bad chunks, don't fail the whole job

            await _update_job(supabase, job_id,
                              progress={"stage": f"Extracting... chunk {i+1}/{len(chunks)}",
                                        "pages_processed": chunk["page_end"],
                                        "pages_total": total_pages,
                                        "requirements_found": len(all_requirements),
                                        "contradictions_found": 0})

        # ── Step 3: Contradiction detection ──────────────────────────────────
        await _update_job(supabase, job_id, status="detecting",
                          progress={"stage": "Detecting cross-document contradictions...",
                                    "pages_processed": total_pages,
                                    "pages_total": total_pages,
                                    "requirements_found": len(all_requirements),
                                    "contradictions_found": 0})

        contradictions = []
        if len(all_requirements) >= 2:
            req_summary = "\n".join(
                f"[{r['req_id']}] §{r['clause']} p.{r['page_number']}: {r['text'][:200]}"
                for r in all_requirements[:80]  # cap to avoid token overflow
            )
            contra_prompt = f"""You are an expert industrial specification reviewer.

## Standards Ontology Context
{ONTOLOGY_CONTEXT}

## Task
Review these requirements extracted from an industrial RFQ and identify CONTRADICTIONS — where two requirements conflict with each other, using your knowledge of engineering standards equivalences.

Examples of contradictions to catch:
- One clause specifies carbon steel, another specifies duplex stainless for the same application
- One clause requires ASME Section I, another implies Section VIII
- Pressure class conflicts (valve rated lower than piping spec)
- Material specs that conflict with NACE MR0175 requirements elsewhere

Requirements list:
{req_summary}

Return a JSON array of contradictions (empty array if none):
[{{"req_id_a": "REQ-001", "req_id_b": "REQ-005", "description": "...", "severity": "critical|high|medium|low"}}]

Only flag real engineering contradictions. Do not flag stylistic differences.
"""
            try:
                contra_resp = await _groq(api_key, contra_prompt, 2048)
                found = _parse_json_block(contra_resp)
                if isinstance(found, list):
                    req_id_map = {r["req_id"]: r["id"] for r in all_requirements}
                    for c in found:
                        row = {
                            "project_id": project_id,
                            "req_id_a": req_id_map.get(c.get("req_id_a")),
                            "req_id_b": req_id_map.get(c.get("req_id_b")),
                            "description": c.get("description", ""),
                            "severity": c.get("severity", "medium"),
                            "resolved": False,
                        }
                        if row["req_id_a"] and row["req_id_b"]:
                            supabase.table("contradictions").insert(row).execute()
                            contradictions.append(row)
            except Exception:
                pass

        # ── Step 4: Auto-generate deviation suggestions ───────────────────────
        high_risk = [r for r in all_requirements if r.get("deviation_likely") and r.get("risk_level") in ("high", "critical")]
        dev_counter = 1
        for req in high_risk[:20]:
            dev_row = {
                "project_id": project_id,
                "requirement_id": req["id"],
                "dev_id": f"DEV-{dev_counter:03d}",
                "clause": req["clause"],
                "doc_ref": filename,
                "customer_spec": req["text"],
                "proposed_deviation": req.get("deviation_hint", "To be determined — requires engineering review."),
                "justification": "AI-suggested — requires engineer verification.",
                "status": "pending",
            }
            try:
                supabase.table("deviations").insert(dev_row).execute()
                dev_counter += 1
            except Exception:
                pass

        # ── Done ─────────────────────────────────────────────────────────────
        await _update_job(supabase, job_id, status="done",
                          progress={"stage": "Complete",
                                    "pages_processed": total_pages,
                                    "pages_total": total_pages,
                                    "requirements_found": len(all_requirements),
                                    "contradictions_found": len(contradictions)},
                          completed_at="now()")

        # ── Notify n8n ───────────────────────────────────────────────────────
        import os
        n8n_base = os.getenv("N8N_WEBHOOK_BASE", "http://localhost:5678/webhook")
        project_row = supabase.table("projects").select("name,customer").eq("id", project_id).execute()
        project_name = project_row.data[0]["name"] if project_row.data else "Unknown Project"
        customer = project_row.data[0].get("customer", "") if project_row.data else ""
        high_risk = sum(1 for r in all_requirements if r.get("risk_level") == "high")
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                await client.post(f"{n8n_base}/analysis-complete", json={
                    "project_id": project_id,
                    "project_name": project_name,
                    "customer": customer,
                    "filename": filename,
                    "requirements_found": len(all_requirements),
                    "contradictions_found": len(contradictions),
                    "high_risk_count": high_risk,
                })
        except Exception:
            pass  # n8n notification is best-effort, never block the pipeline

    except Exception as e:
        await _update_job(supabase, job_id, status="failed", error=str(e))
