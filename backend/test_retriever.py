"""Minimal verification for GaiaScout hybrid retrieval."""

import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BACKEND_DIR))

from knowledge.vector_store import HybridRetriever  # noqa: E402


def test_hybrid_retrieval() -> None:
    retriever = HybridRetriever(top_k=5)
    results = retriever.search(
        "low soil organic carbon, drought, and biodiversity loss"
    )

    assert results, "Retriever returned no results."
    assert len(results) <= 5

    for result in results:
        assert result["text"]
        assert result["metadata"]["source"]
        assert result["metadata"]["source_url"]

    print("Hybrid retrieval test passed.")
    print(f"Top result: {results[0]['metadata']['topic']}")


if __name__ == "__main__":
    test_hybrid_retrieval()
