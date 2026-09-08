# Known Limitations

## Current limitations

- The evaluation program currently uses a mock backend.
- Evaluation scores require manual review.
- The initial evaluation set contains only a small number of questions.
- Final citation accuracy cannot be tested until document metadata is available.

## PDF extraction: scanned/image-only pages

Files with ".scan." in the filename inside `ephemera/` (e.g.
`sermon_concerning_marsh_revenant.scan.pdf`) contain no real text layer --
they are image-based (photographed/scanned) pages, not digitally-typed text.

Tested: sermon_concerning_marsh_revenant.scan.pdf (2 pages) -- both pages
returned 0 characters of extracted text using pypdf.

Impact: these documents will be MISSING from search results entirely,
since there is no text to chunk or embed.

Fix (out of scope this week per P3 priority rules): OCR (Optical Character
Recognition) would be needed to read text out of scanned images. Not
attempted, given the 1-week timeline and P0/P1 priorities.

## Cross-document authority & Codex indexing dependency

Observation:
Wiki articles often hedge difficult historical facts (e.g. "contested", "consult the Codex and Annals") while the resolving facts reside inside multi-hundred-page Codex DOCX/PDF data books (e.g. Codex Vaeloria I & II).

Impact & Dependency:
If Member 1's retrieval system only indexes wiki articles or fails to effectively chunk and retrieve dense tables/registries inside Codex files, the reasoning agent will be trapped by wiki hedges and conclude facts are "disputed/unresolved" even when ground-truth answers exist in the archive. Full-archive accuracy strictly depends on high-quality extraction and embedding of Codex documents.