from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field
from pydantic import HttpUrl


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class SourceOut(ORMModel):
    id: int
    name: str
    short_name: str | None
    category: str | None
    evidence_tier: int
    languages: str | None
    tags: str | None
    base_url: str
    source_type: str
    input_kind: str
    enabled: bool
    crawl_delay: float
    frequency: str
    requires_javascript: bool
    health: str
    last_run_at: datetime | None
    next_run_at: datetime | None


class SourceCreate(BaseModel):
    name: str = Field(min_length=2, max_length=240)
    short_name: str | None = None
    category: str | None = None
    evidence_tier: int = Field(default=3, ge=1, le=3)
    languages: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    base_url: HttpUrl
    source_type: str
    input_kind: str = "website"
    enabled: bool = True
    crawl_delay: float = Field(default=2, ge=0.5, le=120)
    frequency: str = "daily"
    requires_javascript: bool = False


class SourceAnalyze(BaseModel):
    url: HttpUrl


class PageTextOut(ORMModel):
    page_number: int
    text: str


class VersionOut(ORMModel):
    id: int
    sha256: str
    file_size: int
    mime_type: str
    file_path: str
    extracted_text: str
    page_count: int
    downloaded_at: datetime
    pages: list[PageTextOut] = []


class DocumentOut(ORMModel):
    id: int
    source_id: int | None
    title: str
    department: str | None
    category: str | None
    document_type: str
    source_page: str | None
    document_url: str
    published_date: datetime | None
    first_seen_at: datetime
    last_seen_at: datetime
    processing_status: str
    versions: list[VersionOut] = []


class SegmentOut(ORMModel):
    id: int
    start_seconds: float
    duration_seconds: float
    text: str
    language: str


class VideoOut(ORMModel):
    id: int
    video_id: str
    video_url: str
    title: str
    channel_name: str | None
    channel_url: str | None
    published_at: datetime | None
    duration: int | None
    description: str | None
    thumbnail_url: str | None
    language: str
    transcript_available: bool
    transcript_language: str | None
    transcript_text: str | None
    scraped_at: datetime
    segments: list[SegmentOut] = []


class NewsOut(ORMModel):
    id: int
    publisher: str
    title: str
    article_url: str
    canonical_url: str | None
    author: str | None
    published_at: datetime | None
    description: str | None
    article_text: str
    language: str
    image_url: str | None
    category: str | None
    location: str | None
    scraped_at: datetime
    last_seen_at: datetime
    sha256: str
    mentions: str | None


class YouTubeRequest(BaseModel):
    url: str
    language: str = "mr"


class RunOut(ORMModel):
    id: int
    source_id: int
    status: str
    started_at: datetime | None
    finished_at: datetime | None
    items_found: int
    items_created: int
    items_updated: int
    duplicates: int
    pages_scanned: int
    errors: int
    duration_ms: int | None
    source: SourceOut


class LogOut(ORMModel):
    id: int
    run_id: int | None
    source_id: int | None
    level: str
    message: str
    context: str | None
    created_at: datetime


class Page(BaseModel):
    items: list[Any]
    total: int
    page: int
    page_size: int
