"""
metadata.py
Provides stable chunk ID generation and metadata preparation for ChromaDB vector store.
"""

import re
from pathlib import Path
from typing import Any, Dict, Optional


def sanitize_identifier(text: str) -> str:
    """Sanitize a string so it is safe to use in chunk IDs."""
    clean = re.sub(r"[^\w\-_.]", "_", text)
    return re.sub(r"_+", "_", clean).strip("_")


def generate_chunk_id(
    source: str,
    page: Optional[int] = None,
    chunk_idx: int = 0,
) -> str:
    """
    Generate a deterministic, stable chunk ID based on document source,
    page number (if applicable), and chunk index.

    Examples:
        generate_chunk_id("armory.pdf", page=11, chunk_idx=0)
        -> "armory_p11_c0"
        generate_chunk_id("gloamreach.md", page=None, chunk_idx=1)
        -> "gloamreach_p0_c1"
    """
    stem = sanitize_identifier(Path(source).stem)
    page_num = page if (page is not None and page > 0) else 0
    return f"{stem}_p{page_num}_c{chunk_idx}"


def build_chunk_metadata(
    source: str,
    category: str,
    doc_type: str,
    page: Optional[int] = None,
    chunk_idx: int = 0,
    total_chunks: int = 1,
) -> Dict[str, Any]:
    """
    Construct a metadata dict compatible with ChromaDB.
    ChromaDB requires all metadata values to be primitive types (str, int, float, bool).
    """
    page_val = int(page) if (page is not None and page > 0) else 0

    return {
        "source": str(source),
        "category": str(category),
        "doc_type": str(doc_type),
        "page": page_val,
        "chunk_idx": int(chunk_idx),
        "total_chunks": int(total_chunks),
    }
