"""
reranker.py
Voyage AI reranker using the rerank-2.5 model.
Reranks retrieved candidate passages to improve ordering before returning to the agent.
Supports offline test mode when USE_MOCK_EMBEDDINGS=1 or api_key='mock'.
"""

import os
import re
from typing import Any, Dict, List, Optional

import voyageai
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential

from src.retrieval.embeddings import get_voyage_api_key

load_dotenv()

DEFAULT_RERANK_MODEL = os.getenv("VOYAGE_RERANK_MODEL", "rerank-2.5")


class VoyageReranker:
    """Wrapper for Voyage AI reranking model with retry logic."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = DEFAULT_RERANK_MODEL,
    ):
        self.api_key = get_voyage_api_key(api_key)
        self.model = model
        self.is_mock = self.api_key == "mock"

        if not self.is_mock:
            self.client = voyageai.Client(api_key=self.api_key)
        else:
            self.client = None

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        reraise=True,
    )
    def _call_rerank(
        self,
        query: str,
        documents: List[str],
        top_k: Optional[int] = None,
    ):
        """Call Voyage rerank API with retry mechanism."""
        return self.client.rerank(
            query=query,
            documents=documents,
            model=self.model,
            top_k=top_k,
        )

    def rerank(
        self,
        query: str,
        candidates: List[Dict[str, Any]],
        top_k: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Rerank candidate chunks according to semantic relevance to the query.

        Args:
            query: The search query string.
            candidates: List of candidate chunk dicts, each containing 'text'.
            top_k: Optional limit on the number of returned chunks.

        Returns:
            List of candidate chunk dicts updated with reranker scores,
            ordered by descending relevance.
        """
        if not candidates:
            return []

        clean_query = query.strip()
        if not clean_query:
            return candidates[:top_k] if top_k else candidates

        effective_top_k = min(top_k or len(candidates), len(candidates))

        if self.is_mock:
            # Local token overlap reranking for offline testing
            q_terms = set(re.findall(r"\w+", clean_query.lower()))
            scored = []
            for c in candidates:
                c_text = c.get("text", "").lower()
                c_terms = set(re.findall(r"\w+", c_text))
                overlap = len(q_terms & c_terms)
                score = min(0.99, c.get("score", 0.5) + (overlap * 0.05))
                item_copy = dict(c)
                item_copy["score"] = round(score, 4)
                scored.append(item_copy)
            scored.sort(key=lambda x: x["score"], reverse=True)
            return scored[:effective_top_k]

        documents = [c.get("text", "") for c in candidates]
        try:
            rerank_result = self._call_rerank(
                query=clean_query,
                documents=documents,
                top_k=effective_top_k,
            )

            reranked_chunks: List[Dict[str, Any]] = []
            for r in rerank_result.results:
                orig_item = candidates[r.index]
                item_copy = dict(orig_item)
                item_copy["score"] = round(float(r.relevance_score), 4)
                reranked_chunks.append(item_copy)

            return reranked_chunks
        except Exception as e:
            print(f"Warning: Voyage reranker call failed: {e}. Falling back to vector store rank.")
            return candidates[:effective_top_k]


if __name__ == "__main__":
    print("Testing VoyageReranker...")
    try:
        reranker = VoyageReranker()
        print(f"Initialized VoyageReranker with model: {reranker.model} (mock={reranker.is_mock})")
    except ValueError as e:
        print(f"Expected without API key: {e}")
