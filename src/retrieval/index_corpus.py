"""
index_corpus.py
End-to-end indexing pipeline:
Loads corpus documents -> Chunks passages -> Generates Voyage AI embeddings ->
Persists into ChromaDB vector store with duplicate prevention.
"""

import argparse
import os
import sys
import time
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

from src.ingestion.loader import load_corpus
from src.processing.chunker import chunk_corpus
from src.retrieval.embeddings import VoyageEmbedder
from src.retrieval.vector_store import ChromaVectorStore

load_dotenv()


def run_indexing(
    corpus_root: Path = Path("data/corpus/Ashen_Era_Archive"),
    db_path: Path = Path("data/vector_db"),
    batch_size: int = 64,
    limit_docs: Optional[int] = None,
) -> int:
    """
    Execute full indexing process.

    Args:
        corpus_root: Root directory of the Ashen Era Archive.
        db_path: Persistent ChromaDB storage path.
        batch_size: Batch size for embedding and DB insertion.
        limit_docs: Optional limit on number of raw documents to process (for testing).

    Returns:
        Total number of chunks now in the vector store.
    """
    print(f"=== Ashen Era Archive Indexing Pipeline ===")
    print(f"Corpus path: {corpus_root}")
    print(f"Vector DB path: {db_path}")

    start_time = time.time()

    # 1. Ingestion
    print("\n[1/4] Loading documents from archive...")
    documents = load_corpus(root=corpus_root)
    if limit_docs:
        print(f"Limiting to first {limit_docs} documents for testing.")
        documents = documents[:limit_docs]
    print(f"Loaded {len(documents)} document/page items.")

    # 2. Chunking
    print("\n[2/4] Chunking documents into passages (500-800 tokens)...")
    chunks = chunk_corpus(documents)
    print(f"Generated {len(chunks)} chunks.")

    if not chunks:
        print("No chunks generated. Exiting.")
        return 0

    # 3. Initialize Vector Store & Deduplication Check
    print("\n[3/4] Checking vector store for duplicate prevention...")
    store = ChromaVectorStore(db_path=db_path)
    existing_ids = store.get_existing_ids()
    print(f"Vector store currently contains {len(existing_ids)} indexed chunks.")

    new_chunks = [c for c in chunks if c["chunk_id"] not in existing_ids]
    print(f"New chunks requiring embedding: {len(new_chunks)}")

    if not new_chunks:
        print("All chunks are already indexed! No new embeddings needed.")
        print(f"Vector store has {store.count()} total items.")
        return store.count()

    # 4. Embeddings with Voyage AI
    print(f"\n[4/4] Generating Voyage AI embeddings for {len(new_chunks)} chunks...")
    embedder = VoyageEmbedder()

    total_new = len(new_chunks)
    added_count = 0

    for i in range(0, total_new, batch_size):
        batch = new_chunks[i : i + batch_size]
        batch_texts = [c["text"] for c in batch]
        print(f"  Embedding batch {i // batch_size + 1}/{(total_new + batch_size - 1) // batch_size} ({len(batch)} chunks)...")

        embeddings = embedder.embed_documents(batch_texts, batch_size=batch_size)
        store.add_chunks(batch, embeddings)
        added_count += len(batch)

    elapsed = time.time() - start_time
    print(f"\n=== Indexing Complete ===")
    print(f"Successfully added: {added_count} chunks in {elapsed:.1f}s")
    print(f"Total chunks in vector store: {store.count()}")

    return store.count()


def main():
    parser = argparse.ArgumentParser(description="Index Ashen Era Archive into ChromaDB")
    parser.add_argument(
        "--corpus",
        type=Path,
        default=Path("data/corpus/Ashen_Era_Archive"),
        help="Path to corpus directory",
    )
    parser.add_argument(
        "--db-path",
        type=Path,
        default=Path("data/vector_db"),
        help="Path to ChromaDB directory",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=64,
        help="Embedding batch size",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit number of documents (for testing)",
    )
    args = parser.parse_args()

    run_indexing(
        corpus_root=args.corpus,
        db_path=args.db_path,
        batch_size=args.batch_size,
        limit_docs=args.limit,
    )


if __name__ == "__main__":
    main()
