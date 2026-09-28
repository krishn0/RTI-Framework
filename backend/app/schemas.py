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


# ==========================================
# RTI Intelligence Schemas (Phase 1)
# ==========================================

class InvestigationCreate(BaseModel):
    query: str = Field(min_length=3, max_length=1000)
    user_id: str | None = None


class ClaimSourceOut(ORMModel):
    id: int
    claim_id: int
    document_id: int | None
    document_version_id: int | None
    page_number: int | None
    timestamp_seconds: float | None
    source_url: str
    quoted_excerpt: str
    retrieval_score: float | None
    source_authority_score: float | None


class EvidenceClaimOut(ORMModel):
    id: int
    investigation_id: int
    subject_entity_type: str
    subject_entity_id: str | None
    subject_text: str
    predicate: str
    value_text: str
    normalized_value_json: str | None
    valid_from: datetime | None
    valid_to: datetime | None
    status: str
    confidence_label: str
    created_at: datetime
    sources: list[ClaimSourceOut] = []


class EvidenceGapOut(ORMModel):
    id: int
    investigation_id: int
    project_id: str | None
    gap_type: str
    expected_record_type: str
    description: str
    status: str
    responsible_authority_id: str | None
    created_at: datetime


class ContradictionOut(ORMModel):
    id: int
    investigation_id: int
    claim_a_id: int
    claim_b_id: int
    contradiction_type: str
    resolution_status: str
    resolution_note: str | None


class InvestigationStepOut(ORMModel):
    id: int
    investigation_id: int
    step_type: str
    agent_name: str
    status: str
    input_json: str | None
    output_json: str | None
    started_at: datetime | None
    finished_at: datetime | None
    error_message: str | None


class RTIQuestionOut(ORMModel):
    id: int
    rti_application_id: int
    sequence_no: int
    gap_id: int | None
    question_text: str
    requested_record_type: str


class RTIResponseItemOut(ORMModel):
    id: int
    rti_response_id: int
    rti_question_id: int | None
    classification: str
    answer_text: str
    evidence_json: str | None


class RTIResponseCreate(BaseModel):
    raw_text: str
    document_id: int | None = None
    received_date: datetime | None = None


class RTIResponseOut(ORMModel):
    id: int
    rti_application_id: int
    document_id: int | None
    received_date: datetime | None
    raw_text: str
    created_at: datetime
    items: list[RTIResponseItemOut] = []


class RTIApplicationOut(ORMModel):
    id: int
    investigation_id: int
    authority_name: str
    authority_id: str | None
    subject: str
    draft_text: str
    status: str
    created_at: datetime
    questions: list[RTIQuestionOut] = []
    responses: list[RTIResponseOut] = []


class ProjectEventOut(ORMModel):
    id: int
    project_id: str
    event_type: str
    event_date: datetime | None = None
    value_json: str | None = None
    source_claim_id: int | None = None


class FinancialEventOut(ORMModel):
    id: int
    project_id: str
    event_type: str
    amount: float
    currency: str = "INR"
    event_date: datetime | None = None
    source_claim_id: int | None = None


class InvestigationDetailOut(ORMModel):
    id: int
    query: str
    normalized_query: str
    status: str
    user_id: str | None
    summary: str | None
    created_at: datetime
    updated_at: datetime
    steps: list[InvestigationStepOut] = []
    claims: list[EvidenceClaimOut] = []
    gaps: list[EvidenceGapOut] = []
    contradictions: list[ContradictionOut] = []
    rti_applications: list[RTIApplicationOut] = []
    project_events: list[ProjectEventOut] = []
    financial_events: list[FinancialEventOut] = []



class DocumentChunkOut(ORMModel):
    id: int
    document_id: int
    document_version_id: int | None
    page_number: int | None
    chunk_index: int
    text: str
    language: str
    token_count: int
    created_at: datetime


class EvidenceItemOut(BaseModel):
    chunk_id: int | None = None
    document_id: int | None = None
    page_number: int | None = None
    text: str
    source_title: str
    content_type: str
    semantic_score: float
    keyword_score: float
    final_score: float
    provenance: dict[str, Any] = {}


class EvidencePackOut(BaseModel):
    query: str
    normalized_query: str
    filters: dict[str, Any] = {}
    evidence: list[EvidenceItemOut] = []
    total_found: int = 0
    generated_at: str


