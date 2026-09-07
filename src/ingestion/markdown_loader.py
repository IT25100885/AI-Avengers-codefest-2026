"""
markdown_loader.py
Loads .md wiki files from the Ashen Era corpus, normalizing fan-wiki
syntax (links, headings, images) to plain text for consistent chunking
and embedding alongside PDF/DOCX/TXT loaders.
"""

import re
from pathlib import Path
from typing import Dict

_WIKI_LINK_PATTERN = re.compile(r"\[\[([^|\]]+)(?:\|([^\]]+))?\]\]")
_IMAGE_LINE_PATTERN = re.compile(r"^\s*!\[[^\]]*\]\([^)]*\)\s*$")
_HEADING_PATTERN = re.compile(r"^#+\s*")
_BOLD_PATTERN = re.compile(r"\*\*([^*]+)\*\*")
_ITALIC_PATTERN = re.compile(r"(?<!\*)\*([^*]+)\*(?!\*)")


def _wiki_link_replacement(match: re.Match) -> str:
    """Use display text when present, otherwise the link target."""
    target, display = match.group(1), match.group(2)
    return display.strip() if display else target.strip()


def _normalize_wiki_markdown(raw: str) -> str:
    """
    Convert fan-wiki markdown to plain text while preserving readable
    structure (section headings, infobox tables, paragraph breaks).
    """
    lines = []
    for line in raw.splitlines():
        if _IMAGE_LINE_PATTERN.match(line):
            continue

        line = _WIKI_LINK_PATTERN.sub(_wiki_link_replacement, line)
        line = _HEADING_PATTERN.sub("", line)
        line = _BOLD_PATTERN.sub(r"\1", line)
        line = _ITALIC_PATTERN.sub(r"\1", line)
        lines.append(line)

    return "\n".join(lines).strip()


def load_markdown(file_path: Path, category: str) -> Dict:
    """
    Reads a single .md file and returns normalized text with metadata.

    Args:
        file_path: path to the .md file
        category: which corpus folder it came from (e.g. "wiki")

    Returns:
        A dict with: filename, category, doc_type, text
    """
    raw = file_path.read_text(encoding="utf-8", errors="replace")
    text = _normalize_wiki_markdown(raw)

    return {
        "filename": file_path.name,
        "category": category,
        "doc_type": "markdown",
        "text": text,
    }


if __name__ == "__main__":
    test_files = [
        ("data/corpus/Ashen_Era_Archive/wiki/gloamreach.md", "wiki"),
        ("data/corpus/Ashen_Era_Archive/wiki/ashreach.md", "wiki"),
    ]

    for path_str, category in test_files:
        test_file = Path(path_str)
        print(f"\n{'=' * 60}")
        print(f"Testing: {test_file.name}")
        print("=" * 60)

        if not test_file.exists():
            print(f"Test file not found: {test_file}")
            continue

        result = load_markdown(test_file, category=category)
        print(f"Filename: {result['filename']}")
        print(f"Category: {result['category']}")
        print(f"Doc type: {result['doc_type']}")
        print(f"Total characters: {len(result['text'])}")
        print(f"Wiki links remaining (should be 0): {result['text'].count('[[')}")
        print(f"Text preview (first 400 chars):\n{result['text'][:400]}")
