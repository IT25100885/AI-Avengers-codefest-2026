"""
Check whether the Ashen Era Archive has been indexed into the local ChromaDB
vector store yet.

Run this from the repo root:
    python3 check_index_status.py

This directly inspects the vector store's document count rather than
inferring it indirectly from a search() call, so it works even if search()
itself has an issue unrelated to indexing.
"""

from src.retrieval.search import get_vector_store

try:
    store = get_vector_store()
    count = store.count()

    if count == 0:
        print("NOT INDEXED — the vector store exists but is empty.")
        print("Run: python3 -m src.retrieval.index_corpus")
    else:
        print(f"INDEXED — {count} chunks currently in the vector store.")

except Exception as e:
    print(f"Could not check index status: {e}")
    print("This may mean ChromaDB itself isn't set up yet, or a dependency is missing.")
