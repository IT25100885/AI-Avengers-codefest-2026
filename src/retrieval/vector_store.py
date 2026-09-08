"""
vector_store.py
Persistent ChromaDB vector store for the Ashen Era Archive.
Supports chunk insertion with duplicate prevention and cosine similarity querying.
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

import chromadb
from chromadb.config import Settings

DEFAULT_DB_PATH = Path(os.getenv("CHROMA_DB_PATH", "data/vector_db"))
DEFAULT_COLLECTION = os.getenv("CHROMA_COLLECTION_NAME", "ashen_era_archive")


class ChromaVectorStore:
    """Manages persistent ChromaDB vector storage and semantic similarity retrieval."""

    def __init__(
        self,
        db_path: Path = DEFAULT_DB_PATH,
        collection_name: str = DEFAULT_COLLECTION,
    ):
        self.db_path = Path(db_path)
        self.db_path.mkdir(parents=True, exist_ok=True)
        self.collection_name = collection_name

        self.client = chromadb.PersistentClient(
            path=str(self.db_path),
            settings=Settings(anonymized_telemetry=False),
        )
        # Use cosine distance for embedding similarity
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def count(self) -> int:
        """Return the number of items stored in the collection."""
        return self.collection.count()

    def get_existing_ids(self) -> Set[str]:
        """Fetch all existing chunk IDs in the collection to prevent duplicate ingestion."""
        count = self.count()
        if count == 0:
            return set()
        # Fetch IDs in batches if large
        results = self.collection.get(include=[])
        return set(results.get("ids", []))

    def add_chunks(
        self,
        chunks: List[Dict[str, Any]],
        embeddings: List[List[float]],
        batch_size: int = 200,
    ) -> int:
        """
        Add chunks and their embeddings into ChromaDB with duplicate prevention.

        Args:
            chunks: List of chunk dicts (must have chunk_id, text, and metadata).
            embeddings: Corresponding list of embedding vectors.
            batch_size: Number of records per insertion batch.

        Returns:
            Count of newly added/updated records.
        """
        if len(chunks) != len(embeddings):
            raise ValueError(
                f"Mismatch: {len(chunks)} chunks vs {len(embeddings)} embeddings."
            )

        if not chunks:
            return 0

        existing_ids = self.get_existing_ids()
        new_chunks = []
        new_embeddings = []

        for ch, emb in zip(chunks, embeddings):
            cid = ch["chunk_id"]
            if cid not in existing_ids:
                new_chunks.append(ch)
                new_embeddings.append(emb)

        if not new_chunks:
            return 0

        total_added = 0
        for i in range(0, len(new_chunks), batch_size):
            batch_ch = new_chunks[i : i + batch_size]
            batch_emb = new_embeddings[i : i + batch_size]

            ids = [c["chunk_id"] for c in batch_ch]
            documents = [c["text"] for c in batch_ch]
            metadatas = [c.get("metadata", {}) for c in batch_ch]

            # Upsert ensures duplicate prevention and idempotent re-runs
            self.collection.upsert(
                ids=ids,
                documents=documents,
                metadatas=metadatas,
                embeddings=batch_emb,
            )
            total_added += len(ids)

        return total_added

    def query(
        self,
        query_embedding: List[float],
        n_results: int = 15,
        where: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Query the persistent store for the most similar chunks.

        Args:
            query_embedding: Query embedding vector.
            n_results: Number of results to retrieve.
            where: Optional ChromaDB metadata filter.

        Returns:
            List of dicts formatted with required retrieval schema:
            [
                {
                    "chunk_id": "...",
                    "text": "...",
                    "source": "...",
                    "page": ...,
                    "category": "...",
                    "score": ...
                }
            ]
        """
        if self.count() == 0:
            return []

        # Request at most the count of available items
        fetch_k = min(n_results, self.count())

        kwargs: Dict[str, Any] = {
            "query_embeddings": [query_embedding],
            "n_results": fetch_k,
            "include": ["documents", "metadatas", "distances"],
        }
        if where:
            kwargs["where"] = where

        query_res = self.collection.query(**kwargs)

        results: List[Dict[str, Any]] = []
        ids = query_res["ids"][0] if query_res["ids"] else []
        docs = query_res["documents"][0] if query_res["documents"] else []
        metas = query_res["metadatas"][0] if query_res["metadatas"] else []
        distances = query_res["distances"][0] if query_res["distances"] else []

        for chunk_id, doc, meta, dist in zip(ids, docs, metas, distances):
            # In cosine space, cosine_sim = 1 - distance
            score = max(0.0, min(1.0, 1.0 - dist))
            page_val = meta.get("page")
            page_num = page_val if (isinstance(page_val, int) and page_val > 0) else None

            results.append({
                "chunk_id": chunk_id,
                "text": doc,
                "source": meta.get("source", "unknown"),
                "page": page_num,
                "category": meta.get("category", "unknown"),
                "score": round(score, 4),
            })

        return results


if __name__ == "__main__":
    store = ChromaVectorStore(db_path=Path("data/test_chroma"))
    print(f"ChromaVectorStore initialized. Current items: {store.count()}")
    # Clean up test dir
    import shutil
    try:
        del store
        shutil.rmtree("data/test_chroma", ignore_errors=True)
        print("Cleanup done.")
    except Exception as e:
        pass
