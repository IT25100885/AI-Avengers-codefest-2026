"""
search.py
Production retrieval function for Member 2's reasoning agent and Member 3's UI.
Connects Voyage AI embeddings, persistent ChromaDB vector store, and Voyage reranker.

Contract:
search(query, top_k=15) -> List[Dict]
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

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.retrieval.embeddings import VoyageEmbedder
from src.retrieval.reranker import VoyageReranker
from src.retrieval.vector_store import ChromaVectorStore

_STORE_INSTANCE: Optional[ChromaVectorStore] = None
_EMBEDDER_INSTANCE: Optional[VoyageEmbedder] = None
_RERANKER_INSTANCE: Optional[VoyageReranker] = None


def get_vector_store() -> ChromaVectorStore:
    """Get or create singleton ChromaVectorStore instance."""
    global _STORE_INSTANCE
    if _STORE_INSTANCE is None:
        db_path = Path(os.getenv("CHROMA_DB_PATH", "data/vector_db"))
        col_name = os.getenv("CHROMA_COLLECTION_NAME", "ashen_era_archive")
        _STORE_INSTANCE = ChromaVectorStore(db_path=db_path, collection_name=col_name)
    return _STORE_INSTANCE


def get_embedder() -> VoyageEmbedder:
    """Get or create singleton VoyageEmbedder instance."""
    global _EMBEDDER_INSTANCE
    if _EMBEDDER_INSTANCE is None:
        _EMBEDDER_INSTANCE = VoyageEmbedder()
    return _EMBEDDER_INSTANCE


def get_reranker() -> VoyageReranker:
    """Get or create singleton VoyageReranker instance."""
    global _RERANKER_INSTANCE
    if _RERANKER_INSTANCE is None:
        _RERANKER_INSTANCE = VoyageReranker()
    return _RERANKER_INSTANCE


def search(query: str, top_k: int = 15) -> List[Dict[str, Any]]:
    """
    Search the persistent Ashen Era Archive using Voyage AI embeddings,
    ChromaDB similarity search, and Voyage rerank-2.5 reranker.

    Args:
        query: User or agent question / sub-query.
        top_k: Number of highest-ranked results to return (default: 15).

    Returns:
        List of dicts strictly adhering to the agreed contract:
        [
            {
                "chunk_id": str,
                "text": str,
                "source": str,
                "page": Optional[int],
                "category": str,
                "score": float
            }
        ]
    """
    clean_query = query.strip()
    if not clean_query:
        return []

    store = get_vector_store()
    if store.count() == 0:
        # If vector DB has not been indexed yet, warn and return empty
        print(
            "Warning: ChromaDB collection is empty. Run 'src.retrieval.index_corpus' "
            "to index the Ashen Era Archive."
        )
        return []

    embedder = get_embedder()

    # 1. Embed query with Voyage AI (input_type="query")
    query_vector = embedder.embed_query(clean_query)

    # 2. Retrieve initial candidate pool from ChromaDB (2x top_k or at least 30)
    candidate_limit = max(top_k * 2, 30)
    raw_candidates = store.query(query_embedding=query_vector, n_results=candidate_limit)

    if not raw_candidates:
        return []

    # 3. Rerank candidates with Voyage rerank-2.5
    try:
        reranker = get_reranker()
        reranked = reranker.rerank(query=clean_query, candidates=raw_candidates, top_k=top_k)
    except Exception as e:
        print(f"Warning: Reranker failed ({e}), using initial similarity scores.")
        reranked = raw_candidates[:top_k]

    # 4. Standardize output schema to match Member 1 contract exactly
    formatted_results: List[Dict[str, Any]] = []
    for item in reranked[:top_k]:
        formatted_results.append({
            "chunk_id": str(item.get("chunk_id", "")),
            "text": str(item.get("text", "")),
            "source": str(item.get("source", "unknown")),
            "page": item.get("page"),
            "category": str(item.get("category", "unknown")),
            "score": round(float(item.get("score", 0.0)), 4),
        })

    return formatted_results


if __name__ == "__main__":
    import sys

    test_q = "Gauntlet of Sorrowfell forging"
    print(f"Executing search for: '{test_q}'...")
    try:
        results = search(test_q, top_k=5)
        print(f"Found {len(results)} results:")
        for r in results:
            print(f"  [{r['score']}] ({r['source']}, p.{r['page']}) {r['text'][:80]}...")
    except Exception as err:
        print(f"Search failed as expected without key/index: {err}")
