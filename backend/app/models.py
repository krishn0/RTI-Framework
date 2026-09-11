from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


def now():
    return datetime.now(timezone.utc)


class Source(Base):
    __tablename__ = "sources"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(240))
    short_name: Mapped[str | None] = mapped_column(String(100))
    category: Mapped[str | None] = mapped_column(String(50), index=True)
    evidence_tier: Mapped[int] = mapped_column(Integer, default=3)
    languages: Mapped[str | None] = mapped_column(Text)
    tags: Mapped[str | None] = mapped_column(Text)
    base_url: Mapped[str] = mapped_column(String(1000), unique=True)
    source_type: Mapped[str] = mapped_column(String(50), index=True)
    input_kind: Mapped[str] = mapped_column(String(40), default="website")
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    crawl_delay: Mapped[float] = mapped_column(Float, default=2)
    frequency: Mapped[str] = mapped_column(String(40), default="daily")
    requires_javascript: Mapped[bool] = mapped_column(Boolean, default=False)
    health: Mapped[str] = mapped_column(String(30), default="healthy")
    last_run_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    next_run_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, onupdate=now)


class ScraperRun(Base):
    __tablename__ = "scraper_runs"
    id: Mapped[int] = mapped_column(primary_key=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id"), index=True)
    status: Mapped[str] = mapped_column(String(30), default="queued", index=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    items_found: Mapped[int] = mapped_column(Integer, default=0)
    items_created: Mapped[int] = mapped_column(Integer, default=0)
    items_updated: Mapped[int] = mapped_column(Integer, default=0)
    duplicates: Mapped[int] = mapped_column(Integer, default=0)
    pages_scanned: Mapped[int] = mapped_column(Integer, default=0)
    errors: Mapped[int] = mapped_column(Integer, default=0)
    duration_ms: Mapped[int | None] = mapped_column(Integer)
    source: Mapped["Source"] = relationship()


class ScraperLog(Base):
    __tablename__ = "scraper_logs"
    id: Mapped[int] = mapped_column(primary_key=True)
    run_id: Mapped[int | None] = mapped_column(ForeignKey("scraper_runs.id"), index=True)
    source_id: Mapped[int | None] = mapped_column(ForeignKey("sources.id"), index=True)
    level: Mapped[str] = mapped_column(String(20), index=True)
    message: Mapped[str] = mapped_column(Text)
    context: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, index=True)


class Document(Base):
    __tablename__ = "documents"
    id: Mapped[int] = mapped_column(primary_key=True)
    source_id: Mapped[int | None] = mapped_column(ForeignKey("sources.id"), index=True)
    title: Mapped[str] = mapped_column(String(600), index=True)
    department: Mapped[str | None] = mapped_column(String(240), index=True)
    category: Mapped[str | None] = mapped_column(String(120), index=True)
    document_type: Mapped[str] = mapped_column(String(80), default="document")
    source_page: Mapped[str | None] = mapped_column(String(1200))
    document_url: Mapped[str] = mapped_column(String(1200), unique=True)
    published_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    first_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    processing_status: Mapped[str] = mapped_column(String(40), default="processed", index=True)
    versions: Mapped[list["DocumentVersion"]] = relationship(back_populates="document", cascade="all, delete-orphan", order_by="desc(DocumentVersion.downloaded_at)")


class DocumentVersion(Base):
    __tablename__ = "document_versions"
    __table_args__ = (UniqueConstraint("document_id", "sha256"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id"), index=True)
    sha256: Mapped[str] = mapped_column(String(64), index=True)
    file_size: Mapped[int] = mapped_column(Integer)
    mime_type: Mapped[str] = mapped_column(String(120))
    file_path: Mapped[str] = mapped_column(String(1000))
    raw_extracted_text: Mapped[str] = mapped_column(Text, default="")
    extracted_text: Mapped[str] = mapped_column(Text, default="")
    page_count: Mapped[int] = mapped_column(Integer, default=0)
    downloaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    document: Mapped["Document"] = relationship(back_populates="versions")
    pages: Mapped[list["DocumentPage"]] = relationship(back_populates="version", cascade="all, delete-orphan", order_by="DocumentPage.page_number")


class DocumentPage(Base):
    __tablename__ = "document_pages"
    __table_args__ = (UniqueConstraint("version_id", "page_number"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    version_id: Mapped[int] = mapped_column(ForeignKey("document_versions.id"), index=True)
    page_number: Mapped[int] = mapped_column(Integer)
    text: Mapped[str] = mapped_column(Text, default="")
    version: Mapped["DocumentVersion"] = relationship(back_populates="pages")


class YouTubeVideo(Base):
    __tablename__ = "youtube_videos"
    id: Mapped[int] = mapped_column(primary_key=True)
    source_id: Mapped[int | None] = mapped_column(ForeignKey("sources.id"), index=True)
    video_id: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    video_url: Mapped[str] = mapped_column(String(1000))
    title: Mapped[str] = mapped_column(String(600), index=True)
    channel_name: Mapped[str | None] = mapped_column(String(240))
    channel_url: Mapped[str | None] = mapped_column(String(1000))
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    duration: Mapped[int | None] = mapped_column(Integer)
    description: Mapped[str | None] = mapped_column(Text)
    thumbnail_url: Mapped[str | None] = mapped_column(String(1000))
    language: Mapped[str] = mapped_column(String(20), default="mr")
    transcript_available: Mapped[bool] = mapped_column(Boolean, default=False)
    transcript_language: Mapped[str | None] = mapped_column(String(20))
    transcript_text: Mapped[str | None] = mapped_column(Text)
    scraped_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    segments: Mapped[list["YouTubeTranscriptSegment"]] = relationship(back_populates="video", cascade="all, delete-orphan", order_by="YouTubeTranscriptSegment.start_seconds")


class YouTubeTranscriptSegment(Base):
    __tablename__ = "youtube_transcript_segments"
    id: Mapped[int] = mapped_column(primary_key=True)
    video_id: Mapped[int] = mapped_column(ForeignKey("youtube_videos.id"), index=True)
    start_seconds: Mapped[float] = mapped_column(Float)
    duration_seconds: Mapped[float] = mapped_column(Float)
    text: Mapped[str] = mapped_column(Text)
    language: Mapped[str] = mapped_column(String(20), default="mr")
    video: Mapped["YouTubeVideo"] = relationship(back_populates="segments")


class NewsArticle(Base):
    __tablename__ = "news_articles"
    id: Mapped[int] = mapped_column(primary_key=True)
    source_id: Mapped[int | None] = mapped_column(ForeignKey("sources.id"), index=True)
    publisher: Mapped[str] = mapped_column(String(240), index=True)
    title: Mapped[str] = mapped_column(String(600), index=True)
    article_url: Mapped[str] = mapped_column(String(1200), unique=True)
    canonical_url: Mapped[str | None] = mapped_column(String(1200), unique=True)
    author: Mapped[str | None] = mapped_column(String(240))
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    description: Mapped[str | None] = mapped_column(Text)
    article_text: Mapped[str] = mapped_column(Text)
    language: Mapped[str] = mapped_column(String(20), default="en")
    image_url: Mapped[str | None] = mapped_column(String(1200))
    category: Mapped[str | None] = mapped_column(String(120))
    location: Mapped[str | None] = mapped_column(String(120), index=True)
    scraped_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    sha256: Mapped[str] = mapped_column(String(64), index=True)
    mentions: Mapped[str | None] = mapped_column(Text)


class ContentIndex(Base):
    __tablename__ = "content_index"
    __table_args__ = (UniqueConstraint("content_type", "content_id"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    content_type: Mapped[str] = mapped_column(String(40), index=True)
    content_id: Mapped[int] = mapped_column(Integer, index=True)
    parent_content_id: Mapped[int | None] = mapped_column(Integer, index=True)
    source_id: Mapped[int | None] = mapped_column(ForeignKey("sources.id"), index=True)
    title: Mapped[str] = mapped_column(String(600), index=True)
    source: Mapped[str] = mapped_column(String(240))
    source_url: Mapped[str] = mapped_column(String(1200))
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    language: Mapped[str] = mapped_column(String(20), default="en")
    department: Mapped[str | None] = mapped_column(String(240), index=True)
    district: Mapped[str | None] = mapped_column(String(120), index=True)
    document_type: Mapped[str | None] = mapped_column(String(80), index=True)
    publisher: Mapped[str | None] = mapped_column(String(240), index=True)
    channel: Mapped[str | None] = mapped_column(String(240), index=True)
    timestamp_seconds: Mapped[float | None] = mapped_column(Float)
    text: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
