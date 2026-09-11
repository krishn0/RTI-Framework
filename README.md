# CoreScapper — Public Information Collection & Intelligence Platform

> **Built with ❤️ by Krishna and team.**

**CoreScapper** is an end-to-end intelligence and public information collection platform designed to ingest, version, index, search, and monitor public records from government portals, news publications, and official YouTube channels.

It combines an automated, ethical web scraping backend with a lightning-fast full-text search engine, document version control, and dual user interfaces: a **Public Evidence Search Portal** and a comprehensive **Technical Admin Console**.

---

## 🌟 Key Features

### 1. 🔍 Unified Multimodal Search Engine
* **Natural Language Query Parsing**: Extracts locations, departments, dates, currency amounts (₹), and tender IDs automatically.
* **Multilingual Support**: Supports Marathi (मराठी), Hindi (हिंदी), and English search queries and document processing.
* **Exact Timestamp Matching**: Direct deep-linking to the exact second in YouTube video transcripts.
* **Page-Level PDF Matching**: Pinpoints specific page numbers within large multi-page government resolutions and gazettes.
* **Term Highlighting & Snippets**: Visual highlighting of matched search terms in results.
* **Granular Filtering**: Filter search results by content type (Government Document, News, Video), Department, District, Language, and Date range.

### 2. 📑 Government Document & PDF Archiving
* **Automated PDF Extraction**: Uses `PyMuPDF` (fitz) to extract searchable text, page counts, and metadata.
* **Immutable Version History**: Every document download is hashed with **SHA-256**. If a government department modifies a circular, a new version is recorded without overwriting past revisions.
* **Deduplication**: Avoids re-processing identical files, saving storage and bandwidth.

### 3. 🎥 YouTube Transcript Intelligence
* **Caption & Subtitle Extraction**: Automatically downloads timestamped official captions in Marathi/Hindi/English.
* **Segment Indexing**: Parses video into timestamped chunks with direct jump links (`?t=XXs`).
* **Metadata Tracking**: Captures channel names, duration, publication date, thumbnails, and descriptions.

### 4. 📰 News & Media Monitoring
* **Article Extraction**: Uses `BeautifulSoup4` with custom extraction heuristics for headlines, authors, publish dates, locations, and body text.
* **Entity & Mention Extraction**: Automatically extracts mentions of budgets, amounts (e.g. ₹50 crore), and infrastructure keywords.
* **Original Attribution**: Preserves canonical source URLs and publisher attributions.

### 5. ⚙️ Operational Admin Console
* **Live Analytics Dashboard**: Visual metrics with Recharts tracking documents collected today, active scrapers, failed jobs, and version changes.
* **Source Registry & Discovery**: Register any public URL; CoreScapper automatically analyzes the URL, detects source type, input structure, and whether JavaScript rendering is needed.
* **Automated Background Scheduler**: Built-in 30-second polling scheduler powered by `APScheduler` that triggers scrapers on configurable intervals (every 30 mins, hourly, daily, weekly).
* **Manual Collector Controls**: Instant "Run Now" buttons, pause/resume switches, and detailed run performance metrics (items found, created, updated, duration, and error count).
* **Structured System Logs**: Level-filtered audit trail (DEBUG, INFO, WARNING, ERROR) for complete transparency.

### 6. 🛡️ Ethical Scraping & Security
* **Robots.txt Compliance**: Automatically reads and enforces `robots.txt` rules per domain.
* **Crawl Delays & Rate Limiting**: Applies configurable polite delays between requests (default: 2.0s).
* **SSRF Protection**: Blocks private, loopback, link-local, and reserved IP ranges to protect local infrastructure.
* **No Authentication Bypass**: Strictly ingests public data without attempting CAPTCHA, authentication, or paywall bypass.

---

## 🏗️ Architecture & Tech Stack

| Layer | Technologies Used |
|---|---|
| **Backend API** | FastAPI, Python 3.10+, Uvicorn, Pydantic |
| **Database & ORM** | SQLAlchemy 2.0, PostgreSQL (Production) / SQLite (Zero-config local) |
| **Extraction & Scrapers** | HTTPX, BeautifulSoup4, PyMuPDF, Playwright (Headless Chromium), YouTube Transcript API |
| **Scheduling** | APScheduler (Background Scheduler) |
| **Frontend UI** | React 18, Vite, Tailwind CSS, React Router v6, Axios, Recharts, Lucide Icons |
| **Containerization** | Docker, Docker Compose |

---

## 🚀 Getting Started

### Prerequisites
* **Python 3.10+** (check with `python --version`)
* **Node.js 18+** & **npm** (check with `node -v` and `npm -v`)
* *(Optional)* **Docker & Docker Compose**

---

### Option 1: Running Locally (Windows PowerShell)

#### Step 1: Start the Backend

1. Open a terminal and navigate to the backend directory:
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

4. *(Optional — required only for JavaScript-heavy sites)* Install Playwright Chromium:
   ```powershell
   playwright install chromium
   ```

5. Start the FastAPI development server:
   ```powershell
   uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
   ```
   > The API will start at `http://127.0.0.1:8000`. Test it by opening `http://127.0.0.1:8000/docs` in your browser.

