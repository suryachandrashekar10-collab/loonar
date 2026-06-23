from fastapi import FastAPI, UploadFile, File, HTTPException, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, Response
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
from pdf_parser import extract_text_with_pages, pages_to_chunks
from excel_exporter import generate_deviation_register
from embeddings import semantic_search, embed_and_store_chunks

load_dotenv()

app = FastAPI(title="Loonar API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")
GEMINI_KEY = os.getenv("GROQ_API_KEY", "")
OPENAI_KEY = os.getenv("GOOGLE_API_KEY", "") or os.getenv("OPENAI_API_KEY", "") or os.getenv("GROQ_API_KEY", "")

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
    try:
        # Use summary view (includes counts) when available
        return supabase.from_("project_summary").select("*").order("created_at", desc=True).execute().data
    except Exception:
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
        try:
            supabase.storage.from_("documents").upload(storage_path, contents)
        except Exception:
            supabase.storage.from_("documents").update(storage_path, contents)
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

    # Real PDF extraction with page tracking
    pages = extract_text_with_pages(contents, file.filename)
    chunks = pages_to_chunks(pages)

    if supabase and GEMINI_KEY:
        background_tasks.add_task(
            run_analysis,
            supabase, GEMINI_KEY, OPENAI_KEY, job_id,
            project_id, doc_id, pages, chunks, file.filename
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
                    payload = json.dumps({"status": status, "progress": progress, "error": job.get("error"), "project_id": job.get("project_id")})
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
        "id,project_id,document_id,req_id,clause,category,text,risk_level,confidence,page_number,verified,verified_by,verified_at,source_chunk_id,created_at"
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

@app.get("/projects/{project_id}/deviations/export")
def export_deviations_excel(project_id: str):
    """Download deviation register as formatted Excel file."""
    project = {"name": "Project", "customer": "", "rfq_ref": "", "value_eur": None}
    deviations = []

    if supabase:
        proj = supabase.table("projects").select("*").eq("id", project_id).execute()
        if proj.data:
            project = proj.data[0]
        devs = supabase.table("deviations").select("*").eq("project_id", project_id).order("dev_id").execute()
        deviations = devs.data or []

    if not deviations:
        # Demo data so export always works
        deviations = [
            {"dev_id": "DEV-001", "clause": "4.2.1", "doc_ref": "SPC-MECH-001", "customer_spec": "ASTM A350 LF2 low-temp carbon steel rated to -50°C", "proposed_deviation": "Standard A105 available to -29°C. LF2 available on extended lead time (+4 wks).", "justification": "Stock availability constraint. LF2 can be sourced from certified stockist within revised schedule.", "status": "pending"},
            {"dev_id": "DEV-002", "clause": "9.1.2", "doc_ref": "SPC-MECH-001", "customer_spec": "ASME Section I (Power Boilers) certification mandatory", "proposed_deviation": "Standard product certified under ASME Section VIII. Section I requires separate design qualification.", "justification": "Section I qualification requires +8 weeks and welder requalification. Request acceptance of Section VIII with supplemental test report.", "status": "rejected"},
            {"dev_id": "DEV-003", "clause": "8.3.1", "doc_ref": "SPC-MECH-001", "customer_spec": "Third-party inspection by SGS mandatory", "proposed_deviation": "Bureau Veritas proposed as equivalent TPI authority.", "justification": "Bureau Veritas holds equivalent accreditation and is preferred vendor for this facility location.", "status": "accepted"},
            {"dev_id": "DEV-004", "clause": "6.4.2", "doc_ref": "SPC-MECH-001", "customer_spec": "Ring-type joint (RTJ) flange face for all Class 900 valves", "proposed_deviation": "Raised face (RF) standard. RTJ available on request with 2-week premium.", "justification": "Seeking written confirmation RTJ required for all items or only for HP gas lines.", "status": "clarification"},
        ]

    excel_bytes = generate_deviation_register(deviations, project)
    filename = f"deviation_register_{project_id[:8]}.xlsx"
    return Response(
        content=excel_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


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

@app.post("/library/upload")
async def upload_library_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    doc_type: str = Form("proposal"),
    tags: str = Form(""),
):
    """Index a past proposal, manual, or standard into the content library."""
    contents = await file.read()
    doc_id = str(uuid.uuid4())

    if supabase:
        supabase.storage.from_("documents").upload(f"library/{file.filename}", contents)
        supabase.table("documents").insert({
            "id": doc_id,
            "filename": file.filename,
            "doc_type": doc_type,
            "storage_path": f"library/{file.filename}",
        }).execute()

    pages = extract_text_with_pages(contents, file.filename)
    chunks = pages_to_chunks(pages, chunk_size=1500)

    if supabase:
        background_tasks.add_task(
            _index_library_document, doc_id, file.filename, doc_type, tags, chunks
        )

    return {"document_id": doc_id, "chunks": len(chunks), "pages": len(pages), "status": "indexing"}


async def _index_library_document(doc_id, filename, doc_type, tags, chunks):
    """Background task: embed and store library chunks."""
    if not supabase:
        return
    tag_list = [t.strip() for t in tags.split(",") if t.strip()]
    for i, chunk in enumerate(chunks):
        row = {
            "id": str(uuid.uuid4()),
            "document_id": doc_id,
            "chunk_index": i,
            "chunk_text": chunk["text"],
            "page_start": chunk["page_start"],
            "page_end": chunk["page_end"],
            "doc_type": doc_type,
            "tags": tag_list,
            "filename": filename,
        }
        try:
            result = supabase.table("content_library").insert(row).execute()
            chunk["db_id"] = result.data[0]["id"]
        except Exception:
            pass

    if OPENAI_KEY:
        await embed_and_store_chunks(supabase, OPENAI_KEY, chunks, doc_id)


@app.post("/library/search")
async def search_library(req: LibrarySearchRequest):
    if supabase and (OPENAI_KEY or True):
        results = await semantic_search(supabase, OPENAI_KEY, req.query, req.limit)
        if results:
            return {"results": results, "method": "semantic"}

    # Mock results for demo
    return {"results": [
        {"chunk_text": "Shell LNG Terminal Gate 3A — NACE MR0175 deviations accepted for body material substitution from duplex to super duplex on sour service lines. Deviation justified on basis of ISO 15156 Part 2 compliance.", "filename": "Shell_LNG_2023_proposal.pdf", "doc_type": "proposal", "page_start": 34, "relevance": 0.94},
        {"chunk_text": "Saudi Aramco EPIC — ASME Section VIII accepted in lieu of Section I for steam-traced valve assemblies below 15 psig design pressure. Written concession issued by client engineering.", "filename": "ARAMCO_EPIC_2022.pdf", "doc_type": "proposal", "page_start": 112, "relevance": 0.88},
        {"chunk_text": "TotalEnergies Downstream — Bureau Veritas accepted as equivalent TPI authority to SGS for all mechanical equipment. Basis: ILAC/MRA mutual recognition agreement.", "filename": "TotalEnergies_2023.pdf", "doc_type": "proposal", "page_start": 7, "relevance": 0.81},
    ], "method": "mock"}


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
