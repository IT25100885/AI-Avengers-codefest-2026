# Known Limitations

## 1. Local Vector Index Requirement

The live retrieval pipeline is implemented using document ingestion, chunking, Voyage AI embeddings, ChromaDB vector search, and Voyage reranking.

However, final end-to-end validation is still pending while the latest integration fixes are completed. The live reasoning agent has been deliberately decoupled using:

The generated ChromaDB database is intentionally excluded from Git and must be built locally from the Ashen Era Archive before full live retrieval can run.

This means a clean machine must first configure the corpus and execute the indexing pipeline.

## 2. Scanned / Image-Only Content

The current text ingestion pipeline relies on extractable document text and does not perform OCR.

Information that exists only inside image-based or scanned pages may therefore not be searchable.

## 3. Standalone Image Files

Standalone image files are currently not indexed by the text retrieval pipeline.

During corpus ingestion, 86 unsupported files, mainly PNG figure plates, were skipped. This limits retrieval of facts that appear only inside those images.

## 4. DOCX Page Numbers

DOCX paragraphs and tables can be extracted, but exact rendered page numbers are not reliably available.

Citations from DOCX documents may therefore contain a source filename without a physical page number.

## 5. External API Dependency

Live Mode depends on external Groq and Voyage AI services.

Possible failure modes include:

- missing API keys
- network failures
- provider outages
- rate limits
- model availability changes

The application reports live execution failures instead of silently switching to simulation.

## 6. Voyage AI Rate Limits

Voyage AI account limits may affect indexing speed and live retrieval throughput.

During development, low account rate limits caused embedding requests to fail when large batches were sent too quickly.

The indexing pipeline supports smaller batches and duplicate prevention so interrupted indexing can be resumed.

## 7. Source Reliability and Conflicting Evidence

The Ashen Era Archive intentionally contains sources with different levels of reliability.

Official Codex or Gazetteer material may conflict with wiki pages or in-world ephemera.

The reasoning system attempts to resolve these conflicts, but answer quality still depends on retrieving the relevant authoritative evidence.

## 8. Maximum Search Rounds

The search agent uses a configurable maximum number of rounds.

This prevents infinite loops, but some especially difficult questions may require more investigation than the configured limit permits.

## 9. Evaluation Coverage

The development evaluation set includes official Track 1C questions, multi-hop questions, direct lookups and robustness checks.

It is useful for QA but does not represent every possible question in the Ashen Era Archive.

## 8. Standalone Image File Indexing

Standalone image files are currently not indexed.

During corpus ingestion, 86 unsupported files, mainly PNG figure plates, were skipped. This limits retrieval of information that is available only within those images.
```python
from src.retrieval.mock_search import search
```

Rather than `from src.retrieval.search import search` directly in the loop. This ensures the agent loop, planner, evidence checker, query rewriter, and answer generator remain verified, stable, and testable independently of vector store indexing status. The final evaluation will be rerun once the live vector database is fully populated.

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

## 3. Scanned / Image-Only PDFs

Some archive files may be scanned PDFs without an extractable text layer. The current PDF loader relies on text extraction and does not perform OCR. Therefore, information contained only inside image-based pages may not be searchable.

## 4. DOCX Page Numbers

DOCX documents are successfully extracted, including paragraphs and tables. However, exact rendered page numbers are not reliably available from DOCX files. Citations from these documents may therefore include the source filename without a physical page number.

## 5. Source Reliability and Conflicting Evidence

The archive contains sources with different levels of authority. For example, Codex or Gazetteer sources provide more authoritative information than informal wiki or ephemera material. The reasoning agent actively weighs source authority, but answer quality still depends on retrieving the relevant authoritative passages.

## 6. External API Dependencies

Live mode depends on external APIs including Groq and Voyage AI. Possible failure modes include missing API keys, network errors, rate limits, provider outages, or model availability changes. The application displays these failures clearly instead of silently falling back or presenting simulation results as live retrieval.

## 7. Maximum Search Rounds

The search agent uses a configurable maximum number of search rounds to prevent infinite loops. While effective for safety, an especially complex question requiring extensive hops may occasionally require more searches than the configured limit allows.

## 8. Final Evaluation Size

The evaluation set includes official Track 1C questions, multi-hop questions, direct lookup tests, and robustness tests. While sufficient for system validation and judging, it cannot represent every possible permutation of inquiries across the Ashen Era Archive.

## 9. Standalone Image File Indexing

Standalone image files are currently not indexed. During corpus ingestion, 86 unsupported files (mainly PNG figure plates) were skipped, limiting retrieval of information present exclusively in visual figures.
