"""
loader.py
Unified ingestion entry point. Walks the corpus folder and dispatches
each file to the correct loader based on its extension, returning a
single flat list of "documents" ready for chunking.

Every item in the returned list has at minimum: filename, category,
doc_type, text. PDF items additionally have "page".
"""

from pathlib import Path
from typing import Dict, List

from src.ingestion.text_loader import load_txt
from src.ingestion.pdf_loader import load_pdf
from src.ingestion.docx_loader import load_docx
from src.ingestion.markdown_loader import load_markdown

CORPUS_ROOT = Path("data/corpus/Ashen_Era_Archive")

# Which loader function handles which file extension
LOADERS = {
    ".txt": load_txt,
    ".pdf": load_pdf,
    ".docx": load_docx,
    ".md": load_markdown,
}


def load_corpus(root: Path = CORPUS_ROOT) -> List[Dict]:
    """
    Walks the corpus folder and loads every supported file.

    Returns a flat list of document dicts. PDF files contribute one
    dict PER PAGE (since load_pdf returns a list); all other formats
    contribute a single dict for the whole file.
    """
    all_documents: List[Dict] = []
    skipped: List[str] = []

    if not root.exists():
        raise FileNotFoundError(f"Corpus root path not found: {root}")

    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue

        ext = path.suffix.lower()
        loader_fn = LOADERS.get(ext)

        if loader_fn is None:
            skipped.append(path.name)
            continue

        # category = the folder directly under the archive root
        relative = path.relative_to(root)
        category = relative.parts[0] if len(relative.parts) > 1 else "root"

        try:
            result = loader_fn(path, category)
            # PDF loader returns a LIST (one dict per page); others return ONE dict
            if isinstance(result, list):
                all_documents.extend(result)
            else:
                all_documents.append(result)
        except Exception as err:
            print(f"Warning: Failed to load {path.name}: {err}")

    print(f"Loaded {len(all_documents)} document/page entries.")
    print(f"Skipped {len(skipped)} unsupported files: {skipped[:10]}{'...' if len(skipped) > 10 else ''}")

    return all_documents


if __name__ == "__main__":
    docs = load_corpus()

    # Quick breakdown by doc_type, so we can sanity-check counts
    from collections import Counter
    by_type = Counter(d["doc_type"] for d in docs)
    by_category = Counter(d["category"] for d in docs)

    print("\n--- By doc_type ---")
    for doc_type, count in by_type.most_common():
        print(f"  {doc_type:10s} {count}")

    print("\n--- By category ---")
    for category, count in by_category.most_common():
        print(f"  {category:10s} {count}")