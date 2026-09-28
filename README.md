# RTI Intelligence — Public Records Search & Multi-Agent Investigation Platform

> **Built with ❤️ by Krishna and team.**

**RTI Intelligence** is an end-to-end civic intelligence and public records platform designed to ingest, version, index, cross-verify, and audit public documents from government portals, news publications, and official legislative video broadcasts.

It pairs an automated, ethical data collection pipeline with a **Closed-Loop Multi-Agent Investigation System**, a **ChatGPT-style Connecting-Dots reasoning interface**, and an automated **Section 6(1) RTI Application Drafter** to empower citizens, journalists, and researchers with evidence-backed transparency.

---

## 🌟 Key Features

### 1. 🤖 Multi-Agent Investigation & Evidence Cross-Verification
* **Multi-Agent Pipeline**: Automatically decomposes complex citizen inquiries across specialized agents (Government Data Agent, Tender & Budget Agent, Timeline & Work Order Agent, and Media/YouTube Evidence Agent).
* **Contradiction & Anomaly Detection**: Highlights discrepancies between administrative budget approvals (Government Resolutions/GRs), awarded commercial bids (MahaTenders), and on-ground progress.
* **Evidence Gap Identification**: Flags missing statutory chain-of-custody records, including digital Measurement Books (MB) and mandatory Quality Assurance / Final Handover Certificates.
* **ChatGPT-Style "Connecting Dots..." Experience**: Minimalist, real-time reasoning and evidence triangulation stream that connects dots cleanly without interface clutter.

### 2. 📜 Statutory Section 6(1) RTI Application Generator
* **Legally-Grounded Drafting**: Automatically generates compliant **Form A** Right to Information applications addressed to the respective department's Public Information Officer (PIO).
* **Targeted Document Requests**: Pins specific missing files (e.g. revised sanction orders, milestone inspection logs, test certificates) citing relevant provisions of the **Right to Information Act, 2005**.
* **Official PIO Response Analyzer**: Upload or paste official departmental replies to automatically extract compliance status, admissions of delay, or unlawful refusal grounds.

### 3. 🔍 Unified Multimodal Search Engine
* **Natural Language Query Parsing**: Extracts locations, departments, dates, currency values (₹), and tender IDs from raw queries.
* **Multilingual Querying**: Native support for **Marathi (मराठी)**, **Hindi (हिंदी)**, and **English**.
* **Exact Timestamp Deep-Linking**: Direct links to the exact second in YouTube video transcripts (`?t=XXs`).
* **Page-Level PDF Citations**: Jump straight to relevant pages within government gazettes and administrative resolutions.
* **Dynamic Highlight Snippets**: Visual highlighting of matched keywords, project names, and financial figures.
* **Granular Filtering**: Filter by content type (Government Document, News, Video), Department, District, Language, and Date range.

### 4. 📑 Government Document & PDF Archiving
* **Automated PDF Text Extraction**: Uses `PyMuPDF` (fitz) for page-by-page text extraction and metadata extraction.
* **Immutable Version History**: Every document is hashed with **SHA-256**. When departments modify circulars, new revisions are versioned without overwriting past history.
* **Deduplication & Caching**: Prevents redundant network requests and stores local verified snapshots.

### 5. 🎥 YouTube Transcript Intelligence
* **Caption & Subtitle Extraction**: Extracts official timestamped captions in Marathi, Hindi, and English.
* **Segment Indexing**: Indexes video transcripts into timestamped segments for sub-second keyword search.
* **Attribution Metadata**: Captures channel names, publish dates, durations, and original video links.

### 6. ⚙️ Operational Admin Console & Scraper Observability
* **Live Analytics Dashboard**: Visual metrics tracking indexed records, active sources, daily ingest volume, and error rates using Recharts.
* **Source Registry & Discovery**: Auto-detects website structures, input types, and JavaScript rendering requirements.
* **Automated Scheduler**: Background polling scheduler powered by `APScheduler` for configurable recurring syncs.
* **Manual Collector Controls**: Instant "Run Now" triggers, pause/resume switches, and granular execution telemetry.
* **Structured System Logs**: Level-filtered audit trail (DEBUG, INFO, WARNING, ERROR) for total pipeline observability.

### 7. 🛡️ Ethical Scraping & Security
* **Robots.txt Compliance**: Strictly respects `robots.txt` directives per domain.
* **Polite Rate Limiting**: Built-in request pacing and crawl delays.
* **SSRF Protection**: Blocks internal, loopback, link-local, and reserved IP addresses.
* **Public-Only Access**: Collects exclusively public data without attempting authentication or paywall bypass.

---

## 🏗️ Architecture & Tech Stack

| Layer | Technologies Used |
|---|---|
| **Backend API** | FastAPI, Python 3.10+, Uvicorn, Pydantic |
| **Multi-Agent & LLM** | Groq API (Llama-3.3-70B-Versatile / Mixtral-8x7b), LangGraph StateGraph |
| **Vector Store & RAG** | ChromaDB / pgvector, Sentence Transformers, Hybrid SQL + Vector Ranking |
| **Database & ORM** | SQLAlchemy 2.0, SQLite (Zero-config local) / PostgreSQL (Production) |
| **Extraction & Scraping** | HTTPX, BeautifulSoup4, PyMuPDF, Playwright (Headless Chromium), YouTube Transcript API |
| **Scheduling** | APScheduler |
| **Frontend UI** | React 18, Vite, Tailwind CSS, React Router v6, Axios, Recharts, Lucide Icons |
| **Containerization** | Docker, Docker Compose |

---

