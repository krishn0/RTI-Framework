import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import fitz
import httpx
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from youtube_transcript_api import YouTubeTranscriptApi

from . import models
from .marathi import normalize_marathi_pdf_text


STORAGE_PATH = Path(__import__("os").getenv("STORAGE_PATH", "storage"))
USER_AGENT = "MahaIntelCollector/1.0 (+public-information-research)"
MAHARASHTRA_DISTRICTS = ["Ahmednagar", "Akola", "Amravati", "Aurangabad", "Beed", "Bhandara", "Buldhana", "Chandrapur", "Dhule", "Gadchiroli", "Gondia", "Hingoli", "Jalgaon", "Jalna", "Kolhapur", "Latur", "Mumbai", "Nagpur", "Nanded", "Nandurbar", "Nashik", "Osmanabad", "Palghar", "Parbhani", "Pune", "Raigad", "Ratnagiri", "Sangli", "Satara", "Sindhudurg", "Solapur", "Thane", "Wardha", "Washim", "Yavatmal"]


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def detect_language(text: str) -> str:
    sample = text[:10000]
    devanagari = sum("\u0900" <= char <= "\u097f" for char in sample)
    letters = sum(char.isalpha() for char in sample) or 1
    return "mr" if devanagari / letters > 0.15 else "en"


def detect_district(text: str) -> str | None:
    lower = text.lower()
    return next((district for district in MAHARASHTRA_DISTRICTS if re.search(rf"\b{re.escape(district.lower())}\b", lower)), None)


def extract_date(text: str) -> datetime | None:
    match = re.search(r"\b(\d{1,2})[/-](\d{1,2})[/-](\d{4})\b", text or "")
    if not match:
        return None
    try:
        return datetime(int(match.group(3)), int(match.group(2)), int(match.group(1)), tzinfo=timezone.utc)
    except ValueError:
        return None


def index_content(db: Session, content_type: str, content_id: int, title: str, source: str, url: str, text: str, published_at=None, language="en", source_id=None, department=None, district=None, document_type=None, publisher=None, channel=None, parent_content_id=None, timestamp_seconds=None):
    row = db.query(models.ContentIndex).filter_by(content_type=content_type, content_id=content_id).first()
    values = dict(source_id=source_id, parent_content_id=parent_content_id, title=title, source=source, source_url=url, text=text, published_at=published_at, language=language, department=department, district=district, document_type=document_type, publisher=publisher, channel=channel, timestamp_seconds=timestamp_seconds)
    if row:
        for key, value in values.items():
            setattr(row, key, value)
    else:
        db.add(models.ContentIndex(content_type=content_type, content_id=content_id, **values))


def extract_pdf(data: bytes) -> str:
    return "\n".join(extract_pdf_pages(data))


def extract_pdf_pages(data: bytes) -> list[str]:
    with fitz.open(stream=data, filetype="pdf") as pdf:
        return [normalize_marathi_pdf_text(page.get_text("text")) for page in pdf]


def ingest_document(db: Session, *, source: models.Source, title: str, url: str, data: bytes, department=None, category=None, published_at=None):
    digest = sha256(data)
    doc = db.query(models.Document).filter_by(document_url=url).first()
    created = doc is None
    if not doc:
        doc = models.Document(source_id=source.id, title=title, department=department, category=category, document_url=url, source_page=source.base_url, published_date=published_at)
        db.add(doc)
        db.flush()
    else:
        doc.last_seen_at = datetime.now(timezone.utc)
        if published_at and not doc.published_date:
            doc.published_date = published_at
    if db.query(models.DocumentVersion).filter_by(document_id=doc.id, sha256=digest).first():
        return doc, "duplicate"
    STORAGE_PATH.mkdir(parents=True, exist_ok=True)
    path = STORAGE_PATH / f"{doc.id}-{digest[:12]}.pdf"
    path.write_bytes(data)
    with fitz.open(stream=data, filetype="pdf") as pdf:
        raw_pages = [page.get_text("text") for page in pdf]
    pages = [normalize_marathi_pdf_text(page) for page in raw_pages]
    text = "\n".join(pages)
    version = models.DocumentVersion(document_id=doc.id, sha256=digest, file_size=len(data), mime_type="application/pdf", file_path=str(path), raw_extracted_text="\n".join(raw_pages), extracted_text=text, page_count=len(pages))
    db.add(version); db.flush()
    for number, page_text in enumerate(pages, 1):
        db.add(models.DocumentPage(version_id=version.id, page_number=number, text=page_text))
    index_content(db, "government_document", doc.id, title, source.name, url, text, published_at, language=detect_language(text), source_id=source.id, department=department, district=detect_district(f"{title} {text[:5000]}"), document_type=doc.document_type)
    return doc, "created" if created else "versioned"


