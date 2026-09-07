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