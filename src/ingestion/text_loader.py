"""
text_loader.py
Loads plain .txt files from the Ashen Era corpus.
Returns extracted text along with metadata: filename, category, doc_type.
"""

from pathlib import Path
from typing import Dict


def load_txt(file_path: Path, category: str) -> Dict:
    """
    Reads a single .txt file and returns its content with metadata.

    Args:
        file_path: path to the .txt file
        category: which corpus folder it came from (e.g. "ephemera")

    Returns:
        A dict with: filename, category, doc_type, text
    """
    text = file_path.read_text(encoding="utf-8", errors="replace")

    return {
        "filename": file_path.name,
        "category": category,
        "doc_type": "txt",
        "text": text,
    }


if __name__ == "__main__":
    # Quick manual test -- point this at ONE real .txt file from your corpus
    # once you've extracted Ashen_Era_Archive.zip into data/corpus/
    test_file = Path("data/corpus/Ashen_Era_Archive/ephemera/field_report_concerning_gloamreach.txt")

    if test_file.exists():
        result = load_txt(test_file, category="ephemera")
        print(f"Filename: {result['filename']}")
        print(f"Category: {result['category']}")
        print(f"Doc type: {result['doc_type']}")
        print(f"Text preview (first 300 chars):\n{result['text'][:300]}")
    else:
        print(f"Test file not found: {test_file}")
        print("Edit the 'test_file' path above to point at a real .txt file in your corpus.")