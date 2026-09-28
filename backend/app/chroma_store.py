"""ChromaDB Vector Store Integration for RTI Intelligence.

Provides persistent ANN vector indexing and semantic retrieval over document chunks.
"""
from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any

logger = logging.getLogger("corescapper.chromadb")

_CHROMA_CLIENT = None
_CHROMA_COLLECTION = None

STORAGE_PATH = Path(os.getenv("STORAGE_PATH", "storage"))
CHROMA_DB_PATH = STORAGE_PATH / "chroma_db"


def get_chroma_collection():
    """Lazily initializes and returns the persistent ChromaDB collection."""
    global _CHROMA_CLIENT, _CHROMA_COLLECTION
    if _CHROMA_COLLECTION is not None:
        return _CHROMA_COLLECTION

    try:
        import chromadb
        from chromadb.config import Settings

        CHROMA_DB_PATH.mkdir(parents=True, exist_ok=True)
        _CHROMA_CLIENT = chromadb.PersistentClient(path=str(CHROMA_DB_PATH))
        _CHROMA_COLLECTION = _CHROMA_CLIENT.get_or_create_collection(
            name="rti_document_chunks",
            metadata={"description": "Maharashtra RTI semantic chunks & public gazettes"}
        )
        return _CHROMA_COLLECTION
    except Exception as e:
        logger.warning(f"Failed to initialize ChromaDB persistent client: {e}")
        return None


def index_chunks_to_chroma(chunks: list[dict[str, Any]]) -> int:
    """Indexes a batch of document chunks into ChromaDB."""
    collection = get_chroma_collection()
    if not collection or not chunks:
        return 0

    ids = []
    documents = []
    metadatas = []

    for c in chunks:
        chunk_id = str(c.get("id") or c.get("chunk_id"))
        text = (c.get("text") or "").strip()
        if not chunk_id or not text:
            continue

        ids.append(f"chunk_{chunk_id}")
        documents.append(text)
        metadatas.append({
            "chunk_id": int(c.get("id") or c.get("chunk_id")),
            "document_id": int(c.get("document_id") or 0),
            "page_number": int(c.get("page_number") or 1),
            "department": str(c.get("department") or ""),
            "source_title": str(c.get("source_title") or ""),
            "source_url": str(c.get("source_url") or ""),
        })

    if not ids:
        return 0

    try:
        collection.upsert(ids=ids, documents=documents, metadatas=metadatas)
        return len(ids)
    except Exception as e:
        logger.error(f"Error upserting chunks to ChromaDB: {e}")
        return 0


def query_chroma_vector_db(
    query: str,
    n_results: int = 15,
    department_filter: str | None = None
) -> list[dict[str, Any]]:
    """Queries ChromaDB for approximate nearest neighbor (ANN) semantic chunks."""
    collection = get_chroma_collection()
    if not collection:
        return []

    where_clause = None
    if department_filter:
        where_clause = {"department": {"$eq": department_filter}}

    try:
        results = collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where_clause
        )
        hits = []
        if results and "ids" in results and results["ids"] and results["ids"][0]:
            num_hits = len(results["ids"][0])
            for i in range(num_hits):
                meta = results["metadatas"][0][i] if results["metadatas"] else {}
                doc_text = results["documents"][0][i] if results["documents"] else ""
                distance = results["distances"][0][i] if results.get("distances") else 0.5
                # Distance to similarity
                similarity = max(0.0, min(1.0, 1.0 - (distance / 2.0)))
                hits.append({
                    "chunk_id": meta.get("chunk_id"),
                    "document_id": meta.get("document_id"),
                    "page_number": meta.get("page_number", 1),
                    "text": doc_text,
                    "department": meta.get("department", ""),
                    "source_title": meta.get("source_title", ""),
                    "source_url": meta.get("source_url", ""),
                    "semantic_score": similarity,
                })
        return hits
    except Exception as e:
        logger.debug(f"ChromaDB query fallback: {e}")
        return []
