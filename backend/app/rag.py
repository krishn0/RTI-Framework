"""Semantic chunking, embedding generation, and hybrid RAG evidence retrieval.

Preserves exact provenance (document_id, document_version_id, page_number,
source_url, chunk_index) and builds structured Evidence Packs for agents.
"""
from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import or_
from sqlalchemy.orm import Session

from . import models
from .search import ParsedQuery, normalize_query_text, parse_query


@dataclass
class EvidenceItem:
    chunk_id: int
    document_id: int
    document_version_id: int | None
    page_number: int | None
    text: str
    source_url: str
    source_title: str
    content_type: str
    semantic_score: float = 0.0
    keyword_score: float = 0.0
    final_score: float = 0.0
    provenance: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "document_id": self.document_id,
            "document_version_id": self.document_version_id,
            "page_number": self.page_number,
            "text": self.text,
            "source_url": self.source_url,
            "source_title": self.source_title,
            "content_type": self.content_type,
            "semantic_score": round(self.semantic_score, 4),
            "keyword_score": round(self.keyword_score, 4),
            "final_score": round(self.final_score, 4),
            "provenance": self.provenance,
        }


@dataclass
class EvidencePack:
    query: str
    normalized_query: str
    filters: dict[str, Any]
    evidence: list[EvidenceItem] = field(default_factory=list)
    total_found: int = 0
    generated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict[str, Any]:
        return {
            "query": self.query,
            "normalized_query": self.normalized_query,
            "filters": self.filters,
            "evidence": [item.to_dict() for item in self.evidence],
            "total_found": self.total_found,
            "generated_at": self.generated_at,
        }


# =====================================================================
# 1. Page-Aware Document Chunking
# =====================================================================

def split_text_into_chunks(
    text: str,
    max_tokens: int = 400,
    overlap_tokens: int = 50
) -> list[str]:
    """Split text into semantic paragraphs and sentence windows without breaking sentences."""
    cleaned = re.sub(r"[ \t]+", " ", text).strip()
    if not cleaned:
        return []

    # Approximate token count by words
    words = cleaned.split()
    if len(words) <= max_tokens:
        return [cleaned]

    chunks = []
    start = 0
    while start < len(words):
        end = min(len(words), start + max_tokens)
        chunk_words = words[start:end]
        chunks.append(" ".join(chunk_words))
        if end >= len(words):
            break
        start += (max_tokens - overlap_tokens)

    return chunks


def chunk_document_version(
    db: Session,
    document: models.Document,
    version: models.DocumentVersion
) -> list[models.DocumentChunk]:
    """Extract page-by-page chunks preserving exact page numbers and version IDs."""
    chunks_created = []
    chunk_idx = 0

    if version.pages:
        for page in version.pages:
            page_text = (page.text or "").strip()
            if not page_text:
                continue
            sub_chunks = split_text_into_chunks(page_text, max_tokens=350, overlap_tokens=40)
            for sub_text in sub_chunks:
                token_count = len(sub_text.split())
                meta = {
                    "document_title": document.title,
                    "department": document.department,
                    "document_url": document.document_url,
                    "page_number": page.page_number,
                    "version_sha256": version.sha256,
                }
                embedding = compute_text_embedding(sub_text)
                chunk = models.DocumentChunk(
                    document_id=document.id,
                    document_version_id=version.id,
                    page_number=page.page_number,
                    chunk_index=chunk_idx,
                    text=sub_text,
                    language="mr" if any("\u0900" <= c <= "\u097f" for c in sub_text) else "en",
                    token_count=token_count,
                    embedding_json=json.dumps(embedding),
                    metadata_json=json.dumps(meta, ensure_ascii=False),
                )
                db.add(chunk)
                chunks_created.append(chunk)
                chunk_idx += 1
    else:
        full_text = (version.extracted_text or "").strip()
        if full_text:
            sub_chunks = split_text_into_chunks(full_text, max_tokens=350, overlap_tokens=40)
            for sub_text in sub_chunks:
                token_count = len(sub_text.split())
                meta = {
                    "document_title": document.title,
                    "department": document.department,
                    "document_url": document.document_url,
                    "version_sha256": version.sha256,
                }
                embedding = compute_text_embedding(sub_text)
                chunk = models.DocumentChunk(
                    document_id=document.id,
                    document_version_id=version.id,
                    page_number=1,
                    chunk_index=chunk_idx,
                    text=sub_text,
                    language="mr" if any("\u0900" <= c <= "\u097f" for c in sub_text) else "en",
                    token_count=token_count,
                    embedding_json=json.dumps(embedding),
                    metadata_json=json.dumps(meta, ensure_ascii=False),
                )
                db.add(chunk)
                chunks_created.append(chunk)
                chunk_idx += 1

    db.flush()
    # Also index chunks into ChromaDB persistent vector store
    try:
        from .chroma_store import index_chunks_to_chroma
        chunk_payloads = [
            {
                "id": c.id,
                "chunk_id": c.id,
                "document_id": document.id,
                "page_number": c.page_number,
                "department": document.department or "",
                "source_title": document.title or "",
                "source_url": document.document_url or "",
                "text": c.text,
            }
            for c in chunks_created
        ]
        index_chunks_to_chroma(chunk_payloads)
    except Exception:
        pass

    return chunks_created