def repair_legacy_marathi_documents(db: Session) -> int:
    """Normalize existing PDF text and refresh its search index, idempotently."""
    repaired = 0
    for version in db.query(models.DocumentVersion).all():
        original = version.raw_extracted_text or version.extracted_text or ""
        normalized = normalize_marathi_pdf_text(original)
        if normalized == version.extracted_text:
            continue
        if not version.raw_extracted_text:
            version.raw_extracted_text = version.extracted_text or ""
        version.extracted_text = normalized
        for page in version.pages:
            page.text = normalize_marathi_pdf_text(page.text)
        repaired += 1

    if repaired:
        for item in db.query(models.ContentIndex).filter_by(content_type="government_document").all():
            latest = db.query(models.DocumentVersion).filter_by(document_id=item.content_id).order_by(models.DocumentVersion.downloaded_at.desc()).first()
            if latest:
                item.text = latest.extracted_text
                item.language = detect_language(latest.extracted_text)
                item.district = detect_district(f"{item.title} {latest.extracted_text[:5000]}")
    db.commit()
    return repaired


def video_id_from_url(value: str) -> str:
    if re.fullmatch(r"[\w-]{11}", value):
        return value
    parsed = urlparse(value)
    if parsed.hostname in {"youtu.be", "www.youtu.be"}:
        return parsed.path.strip("/").split("/")[0]
    if "/shorts/" in parsed.path:
        return parsed.path.split("/shorts/")[1].split("/")[0]
    return parse_qs(parsed.query).get("v", [""])[0]


def ingest_youtube(db: Session, url: str, language="mr", source: models.Source | None = None):
    video_id = video_id_from_url(url)
    if not video_id:
        raise ValueError("A valid YouTube video URL or ID is required")
    existing = db.query(models.YouTubeVideo).filter_by(video_id=video_id).first()
    if existing:
        if source and not existing.source_id:
            existing.source_id = source.id
            db.commit(); db.refresh(existing)
        ensure_video_segment_index(db, existing)
        return existing
    metadata = {}
    with httpx.Client(timeout=20, headers={"User-Agent": USER_AGENT}) as client:
        response = client.get("https://www.youtube.com/oembed", params={"url": f"https://www.youtube.com/watch?v={video_id}", "format": "json"})
        response.raise_for_status()
        metadata = response.json()
    transcript = []
    transcript_language = language
    ytta = YouTubeTranscriptApi()
    try:
        fetched = ytta.fetch(video_id, languages=[language, "mr", "en", "hi"])
        transcript_language = fetched.language_code
        transcript = [{"text": item.text, "start": item.start, "duration": item.duration} for item in fetched]
    except Exception:
        try:
            transcript_list = ytta.list(video_id)
            try:
                t = transcript_list.find_transcript([language, "mr", "en", "hi"])
            except Exception:
                t = next(iter(transcript_list), None)
            if t:
                fetched = t.fetch()
                transcript_language = t.language_code
                transcript = [{"text": item.text, "start": item.start, "duration": item.duration} for item in fetched]
        except Exception:
            transcript = []

    video = models.YouTubeVideo(source_id=source.id if source else None, video_id=video_id, video_url=f"https://www.youtube.com/watch?v={video_id}", title=metadata.get("title", video_id), channel_name=metadata.get("author_name"), channel_url=metadata.get("author_url"), thumbnail_url=metadata.get("thumbnail_url"), language=language, transcript_available=bool(transcript), transcript_language=transcript_language if transcript else None, transcript_text=" ".join(x["text"] for x in transcript))
    db.add(video)
    db.flush()
    for item in transcript:
        segment = models.YouTubeTranscriptSegment(video_id=video.id, start_seconds=item["start"], duration_seconds=item.get("duration", 0), text=item["text"], language=transcript_language)
        db.add(segment)
    db.commit()
    db.refresh(video)
    ensure_video_segment_index(db, video)
    return video


