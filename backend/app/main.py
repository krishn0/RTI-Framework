import json
import ipaddress
import logging
import os
import re
import socket
import time
from datetime import datetime, timedelta, timezone
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup
from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func, or_
from sqlalchemy.orm import Session, selectinload

from . import models, schemas
from .database import Base, SessionLocal, engine, get_db
from .ingestion import backfill_youtube_segment_index, detect_district, detect_language, extract_date, ingest_youtube, repair_legacy_marathi_documents
from .search import make_snippet, parse_query, score_record

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("corescapper")
app = FastAPI(title="CoreScapper API", version="1.0.0")
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")
app.add_middleware(CORSMiddleware, allow_origins=cors_origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])


@app.on_event("startup")
def startup():
    Base.metadata.create_all(engine)
    from .migrations import upgrade_development_database
    upgrade_development_database(engine)
    Base.metadata.create_all(engine)
    if os.getenv("RECOVER_ORPHANED_RUNS", "true").lower() in {"1", "true", "yes"}:
        with SessionLocal() as db:
            orphaned = db.query(models.ScraperRun).filter(models.ScraperRun.status.in_(("queued", "running"))).all()
            for run in orphaned:
                run.status = "interrupted"
                run.finished_at = datetime.now(timezone.utc)
                run.errors += 1
                db.add(models.ScraperLog(run_id=run.id, source_id=run.source_id, level="WARNING", message="Run interrupted by collector process restart; source will be scheduled again"))
            db.commit()
    if os.getenv("BOOTSTRAP_LIVE_SOURCES", "true").lower() in {"1", "true", "yes"}:
        with SessionLocal() as db:
            if db.query(models.Source).count() == 0:
                import_source_registry(db)
            repaired = repair_legacy_marathi_documents(db)
            if repaired:
                logger.info("Normalized legacy Marathi text in %s document versions", repaired)
            indexed_segments = backfill_youtube_segment_index(db)
            if indexed_segments:
                logger.info("Indexed %s timestamped YouTube transcript segments", indexed_segments)
            active_run = db.query(models.ScraperRun).filter(models.ScraperRun.status.in_(("queued", "running"))).first()
            if not active_run:
                for item in db.query(models.ContentIndex).all():
                    if item.content_type == "government_document":
                        document = db.get(models.Document, item.content_id)
                        version = db.query(models.DocumentVersion).filter_by(document_id=item.content_id).order_by(models.DocumentVersion.downloaded_at.desc()).first()
                        if version:
                            item.language = detect_language(version.extracted_text)
                            item.district = detect_district(f"{item.title} {version.extracted_text[:5000]}")
                        if document and not document.published_date:
                            document.published_date = extract_date(document.title)
                            item.published_at = document.published_date
                    elif item.content_type == "news_article" and not item.district:
                        item.district = detect_district(f"{item.title} {item.text[:5000]}")
                db.commit()
    from .scheduler import start_scheduler
    start_scheduler()


@app.on_event("shutdown")
def shutdown():
    from .scheduler import stop_scheduler
    stop_scheduler()


@app.get("/health")
def health():
    return {"status": "ok", "time": datetime.now(timezone.utc)}


@app.get("/api/stats")
def stats(db: Session = Depends(get_db)):
    today = datetime.now(timezone.utc).date()
    collected_today = db.query(models.ContentIndex).filter(func.date(models.ContentIndex.created_at) == today).count()
    return {
        "active_sources": db.query(models.Source).filter_by(enabled=True).count(),
        "documents": db.query(models.Document).count(),
        "youtube_videos": db.query(models.YouTubeVideo).count(),
        "transcript_segments": db.query(models.YouTubeTranscriptSegment).count(),
        "news_articles": db.query(models.NewsArticle).count(),
        "documents_today": db.query(models.Document).filter(func.date(models.Document.first_seen_at) == today).count(),
        "collected_today": collected_today,
        "failed_jobs": db.query(models.ScraperRun).filter(models.ScraperRun.status.in_(("failed", "interrupted"))).count(),
        "changed_content": db.query(models.Document).join(models.DocumentVersion).group_by(models.Document.id).having(func.count(models.DocumentVersion.id) > 1).count(),
    }


@app.get("/api/recent")
def recent_content(limit: int = Query(6, ge=1, le=30), db: Session = Depends(get_db)):
    rows = db.query(models.ContentIndex).order_by(models.ContentIndex.created_at.desc()).limit(limit).all()
    return [{"content_type": row.content_type, "content_id": row.content_id, "title": row.title, "source_name": row.source, "source_url": row.source_url, "published_at": row.published_at, "created_at": row.created_at} for row in rows]


