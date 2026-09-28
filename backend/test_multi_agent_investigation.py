"""End-to-End Multi-Agent RTI Investigation & Pipeline Tests."""
import unittest
import uuid
from fastapi.testclient import TestClient
from app.database import SessionLocal, engine, Base
from app import models
from app.main import app
from app.agents import (
    InvestigationPlanner,
    GovernmentDataAgent,
    TenderBudgetAgent,
    AuditTimelineAgent,
    ContradictionEngine,
    EvidenceGapDetector,
    RTIGeneratorEngine,
    run_investigation_pipeline
)
from app.rag import chunk_document_version
from app.migrations import upgrade_development_database


class MultiAgentPipelineTestCase(unittest.TestCase):
    def setUp(self):
        Base.metadata.create_all(engine)
        upgrade_development_database(engine)
        self.db = SessionLocal()
        self.client = TestClient(app)

    def tearDown(self):
        self.db.close()

    def test_multi_agent_pipeline_execution(self):
        uid = str(uuid.uuid4())[:8]
        # Seed test government document
        doc = models.Document(
            title=f"PWD Solapur Highway Widening Project Approval ({uid})",
            department="Public Works Department",
            document_url=f"https://pwd.gov.in/solapur-{uid}.pdf"
        )
        self.db.add(doc)
        self.db.flush()

        version = models.DocumentVersion(
            document_id=doc.id,
            sha256=f"sha_{uid}",
            file_size=50000,
            mime_type="application/pdf",
            file_path=f"/storage/solapur-{uid}.pdf",
            page_count=2
        )
        self.db.add(version)
        self.db.flush()

        p1 = models.DocumentPage(
            version_id=version.id,
            page_number=1,
            text="GR No. PWD-2024/CR-102. Administrative approval granted for Solapur road widening with sanctioned amount of ₹150 Crore."
        )
        p2 = models.DocumentPage(
            version_id=version.id,
            page_number=2,
            text="Contract awarded to M/s Solapur Infra Ltd. Completion deadline set for December 2025. No completion certificate issued yet."
        )
        self.db.add_all([p1, p2])
        self.db.flush()
        chunk_document_version(self.db, doc, version)
        self.db.commit()

        # Run investigation
        created_inv = run_investigation_pipeline(self.db, query=f"Solapur road widening PWD ({uid})")

        # Fetch fully loaded investigation
        from sqlalchemy.orm import selectinload
        inv = self.db.query(models.Investigation).options(
            selectinload(models.Investigation.steps),
            selectinload(models.Investigation.claims),
            selectinload(models.Investigation.gaps),
            selectinload(models.Investigation.contradictions),
            selectinload(models.Investigation.rti_applications).selectinload(models.RTIApplication.questions),
        ).filter_by(id=created_inv.id).first()

        self.assertIsNotNone(inv)
        self.assertEqual(inv.status, "completed")
        self.assertGreater(len(inv.steps), 3)
        self.assertGreater(len(inv.claims), 0)
        self.assertGreater(len(inv.gaps), 0)
        self.assertGreater(len(inv.rti_applications), 0)

        # Verify generated RTI
        rti = inv.rti_applications[0]
        self.assertIn("Section 6(1)", rti.draft_text)
        self.assertIn("Public Information Officer", rti.authority_name)
        self.assertGreater(len(rti.questions), 0)

    def test_investigation_api_endpoints(self):
        # Trigger investigation via API
        response = self.client.post("/api/investigations", json={
            "query": "Pune ring road construction tender expenditure"
        })
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertIn("id", data)
        self.assertEqual(data["status"], "completed")
        self.assertIn("steps", data)
        self.assertIn("claims", data)
        self.assertIn("gaps", data)
        self.assertIn("rti_applications", data)

        inv_id = data["id"]
        # Fetch investigation
        get_res = self.client.get(f"/api/investigations/{inv_id}")
        self.assertEqual(get_res.status_code, 200)
        self.assertEqual(get_res.json()["id"], inv_id)

    def test_rti_response_processing_closed_loop(self):
        # 1. Create investigation with an RTI application
        inv_res = self.client.post("/api/intelligence/investigations", json={
            "query": "Nagpur Metro line phase 2 financial audit"
        })
        self.assertEqual(inv_res.status_code, 201)
        inv_data = inv_res.json()
        self.assertGreater(len(inv_data["rti_applications"]), 0)
        rti_app = inv_data["rti_applications"][0]
        rti_id = rti_app["id"]

        # 2. Submit official response text
        reply_text = (
            "Point 1: Certified copies of Sanction Order No. NGP-2024/09 for ₹450 Crore are enclosed herewith.\n"
            "Point 2: Information regarding internal contractor dispute is exempt under Section 8(1)(d) of RTI Act.\n"
            "Point 3: Measurement Book MB-882 is available and attached in Annexure-A.\n"
        )
        resp_res = self.client.post(f"/api/intelligence/rti/{rti_id}/response", json={
            "raw_text": reply_text
        })
        self.assertEqual(resp_res.status_code, 200)
        resp_data = resp_res.json()
        self.assertEqual(resp_data["rti_application_id"], rti_id)
        self.assertGreater(len(resp_data["items"]), 0)

        # 3. Analyze classifications
        analysis_res = self.client.get(f"/api/intelligence/rti/{rti_id}/response-analysis")
        self.assertEqual(analysis_res.status_code, 200)
        analysis = analysis_res.json()
        self.assertIn("classifications", analysis)
        self.assertGreater(analysis["responses_count"], 0)

    def test_langgraph_stategraph_execution(self):
        try:
            from app.graph import build_investigation_graph
        except ImportError:
            self.skipTest("langgraph not installed in local environment")

        graph = build_investigation_graph(self.db)
        initial_state = {
            "investigation_id": 999,
            "query": "Maharashtra Highway bridge repair and audit tender",
            "department": "Public Works Department",
            "milestones": [],
            "evidence_chunks": [],
            "findings": [],
            "claims": [],
            "contradictions": [],
            "gaps": [],
            "project_events": [],
            "financial_events": [],
            "rti_application": {},
            "status": "init",
            "summary": "",
        }

        result = graph.invoke(initial_state)
        self.assertIsNotNone(result)
        self.assertEqual(result["status"], "completed")
        self.assertIn("milestones", result)
        self.assertGreater(len(result["milestones"]), 0)
        self.assertIn("gaps", result)
        self.assertIn("rti_application", result)
        self.assertIn("draft_text", result["rti_application"])
        self.assertIn("Section 6(1)", result["rti_application"]["draft_text"])


if __name__ == "__main__":
    unittest.main()

