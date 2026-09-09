# Known Limitations

## 1. Local Vector Index Requirement

The live retrieval pipeline is implemented using document ingestion, chunking, Voyage AI embeddings, ChromaDB vector search, and Voyage reranking.

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

