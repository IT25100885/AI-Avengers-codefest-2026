"""
Unit tests for Member 3 Streamlit UI backend and data contracts.
Tests adherence to SLIIT Codefest 2026 Track 1C specification.
"""

import unittest
from src.ui.mock_backend import mock_answer_question, MOCK_DATABASE


class TestUIBackendContract(unittest.TestCase):
    def test_contract_schema_keys(self):
        """Verify the returned dictionary has the required keys."""
        res = mock_answer_question("Which war was won by Isolde Mournvale's organization?")
        self.assertIn("answer", res)
        self.assertIn("search_steps", res)
        self.assertIn("sources", res)
        self.assertIsInstance(res["answer"], str)
        self.assertIsInstance(res["search_steps"], list)
        self.assertIsInstance(res["sources"], list)

    def test_search_steps_schema(self):
        """Verify each search step conforms to the Section 6 specification."""
        res = mock_answer_question("Which war was won by Isolde Mournvale's organization?")
        self.assertGreaterEqual(len(res["search_steps"]), 1)
        for step in res["search_steps"]:
            self.assertIn("round", step)
            self.assertIn("query", step)
            self.assertIn("sources_found", step)
            self.assertIn("status", step)
            self.assertIn(step["status"], ["sufficient", "insufficient"])
            self.assertIsInstance(step["round"], int)
            self.assertIsInstance(step["query"], str)
            self.assertIsInstance(step["sources_found"], int)

    def test_sources_schema(self):
        """Verify sources have source filename and optional page."""
        res = mock_answer_question("Which war was won by Isolde Mournvale's organization?")
        self.assertGreaterEqual(len(res["sources"]), 1)
        for s in res["sources"]:
            self.assertIn("source", s)
            self.assertIsInstance(s["source"], str)

    def test_multihop_scenario(self):
        """Verify multi-hop query performs multiple rounds and ends with sufficient status."""
        q = "Which war was won by the organization that included Isolde Mournvale as one of its members?"
        res = mock_answer_question(q)
        steps = res["search_steps"]
        self.assertEqual(len(steps), 2)
        self.assertEqual(steps[0]["status"], "insufficient")
        self.assertEqual(steps[1]["status"], "sufficient")
        self.assertIn("War of Drowned Light", res["answer"])
        self.assertIn("The Silent Choir", res["answer"])

    def test_contested_lore_scenario(self):
        """Verify contested lore query does not hallucinate and exercises max search rounds."""
        q = "State the precise year in the Age of Shadows that marks the true founding of Gloamreach."
        res = mock_answer_question(q)
        steps = res["search_steps"]
        self.assertEqual(len(steps), 3)
        self.assertTrue(all(s["status"] == "insufficient" for s in steps))
        self.assertIn("contested", res["answer"].lower())

    def test_unrecorded_artifact_scenario(self):
        """Verify unrecorded artifact reports absence of evidence."""
        q = "In which year was the 'Gauntlet of Sorrowfell' actually forged?"
        res = mock_answer_question(q)
        self.assertTrue("cannot be determined" in res["answer"] or "no record" in res["answer"].lower())

    def test_empty_question_handling(self):
        """Verify empty question returns a friendly error without crashing."""
        res = mock_answer_question("")
        self.assertIn("answer", res)
        self.assertEqual(len(res["search_steps"]), 0)
        self.assertEqual(len(res["sources"]), 0)

    def test_arbitrary_question_fallback(self):
        """Verify arbitrary question produces valid multi-round mock data."""
        res = mock_answer_question("Who is the high commander of the Pale Coast fleet?")
        self.assertIn("answer", res)
        self.assertGreaterEqual(len(res["search_steps"]), 1)
        self.assertGreaterEqual(len(res["sources"]), 1)


if __name__ == "__main__":
    unittest.main()
