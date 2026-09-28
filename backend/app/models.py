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


# ==========================================
# RTI Intelligence Layer Models (Phase 1)
# ==========================================

class DocumentChunk(Base):
    __tablename__ = "document_chunks"
    __table_args__ = (UniqueConstraint("document_id", "document_version_id", "page_number", "chunk_index", name="uq_chunk_pos"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id"), index=True)
    document_version_id: Mapped[int | None] = mapped_column(ForeignKey("document_versions.id"), index=True)
    page_number: Mapped[int | None] = mapped_column(Integer, index=True)
    chunk_index: Mapped[int] = mapped_column(Integer, default=0)
    text: Mapped[str] = mapped_column(Text)
    language: Mapped[str] = mapped_column(String(20), default="mr")
    token_count: Mapped[int] = mapped_column(Integer, default=0)
    embedding_json: Mapped[str | None] = mapped_column(Text)  # Vector fallback for SQLite/Postgres
    metadata_json: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class Investigation(Base):
    __tablename__ = "investigations"
    id: Mapped[int] = mapped_column(primary_key=True)
    query: Mapped[str] = mapped_column(String(1000))
    normalized_query: Mapped[str] = mapped_column(String(1000))
    status: Mapped[str] = mapped_column(String(40), default="pending", index=True)  # pending, planning, in_progress, completed, failed
    user_id: Mapped[str | None] = mapped_column(String(100), index=True)
    summary: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, onupdate=now)
    steps: Mapped[list["InvestigationStep"]] = relationship(back_populates="investigation", cascade="all, delete-orphan", order_by="InvestigationStep.id")
    claims: Mapped[list["EvidenceClaim"]] = relationship(back_populates="investigation", cascade="all, delete-orphan")
    gaps: Mapped[list["EvidenceGap"]] = relationship(back_populates="investigation", cascade="all, delete-orphan")
    contradictions: Mapped[list["Contradiction"]] = relationship(back_populates="investigation", cascade="all, delete-orphan")
    rti_applications: Mapped[list["RTIApplication"]] = relationship(back_populates="investigation", cascade="all, delete-orphan")
    project_events: Mapped[list["ProjectEvent"]] = relationship(back_populates="investigation", cascade="all, delete-orphan")
    financial_events: Mapped[list["FinancialEvent"]] = relationship(back_populates="investigation", cascade="all, delete-orphan")


class InvestigationStep(Base):
    __tablename__ = "investigation_steps"
    id: Mapped[int] = mapped_column(primary_key=True)
    investigation_id: Mapped[int] = mapped_column(ForeignKey("investigations.id"), index=True)
    step_type: Mapped[str] = mapped_column(String(80), index=True)
    agent_name: Mapped[str] = mapped_column(String(80), index=True)
    status: Mapped[str] = mapped_column(String(40), default="queued", index=True)  # queued, running, completed, failed
    input_json: Mapped[str | None] = mapped_column(Text)
    output_json: Mapped[str | None] = mapped_column(Text)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    error_message: Mapped[str | None] = mapped_column(Text)
    investigation: Mapped["Investigation"] = relationship(back_populates="steps")


class EvidenceClaim(Base):
    __tablename__ = "evidence_claims"
    id: Mapped[int] = mapped_column(primary_key=True)
    investigation_id: Mapped[int] = mapped_column(ForeignKey("investigations.id"), index=True)
    subject_entity_type: Mapped[str] = mapped_column(String(80), index=True)
    subject_entity_id: Mapped[str | None] = mapped_column(String(120), index=True)
    subject_text: Mapped[str] = mapped_column(String(600))
    predicate: Mapped[str] = mapped_column(String(120), index=True)
    value_text: Mapped[str] = mapped_column(Text)
    normalized_value_json: Mapped[str | None] = mapped_column(Text)
    valid_from: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    valid_to: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(40), default="PROPOSED", index=True)  # PROPOSED, SUPPORTED, VERIFIED, PARTIAL, CONTRADICTED, MISSING, STALE
    confidence_label: Mapped[str] = mapped_column(String(40), default="MEDIUM")  # HIGH, MEDIUM, LOW
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    investigation: Mapped["Investigation"] = relationship(back_populates="claims")
    sources: Mapped[list["ClaimSource"]] = relationship(back_populates="claim", cascade="all, delete-orphan")


