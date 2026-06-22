from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import httpx
import os
from dotenv import load_dotenv
from supabase import create_client
from pydantic import BaseModel
from typing import Optional
import uuid

load_dotenv()

app = FastAPI(title="Loonar API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5177", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
N8N_BASE     = os.getenv("N8N_WEBHOOK_BASE", "http://localhost:5678/webhook")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL else None


# ── Models ─────────────────────────────────────────────────────────────────

class ProjectCreate(BaseModel):
    name: str
    customer: str
    rfq_ref: Optional[str] = None
    value_eur: Optional[float] = None
    deadline: Optional[str] = None

class AddendumDiffRequest(BaseModel):
    project_id: str
    original_doc_id: str
    addendum_doc_id: str

class LibrarySearchRequest(BaseModel):
    query: str
    limit: int = 10

class BidAssessmentRequest(BaseModel):
    project_id: str
    scores: dict
    key_risks: list[str]


# ── Health ──────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok", "service": "loonar-api"}


# ── Projects ────────────────────────────────────────────────────────────────

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
    res = supabase.table("projects").select("*").order("created_at", desc=True).execute()
    return res.data


# ── RFQ Upload + Ingestion ──────────────────────────────────────────────────

@app.post("/rfq/upload")
async def upload_rfq(
    project_id: str = Form(...),
    file: UploadFile = File(...),
):
    contents = await file.read()

    # Store in Supabase Storage
    storage_path = f"rfq/{project_id}/{file.filename}"
    if supabase:
        supabase.storage.from_("documents").upload(storage_path, contents)
        doc = supabase.table("documents").insert({
            "project_id": project_id,
            "filename": file.filename,
            "doc_type": "rfq",
            "storage_path": storage_path,
        }).execute().data[0]
        doc_id = doc["id"]
    else:
        doc_id = str(uuid.uuid4())

    # Trigger n8n ingestion pipeline
    async with httpx.AsyncClient(timeout=10) as client:
        try:
            await client.post(f"{N8N_BASE}/rfq-ingest", json={
                "project_id": project_id,
                "document_id": doc_id,
                "storage_path": storage_path,
                "filename": file.filename,
            })
        except Exception:
            pass  # n8n may not be running yet; processing will be async

    return {"document_id": doc_id, "status": "processing", "filename": file.filename}


# ── Requirements ────────────────────────────────────────────────────────────

@app.get("/projects/{project_id}/requirements")
def get_requirements(project_id: str):
    if not supabase:
        return []
    res = supabase.table("requirements") \
        .select("*") \
        .eq("project_id", project_id) \
        .order("req_id") \
        .execute()
    return res.data

@app.get("/projects/{project_id}/contradictions")
def get_contradictions(project_id: str):
    if not supabase:
        return []
    res = supabase.table("contradictions") \
        .select("*, req_a:req_id_a(*), req_b:req_id_b(*)") \
        .eq("project_id", project_id) \
        .execute()
    return res.data


# ── Deviations ──────────────────────────────────────────────────────────────

@app.get("/projects/{project_id}/deviations")
def get_deviations(project_id: str, status: Optional[str] = None):
    if not supabase:
        return []
    q = supabase.table("deviations").select("*").eq("project_id", project_id)
    if status:
        q = q.eq("status", status)
    return q.order("dev_id").execute().data

@app.patch("/deviations/{deviation_id}")
def update_deviation(deviation_id: str, body: dict):
    if not supabase:
        return {"id": deviation_id, **body}
    res = supabase.table("deviations").update(body).eq("id", deviation_id).execute()
    return res.data[0]


# ── Content Library Search ──────────────────────────────────────────────────

@app.post("/library/search")
async def search_library(req: LibrarySearchRequest):
    # Trigger n8n semantic search workflow
    async with httpx.AsyncClient(timeout=30) as client:
        try:
            r = await client.post(f"{N8N_BASE}/library-search", json={
                "query": req.query,
                "limit": req.limit,
            })
            return r.json()
        except Exception:
            return {"results": [], "mock": True}


# ── Addendum Diff ───────────────────────────────────────────────────────────

@app.post("/addendum/diff")
async def diff_addendum(req: AddendumDiffRequest):
    async with httpx.AsyncClient(timeout=60) as client:
        try:
            r = await client.post(f"{N8N_BASE}/addendum-diff", json=req.model_dump())
            return r.json()
        except Exception:
            return {"changes": [], "mock": True}

@app.get("/projects/{project_id}/addendum-changes")
def get_addendum_changes(project_id: str):
    if not supabase:
        return []
    res = supabase.table("addendum_changes") \
        .select("*") \
        .eq("project_id", project_id) \
        .order("created_at", desc=True) \
        .execute()
    return res.data


# ── Bid/No-Bid ──────────────────────────────────────────────────────────────

@app.post("/bid-assessment")
def save_bid_assessment(req: BidAssessmentRequest):
    total = sum(
        v * {"technical": 0.30, "delivery": 0.25, "margin": 0.20,
             "relationship": 0.15, "strategic": 0.10}.get(k, 0)
        for k, v in req.scores.items()
    )
    verdict = "bid" if total >= 75 else "conditional" if total >= 55 else "no-bid"
    payload = {
        "project_id": req.project_id,
        "scores": req.scores,
        "total_score": round(total, 1),
        "verdict": verdict,
        "key_risks": req.key_risks,
    }
    if supabase:
        res = supabase.table("bid_assessments").insert(payload).execute()
        return res.data[0]
    return {**payload, "mock": True}