## 🚀 Getting Started

### Prerequisites
* **Python 3.10+** (check with `python --version`)
* **Node.js 18+** & **npm** (check with `node -v` and `npm -v`)
* *(Optional)* **Groq API Key** (for live LLM multi-agent reasoning)

---

### Running Locally (Windows PowerShell)

#### Step 1: Start the Backend

1. Navigate to the `backend` directory:
   ```powershell
   cd backend
   ```

2. Create and activate a Python virtual environment:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. Install backend dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

4. *(Optional)* Set your Groq API Key for live AI investigation in `.env`:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   DATABASE_URL=sqlite:///./maha_intel.db
   ```

5. Start the FastAPI development server:
   ```powershell
   uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
   ```
   > The API will start at `http://127.0.0.1:8000`. Test it by opening `http://127.0.0.1:8000/docs` in your browser.

---

#### Step 2: Start the Frontend

1. Open a second terminal window and navigate to the `frontend` directory:
   ```powershell
   cd frontend
   ```

2. Install Node dependencies:
   ```powershell
   npm install
   ```

3. Start the Vite development server:
   ```powershell
   npm run dev
   ```
   > The frontend will start at `http://localhost:5173`.

---

### Running Locally (Linux / macOS Bash)

#### Step 1: Backend
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

#### Step 2: Frontend
```bash
cd frontend
npm install
npm run dev
```

---

### Running with Docker Compose

To start the full stack with a single command:
```bash
docker compose up --build
```

---

## 🌐 Application URLs

| Service | URL | Description |
|---|---|---|
| **Public Search Portal** | `http://localhost:5173` | Unified search across government records, news & video transcripts |
| **AI Investigation & RTI** | `http://localhost:5173/investigate` | Multi-agent civic audit, connecting-dots reasoning & RTI generator |
| **Admin Console** | `http://localhost:5173/admin` | Source management, scraper runs, scheduler & log viewer |
| **Interactive API Docs** | `http://localhost:8000/docs` | Swagger UI documentation for all endpoints |
| **Alternative API Docs** | `http://localhost:8000/redoc` | ReDoc API specification |
| **Backend Health Check** | `http://localhost:8000/health` | API and database health status |

---

## 📡 API Endpoints Overview

### AI Investigation & RTI
* `POST /api/investigations` — Initiate a multi-agent investigation for a citizen query.
* `GET /api/investigations/{id}` — Retrieve an existing investigation with all agent findings, milestones, claims, and RTI drafts.
* `POST /api/intelligence/rti/{id}/response` — Submit an official PIO reply text for automated statutory compliance analysis.
* `GET /api/intelligence/rti/{id}/response-analysis` — View classification breakdown of official replies.

### Public Search & Content
* `GET /api/search?q={query}` — Unified search across all indexed government documents, news articles, and video transcripts.
* `GET /api/recent?limit=6` — Retrieve recently ingested public records.
* `GET /api/documents/{id}` — Full document view with page-by-page extracted text and SHA-256 version history.
* `GET /api/youtube/{id}` — Video details with searchable, timestamped transcript segments.
* `GET /api/news/{id}` — News article content with extracted financial and infrastructure mentions.

### Collector & Source Administration
* `GET /api/sources` — List all registered public sources and health statuses.
* `POST /api/sources` — Register a new public source.
* `POST /api/sources/analyze` — Auto-detect website structure, input kind, and JavaScript rendering needs.
* `PATCH /api/sources/{id}?enabled={bool}` — Enable or disable automated scraper runs.
* `GET /api/scrapers` — View execution history, yield, latency, and error counts.
* `POST /api/scrapers/{id}/run` — Manually trigger an immediate collector run.
* `GET /api/logs` — Query structured collector events and error logs.

---

## 📁 Project Structure

```text
scapper/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py             # FastAPI application, routing, and CORS
│   │   ├── models.py           # SQLAlchemy database models (Intelligence & Records)
│   │   ├── schemas.py          # Pydantic validation schemas
│   │   ├── database.py         # Database engine and connection pooling
│   │   ├── agents.py           # Multi-agent investigation and verification engine
│   │   ├── rag.py              # Retrieval-Augmented Generation (Hybrid vector/SQL)
│   │   ├── llm.py              # Groq LLM integration and fallback engine
│   │   ├── chroma_store.py     # ChromaDB vector embedding store
│   │   ├── graph.py            # LangGraph multi-agent orchestration graph
│   │   ├── ingestion.py        # PDF, News, and YouTube extraction logic
│   │   ├── search.py           # Natural language query parsing & snippet scoring
│   │   ├── scheduler.py        # Background automated scraper dispatcher
│   │   ├── source_registry.py  # Curated registry of live public sources
│   │   └── migrations.py       # Auto-upgrade database schema migrations
│   ├── storage/                # Local PDF and document cache
│   ├── requirements.txt        # Python dependencies
│   └── Dockerfile              # Backend containerization file
├── frontend/
│   ├── src/
│   │   ├── App.jsx             # Admin console, dashboard, router, and collector UI
│   │   ├── public.jsx          # Public search portal, Investigation & RTI generator
│   │   ├── api.js              # Axios API client
│   │   ├── index.css           # Styling and design system
│   │   └── main.jsx            # React root mount
│   ├── index.html              # HTML entrypoint
│   ├── package.json            # Frontend dependencies & scripts
│   └── vite.config.js          # Vite configuration
├── docker-compose.yml          # Multi-container orchestration
└── README.md                   # Project documentation
```

---

## 👥 Credits

Developed and maintained by **Krishna and team**.
