"""Unit tests for Phase 2: RAG, Semantic Chunking, and Hybrid Retrieval."""
import unittest
from app.database import SessionLocal, engine, Base
from app import models
from app.rag import (
    split_text_into_chunks,
    chunk_document_version,
    compute_text_embedding,
    cosine_similarity,
    retrieve_hybrid_evidence
)


class RAGRetrievalTestCase(unittest.TestCase):
    def setUp(self):
        Base.metadata.create_all(engine)
        self.db = SessionLocal()

    def tearDown(self):
        self.db.close()

    def test_text_chunking_and_overlap(self):
        sample_text = " ".join([f"Word{i}" for i in range(100)])
        chunks = split_text_into_chunks(sample_text, max_tokens=30, overlap_tokens=5)
        self.assertGreater(len(chunks), 1)
        self.assertTrue(chunks[0].startswith("Word0"))

    def test_chunk_document_version_preserves_page_provenance(self):
        import uuid
        uid = str(uuid.uuid4())[:8]
        # Create dummy document and version with pages
        doc = models.Document(
            title=f"Nashik Highway PWD Resolution 2024 ({uid})",
            department="Public Works Department",
            document_url=f"https://pwd.gov.in/nashik-gr-{uid}.pdf"
        )
        self.db.add(doc)
        self.db.flush()

        version = models.DocumentVersion(
            document_id=doc.id,
            sha256=f"abc123sha256_{uid}",
            file_size=10240,
            mime_type="application/pdf",
            file_path="/storage/nashik-gr.pdf",
            page_count=2
        )
        self.db.add(version)
        self.db.flush()

        page1 = models.DocumentPage(
            version_id=version.id,
            page_number=1,
            text="Government of Maharashtra PWD sanctions ₹85 Crore for Nashik bypass road widening."
        )
        page2 = models.DocumentPage(
            version_id=version.id,
            page_number=2,
            text="Contract awarded to ABC Infrastructure Ltd. Completion deadline set for March 2025."
        )
        self.db.add_all([page1, page2])
        self.db.flush()

        # Chunk version
        chunks = chunk_document_version(self.db, doc, version)
        self.db.commit()

        self.assertEqual(len(chunks), 2)
        self.assertEqual(chunks[0].page_number, 1)
        self.assertIn("₹85 Crore", chunks[0].text)
        self.assertEqual(chunks[1].page_number, 2)
        self.assertIn("ABC Infrastructure", chunks[1].text)
        self.assertIsNotNone(chunks[0].embedding_json)

    def test_hybrid_evidence_pack_retrieval(self):
        # Query for Nashik bypass
        pack = retrieve_hybrid_evidence(
            self.db,
            query="Nashik bypass road widening sanction",
            filters={"department": "Public Works Department"},
            top_k=5
        )
        res = pack.to_dict()
        self.assertIn("query", res)
        self.assertIn("evidence", res)
        self.assertGreater(len(res["evidence"]), 0)

        top_evidence = res["evidence"][0]
        self.assertIsNotNone(top_evidence["page_number"])
        self.assertIn("Nashik", top_evidence["text"])
        self.assertGreater(top_evidence["final_score"], 0.3)
        self.assertIn("Public Works Department", top_evidence["provenance"]["department"])


if __name__ == "__main__":
    unittest.main()
