"""
chunker.py
Splits documents into coherent passages of approximately 500-800 tokens with overlap.
Preserves source filename, page number, category, and document type for each chunk.
"""

import re
from typing import Any, Dict, List, Optional

from src.processing.metadata import build_chunk_metadata, generate_chunk_id

# Target token parameters per Team Guide (500-800 tokens)
TARGET_CHUNK_TOKENS = 650
MAX_CHUNK_TOKENS = 800
CHUNK_OVERLAP_TOKENS = 100

# Word-to-token ratio approximation (average ~1.3 tokens per word)
WORDS_PER_TOKEN = 0.75
TARGET_CHUNK_WORDS = int(TARGET_CHUNK_TOKENS * WORDS_PER_TOKEN)     # ~480 words
MAX_CHUNK_WORDS = int(MAX_CHUNK_TOKENS * WORDS_PER_TOKEN)           # ~600 words
OVERLAP_WORDS = int(CHUNK_OVERLAP_TOKENS * WORDS_PER_TOKEN)         # ~75 words


def estimate_token_count(text: str) -> int:
    """Rough estimate of token count based on whitespace and punctuation."""
    words = len(text.split())
    # 1 word ~ 1.3 tokens
    return max(1, int(words * 1.33))


def _split_into_sentences(text: str) -> List[str]:
    """Split text into sentences while preserving sentence endings."""
    # Split on sentence terminals followed by whitespace
    sentence_end = re.compile(r"(?<=[.!?])\s+")
    parts = sentence_end.split(text.strip())
    return [p.strip() for p in parts if p.strip()]


def _chunk_text(
    text: str,
    target_words: int = TARGET_CHUNK_WORDS,
    max_words: int = MAX_CHUNK_WORDS,
    overlap_words: int = OVERLAP_WORDS,
) -> List[str]:
    """
    Split text into chunks of target word length with overlap,
    aligning to paragraph and sentence boundaries wherever possible.
    """
    cleaned = text.strip()
    if not cleaned:
        return []

    words = cleaned.split()
    if len(words) <= max_words:
        return [cleaned]

    # Split first by paragraphs
    paragraphs = [p.strip() for p in cleaned.split("\n\n") if p.strip()]
    chunks = []
    current_sentences: List[str] = []
    current_word_count = 0

    for para in paragraphs:
        sentences = _split_into_sentences(para)
        for sentence in sentences:
            s_words = len(sentence.split())

            if current_word_count + s_words > max_words and current_sentences:
                chunk_str = " ".join(current_sentences).strip()
                chunks.append(chunk_str)

                # Overlap: keep trailing sentences up to overlap_words
                overlap_accum: List[str] = []
                overlap_count = 0
                for prev in reversed(current_sentences):
                    pw_count = len(prev.split())
                    if overlap_count + pw_count <= overlap_words or not overlap_accum:
                        overlap_accum.insert(0, prev)
                        overlap_count += pw_count
                    else:
                        break

                current_sentences = list(overlap_accum)
                current_word_count = overlap_count

            current_sentences.append(sentence)
            current_word_count += s_words

    if current_sentences:
        chunk_str = " ".join(current_sentences).strip()
        # Avoid tiny orphaned chunks if we already have chunks
        if chunks and len(chunk_str.split()) < 30:
            chunks[-1] = chunks[-1] + "\n\n" + chunk_str
        else:
            chunks.append(chunk_str)

    return chunks


def chunk_document(doc: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Split a single document dict (from loader) into one or more chunk dicts.

    Args:
        doc: Dict containing:
            - 'filename' or 'source': str
            - 'category': str
            - 'doc_type': str
            - 'text': str
            - 'page': Optional[int]

    Returns:
        List of chunk dicts matching the required retrieval schema.
    """
    text = doc.get("text", "")
    if not text or not text.strip():
        return []

    source = doc.get("filename") or doc.get("source") or "unknown"
    category = doc.get("category", "unknown")
    doc_type = doc.get("doc_type", "unknown")
    page = doc.get("page")

    raw_chunks = _chunk_text(text)
    total_chunks = len(raw_chunks)
    result = []

    for idx, chunk_text in enumerate(raw_chunks):
        chunk_id = generate_chunk_id(source=source, page=page, chunk_idx=idx)
        meta = build_chunk_metadata(
            source=source,
            category=category,
            doc_type=doc_type,
            page=page,
            chunk_idx=idx,
            total_chunks=total_chunks,
        )

        result.append({
            "chunk_id": chunk_id,
            "text": chunk_text,
            "source": source,
            "page": page if (page is not None and page > 0) else None,
            "category": category,
            "doc_type": doc_type,
            "metadata": meta,
        })

    return result


def chunk_corpus(documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Chunk an entire list of documents produced by load_corpus().

    Returns:
        Flat list of chunk dictionaries.
    """
    all_chunks: List[Dict[str, Any]] = []
    seen_ids = set()

    for doc in documents:
        chunks = chunk_document(doc)
        for ch in chunks:
            cid = ch["chunk_id"]
            # Disambiguate if duplicate chunk IDs occur
            if cid in seen_ids:
                dup_idx = 1
                while f"{cid}_{dup_idx}" in seen_ids:
                    dup_idx += 1
                cid = f"{cid}_{dup_idx}"
                ch["chunk_id"] = cid
                ch["metadata"]["chunk_id"] = cid

            seen_ids.add(cid)
            all_chunks.append(ch)

    return all_chunks


if __name__ == "__main__":
    test_doc = {
        "filename": "the_annals_of_the_ashen_era.docx",
        "category": "codex",
        "doc_type": "docx",
        "page": None,
        "text": ("This is a test paragraph for chunking. " * 60) + "\n\n" + ("Second section content. " * 80),
    }

    chunks = chunk_document(test_doc)
    print(f"Produced {len(chunks)} chunks.")
    for c in chunks:
        tokens = estimate_token_count(c["text"])
        print(f"Chunk ID: {c['chunk_id']} | Estimated tokens: {tokens} | Page: {c['page']}")
