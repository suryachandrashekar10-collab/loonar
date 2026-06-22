# Loonar — Industrial RFQ Intelligence Platform

AI-powered platform for industrial bid teams. Upload an RFQ PDF and get every technical requirement extracted, contradictions flagged, and a deviation register generated — in under 60 seconds.

Built as a proof-of-concept for the industrial equipment supply chain space (valves, pumps, pressure vessels).

---

## What it does

- **RFQ Analyzer** — Upload a PDF, Llama 3.3 70B extracts every requirement with page citations, risk levels, and confidence scores
- **Contradiction Detection** — Flags where two clauses in the same document conflict (e.g. carbon steel vs duplex stainless for the same service)
- **Deviation Register** — Auto-generates deviations for requirements your standard product can't meet; export as color-coded Excel
- **Content Library** — Index past proposals for semantic search ("find all previous responses to NACE MR0175 requirements")
- **Projects** — Track multiple live bids with pipeline value

---

## Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React + Vite + Tailwind CSS |
| Backend | FastAPI (Python 3.12) |
| Database | Supabase (PostgreSQL + pgvector) |
| LLM | Groq — Llama 3.3 70B (free) |
| Embeddings | Google text-embedding-004 (free) |
| PDF parsing | pdfplumber + pypdf |

---

## Setup

### Prerequisites
- Python 3.12
- Node.js 18+
- A free [Supabase](https://supabase.com) account
- A free [Groq](https://console.groq.com) API key

### 1. Clone the repo

```bash
git clone https://github.com/suryachandrashekar10-collab/loonar.git
cd loonar
```

### 2. Configure environment

```bash
cp .env.example .env
```

Edit `.env` and fill in:

```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-role-key
GROQ_API_KEY=gsk_...
```

Get your keys:
- **Supabase**: Project Settings → API → `service_role` key (not `anon`)
- **Groq**: [console.groq.com](https://console.groq.com) → API Keys → Create

### 3. Set up Supabase

In your Supabase project → SQL Editor, run these files in order:

```
supabase/migrations/001_initial_schema.sql
supabase/migrations/002_citation_and_corrections.sql
supabase/migrations/003_pgvector_search.sql
supabase/seed.sql
```

Then go to **Storage → New bucket** → name: `documents` → private.

### 4. Backend

```bash
cd backend
py -3.12 -m venv .venv          # Windows
# python3.12 -m venv .venv      # Mac/Linux
.\.venv\Scripts\Activate.ps1    # Windows
# source .venv/bin/activate     # Mac/Linux

pip install -r requirements.txt

# Verify everything is connected
python setup_check.py

# Start the server
uvicorn main:app --reload --port 8000
```

### 5. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173)

---

## Testing

Generate sample RFQ PDFs:

```bash
cd backend
python generate_sample_rfq.py   # Shell LNG terminal (valves)
python generate_rfq_pump.py     # BP North Sea (centrifugal pumps)
```

Then:
1. Go to **Projects → New Project**
2. Click the project → **RFQ Analyzer**
3. Upload one of the generated PDFs
4. Watch live extraction run

---

## Project structure

```
loonar/
├── backend/
│   ├── main.py              # FastAPI app + all endpoints
│   ├── analyzer.py          # Groq extraction + contradiction detection
│   ├── pdf_parser.py        # pdfplumber page extraction
│   ├── embeddings.py        # Google text-embedding-004
│   ├── excel_exporter.py    # openpyxl deviation register export
│   ├── setup_check.py       # Connectivity validator
│   └── requirements.txt
├── frontend/
│   └── src/pages/
│       ├── RFQAnalyzer.tsx
│       ├── Projects.tsx
│       ├── DeviationRegister.tsx
│       └── ContentLibrary.tsx
├── supabase/
│   ├── migrations/
│   └── seed.sql
└── ontology/
    └── valves.yaml          # Industrial standards ontology
```

---

## Notes

- The `.env` file is gitignored — never commit API keys
- Python 3.14 is not supported (pydantic-core incompatibility) — use Python 3.12
- Groq free tier: 30 req/min, sufficient for testing