@app.get("/api/activity")
def collection_activity(days: int = Query(7, ge=1, le=90), db: Session = Depends(get_db)):
    from datetime import timedelta
    today = datetime.now(timezone.utc).date()
    output = []
    for offset in range(days - 1, -1, -1):
        day = today - timedelta(days=offset)
        counts = dict(db.query(models.ContentIndex.content_type, func.count(models.ContentIndex.id)).filter(func.date(models.ContentIndex.created_at) == day).group_by(models.ContentIndex.content_type).all())
        output.append({"date": day.isoformat(), "documents": counts.get("government_document", 0), "news": counts.get("news_article", 0), "videos": counts.get("youtube_transcript", 0)})
    return output


@app.get("/api/sources", response_model=list[schemas.SourceOut])
def sources(source_type: str | None = None, enabled: bool | None = None, db: Session = Depends(get_db)):
    q = db.query(models.Source)
    if source_type: q = q.filter(models.Source.source_type == source_type)
    if enabled is not None: q = q.filter(models.Source.enabled == enabled)
    return q.order_by(models.Source.name).all()


@app.post("/api/sources", response_model=schemas.SourceOut, status_code=201)
def create_source(payload: schemas.SourceCreate, db: Session = Depends(get_db)):
    supported = {"government_website", "government_document", "youtube", "news", "gazette", "court", "audit", "tender_portal"}
    if payload.source_type not in supported:
        raise HTTPException(422, f"Unsupported source type. Choose one of: {', '.join(sorted(supported))}")
    base_url = str(payload.base_url).rstrip("/")
    if db.query(models.Source).filter_by(base_url=base_url).first():
        raise HTTPException(409, "This source URL is already registered")
    row = models.Source(name=payload.name, short_name=payload.short_name, category=payload.category, evidence_tier=payload.evidence_tier, languages=json.dumps(payload.languages, ensure_ascii=False), tags=json.dumps(payload.tags, ensure_ascii=False), base_url=base_url, source_type=payload.source_type, input_kind=payload.input_kind, enabled=payload.enabled, crawl_delay=payload.crawl_delay, frequency=payload.frequency, requires_javascript=payload.requires_javascript, health="pending", next_run_at=datetime.now(timezone.utc) if payload.enabled else None)
    db.add(row); db.commit(); db.refresh(row)
    return row


@app.post("/api/sources/import-registry")
def import_source_registry(db: Session = Depends(get_db)):
    from .source_registry import LIVE_SOURCE_REGISTRY
    now = datetime.now(timezone.utc)
    created = updated = 0
    ids = []
    for position, item in enumerate(LIVE_SOURCE_REGISTRY):
        url = item["url"].rstrip("/")
        row = db.query(models.Source).filter_by(base_url=url).first()
        metadata_values = {
            "name": item["name"], "short_name": item.get("short_name"), "category": item.get("category"),
            "source_type": item["source_type"], "input_kind": item["input_kind"], "evidence_tier": item["evidence_tier"],
            "languages": json.dumps(item.get("languages", []), ensure_ascii=False), "tags": json.dumps(item.get("tags", []), ensure_ascii=False),
        }
        if row:
            for key, value in metadata_values.items(): setattr(row, key, value)
            updated += 1
        else:
            row = models.Source(base_url=url, health="pending", next_run_at=now + timedelta(seconds=60 + position * 90), enabled=True, crawl_delay=2.0, frequency="hourly" if item["source_type"] == "news" else "daily", requires_javascript=False, **metadata_values)
            db.add(row); db.flush(); created += 1
        ids.append(row.id)
    db.commit()
    return {"total": len(ids), "created": created, "updated": updated, "source_ids": ids, "message": "Live sources registered; initial runs are staggered to respect upstream services."}


def ensure_public_host(url: str):
    host = urlparse(url).hostname
    if not host:
        raise HTTPException(400, "URL must include a valid public hostname")
    try:
        addresses = {item[4][0] for item in socket.getaddrinfo(host, None)}
    except socket.gaierror as exc:
        raise HTTPException(400, "The hostname could not be resolved") from exc
    for address in addresses:
        ip = ipaddress.ip_address(address)
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast:
            raise HTTPException(400, "Private and local network URLs are not allowed")