class ClaimSource(Base):
    __tablename__ = "claim_sources"
    id: Mapped[int] = mapped_column(primary_key=True)
    claim_id: Mapped[int] = mapped_column(ForeignKey("evidence_claims.id"), index=True)
    document_id: Mapped[int | None] = mapped_column(ForeignKey("documents.id"), index=True)
    document_version_id: Mapped[int | None] = mapped_column(ForeignKey("document_versions.id"), index=True)
    page_number: Mapped[int | None] = mapped_column(Integer)
    timestamp_seconds: Mapped[float | None] = mapped_column(Float)
    source_url: Mapped[str] = mapped_column(String(1200))
    quoted_excerpt: Mapped[str] = mapped_column(Text)
    retrieval_score: Mapped[float | None] = mapped_column(Float)
    source_authority_score: Mapped[float | None] = mapped_column(Float)
    claim: Mapped["EvidenceClaim"] = relationship(back_populates="sources")


class EvidenceGap(Base):
    __tablename__ = "evidence_gaps"
    id: Mapped[int] = mapped_column(primary_key=True)
    investigation_id: Mapped[int] = mapped_column(ForeignKey("investigations.id"), index=True)
    project_id: Mapped[str | None] = mapped_column(String(120), index=True)
    gap_type: Mapped[str] = mapped_column(String(80), index=True)  # MISSING_COMPLETION_CERT, MISSING_EXPENDITURE, MISSING_WORK_ORDER, UNMATCHED_TENDER
    expected_record_type: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(40), default="IDENTIFIED", index=True)  # IDENTIFIED, RTI_DRAFTED, RTI_SUBMITTED, RESOLVED, UNRESOLVED
    responsible_authority_id: Mapped[str | None] = mapped_column(String(240))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    investigation: Mapped["Investigation"] = relationship(back_populates="gaps")


class Contradiction(Base):
    __tablename__ = "contradictions"
    id: Mapped[int] = mapped_column(primary_key=True)
    investigation_id: Mapped[int] = mapped_column(ForeignKey("investigations.id"), index=True)
    claim_a_id: Mapped[int] = mapped_column(ForeignKey("evidence_claims.id"), index=True)
    claim_b_id: Mapped[int] = mapped_column(ForeignKey("evidence_claims.id"), index=True)
    contradiction_type: Mapped[str] = mapped_column(String(80), index=True)  # AMOUNT_MISMATCH, DATE_ANACHRONISM, AUTHORITY_CONFLICT, STATUS_MISMATCH
    resolution_status: Mapped[str] = mapped_column(String(40), default="DETECTED", index=True)  # DETECTED, RESOLVED, UNRESOLVED
    resolution_note: Mapped[str | None] = mapped_column(Text)
    investigation: Mapped["Investigation"] = relationship(back_populates="contradictions")


class ProjectEvent(Base):
    __tablename__ = "project_events"
    id: Mapped[int] = mapped_column(primary_key=True)
    investigation_id: Mapped[int | None] = mapped_column(ForeignKey("investigations.id"), index=True)
    project_id: Mapped[str] = mapped_column(String(120), index=True)
    event_type: Mapped[str] = mapped_column(String(80), index=True)  # ANNOUNCED, SANCTION, TENDER_ISSUED, WORK_ORDER, COMMENCED, DELAYED, COMPLETED
    event_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    value_json: Mapped[str | None] = mapped_column(Text)
    source_claim_id: Mapped[int | None] = mapped_column(ForeignKey("evidence_claims.id"), index=True)
    investigation: Mapped["Investigation"] = relationship(back_populates="project_events")


