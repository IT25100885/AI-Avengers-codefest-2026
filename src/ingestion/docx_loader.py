"""
docx_loader.py
Loads .docx files from the Ashen Era corpus, extracting paragraphs and
tables in document order so registry-style codex content is preserved.
"""

from pathlib import Path
from typing import Dict, Iterator, Union

from docx import Document
from docx.document import Document as DocumentObject
from docx.oxml.ns import qn
from docx.table import Table
from docx.text.paragraph import Paragraph


def _iter_blocks(parent: DocumentObject) -> Iterator[Union[Paragraph, Table]]:
    """Yield paragraphs and tables in document order."""
    for child in parent.element.body.iterchildren():
        if child.tag == qn("w:p"):
            yield Paragraph(child, parent)
        elif child.tag == qn("w:tbl"):
            yield Table(child, parent)


def _table_to_text(table: Table) -> str:
    """Convert a table to plain text, one row per line."""
    rows = []
    for row in table.rows:
        cells = [cell.text.strip() for cell in row.cells if cell.text.strip()]
        if cells:
            rows.append(" | ".join(cells))
    return "\n".join(rows)


def load_docx(file_path: Path, category: str) -> Dict:
    """
    Reads a single .docx file and returns its content with metadata.

    Args:
        file_path: path to the .docx file
        category: which corpus folder it came from (e.g. "codex")

    Returns:
        A dict with: filename, category, doc_type, text
    """
    doc = Document(str(file_path))
    blocks = []

    for block in _iter_blocks(doc):
        if isinstance(block, Paragraph):
            text = block.text.strip()
            if text:
                blocks.append(text)
        else:
            text = _table_to_text(block)
            if text:
                blocks.append(text)

    return {
        "filename": file_path.name,
        "category": category,
        "doc_type": "docx",
        "text": "\n\n".join(blocks),
    }


if __name__ == "__main__":
    test_files = [
        ("data/corpus/Ashen_Era_Archive/codex/the_annals_of_the_ashen_era.docx", "codex"),
        ("data/corpus/Ashen_Era_Archive/ephemera/letter_concerning_ashreach.docx", "ephemera"),
    ]

    for path_str, category in test_files:
        test_file = Path(path_str)
        print(f"\n{'=' * 60}")
        print(f"Testing: {test_file.name}")
        print("=" * 60)

        if not test_file.exists():
            print(f"Test file not found: {test_file}")
            continue

        result = load_docx(test_file, category=category)
        print(f"Filename: {result['filename']}")
        print(f"Category: {result['category']}")
        print(f"Doc type: {result['doc_type']}")
        print(f"Total characters: {len(result['text'])}")
        print(f"Text preview (first 400 chars):\n{result['text'][:400]}")

        if "annals" in test_file.name:
            has_table_markers = " | " in result["text"]
            print(f"\nTable rows detected (pipe-separated cells): {has_table_markers}")