@app.post("/api/sources/analyze")
def analyze_source(payload: schemas.SourceAnalyze):
    url = str(payload.url)
    ensure_public_host(url)
    parsed = urlparse(url)
    host, path = parsed.hostname.lower(), parsed.path.lower()
    detected = "government_website"
    input_kind = "website"
    requires_javascript = False
    if host in {"youtube.com", "www.youtube.com", "youtu.be", "www.youtu.be"}:
        detected = "youtube"
        input_kind = "video" if host.endswith("youtu.be") or path == "/watch" or "/shorts/" in path else "playlist" if path == "/playlist" else "channel"
        requires_javascript = True
    elif path.endswith(".pdf"):
        detected, input_kind = "government_document", "pdf"
    elif "tender" in host or "tender" in path:
        detected, input_kind, requires_javascript = "tender_portal", "tender portal", True
    elif "gazette" in host or "gazette" in path:
        detected, input_kind = "gazette", "gazette portal"
    elif not (host.endswith(".gov.in") or "maharashtra.gov" in host or host.endswith(".nic.in")):
        detected, input_kind = "news", "news website"
    name = host.removeprefix("www.").split(".")[0].replace("-", " ").title()
    title = None
    try:
        response = httpx.get(url, timeout=12, follow_redirects=True, headers={"User-Agent": "MahaIntelCollector/1.0"})
        response.raise_for_status()
        content_type = response.headers.get("content-type", "")
        if "application/pdf" in content_type:
            detected, input_kind = "government_document", "pdf"
        elif "text/html" in content_type:
            soup = BeautifulSoup(response.text, "html.parser")
            title = soup.title.get_text(" ", strip=True) if soup.title else None
            og_type = soup.select_one('meta[property="og:type"]')
            if detected == "news" and og_type and og_type.get("content", "").lower() == "article":
                input_kind = "news article"
    except httpx.HTTPError:
        pass
    return {"url": url, "source_type": detected, "input_kind": input_kind, "name": (title or name)[:240], "requires_javascript": requires_javascript}


@app.patch("/api/sources/{source_id}", response_model=schemas.SourceOut)
def update_source(source_id: int, enabled: bool, db: Session = Depends(get_db)):
    source = db.get(models.Source, source_id)
    if not source: raise HTTPException(404, "Source not found")
    source.enabled = enabled
    if enabled and not source.next_run_at:
        source.next_run_at = datetime.now(timezone.utc)
    db.commit(); db.refresh(source)
    return source


def paginate(q, page, page_size):
    total = q.count()
    return {"items": q.offset((page-1)*page_size).limit(page_size).all(), "total": total, "page": page, "page_size": page_size}


@app.get("/api/documents")
def documents(q: str | None = None, department: str | None = None, category: str | None = None, page: int = 1, page_size: int = Query(20, le=100), db: Session = Depends(get_db)):
    query = db.query(models.Document).options(selectinload(models.Document.versions)).order_by(models.Document.published_date.desc())
    if q: query = query.filter(or_(models.Document.title.ilike(f"%{q}%"), models.Document.department.ilike(f"%{q}%")))
    if department: query = query.filter(models.Document.department == department)
    if category: query = query.filter(models.Document.category == category)
    return paginate(query, page, page_size)


@app.get("/api/documents/{document_id}", response_model=schemas.DocumentOut)
def document(document_id: int, db: Session = Depends(get_db)):
    row = db.query(models.Document).options(selectinload(models.Document.versions).selectinload(models.DocumentVersion.pages)).filter_by(id=document_id).first()
    if not row: raise HTTPException(404, "Document not found")
    return row


@app.get("/api/youtube")
def youtube(q: str | None = None, page: int = 1, page_size: int = Query(20, le=100), db: Session = Depends(get_db)):
    query = db.query(models.YouTubeVideo).options(selectinload(models.YouTubeVideo.segments)).order_by(models.YouTubeVideo.published_at.desc())
    if q: query = query.filter(or_(models.YouTubeVideo.title.ilike(f"%{q}%"), models.YouTubeVideo.channel_name.ilike(f"%{q}%")))
    return paginate(query, page, page_size)


@app.get("/api/youtube/{video_id}", response_model=schemas.VideoOut)
def youtube_video(video_id: int, db: Session = Depends(get_db)):
    row = db.query(models.YouTubeVideo).options(selectinload(models.YouTubeVideo.segments)).filter_by(id=video_id).first()
    if not row: raise HTTPException(404, "Video not found")
    return row