---

#### Step 2: Start the Frontend

1. Open a second terminal window and navigate to the frontend directory:
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

### Option 2: Running Locally (Linux / macOS Bash)

#### Step 1: Backend
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

#### Step 2: Frontend
```bash
cd frontend
npm install
npm run dev
```

---

### Option 3: Running with Docker Compose

To start the full stack (FastAPI backend + React frontend + SQLite/PostgreSQL) with a single command:

```powershell
docker compose up --build
```

---

## 🌐 Application URLs

| Service | URL | Description |
|---|---|---|
| **Public Search Portal** | `http://localhost:5173` | Clean public records search interface |
| **Admin Console** | `http://localhost:5173/admin` | Source management, scrapers, runs & logs |
| **Interactive API Docs** | `http://localhost:8000/docs` | Swagger UI documentation for all endpoints |
| **Alternative API Docs** | `http://localhost:8000/redoc` | ReDoc API specification |
| **Backend Health Check** | `http://localhost:8000/health` | Service health status |

---

## ⚙️ Configuration & Environment Variables

Create a `.env` file in the `backend/` directory to customize configurations:

| Variable | Default Value | Description |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./maha_intel.db` | Database connection string. Use `postgresql+psycopg://user:pass@host:5432/dbname` for PostgreSQL. |
| `STORAGE_DIR` | `./storage` | Directory path where downloaded PDF files and document versions are stored. |
| `BOOTSTRAP_LIVE_SOURCES` | `true` | When `true`, populates the curated registry of 25 Maharashtra sources on startup. |
| `RECOVER_ORPHANED_RUNS` | `true` | When `true`, automatically resets interrupted scrapers upon server restart. |
| `CORS_ORIGINS` | `http://localhost:5173,http://localhost:3000` | Allowed origins for cross-origin frontend requests. |

---

## 📡 API Endpoints Overview

### Public & Search
* `GET /api/stats` — Summary counts of indexed documents, videos, news, and scraper runs.
* `GET /api/recent?limit=6` — Retrieve recently ingested public records.
* `GET /api/search?q={query}` — Unified search across all indexed documents, news, and videos.
* `GET /api/documents/{id}` — Full document view including page-by-page extracted text and version history.
* `GET /api/youtube/{id}` — Video details with searchable, timestamped transcript segments.
* `GET /api/news/{id}` — News article content with extracted financial/project mentions.

### Scraper & Source Administration
* `GET /api/sources` — List all registered sources and their health status.
* `POST /api/sources` — Register a new public source.
* `POST /api/sources/analyze` — Auto-detect website type, input kind, and JavaScript rendering requirement.
* `PATCH /api/sources/{id}?enabled={bool}` — Enable or disable automated scraper runs.
* `GET /api/scrapers` — View execution history, yield, latency, and failure rates.
* `POST /api/scrapers/{id}/run` — Manually trigger an immediate collection run.
* `GET /api/logs` — Query structured collector events and error logs.

---

## 📁 Project Structure

```text
scapper/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── database.py         # SQLAlchemy engine and session setup
│   │   ├── models.py           # Database models (Sources, Documents, News, Videos, etc.)
│   │   ├── schemas.py          # Pydantic schemas for request/response validation
│   │   ├── main.py             # FastAPI entrypoint, endpoints, and CORS middleware
│   │   ├── ingestion.py        # PDF, News, and YouTube extraction logic
│   │   ├── search.py           # NLP search parsing, query scoring & snippet generation
│   │   ├── scheduler.py        # Background automated scraper dispatcher
│   │   ├── source_registry.py  # Curated registry of 25 live Maharashtra sources
│   │   └── migrations.py       # Auto-upgrade database schema migrations
│   ├── storage/                # Local document and PDF storage
│   ├── requirements.txt        # Python backend dependencies
│   └── Dockerfile              # Backend containerization file
├── frontend/
│   ├── src/
│   │   ├── App.jsx             # Admin console, dashboard, router, and collector UI
│   │   ├── public.jsx          # Public search portal, document, video & news viewers
│   │   ├── api.js              # Axios instance configuration
│   │   ├── index.css           # Styling and design system
│   │   └── main.jsx            # React root mount
│   ├── index.html              # HTML entrypoint
│   ├── package.json            # Frontend dependencies & scripts
│   └── vite.config.js          # Vite configuration
├── docker-compose.yml          # Multi-container orchestration
└── README.md                   # Project documentation
```

---

## ❓ Troubleshooting

### 1. Frontend shows "Network Error"
* **Cause**: The FastAPI backend is not running on port 8000.
* **Fix**: Ensure the backend is running using `uvicorn app.main:app --port 8000` inside the `backend` directory.

### 2. PowerShell script execution policy error
* **Cause**: Windows PowerShell restricts running `.ps1` scripts by default.
* **Fix**: Run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` and then run `.venv\Scripts\Activate.ps1`.

### 3. JavaScript-rendered source fails to extract
* **Cause**: Playwright browsers are not installed.
* **Fix**: Run `playwright install chromium` inside the active Python virtual environment.

---

## 👥 Credits

Developed and maintained by **Krishna and team**.
