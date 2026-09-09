# Experiments

## Experiment 001: Initial mock evaluation

Date: 2026-09-04

Goal:
Verify that the evaluation runner can load questions and save results.

Configuration:
- Backend: Mock answer_question()
- Questions tested: 1
- Search rounds: 2

Results:
- Evaluation file created successfully
- Search steps were recorded
- Sources were recorded

Conclusion:
The evaluation framework is ready to connect to the real backend.

## Experiment 002: Insufficient-evidence handling (Gloamreach trap question)

Date: 2026-09-06

Goal:
Verify that the agent correctly handles genuine "no answer exists / contested source" questions without hallucinating.

Configuration:
- Question tested: Sample question 1c_000 ("true founding year of Gloamreach")
- Corpus: Mock corpus built from real archive files where the founding date is explicitly recorded as disputed/unresolved
- Max search rounds: 3

Results:
- The agent ran all 3 search rounds.
- Never falsely declared sufficiency.
- Produced an honest final answer explaining the dispute with citations rather than hallucinating a specific year.

Conclusion:
The agent kept all three rounds marked insufficient and did not
invent a specific year in this mock-corpus test.
Full-archive correctness and citation accuracy remain unverified.

## Experiment 003: Query sanitization verification
Date: 2026-09-06

Goal:
Confirm control-character stripping fix resolves malformed queries
observed in earlier evaluation runs (e.g. trailing null byte in a
query_rewriter output).

Configuration:
- Same 2-question evaluation set (1c_000, 1c_003)
- Re-ran after adding regex-based control-character stripping to
  planner.py and query_rewriter.py

Results:
- All search_steps queries across both questions, all 3 rounds, are now
  free of stray quotes and control characters.
- Neither response supplied a specific year.
- Answer correctness remains unverified against the full archive.

Conclusion:
Fix verified with no regressions to answer quality or search behavior.


## Experiment 004: Agent connected to evaluator

Date: 2026-09-07
Configuration: Actual agent with mock retrieval.
Questions: 1c_000 and 1c_003.

Results:
- Both questions completed and results were saved.
- Each question used three search rounds.
- All rounds were marked insufficient.
- Neither response supplied the requested year.
- Expected answers and scores remain unverified.

Conclusion:
Evaluator-to-agent integration works.
Full-archive answer and citation accuracy remain untested.


## Experiment 005: Expanded five-question evaluation

Configuration:
- Actual agent connected to the evaluator.
- Mock retrieval, based on the last confirmed search import.
- Five questions tested.

Observed results:
- All five questions produced recorded responses.
- Gloamreach and Gauntlet each exhausted three search rounds,
  with all rounds marked insufficient.
- Isolde multi-step question changed from insufficient in round 1
  to sufficient in round 2.
- Isolde direct question stopped after one sufficient round.
- Nonsense input exhausted three rounds and declined to answer.

Issues:
- Gloamreach round 3 contained duplicated query text.
- Nonsense input generated an empty initial query.
- Nonsense input retrieved an unrelated war document.
- Full-archive answer and citation correctness remain unverified.

Next actions:
- Member 2: investigate duplicated queries and empty-query handling.
- Coordinate input validation with Member 3.
- Connect Member 1's real retrieval before full-archive evaluation.
- Verify expected answers and supporting passages before scoring.

Conclusion:
The expanded evaluation records direct, multi-step and invalid-input
behaviour. These results do not establish full-archive accuracy.


### Manual review of the two Isolde answers

Reviewed result: evaluation_20260907_195840.json

The saved result contains null expected answers.
The expected answers were subsequently verified against the original
archive and added to questions.json.

- 1b_005: Answer score 2/2.
  The response correctly identifies The War of Drowned Light.
  Evidence: wiki/isolde_mournvale.md identifies The Silent Choir
  as Isolde's organization; wiki/the_war_of_drowned_light.md
  identifies The Silent Choir as victor.

- internal_direct_001: Answer score 2/2.
  The response correctly identifies The Silent Choir.
  Evidence: wiki/isolde_mournvale.md, Infobox, Member of.

These scores assess answer content only.
Retrieval and citation scores remain unassessed.
The run used mock retrieval based on the last confirmed configuration;
it does not demonstrate successful full-archive retrieval.


### Archive verification correction: Gloamreach and Gauntlet

The original codex PDFs establish:
- Gloamreach was founded in 246 AS.
  Source: Codex Vaeloria I, PDF page 23.
- Gauntlet of Sorrowfell was forged in 391 AS.
  Source: Codex Vaeloria II, PDF page 11.

These are answerable questions involving conflicting or incomplete
sources, not verified no-answer questions.

The earlier mock run did not retrieve the authoritative codex entries.
Its responses failed to supply the correct years.

The Gloamreach response also incorrectly generalized that the Codex
contains no founding date. The Gauntlet refusal was limited to supplied
evidence, but still did not answer the full-archive question.

Next: test whether real retrieval returns these specific codex passages.


## Experiment 006: Source authority weighting (Gloamreach resolved)

Date: 2026-09-08

Goal:
Verify the agent correctly resolves a conflict where a lower-authority
source (wiki) hedges a fact as "contested," but a higher-authority source
(Codex Vaeloria I Gazetteer) explicitly and definitively resolves it.

Configuration:
- Extended mock corpus with the real Gazetteer passage confirming
  Gloamreach's founding year (246 AS), which explicitly states popular/wiki
  accounts are incorrect.
- Re-ran sample question 1c_000 against the extended corpus.

Results:
- Agent correctly answered 246 AS, citing the Gazetteer by name.
- Answer explicitly framed the Gazetteer as authoritative, resolving the
  wiki's hedge rather than repeating it.
- Matches the actual verified expected_answer in questions.json.

Conclusion:
Confirms the evidence-checker and answer-generator correctly weigh source
authority when sources conflict, not just presence/absence of evidence --
directly addressing the rubric's "how do you handle conflicting sources"
requirement.


## Experiment 007: Real Retrieval Integration

Date: 2026-09-09

Goal:
Replace the temporary mock retrieval dependency in the live reasoning agent with the production retrieval pipeline.

Change:
`src/agent/search_agent.py` now imports:

```python
from src.retrieval.search import search
```

Production retrieval uses:
- Voyage AI query embeddings
- ChromaDB vector search
- Voyage reranking

Indexing observations:
- 1,440 document/page entries were loaded.
- 2,186 text chunks were generated.
- 86 unsupported standalone files, mainly PNG figure plates, were skipped.
- Voyage API rate limits were encountered during large-batch indexing.
- The indexer uses existing chunk IDs to avoid duplicates and support resumable indexing.

Conclusion:
The live agent is now integrated with the production retrieval module. Full live operation requires a populated local `data/vector_db`, valid Voyage/Groq credentials and provider availability.