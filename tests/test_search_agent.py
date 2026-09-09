"""
test_search_agent.py

Unit tests for the Track 1C iterative search agent (src/agent/search_agent.py):
- Multi-hop question resolution requiring genuine multi-round search
- Honest handling of genuinely insufficient evidence (no hallucination)
- Correct resolution of conflicting sources by authority (Codex overrides wiki hedge)
- Loop safety guarantees (round cap, no duplicate queries, clean query strings)

Run with:
    python3 -m pytest tests/test_search_agent.py -v
or:
    python3 -m unittest tests.test_search_agent -v

NOTE: These tests run against the deterministic mock corpus
(src/retrieval/mock_search.py), but DO make real LLM calls via src.llm.client,
since the planner/evidence-checker/rewriter/answer-generator all depend on
the LLM. This means:
  - A valid GROQ_API_KEY must be present in your local .env to run these.
  - LLM output is not perfectly deterministic even at low temperature, so
    assertions check structural/factual correctness (e.g. a key fact
    appearing in the answer) rather than exact string matches.
  - Running the full suite consumes real Groq API calls.
"""

import unittest

from src.agent.search_agent import answer_question


class TestMultiHopResolution(unittest.TestCase):
    """Verify the agent performs genuine multi-round search on questions that
    cannot be answered from a single retrieval pass."""

    def test_isolde_mournvale_requires_multiple_rounds(self):
        question = (
            "Which war was won by the organization that included Isolde "
            "Mournvale as one of its members?"
        )
        result = answer_question(question)

        # Must actually search more than once -- a single round here would
        # mean the system is behaving like basic RAG, not Track 1C.
        self.assertGreaterEqual(
            len(result["search_steps"]), 2,
            f"Expected multi-round search, got {len(result['search_steps'])} round(s)"
        )

        # The final round must be marked sufficient once the answer is found.
        self.assertEqual(result["search_steps"][-1]["status"], "sufficient")

        # The correct answer (War of Drowned Light) must appear in the answer text.
        self.assertIn("drowned light", result["answer"].lower())

        # Must cite the two chunks that actually establish the fact chain.
        cited_sources = {s["source"] for s in result["sources"]}
        self.assertIn("isolde_mournvale.md", cited_sources)
        self.assertIn("the_war_of_drowned_light.md", cited_sources)


class TestHonestInsufficientEvidence(unittest.TestCase):
    """Verify the agent does NOT hallucinate when evidence genuinely does not
    contain an answer, or explicitly states a fact is disputed."""

    def test_gauntlet_of_sorrowfell_no_data_in_mock(self):
        """The base mock corpus has no data on this artifact -- the agent
        must say so honestly rather than inventing a year."""
        question = "In which year was the 'Gauntlet of Sorrowfell' actually forged?"
        result = answer_question(question)

        # Must never falsely declare sufficiency, since no round should find
        # real evidence for this in the base mock corpus.
        self.assertTrue(
            all(step["status"] == "insufficient" for step in result["search_steps"])
        )

        answer_lower = result["answer"].lower()
        honest_phrases = ("no information", "does not", "not contain", "no relevant")
        self.assertTrue(
            any(phrase in answer_lower for phrase in honest_phrases),
            f"Expected an honest 'no information found' answer, got: {result['answer']}"
        )

    def test_nonsense_input_does_not_crash_or_hallucinate(self):
        question = "asdfgh qwerty zxcvbn ???"
        result = answer_question(question)

        self.assertIn("answer", result)
        self.assertIn("search_steps", result)
        self.assertIn("sources", result)

        self.assertLessEqual(len(result["search_steps"]), 3)
        self.assertTrue(
            all(step["status"] == "insufficient" for step in result["search_steps"])
        )


class TestSourceAuthorityResolution(unittest.TestCase):
    """Verify the agent resolves a conflict where a lower-authority source
    hedges a fact but a higher-authority source resolves it definitively.
    Requires the extended mock corpus (with the Gazetteer chunk) to be active."""

    def test_gloamreach_founding_year_resolved_by_codex(self):
        question = (
            "State the precise year in the Age of Shadows that marks the "
            "true founding of Gloamreach."
        )
        result = answer_question(question)

        # The correct, verified answer is 246 AS (from the real Gazetteer codex).
        self.assertIn(
            "246", result["answer"],
            f"Expected the answer to state 246 AS, got: {result['answer']}"
        )

        cited_sources = {s["source"] for s in result["sources"]}
        self.assertTrue(
            any("gazetteer" in s.lower() for s in cited_sources),
            f"Expected the Gazetteer codex to be cited, got sources: {cited_sources}"
        )


class TestLoopSafety(unittest.TestCase):
    """Verify the loop's structural guarantees hold regardless of question content."""

    def test_search_steps_never_exceed_max_rounds(self):
        question = "What is the population of a city not covered in this archive?"
        result = answer_question(question)
        self.assertLessEqual(len(result["search_steps"]), 3)

    def test_no_duplicate_queries_across_rounds(self):
        question = (
            "Which war was won by the organization that included Isolde "
            "Mournvale as one of its members?"
        )
        result = answer_question(question)
        queries = [step["query"].strip().lower() for step in result["search_steps"]]
        self.assertEqual(
            len(queries), len(set(queries)),
            f"Expected no duplicate queries across rounds, got: {queries}"
        )

    def test_no_control_characters_or_stray_quotes_in_queries(self):
        question = (
            "Which war was won by the organization that included Isolde "
            "Mournvale as one of its members?"
        )
        result = answer_question(question)
        for step in result["search_steps"]:
            query = step["query"]
            self.assertNotIn('"', query, f"Found stray quote in query: {query!r}")
            self.assertNotIn("'", query, f"Found stray quote in query: {query!r}")
            self.assertTrue(
                all(ord(c) >= 32 or c.isspace() for c in query),
                f"Found control character in query: {query!r}"
            )


if __name__ == "__main__":
    unittest.main()