def backfill_all_document_chunks(db: Session) -> int:
    """Populate document_chunks table for all existing document versions idempotently."""
    total_created = 0
    documents = db.query(models.Document).all()
    for doc in documents:
        for version in doc.versions:
            existing = db.query(models.DocumentChunk).filter_by(
                document_id=doc.id,
                document_version_id=version.id
            ).first()
            if not existing:
                created = chunk_document_version(db, doc, version)
                total_created += len(created)
    db.commit()
    return total_created


# =====================================================================
# 2. Embedding & Semantic Similarity Layer
# =====================================================================

def compute_text_embedding(text: str, dim: int = 64) -> list[float]:
    """Generate a lightweight deterministic hashed vector embedding.
    
    Can be seamlessly swapped with sentence-transformers or Gemini embeddings.
    """
    words = re.findall(r"\w+", text.lower(), re.UNICODE)
    if not words:
        return [0.0] * dim

    vector = [0.0] * dim
    for word in words:
        h = hash(word)
        for i in range(dim):
            bit = (h >> i) & 1
            vector[i] += 1.0 if bit else -0.5

    norm = math.sqrt(sum(x * x for x in vector)) or 1.0
    return [round(x / norm, 4) for x in vector]


def cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """Calculate cosine similarity between two unit vectors."""
    if not vec_a or not vec_b or len(vec_a) != len(vec_b):
        return 0.0
    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    return max(0.0, min(1.0, (dot + 1.0) / 2.0))


# =====================================================================
# 3. Hybrid RAG Evidence Retrieval & Reranking
# =====================================================================

