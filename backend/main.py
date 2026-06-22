from fastapi import FastAPI, UploadFile, File, HTTPException, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import httpx
import os
import json
import asyncio
import uuid
from dotenv import load_dotenv
from supabase import create_client
from pydantic import BaseModel
from typing import Optional
from analyzer import run_analysis

load_dotenv()

app = FastAPI(title="Loonar API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5177", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")
ANTHROPIC_KEY = os.getenv("ANTHROPIC_API_KEY", "")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL else None


# ── Models ──────────────────────────────────────────────────────────────────

class ProjectCreate(BaseModel):
    name: str
    customer: str
    rfq_ref: Optional[str] = None
    value_eur: Optional[float] = None
    deadline: Optional[str] = None

class LibrarySearchRequest(BaseModel):
    query: str
    limit: int = 10

class BidAssessmentRequest(BaseModel):
    project_id: str
    scores: dict
    key_risks: list[str]

class CorrectionCreate(BaseModel):
    requirement_id: str
    project_id: str
    engineer_name: str
    field_changed: str
    original_value: str
    corrected_value: str
    reason: Optional[str] = None

class AddendumDiffRequest(BaseModel):
    project_id: str
    original_doc_id: str
    addendum_doc_id: str


# ── Health ──────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok", "service": "loonar-api", "supabase": bool(supabase)}


# ── Projects ─────────────────────────────────────────────────────────────────

@app.post("/projects")
def create_project(data: ProjectCreate):
    if not supabase:
        return {"id": str(uuid.uuid4()), **data.model_dump(), "mock": True}
    res = supabase.table("projects").insert(data.model_dump()).execute()
    return res.data[0]

@app.get("/projects")
def list_projects():
    if not supabase:
        return []
    return supabase.table("projects").select("*").order("created_at", desc=True).execute().data


# ── RFQ Upload + Async Analysis ───────────────────────────────────────────────

@app.post("/rfq/upload")
async def upload_rfq(
    background_tasks: BackgroundTasks,
    project_id: str = Form(...),
    file: UploadFile = File(...),
):
    contents = await file.read()
    doc_id = str(uuid.uuid4())
    job_id = str(uuid.uuid4())

    storage_path = f"rfq/{project_id}/{file.filename}"

    if supabase:
        supabase.storage.from_("documents").upload(storage_path, contents)
        doc = supabase.table("documents").insert({
            "id": doc_id,
            "project_id": project_id,
            "filename": file.filename,
            "doc_type": "rfq",
            "storage_path": storage_path,
        }).execute().data[0]
        doc_id = doc["id"]

        supabase.table("analysis_jobs").insert({
            "id": job_id,
            "project_id": project_id,
            "document_id": doc_id,
            "status": "queued",
        }).execute()

    # Decode PDF text (real impl uses Reducto; here we use raw text extraction as fallback)
    try:
        extracted_text = contents.decode("utf-8", errors="ignore")
    except Exception:
        extracted_text = str(contents[:50000])

    if supabase and ANTHROPIC_KEY:
        background_tasks.add_task(
            run_analysis,
            supabase, ANTHROPIC_KEY, job_id,
            project_id, doc_id, extracted_text, file.filename
        )

    return {"document_id": doc_id, "job_id": job_id, "status": "queued", "filename": file.filename}


# ── SSE: Stream job progress ──────────────────────────────────────────────────

@app.get("/rfq/status/{job_id}")
async def stream_job_status(job_id: str):
    """Server-Sent Events stream — frontend polls this for live progress."""

    async def event_generator():
        last_status = None
        for _ in range(120):  # max 2 min polling
            if supabase:
                row = supabase.table("analysis_jobs").select("*").eq("id", job_id).execute()
                if row.data:
                    job = row.data[0]
                    status = job["status"]
                    progress = job.get("progress") or {}
                    payload = json.dumps({"status": status, "progress": progress, "error": job.get("error")})
                    yield f"data: {payload}\n\n"
                    if status in ("done", "failed"):
                        break
                    last_status = status
            else:
                # Mock progress for dev without Supabase
                stages = [
                    ("ingesting",   {"stage": "Splitting document...",          "pages_processed": 0,  "requirements_found": 0,  "contradictions_found": 0}),
                    ("extracting",  {"stage": "Extracting requirements...",     "pages_processed": 12, "requirements_found": 8,  "contradictions_found": 0}),
                    ("extracting",  {"stage": "Extracting requirements...",     "pages_processed": 28, "requirements_found": 23, "contradictions_found": 0}),
                    ("detecting",   {"stage": "Detecting contradictions...",    "pages_processed": 42, "requirements_found": 31, "contradictions_found": 0}),
                    ("done",        {"stage": "Complete",                       "pages_processed": 47, "requirements_found": 31, "contradictions_found": 2}),
                ]
                idx = min(_ // 4, len(stages) - 1)
                s, p = stages[idx]
                yield f"data: {json.dumps({'status': s, 'progress': p})}\n\n"
                if s == "done":
                    break

            await asyncio.sleep(1)

    return StreamingResponse(event_generator(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


# ── Requirements + Contradictions ────────────────────────────────────────────

@app.get("/projects/{project_id}/requirements")
def get_requirements(project_id: str, risk_level: Optional[str] = None):
    if not supabase:
        return []
    q = supabase.table("requirements").select(
        "*, chunk:source_chunk_id(page_start, page_end, text)"
    ).eq("project_id", project_id)
    if risk_level:
        q = q.eq("risk_level", risk_level)
    return q.order("req_id").execute().data

@app.get("/projects/{project_id}/contradictions")
def get_contradictions(project_id: str):
    if not supabase:
        return []
    return supabase.table("contradictions").select(
        "*, req_a:req_id_a(req_id, clause, text, page_number), req_b:req_id_b(req_id, clause, text, page_number)"
    ).eq("project_id", project_id).execute().data


# ── Deviations ───────────────────────────────────────────────────────────────

@app.get("/projects/{project_id}/deviations")
def get_deviations(project_id: str, status: Optional[str] = None):
    if not supabase:
        return []
    q = supabase.table("deviations").select("*, requirement:requirement_id(req_id, clause, page_number, confidence)") \
        .eq("project_id", project_id)
    if status:
        q = q.eq("status", status)
    return q.order("dev_id").execute().data

@app.patch("/deviations/{deviation_id}")
def update_deviation(deviation_id: str, body: dict):
    if not supabase:
        return {"id": deviation_id, **body}
    return supabase.table("deviations").update(body).eq("id", deviation_id).execute().data[0]


# ── Human Correction Flywheel ─────────────────────────────────────────────────

@app.post("/corrections")
def log_correction(data: CorrectionCreate):
    """Engineer overrides AI output. Every correction is stored for model improvement."""
    if supabase:
        supabase.table("requirements").update(
            {data.field_changed: data.corrected_value, "verified": True, "verified_by": data.engineer_name}
        ).eq("id", data.requirement_id).execute()

        row = supabase.table("correction_log").insert({
            "requirement_id": data.requirement_id,
            "project_id": data.project_id,
            "engineer_name": data.engineer_name,
            "field_changed": data.field_changed,
            "original_value": data.original_value,
            "corrected_value": data.corrected_value,
            "reason": data.reason,
        }).execute().data[0]
        return row
    return {"id": str(uuid.uuid4()), **data.model_dump(), "mock": True}

@app.get("/projects/{project_id}/corrections")
def get_corrections(project_id: str):
    if not supabase:
        return []
    return supabase.table("correction_log").select("*, requirement:requirement_id(req_id, text)") \
        .eq("project_id", project_id).order("created_at", desc=True).execute().data


# ── Content Library ───────────────────────────────────────────────────────────

@app.post("/library/search")
async def search_library(req: LibrarySearchRequest):
    if not supabase or not ANTHROPIC_KEY:
        return {"results": [], "mock": True}

    # Generate query embedding via Claude, then pgvector similarity search
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(
            "https://api.anthropic.com/v1/messages",
            headers={"x-api-key": ANTHROPIC_KEY, "anthropic-version": "2023-06-01"},
            json={
                "model": "claude-haiku-4-5-20251001",
                "max_tokens": 256,
                "messages": [{"role": "user", "content": f"Semantic search query: {req.query}\nReturn the top {req.limit} most relevant document excerpts from an industrial proposal library."}]
            }
        )
    # For now fall back to full-text search; vector search wired in after embeddings are populated
    results = supabase.table("content_library").select(
        "*, document:document_id(filename, doc_type)"
    ).text_search("chunk_text", req.query.replace(" ", " | ")).limit(req.limit).execute()
    return {"results": results.data}


# ── Bid/No-Bid ───────────────────────────────────────────────────────────────

@app.post("/bid-assessment")
def save_bid_assessment(req: BidAssessmentRequest):
    weights = {"technical": 0.30, "delivery": 0.25, "margin": 0.20, "relationship": 0.15, "strategic": 0.10}
    total = sum(v * weights.get(k, 0) for k, v in req.scores.items())
    verdict = "bid" if total >= 75 else "conditional" if total >= 55 else "no-bid"
    payload = {"project_id": req.project_id, "scores": req.scores,
               "total_score": round(total, 1), "verdict": verdict, "key_risks": req.key_risks}
    if supabase:
        return supabase.table("bid_assessments").insert(payload).execute().data[0]
    return {**payload, "mock": True}


# ── Addendum Diff ─────────────────────────────────────────────────────────────

@app.post("/addendum/diff")
async def diff_addendum(background_tasks: BackgroundTasks, req: AddendumDiffRequest):
    job_id = str(uuid.uuid4())
    # Async diff via n8n or direct Claude call
    async with httpx.AsyncClient(timeout=5) as client:
        try:
            n8n_base = os.getenv("N8N_WEBHOOK_BASE", "http://localhost:5678/webhook")
            await client.post(f"{n8n_base}/addendum-diff", json={**req.model_dump(), "job_id": job_id})
        except Exception:
            pass
    return {"job_id": job_id, "status": "processing"}

@app.get("/projects/{project_id}/addendum-changes")
def get_addendum_changes(project_id: str):
    if not supabase:
        return []
    return supabase.table("addendum_changes").select("*").eq("project_id", project_id) \
        .order("created_at", desc=True).execute().data
