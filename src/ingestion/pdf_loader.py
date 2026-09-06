"""
pdf_loader.py
Loads .pdf files from the Ashen Era corpus, extracting text per page
so page numbers are preserved for later metadata.
"""

from pathlib import Path
from typing import Dict, List
from pypdf import PdfReader


def load_pdf(file_path: Path, category: str) -> List[Dict]:
    """
    Reads a single .pdf file and returns one dict PER PAGE.

    Args:
        file_path: path to the .pdf file
        category: which corpus folder it came from (e.g. "codex")

    Returns:
        A list of dicts, one per page, each with:
        filename, category, doc_type, page, text
    """
    reader = PdfReader(str(file_path))
    pages = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""  # extract_text() can return None
        pages.append({
            "filename": file_path.name,
            "category": category,
            "doc_type": "pdf",
            "page": page_number,
            "text": text,
        })

    return pages
if __name__ == "__main__":
    test_file = Path("data/corpus/Ashen_Era_Archive/codex/the_annals_of_the_ashen_era.pdf")

    if test_file.exists():
        results = load_pdf(test_file, category="codex")
        print(f"Total pages extracted: {len(results)}")

        print(f"\n--- Page 1 preview ---")
        print(f"Filename: {results[0]['filename']}")
        print(f"Category: {results[0]['category']}")
        print(f"Doc type: {results[0]['doc_type']}")
        print(f"Page: {results[0]['page']}")
        print(f"Text preview (first 300 chars):\n{results[0]['text'][:300]}")

        print(f"\n--- Page 5 preview ---")
        print(f"Text preview (first 300 chars):\n{results[4]['text'][:300]}")

        print(f"\n--- Checking for empty pages ---")
        empty_pages = [r['page'] for r in results if len(r['text'].strip()) == 0]
        print(f"Pages with NO extracted text: {empty_pages}")
    else:
        print(f"Test file not found: {test_file}")
        print("Edit the 'test_file' path above to point at a real .pdf in your corpus.")

