import json
import unittest
from app.database import SessionLocal
from app import models
from app.search import parse_query, score_record
from app.main import search, search_documents, search_news, search_youtube_transcripts, rank_results


class UnifiedSearchTestCase(unittest.TestCase):
    def setUp(self):
        self.db = SessionLocal()

    def tearDown(self):
        self.db.close()

    def test_query_parsing_road_projects_pune(self):
        parsed = parse_query("Show road projects in Pune")
        pub = parsed.public()
        self.assertEqual(pub["intent"], "find_projects")
        self.assertIn("road", pub["keywords"])
        self.assertIn("roads", pub["keywords"])
        self.assertEqual(pub["location"], ["Pune"])
        self.assertEqual(pub["entity_type"], "project")
        self.assertIsNone(pub["department"])
        # Filler words must not be in general keywords
        for filler in ["show", "in", "the", "about"]:
            self.assertNotIn(filler, pub["general_keywords"])

    def test_query_parsing_department_and_tender(self):
        parsed = parse_query("Find PWD tenders in Nashik")
        pub = parsed.public()
        self.assertEqual(pub["intent"], "find_tenders")
        self.assertEqual(pub["department"], "Public Works Department")
        self.assertEqual(pub["location"], ["Nashik"])
        self.assertEqual(pub["entity_type"], "tender")

    def test_multi_concept_scoring(self):
        parsed = parse_query("Show road projects in Pune")
        
        # Fake item with Pune + road + project
        item_both = models.ContentIndex(
            title="Pune Road Project Approval",
            department="Maharashtra Public Works Department",
            district="Pune",
            text="The Pune road project has received clearance for widening.",
            source="PWD",
            source_url="http://example.com/1",
            content_type="government_document"
        )
        score_both, concepts_both = score_record(item_both, parsed)
        self.assertTrue(concepts_both["location_hit"])
        self.assertTrue(concepts_both["keyword_hit"])
        self.assertEqual(concepts_both["matched_concepts"], 2)
        self.assertGreater(score_both, 30.0)

        # Fake item with only Pune (water announcement)
        item_loc_only = models.ContentIndex(
            title="Pune Water Supply Announcement",
            department="Water Resources Department",
            district="Pune",
            text="Water supply in Pune will be shut down on Thursday.",
            source="Water Dept",
            source_url="http://example.com/2",
            content_type="news_article"
        )
        score_loc, concepts_loc = score_record(item_loc_only, parsed)
        self.assertTrue(concepts_loc["location_hit"])
        self.assertFalse(concepts_loc["keyword_hit"])
        self.assertEqual(concepts_loc["matched_concepts"], 1)
        # Multi-concept match requires both, so single concept score is lower/zeroed
        self.assertLess(score_loc, score_both)

    def test_unified_search_returns_all_sources(self):
        res = search(q="Show road projects in Pune", db=self.db)
        self.assertEqual(res["query"], "Show road projects in Pune")
        self.assertIn("counts", res)
        self.assertIn("government_document", res["counts"])
        self.assertIn("news_article", res["counts"])
        self.assertIn("youtube_transcript", res["counts"])
        
        # Ensure YouTube transcript results are included
        self.assertGreater(res["counts"]["youtube_transcript"], 0)
        self.assertGreater(res["counts"]["government_document"], 0)
        self.assertGreater(res["counts"]["news_article"], 0)

        # Ensure parsed_query is present
        self.assertIn("parsed_query", res)
        self.assertEqual(res["parsed_query"]["location"], ["Pune"])
        self.assertEqual(res["parsed_query"]["intent"], "find_projects")

        # Check YouTube result item fields
        video_res = [r for r in res["results"] if r["type"] == "youtube_transcript"]
        if video_res:
            first_video = video_res[0]
            self.assertIsNotNone(first_video.get("timestamp_seconds"))
            self.assertIsNotNone(first_video.get("video_url"))
            self.assertIsNotNone(first_video.get("snippet"))
            self.assertIsNotNone(first_video.get("score"))

    def test_find_news_about_pune_metro(self):
        res = search(q="Find news about Pune Metro", db=self.db)
        self.assertEqual(res["parsed_query"]["intent"], "find_news")
        self.assertEqual(res["parsed_query"]["location"], ["Pune"])
        self.assertIn("metro", res["parsed_query"]["keywords"])
        
        # Verify that Pune Metro news article is ranked #1
        self.assertGreater(len(res["results"]), 0)
        top_result = res["results"][0]
        self.assertIn("Pune Metro", top_result["title"])
        self.assertEqual(top_result["type"], "news_article")
        self.assertGreater(top_result["score"], 40.0)


if __name__ == "__main__":
    unittest.main()