@app.post("/api/youtube/scrape", response_model=schemas.VideoOut)
def scrape_youtube(payload: schemas.YouTubeRequest, db: Session = Depends(get_db)):
    try: return ingest_youtube(db, payload.url, payload.language)
    except ValueError as exc: raise HTTPException(400, str(exc)) from exc
    except Exception as exc: raise HTTPException(502, f"YouTube collection failed: {exc}") from exc


@app.get("/api/news")
def news(q: str | None = None, location: str | None = None, category: str | None = None, page: int = 1, page_size: int = Query(20, le=100), db: Session = Depends(get_db)):
    query = db.query(models.NewsArticle).order_by(models.NewsArticle.published_at.desc())
    if q: query = query.filter(or_(models.NewsArticle.title.ilike(f"%{q}%"), models.NewsArticle.article_text.ilike(f"%{q}%")))
    if location: query = query.filter(models.NewsArticle.location == location)
    if category: query = query.filter(models.NewsArticle.category == category)
    return paginate(query, page, page_size)


@app.get("/api/news/{article_id}", response_model=schemas.NewsOut)
def news_article(article_id: int, db: Session = Depends(get_db)):
    row = db.get(models.NewsArticle, article_id)
    if not row: raise HTTPException(404, "Article not found")
    return row


def get_candidate_filters(candidate_terms: list[str]):
    return [
        or_(
            models.ContentIndex.title.ilike(f"%{term}%"),
            models.ContentIndex.text.ilike(f"%{term}%"),
            models.ContentIndex.department.ilike(f"%{term}%"),
            models.ContentIndex.district.ilike(f"%{term}%"),
            models.ContentIndex.channel.ilike(f"%{term}%"),
            models.ContentIndex.publisher.ilike(f"%{term}%"),
        )
        for term in candidate_terms if term
    ]


def apply_common_filters(query, filters: dict):
    if filters.get("department"):
        query = query.filter(models.ContentIndex.department.ilike(f"%{filters['department']}%"))
    if filters.get("district"):
        query = query.filter(models.ContentIndex.district.ilike(f"%{filters['district']}%"))
    if filters.get("language"):
        query = query.filter(models.ContentIndex.language == filters["language"])
    if filters.get("document_type"):
        query = query.filter(models.ContentIndex.document_type == filters["document_type"])
    if filters.get("publisher"):
        query = query.filter(models.ContentIndex.publisher.ilike(f"%{filters['publisher']}%"))
    if filters.get("youtube_channel"):
        query = query.filter(models.ContentIndex.channel.ilike(f"%{filters['youtube_channel']}%"))
    if filters.get("date_from"):
        query = query.filter(models.ContentIndex.published_at >= filters["date_from"])
    if filters.get("date_to"):
        query = query.filter(models.ContentIndex.published_at <= filters["date_to"])
    return query


def search_documents(db: Session, parsed: ParsedQuery, candidate_terms: list[str], filters: dict) -> list[models.ContentIndex]:
    q = db.query(models.ContentIndex).filter(models.ContentIndex.content_type == "government_document")
    conds = get_candidate_filters(candidate_terms)
    if conds:
        q = q.filter(or_(*conds))
    q = apply_common_filters(q, filters)
    return q.limit(2000).all()


def search_news(db: Session, parsed: ParsedQuery, candidate_terms: list[str], filters: dict) -> list[models.ContentIndex]:
    q = db.query(models.ContentIndex).filter(models.ContentIndex.content_type == "news_article")
    conds = get_candidate_filters(candidate_terms)
    if conds:
        q = q.filter(or_(*conds))
    q = apply_common_filters(q, filters)
    return q.limit(2000).all()


def search_youtube_transcripts(db: Session, parsed: ParsedQuery, candidate_terms: list[str], filters: dict) -> list[models.ContentIndex]:
    q = db.query(models.ContentIndex).filter(models.ContentIndex.content_type == "youtube_transcript")
    conds = get_candidate_filters(candidate_terms)
    if conds:
        q = q.filter(or_(*conds))
    q = apply_common_filters(q, filters)
    return q.limit(3000).all()


def rank_results(items: list[models.ContentIndex], parsed: ParsedQuery) -> list[tuple[float, models.ContentIndex]]:
    ranked = []
    for item in items:
        relevance, concepts = score_record(item, parsed)
        if concepts["required_concepts"] > 1 and concepts["matched_concepts"] < concepts["required_concepts"]:
            continue
        if relevance > 0:
            ranked.append((relevance, item))
    ranked.sort(
        key=lambda pair: (
            pair[0],
            pair[1].published_at or pair[1].created_at,
            pair[1].created_at
        ),
        reverse=True
    )
    return ranked


