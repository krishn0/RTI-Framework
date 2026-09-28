"""Unit tests for Phase 1: RTI Intelligence Models and Schema verification."""
import unittest
from datetime import datetime, timezone
from app.database import SessionLocal, engine, Base
from app import models, schemas
from app.migrations import upgrade_development_database


class IntelligenceModelsTestCase(unittest.TestCase):
    def setUp(self):
        Base.metadata.create_all(engine)
        upgrade_development_database(engine)
        self.db = SessionLocal()

    def tearDown(self):
        self.db.close()

    def test_create_investigation_with_steps_and_claims(self):
        # 1. Create Investigation
        inv = models.Investigation(
            query="Audit road construction expenditure Pune PWD",
            normalized_query="audit road construction expenditure pune pwd",
            status="planning",
            summary="Investigating road construction expenditure in Pune"
        )
        self.db.add(inv)
        self.db.flush()

        # 2. Add Investigation Step
        step = models.InvestigationStep(
            investigation_id=inv.id,
            step_type="RETRIEVE_EVIDENCE",
            agent_name="Government Data Agent",
            status="completed",
            input_json='{"keywords": ["road", "pune", "pwd"]}',
            output_json='{"documents_found": 3}'
        )
        self.db.add(step)

        # 3. Add Evidence Claim
        claim = models.EvidenceClaim(
            investigation_id=inv.id,
            subject_entity_type="PROJECT",
            subject_text="Pune Ring Road Section A",
            predicate="SANCTIONED_AMOUNT",
            value_text="₹120 Crore",
            status="SUPPORTED",
            confidence_label="HIGH"
        )
        self.db.add(claim)
        self.db.flush()

        # 4. Add Claim Source
        source = models.ClaimSource(
            claim_id=claim.id,
            source_url="https://pwd.maharashtra.gov.in/gr/2024/102.pdf",
            quoted_excerpt="Sanction of Rs 120 Crore for Pune Ring Road",
            page_number=2,
            retrieval_score=0.92
        )
        self.db.add(source)

        # 5. Add Evidence Gap
        gap = models.EvidenceGap(
            investigation_id=inv.id,
            gap_type="MISSING_COMPLETION_CERT",
            expected_record_type="Completion Certificate",
            description="No completion certificate recorded for Section A",
            status="IDENTIFIED"
        )
        self.db.add(gap)
        self.db.flush()

        # 6. Add RTI Application & Question
        rti = models.RTIApplication(
            investigation_id=inv.id,
            authority_name="Public Information Officer, PWD Pune",
            subject="Information regarding completion certificate for Ring Road Section A",
            draft_text="Under Section 6(1) of RTI Act 2005, please provide...",
            status="DRAFT"
        )
        self.db.add(rti)
        self.db.flush()

        q = models.RTIQuestion(
            rti_application_id=rti.id,
            sequence_no=1,
            gap_id=gap.id,
            question_text="Please provide certified copy of completion certificate.",
            requested_record_type="Completion Certificate"
        )
        self.db.add(q)
        self.db.commit()

        # Verify query and ORM cascade
        fetched = self.db.get(models.Investigation, inv.id)
        self.assertIsNotNone(fetched)
        self.assertEqual(len(fetched.steps), 1)
        self.assertEqual(len(fetched.claims), 1)
        self.assertEqual(len(fetched.claims[0].sources), 1)
        self.assertEqual(len(fetched.gaps), 1)
        self.assertEqual(len(fetched.rti_applications), 1)
        self.assertEqual(len(fetched.rti_applications[0].questions), 1)

        # Pydantic Schema Serialization check
        serialized = schemas.InvestigationDetailOut.model_validate(fetched)
        self.assertEqual(serialized.id, inv.id)
        self.assertEqual(len(serialized.claims), 1)
        self.assertEqual(serialized.claims[0].sources[0].page_number, 2)


if __name__ == "__main__":
    unittest.main()
