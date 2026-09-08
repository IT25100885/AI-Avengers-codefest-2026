"""
Comprehensive unit tests for Member 3 Streamlit UI backend, data contracts,
and integration with the Track 1C search agent.
"""

import unittest
from unittest.mock import patch, MagicMock
from src.ui.mock_backend import mock_answer_question, MOCK_DATABASE
from src.agent.search_agent import answer_question


class TestUIBackendContract(unittest.TestCase):
    def test_contract_schema_keys(self):
        """Verify the returned dictionary has the required keys and evidence fields."""
        res = mock_answer_question("Which war was won by the organization that included Isolde Mournvale as one of its members?")
        self.assertIn("answer", res)
        self.assertIn("search_steps", res)
        self.assertIn("sources", res)
        self.assertIsInstance(res["answer"], str)
        self.assertIsInstance(res["search_steps"], list)
        self.assertIsInstance(res["sources"], list)
        self.assertIn("[DEMONSTRATION / SIMULATION MODE", res["answer"])

    def test_search_steps_schema_and_preserved_fields(self):
        """Verify each search step conforms to specification and preserves missing_info."""
        res = mock_answer_question("Which war was won by the organization that included Isolde Mournvale as one of its members?")
        self.assertGreaterEqual(len(res["search_steps"]), 1)
        for step in res["search_steps"]:
            self.assertIn("round", step)
            self.assertIn("query", step)
            self.assertIn("sources_found", step)
            self.assertIn("status", step)
            self.assertIn("missing_info", step)
            self.assertIn(step["status"], ["sufficient", "insufficient"])
            self.assertIsInstance(step["round"], int)
            self.assertIsInstance(step["query"], str)
            self.assertIsInstance(step["sources_found"], int)

    def test_sources_schema_and_category_preserved(self):
        """Verify sources have source filename, page, and category."""
        res = mock_answer_question("Which war was won by the organization that included Isolde Mournvale as one of its members?")
        self.assertGreaterEqual(len(res["sources"]), 1)
        for s in res["sources"]:
            self.assertIn("source", s)
            self.assertIn("category", s)
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

    def test_corrected_gloamreach_founding_year(self):
        """Verify Gloamreach founding year resolves to 246 AS via Codex Vaeloria I (p. 23)."""
        q = "State the precise year in the Age of Shadows that marks the true founding of Gloamreach."
        res = mock_answer_question(q)
        self.assertIn("246 AS", res["answer"])
        steps = res["search_steps"]
        self.assertEqual(len(steps), 2)
        self.assertEqual(steps[0]["status"], "insufficient")
        self.assertEqual(steps[1]["status"], "sufficient")
        source_names = [s["source"] for s in res["sources"]]
        self.assertTrue(any("codex_vaeloria_i" in s for s in source_names))
        pages = [s.get("page") for s in res["sources"] if "codex_vaeloria_i" in s["source"]]
        self.assertIn(23, pages)

    def test_corrected_gauntlet_forging_year(self):
        """Verify Gauntlet of Sorrowfell resolves to 391 AS via Codex Vaeloria II (p. 11)."""
        q = "In which year was the 'Gauntlet of Sorrowfell' actually forged?"
        res = mock_answer_question(q)
        self.assertIn("391 AS", res["answer"])
        steps = res["search_steps"]
        self.assertEqual(len(steps), 2)
        self.assertEqual(steps[0]["status"], "insufficient")
        self.assertEqual(steps[1]["status"], "sufficient")
        source_names = [s["source"] for s in res["sources"]]
        self.assertTrue(any("codex_vaeloria_ii" in s for s in source_names))
        pages = [s.get("page") for s in res["sources"] if "codex_vaeloria_ii" in s["source"]]
        self.assertIn(11, pages)

    def test_direct_lookup_scenario(self):
        """Verify direct lookup returns The Silent Choir in 1 round without hitting the war scenario."""
        q = "Which organization includes Isolde Mournvale as a member?"
        res = mock_answer_question(q)
        self.assertIn("The Silent Choir", res["answer"])
        self.assertNotIn("War of Drowned Light", res["answer"])
        self.assertEqual(len(res["search_steps"]), 1)
        self.assertEqual(res["search_steps"][0]["status"], "sufficient")

    def test_unsupported_simulation_question(self):
        """Verify unsupported simulation questions return refusal instead of invented lore."""
        q = "Who is the high commander of the Pale Coast fleet?"
        res = mock_answer_question(q)
        self.assertTrue(res.get("is_unsupported"))
        self.assertIn("No simulation available for this question", res["answer"])
        self.assertEqual(res["search_steps"], [])
        self.assertEqual(res["sources"], [])

    def test_empty_question_handling(self):
        """Verify empty question returns a friendly error without crashing."""
        res = mock_answer_question("")
        self.assertIn("answer", res)
        self.assertEqual(len(res["search_steps"]), 0)
        self.assertEqual(len(res["sources"]), 0)


class TestLiveAgentParametersAndCoordination(unittest.TestCase):
    @patch("src.agent.search_agent.generate_answer")
    @patch("src.agent.search_agent.check_sufficiency")
    @patch("src.agent.search_agent.search")
    @patch("src.agent.search_agent.plan_initial_query")
    def test_live_agent_slider_parameter_max_rounds(
        self, mock_plan, mock_search, mock_check, mock_gen
    ):
        """Verify passing max_rounds=1 terminates the live agent loop after 1 round."""
        mock_plan.return_value = "Isolde Mournvale"
        mock_search.return_value = [
            {"chunk_id": "c1", "source": "isolde.md", "page": 1, "category": "wiki", "score": 0.9}
        ]
        # Sufficiency returns insufficient, but max_rounds=1 forces stop
        mock_check.return_value = {
            "status": "insufficient",
            "missing_information": "War outcome missing",
            "reasoning": "Incomplete",
        }
        mock_gen.return_value = "Partial answer"

        res = answer_question("Test question", max_rounds=1, top_k=7)
        self.assertEqual(len(res["search_steps"]), 1)
        self.assertEqual(mock_search.call_count, 1)
        mock_search.assert_called_with("Isolde Mournvale", top_k=7)
        self.assertEqual(res["search_steps"][0]["missing_info"], "War outcome missing")
        self.assertEqual(res["sources"][0]["category"], "wiki")

    @patch("src.app.run_live_pipeline")
    def test_no_automatic_fallback_on_live_failure(self, mock_live):
        """Verify that execute_search in live mode returns None and does not fall back to simulation."""
        from src.app import execute_search

        mock_live.side_effect = ValueError("GROQ_API_KEY is not set")
        res = execute_search(
            question="Which war was won by Isolde Mournvale's organization?",
            mode="Live Agent Pipeline (src.agent.search_agent)",
            max_rounds=3,
            top_k=15,
        )
        self.assertIsNone(res, "execute_search must return None on error and not silently fall back to mock!")


if __name__ == "__main__":
    unittest.main()