@app.get("/api/search")
def search(
    q: str = Query(..., min_length=1),
    content_type: str | None = None,
    department: str | None = None,
    district: str | None = None,
    language: str | None = None,
    document_type: str | None = None,
    publisher: str | None = None,
    youtube_channel: str | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    page: int = 1,
    limit: int = 20,
    page_size: int | None = None,
    db: Session = Depends(get_db)
):
    actual_limit = page_size if page_size is not None else limit
    if not isinstance(page, int):
        page = 1
    if not isinstance(actual_limit, int):
        actual_limit = 20

    parsed = parse_query(q)
    candidate_terms = list(dict.fromkeys([
        *parsed.highlight_terms(),
        *(term for group in parsed.keyword_groups for term in group),
        *parsed.location_terms,
        *parsed.amounts,
        *parsed.dates,
        *parsed.contractor_names,
    ]))
    filters = {
        "department": department,
        "district": district,
        "language": language,
        "document_type": document_type,
        "publisher": publisher,
        "youtube_channel": youtube_channel,
        "date_from": date_from,
        "date_to": date_to,
    }

    document_results = search_documents(db, parsed, candidate_terms, filters)
    news_results = search_news(db, parsed, candidate_terms, filters)
    youtube_results = search_youtube_transcripts(db, parsed, candidate_terms, filters)

    all_candidates = document_results + news_results + youtube_results
    ranked = rank_results(all_candidates, parsed)

    grouped = {}
    for _, item in ranked:
        grouped[item.content_type] = grouped.get(item.content_type, 0) + 1

    normalized_type = "government_document" if content_type == "document" else content_type
    filtered = [pair for pair in ranked if not normalized_type or pair[1].content_type == normalized_type]
    total = len(filtered)
    rows = filtered[(page - 1) * actual_limit: page * actual_limit]

    results = []
    highlight_terms = parsed.highlight_terms()
    for relevance, item in rows:
        snippet = make_snippet(item.text, highlight_terms)
        page_number = None
        if item.content_type == "government_document":
            latest = db.query(models.DocumentVersion).filter_by(document_id=item.content_id).order_by(models.DocumentVersion.downloaded_at.desc()).first()
            if latest:
                page_filters = [models.DocumentPage.text.ilike(f"%{term}%") for term in highlight_terms if term]
                page_match = db.query(models.DocumentPage).filter(models.DocumentPage.version_id == latest.id, or_(*page_filters)).order_by(models.DocumentPage.page_number).first() if page_filters else None
                page_number = page_match.page_number if page_match else None

        source_record = db.get(models.Source, item.source_id) if item.source_id else None
        video_id = item.parent_content_id if item.content_type == "youtube_transcript" else None
        results.append({
            "id": item.id,
            "content_id": video_id or item.content_id,
            "index_content_id": item.content_id,
            "type": item.content_type,
            "content_type": item.content_type,
            "title": item.title,
            "score": round(relevance, 2),
            "source": item.source,
            "source_name": item.source,
            "source_url": item.source_url,
            "channel": item.channel or (item.source if item.content_type == "youtube_transcript" else None),
            "video_url": item.source_url if video_id or item.content_type == "youtube_transcript" else None,
            "published_at": item.published_at,
            "language": item.language,
            "department": item.department,
            "district": item.district,
            "publisher": item.publisher,
            "evidence_tier": source_record.evidence_tier if source_record else None,
            "snippet": snippet,
            "page_number": page_number,
            "timestamp_seconds": item.timestamp_seconds,
            "highlight_terms": highlight_terms,
        })

    counts = {name: grouped.get(name, 0) for name in ("government_document", "news_article", "youtube_transcript")}
    response = {
        "query": q,
        "total": total,
        "counts": counts,
        "results": results,
        "items": results,
        "page": page,
        "limit": actual_limit,
        "parsed_query": parsed.public(),
    }
    return response


@app.get("/api/scrapers", response_model=list[schemas.RunOut])
def scrapers(db: Session = Depends(get_db)):
    return db.query(models.ScraperRun).options(selectinload(models.ScraperRun.source)).order_by(models.ScraperRun.started_at.desc()).all()


