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