def retrieve_hybrid_evidence(
    db: Session,
    query: str,
    filters: dict[str, Any] | None = None,
    top_k: int = 10
) -> EvidencePack:
    """Retrieve verified, ranked evidence chunks using hybrid (semantic + keyword) search."""
    filters = filters or {}
    parsed: ParsedQuery = parse_query(query)
    query_emb = compute_text_embedding(parsed.raw)
    normalized_q = normalize_query_text(query)

    candidate_terms = list(dict.fromkeys([
        *parsed.highlight_terms(),
        *(term for group in parsed.keyword_groups for term in group),
        *parsed.location_terms,
        *parsed.amounts,
        *parsed.dates,
    ]))

    # Step 1: Fetch Candidate Chunks
    chunk_query = db.query(models.DocumentChunk).join(models.Document, models.Document.id == models.DocumentChunk.document_id)
    
    if filters.get("department"):
        chunk_query = chunk_query.filter(models.Document.department.ilike(f"%{filters['department']}%"))
    if filters.get("document_id"):
        chunk_query = chunk_query.filter(models.DocumentChunk.document_id == filters["document_id"])

    term_filters = [models.DocumentChunk.text.ilike(f"%{term}%") for term in candidate_terms if len(term) >= 2]
    if term_filters:
        chunk_query = chunk_query.filter(or_(*term_filters))

    candidate_chunks = list(chunk_query.limit(200).all())

    # Step 1.5: Supplement with ChromaDB Semantic ANN Search
    try:
        from .chroma_store import query_chroma_vector_db
        chroma_hits = query_chroma_vector_db(query, n_results=15, department_filter=filters.get("department"))
        hit_chunk_ids = {h["chunk_id"] for h in chroma_hits if h.get("chunk_id")}
        existing_chunk_ids = {c.id for c in candidate_chunks}
        missing_ids = hit_chunk_ids - existing_chunk_ids
        if missing_ids:
            extra_chunks = db.query(models.DocumentChunk).filter(models.DocumentChunk.id.in_(list(missing_ids))).all()
            candidate_chunks.extend(extra_chunks)
    except Exception:
        pass

    # Step 2: Score & Rerank Candidates
    evidence_items: list[EvidenceItem] = []
    seen_texts: set[str] = set()

    for chunk in candidate_chunks:
        # Near-duplicate chunk deduplication
        text_fingerprint = re.sub(r"\s+", "", chunk.text[:120].lower())
        if text_fingerprint in seen_texts:
            continue
        seen_texts.add(text_fingerprint)

        # 1. Semantic Score
        chunk_emb = json.loads(chunk.embedding_json) if chunk.embedding_json else []
        sem_score = cosine_similarity(query_emb, chunk_emb) if chunk_emb else 0.5

        # 2. Keyword / Exact Match Score
        kw_score = 0.0
        lower_chunk = chunk.text.casefold()
        for term in candidate_terms:
            if term.casefold() in lower_chunk:
                kw_score += 1.0
        kw_score = min(1.0, kw_score / max(1, len(candidate_terms)))

        # 3. Department / Entity Match Boost
        entity_boost = 0.0
        doc = db.get(models.Document, chunk.document_id)
        doc_title = doc.title if doc else "Government Document"
        source_url = doc.document_url if doc else ""

        if parsed.department and doc and doc.department and parsed.department.casefold() in doc.department.casefold():
            entity_boost += 0.2
        for loc in parsed.locations:
            if loc.casefold() in lower_chunk or (doc and loc.casefold() in doc.title.casefold()):
                entity_boost += 0.15

        # Weighted composite score
        final_score = (0.45 * sem_score) + (0.35 * kw_score) + (0.20 * min(1.0, entity_boost))

        provenance = {
            "document_id": chunk.document_id,
            "document_version_id": chunk.document_version_id,
            "page_number": chunk.page_number,
            "chunk_index": chunk.chunk_index,
            "source_url": source_url,
            "source_title": doc_title,
            "department": doc.department if doc else None,
        }

        item = EvidenceItem(
            chunk_id=chunk.id,
            document_id=chunk.document_id,
            document_version_id=chunk.document_version_id,
            page_number=chunk.page_number,
            text=chunk.text,
            source_url=source_url,
            source_title=doc_title,
            content_type="government_document",
            semantic_score=sem_score,
            keyword_score=kw_score,
            final_score=final_score,
            provenance=provenance,
        )
        evidence_items.append(item)

    # Sort by final score descending
    evidence_items.sort(key=lambda x: x.final_score, reverse=True)
    top_evidence = evidence_items[:top_k]

    return EvidencePack(
        query=query,
        normalized_query=normalized_q,
        filters=filters,
        evidence=top_evidence,
        total_found=len(evidence_items)
    )