class FinancialEvent(Base):
    __tablename__ = "financial_events"
    id: Mapped[int] = mapped_column(primary_key=True)
    investigation_id: Mapped[int | None] = mapped_column(ForeignKey("investigations.id"), index=True)
    project_id: Mapped[str] = mapped_column(String(120), index=True)
    event_type: Mapped[str] = mapped_column(String(80), index=True)  # SANCTION, ESTIMATE, AWARD, RELEASE, PAYMENT, EXPENDITURE, COST_ESCALATION
    amount: Mapped[float] = mapped_column(Float, index=True)
    currency: Mapped[str] = mapped_column(String(10), default="INR")
    event_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    source_claim_id: Mapped[int | None] = mapped_column(ForeignKey("evidence_claims.id"), index=True)
    investigation: Mapped["Investigation"] = relationship(back_populates="financial_events")


class RTIApplication(Base):
    __tablename__ = "rti_applications"
    id: Mapped[int] = mapped_column(primary_key=True)
    investigation_id: Mapped[int] = mapped_column(ForeignKey("investigations.id"), index=True)
    authority_name: Mapped[str] = mapped_column(String(300), index=True)
    authority_id: Mapped[str | None] = mapped_column(String(120))
    subject: Mapped[str] = mapped_column(String(600))
    draft_text: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(40), default="DRAFT", index=True)  # DRAFT, FINALIZED, SUBMITTED, REPLIED, APPEALED
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    investigation: Mapped["Investigation"] = relationship(back_populates="rti_applications")
    questions: Mapped[list["RTIQuestion"]] = relationship(back_populates="application", cascade="all, delete-orphan", order_by="RTIQuestion.sequence_no")
    responses: Mapped[list["RTIResponse"]] = relationship(back_populates="application", cascade="all, delete-orphan")


class RTIQuestion(Base):
    __tablename__ = "rti_questions"
    id: Mapped[int] = mapped_column(primary_key=True)
    rti_application_id: Mapped[int] = mapped_column(ForeignKey("rti_applications.id"), index=True)
    sequence_no: Mapped[int] = mapped_column(Integer, default=1)
    gap_id: Mapped[int | None] = mapped_column(ForeignKey("evidence_gaps.id"), index=True)
    question_text: Mapped[str] = mapped_column(Text)
    requested_record_type: Mapped[str] = mapped_column(String(120))
    application: Mapped["RTIApplication"] = relationship(back_populates="questions")


class RTIResponse(Base):
    __tablename__ = "rti_responses"
    id: Mapped[int] = mapped_column(primary_key=True)
    rti_application_id: Mapped[int] = mapped_column(ForeignKey("rti_applications.id"), index=True)
    document_id: Mapped[int | None] = mapped_column(ForeignKey("documents.id"), index=True)
    received_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    raw_text: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    application: Mapped["RTIApplication"] = relationship(back_populates="responses")
    items: Mapped[list["RTIResponseItem"]] = relationship(back_populates="response", cascade="all, delete-orphan")


class RTIResponseItem(Base):
    __tablename__ = "rti_response_items"
    id: Mapped[int] = mapped_column(primary_key=True)
    rti_response_id: Mapped[int] = mapped_column(ForeignKey("rti_responses.id"), index=True)
    rti_question_id: Mapped[int | None] = mapped_column(ForeignKey("rti_questions.id"), index=True)
    classification: Mapped[str] = mapped_column(String(40), default="ANSWERED", index=True)  # ANSWERED, PARTIAL, NOT_ANSWERED, DOCUMENT_ATTACHED, TRANSFERRED, EXEMPTION_CITED, UNCLEAR
    answer_text: Mapped[str] = mapped_column(Text)
    evidence_json: Mapped[str | None] = mapped_column(Text)
    response: Mapped["RTIResponse"] = relationship(back_populates="items")

