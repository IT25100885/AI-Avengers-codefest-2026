# Known Limitations

## 1. Final End-to-End Retrieval Validation Pending

The full retrieval pipeline has now been implemented using document ingestion, chunking, Voyage AI embeddings, ChromaDB, and reranking.

However, final end-to-end validation is still pending while the latest integration fixes are completed.

The final evaluation must be rerun after the live retrieval pipeline is confirmed working correctly.

## 2. Scanned / Image-Only PDFs

Some archive files may be scanned PDFs without an extractable text layer.

The current PDF loader relies on text extraction and does not perform OCR.

Therefore, information contained only inside image-based pages may not be searchable.

## 3. DOCX Page Numbers

DOCX documents are successfully extracted, including paragraphs and tables.

However, exact rendered page numbers are not reliably available from DOCX files.

Citations from these documents may therefore include the source filename without a physical page number.

## 4. Source Reliability and Conflicting Evidence

The archive contains sources with different levels of authority.

For example, Codex or Gazetteer sources may provide more authoritative information than informal wiki or ephemera material.

The reasoning agent attempts to resolve conflicting evidence, but answer quality still depends on retrieving the relevant authoritative sources.

## 5. External API Dependency

Live mode depends on external APIs including Groq and Voyage AI.

Possible failures include:

- missing API keys
- network errors
- rate limits
- provider outages
- model availability changes

The application should display these failures clearly instead of silently presenting simulation results as live retrieval.

## 6. Maximum Search Rounds

The search agent uses a configurable maximum number of search rounds.

This prevents infinite loops, but a difficult question may occasionally require more searches than the configured limit.

## 7. Final Evaluation Size

The evaluation set includes official Track 1C questions, multi-hop questions, direct lookup tests, and robustness tests.

The set is useful for system validation but is still relatively small and cannot represent every possible question over the Ashen Era Archive.

## 8. Standalone Image File Indexing

Standalone image files are currently not indexed.

During corpus ingestion, 86 unsupported files, mainly PNG figure plates, were skipped. This limits retrieval of information that is available only within those images.
```python
from src.retrieval.mock_search import search
```

Rather than `from src.retrieval.search import search`. This is a deliberate decoupling: the agent loop, planner, evidence checker, query rewriter, and answer generator are verified and testable independently of vector store indexing status.

## 2. Voyage AI Rate Limiting Without Billing Configured

Discovered during test suite runs that the team's Voyage AI account has no payment method configured, resulting in throttled rate limits (3 RPM / 10K TPM) per Voyage's free-tier policy.

### Symptoms & Root Cause
- Batch embedding calls in `index_corpus.py` (default batch size of 64 passages) quickly breached the 10,000 TPM threshold, failing with `voyageai.error.RateLimitError`.
- Although Voyage AI provides 200M free tokens, strict throughput caps (3 RPM and 10K TPM) remain enforced until a billing payment method is attached in the Voyage AI user dashboard.
- Concurrently discovered that the local vector database was not populated from Git because `data/vector_db/` was gitignored (commit `7262b81`), leaving only a single test chunk indexed locally rather than the real 2,186-chunk archive content.

### Impact & Actions Taken
- **Action**: Kept `src/agent/search_agent.py` using `mock_search` until both issues are resolved by whoever owns indexing / Voyage billing. This ensures test suites and demo evaluations remain completely green and deterministic without being blocked by API rate limits.
- **Remediation Paths**:
  1. Add a payment method to the [Voyage AI Dashboard](https://dashboard.voyageai.com/) to unlock standard rate limits (free 200M tokens still apply).
  2. Have Member 1 share the pre-indexed `data/vector_db/` directory directly (via shared drive or archive).
  3. Run local indexing using throttled micro-batches (`batch_size=10` with ~20s delay between requests).
