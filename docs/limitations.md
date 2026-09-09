# Known Limitations

## 1. Full-Archive Retrieval Not Yet Integrated

The live reasoning agent currently uses:

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
