"""
embeddings.py
Provides Voyage AI embedding generation with batching and exponential retry/backoff.
Supports voyage-4 family models (e.g. voyage-4-large for documents, voyage-4-lite for queries).
Includes optional local hash-based mode for offline test suites when USE_MOCK_EMBEDDINGS=1.
"""

import hashlib
import os
from typing import List, Optional

import numpy as np
import voyageai
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential

load_dotenv()

DEFAULT_DOC_MODEL = os.getenv("VOYAGE_DOC_MODEL", "voyage-4-large")
DEFAULT_QUERY_MODEL = os.getenv("VOYAGE_QUERY_MODEL", "voyage-4-lite")
MAX_BATCH_SIZE = 128


def get_voyage_api_key(api_key: Optional[str] = None) -> str:
    """Resolve Voyage AI API key from parameter or environment."""
    key = api_key or os.getenv("VOYAGE_API_KEY")
    if os.getenv("USE_MOCK_EMBEDDINGS") == "1" or key == "mock":
        return "mock"
    if not key or key == "your_voyage_api_key_here":
        raise ValueError(
            "VOYAGE_API_KEY is not set. Please set VOYAGE_API_KEY in your .env file "
            "or pass it directly."
        )
    return key


def _local_hash_embedding(text: str, dim: int = 256) -> List[float]:
    """Deterministic normalized n-gram hash embedding for offline testing."""
    words = text.lower().split()
    vec = np.zeros(dim, dtype=np.float32)
    for w in words:
        h = int(hashlib.md5(w.encode("utf-8")).hexdigest(), 16)
        idx = h % dim
        sign = 1.0 if (h // dim) % 2 == 0 else -1.0
        vec[idx] += sign
    norm = np.linalg.norm(vec)
    if norm > 0:
        vec /= norm
    return vec.tolist()


class VoyageEmbedder:
    """Wrapper for Voyage AI embedding model with rate-limit retries and batching."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        doc_model: str = DEFAULT_DOC_MODEL,
        query_model: str = DEFAULT_QUERY_MODEL,
    ):
        self.api_key = get_voyage_api_key(api_key)
        self.doc_model = doc_model
        self.query_model = query_model
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
    def _embed_batch(
        self,
        texts: List[str],
        model: str,
        input_type: Optional[str] = None,
    ) -> List[List[float]]:
        """Call Voyage API on a single batch with retry logic."""
        if self.is_mock:
            return [_local_hash_embedding(t) for t in texts]

        response = self.client.embed(
            texts=texts,
            model=model,
            input_type=input_type,
        )
        return response.embeddings

    def embed_documents(
        self,
        texts: List[str],
        batch_size: int = MAX_BATCH_SIZE,
    ) -> List[List[float]]:
        """
        Generate embeddings for a list of document passages.

        Args:
            texts: List of text strings to embed.
            batch_size: Number of texts per API call (max 128).

        Returns:
            List of embedding vectors (floats).
        """
        all_embeddings: List[List[float]] = []
        batch_size = min(batch_size, MAX_BATCH_SIZE)

        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            embeddings = self._embed_batch(
                texts=batch,
                model=self.doc_model,
                input_type="document",
            )
            all_embeddings.extend(embeddings)

        return all_embeddings

    def embed_query(self, query: str) -> List[float]:
        """
        Generate embedding for a single search query.

        Args:
            query: The search query string.

        Returns:
            Embedding vector as list of floats.
        """
        clean_query = query.strip()
        if not clean_query:
            raise ValueError("Query string cannot be empty.")

        embeddings = self._embed_batch(
            texts=[clean_query],
            model=self.query_model,
            input_type="query",
        )
        return embeddings[0]


if __name__ == "__main__":
    print("Testing VoyageEmbedder...")
    try:
        embedder = VoyageEmbedder()
        print(f"Initialized VoyageEmbedder with model: {embedder.doc_model} (mock={embedder.is_mock})")
    except ValueError as e:
        print(f"Expected without API key: {e}")