def ensure_video_segment_index(db: Session, video: models.YouTubeVideo) -> None:
    """Index each real caption segment with contextual window; never synthesize unavailable captions."""
    segments = list(video.segments)
    for i, segment in enumerate(segments):
        window = segments[max(0, i - 3): min(len(segments), i + 4)]
        context_text = " ".join(s.text for s in window)
        district = detect_district(f"{video.title} {context_text}")
        index_content(
            db, "youtube_transcript", segment.id,
            video.title, video.channel_name or "YouTube", video.video_url,
            context_text, published_at=video.published_at, language=segment.language,
            source_id=video.source_id, channel=video.channel_name,
            parent_content_id=video.id, timestamp_seconds=segment.start_seconds,
            district=district
        )
    db.commit()


def backfill_youtube_segment_index(db: Session) -> int:
    segment_count = db.query(models.YouTubeTranscriptSegment).count()
    db.query(models.ContentIndex).filter_by(content_type="youtube_transcript").delete(synchronize_session=False)
    for video in db.query(models.YouTubeVideo).all():
        ensure_video_segment_index(db, video)
    db.commit()
    return segment_count



def extract_mentions(text: str) -> str:
    amounts = re.findall(r"(?:₹|Rs\.?|INR)\s*[\d,.]+\s*(?:crore|lakh|million|billion)?", text, re.I)
    keywords = [word for word in ["tender", "contractor", "PWD", "MMRDA", "municipal corporation", "water resources"] if word.lower() in text.lower()]
    return json.dumps({"amounts": amounts[:20], "keywords": keywords})


def parse_article_html(url: str, html: str):
    soup = BeautifulSoup(html, "html.parser")
    canonical = soup.select_one('link[rel="canonical"]')
    title = (soup.select_one('meta[property="og:title"]') or soup.title)
    title_text = title.get("content") if title and title.name == "meta" else title.get_text(" ", strip=True) if title else url
    description = soup.select_one('meta[name="description"]') or soup.select_one('meta[property="og:description"]')
    image = soup.select_one('meta[property="og:image"]')
    author = soup.select_one('meta[name="author"]')
    published = soup.select_one('meta[property="article:published_time"]') or soup.select_one('time[datetime]')
    language = (soup.html.get("lang", "en") if soup.html else "en").split("-")[0]
    article = soup.select_one("article") or soup.select_one("main") or soup.body
    for unwanted in article.select("script,style,nav,footer,aside,form") if article else []:
        unwanted.decompose()
    text = "\n".join(p.get_text(" ", strip=True) for p in article.select("p") if len(p.get_text(" ", strip=True)) > 30) if article else ""
    published_value = published.get("content") or published.get("datetime") if published else None
    try:
        from dateutil.parser import parse as parse_date
        published_value = parse_date(published_value) if published_value else None
    except (ValueError, TypeError):
        published_value = None
    return {"title": title_text, "canonical_url": canonical.get("href") if canonical else url, "description": description.get("content") if description else None, "image_url": image.get("content") if image else None, "author": author.get("content") if author else None, "article_text": text, "published_at": published_value, "language": language}