def execute_run(run_id: int):
    with SessionLocal() as db:
        run = db.get(models.ScraperRun, run_id); source = db.get(models.Source, run.source_id)
        started = time.monotonic(); run.status = "running"; run.started_at = datetime.now(timezone.utc); db.commit()
        try:
            from .scrapers import scraper_for
            result = scraper_for(source)(db, source, run).run()
            run.items_found = result["found"]
            run.items_created = result["created"]
            run.items_updated = result["updated"]
            run.duplicates = result["duplicates"]
            run.pages_scanned = result["pages_scanned"]
            run.errors = result["errors"]
            run.status = "completed" if not result["errors"] else "completed_with_errors"
            source.health = "healthy" if not result["errors"] else "warning"
        except Exception as exc:
            run.status = "failed"; run.errors = 1; source.health = "degraded"
            db.add(models.ScraperLog(run_id=run.id, source_id=source.id, level="ERROR", message=str(exc)[:1000]))
        run.finished_at = datetime.now(timezone.utc); run.duration_ms = int((time.monotonic()-started)*1000); source.last_run_at = run.finished_at
        from .scheduler import next_run_for
        source.next_run_at = next_run_for(source.frequency, run.finished_at)
        db.commit()


@app.post("/api/scrapers/{source_id}/run", response_model=schemas.RunOut)
def run_scraper(source_id: int, background: BackgroundTasks, db: Session = Depends(get_db)):
    source = db.get(models.Source, source_id)
    if not source: raise HTTPException(404, "Source not found")
    if not source.enabled: raise HTTPException(409, "Source is disabled")
    run = models.ScraperRun(source_id=source.id, status="queued"); db.add(run); db.commit(); db.refresh(run)
    background.add_task(execute_run, run.id)
    run.source = source
    return run


@app.post("/api/scrapers/{source_id}/pause", response_model=schemas.SourceOut)
def pause_scraper(source_id: int, db: Session = Depends(get_db)):
    source = db.get(models.Source, source_id)
    if not source: raise HTTPException(404, "Source not found")
    source.enabled = False; source.next_run_at = None; db.commit(); db.refresh(source)
    return source


@app.post("/api/scrapers/{source_id}/resume", response_model=schemas.SourceOut)
def resume_scraper(source_id: int, db: Session = Depends(get_db)):
    source = db.get(models.Source, source_id)
    if not source: raise HTTPException(404, "Source not found")
    source.enabled = True; source.next_run_at = datetime.now(timezone.utc); db.commit(); db.refresh(source)
    return source


@app.get("/api/scrapers/{source_id}/runs")
def source_runs(source_id: int, page: int = 1, limit: int = Query(30, le=100), db: Session = Depends(get_db)):
    if not db.get(models.Source, source_id): raise HTTPException(404, "Source not found")
    return paginate(db.query(models.ScraperRun).filter_by(source_id=source_id).order_by(models.ScraperRun.started_at.desc()), page, limit)


@app.get("/api/runs/{run_id}")
def run_detail(run_id: int, db: Session = Depends(get_db)):
    run = db.query(models.ScraperRun).options(selectinload(models.ScraperRun.source)).filter_by(id=run_id).first()
    if not run: raise HTTPException(404, "Run not found")
    return schemas.RunOut.model_validate(run)


@app.get("/api/runs/{run_id}/logs")
def run_logs(run_id: int, db: Session = Depends(get_db)):
    if not db.get(models.ScraperRun, run_id): raise HTTPException(404, "Run not found")
    return db.query(models.ScraperLog).filter_by(run_id=run_id).order_by(models.ScraperLog.created_at).all()


@app.get("/api/scrapers/{source_id}")
def scraper_detail(source_id: int, db: Session = Depends(get_db)):
    source = db.get(models.Source, source_id)
    if not source: raise HTTPException(404, "Source not found")
    runs = db.query(models.ScraperRun).filter_by(source_id=source_id).order_by(models.ScraperRun.started_at.desc()).limit(30).all()
    logs = db.query(models.ScraperLog).filter_by(source_id=source_id).order_by(models.ScraperLog.created_at.desc()).limit(100).all()
    return {"source": schemas.SourceOut.model_validate(source), "runs": runs, "logs": logs}


@app.get("/api/logs")
def logs(level: str | None = None, source_id: int | None = None, page: int = 1, page_size: int = Query(50, le=200), db: Session = Depends(get_db)):
    query = db.query(models.ScraperLog).order_by(models.ScraperLog.created_at.desc())
    if level: query = query.filter(models.ScraperLog.level == level.upper())
    if source_id: query = query.filter(models.ScraperLog.source_id == source_id)
    return paginate(query, page, page_size)
