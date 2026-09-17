"""Hybrid semantic + keyword retrieval for GaiaScout."""

import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List

from dotenv import load_dotenv
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer
import chromadb

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = PROJECT_ROOT / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from knowledge.knowledge_base import get_all_chunks  # noqa: E402

load_dotenv(PROJECT_ROOT / ".env")

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
DEFAULT_CHROMA_DIR = BACKEND_DIR / "data" / "chroma_db"
DOMAINS = [
    "soil_health",
    "land_use",
    "biodiversity_indicators",
    "climate_factors",
    "human_impact",
]


def resolve_path(value: str | None, default: Path) -> Path:
    path = Path(value) if value else default
    return path if path.is_absolute() else PROJECT_ROOT / path


def tokenize(text: str) -> List[str]:
    return re.findall(r"[a-z0-9_]+", text.lower())


class HybridRetriever:
    """Fuse Chroma semantic search and BM25 keyword search with RRF."""

    def __init__(self, top_k: int = 5) -> None:
        self.top_k = top_k
        chroma_dir = resolve_path(os.getenv("CHROMA_PERSIST_DIR"), DEFAULT_CHROMA_DIR)

        if not chroma_dir.exists():
            raise FileNotFoundError(
                f"ChromaDB not found at {chroma_dir}. Run "
                "python backend/knowledge/ingestion.py first."
            )

        self.embedding_model = SentenceTransformer(MODEL_NAME)
        self.client = chromadb.PersistentClient(path=str(chroma_dir))
        self.collections = {
            domain: self.client.get_collection(domain) for domain in DOMAINS
        }

        self.chunks = get_all_chunks()
        self.bm25 = BM25Okapi([tokenize(chunk["text"]) for chunk in self.chunks])

    @staticmethod
    def _global_id(index: int, chunk: Dict[str, Any]) -> str:
        """Match the local per-domain IDs created by ingestion.py."""
        domain_index = 0
        for prior in get_all_chunks()[:index]:
            if prior["domain"] == chunk["domain"]:
                domain_index += 1
        return f"{chunk['domain']}_{domain_index}"

    def _semantic_search(self, query: str) -> List[Dict[str, Any]]:
        query_embedding = self.embedding_model.encode(
            [query], normalize_embeddings=True
        )[0].tolist()

        hits: List[Dict[str, Any]] = []

        for collection in self.collections.values():
            count = collection.count()
            if count == 0:
                continue

            result = collection.query(
                query_embeddings=[query_embedding],
                n_results=min(self.top_k, count),
                include=["documents", "metadatas"],
            )

            ids = result.get("ids", [[]])[0]
            documents = result.get("documents", [[]])[0]
            metadatas = result.get("metadatas", [[]])[0]

            for rank, (doc_id, document, metadata) in enumerate(
                zip(ids, documents, metadatas), start=1
            ):
                hits.append(
                    {
                        "id": doc_id,
                        "text": document,
                        "metadata": metadata,
                        "rank": rank,
                    }
                )

        return hits

    def _keyword_search(self, query: str) -> List[Dict[str, Any]]:
        scores = self.bm25.get_scores(tokenize(query))
        ranked = sorted(enumerate(scores), key=lambda item: item[1], reverse=True)

        hits: List[Dict[str, Any]] = []
        for index, score in ranked[: self.top_k]:
            chunk = self.chunks[index]
            hits.append(
                {
                    "id": self._global_id(index, chunk),
                    "text": chunk["text"],
                    "metadata": {
                        "domain": chunk["domain"],
                        "topic": chunk["topic"],
                        "source": chunk["source"],
                        "year": int(chunk["year"]),
                        "source_url": chunk["source_url"],
                    },
                    "rank": len(hits) + 1,
                    "bm25_score": float(score),
                }
            )
        return hits

    def search(self, query: str, top_k: int | None = None) -> List[Dict[str, Any]]:
        """Return the top evidence chunks using Reciprocal Rank Fusion."""
        final_k = top_k or self.top_k
        fused: Dict[str, Dict[str, Any]] = {}
        rrf_constant = 60

        for hit in self._semantic_search(query):
            entry = fused.setdefault(
                hit["id"],
                {
                    "id": hit["id"],
                    "text": hit["text"],
                    "metadata": hit["metadata"],
                    "semantic_rank": None,
                    "keyword_rank": None,
                    "rrf_score": 0.0,
                },
            )
            entry["semantic_rank"] = hit["rank"]
            entry["rrf_score"] += 1 / (rrf_constant + hit["rank"])

        for hit in self._keyword_search(query):
            entry = fused.setdefault(
                hit["id"],
                {
                    "id": hit["id"],
                    "text": hit["text"],
                    "metadata": hit["metadata"],
                    "semantic_rank": None,
                    "keyword_rank": None,
                    "rrf_score": 0.0,
                },
            )
            entry["keyword_rank"] = hit["rank"]
            entry["rrf_score"] += 1 / (rrf_constant + hit["rank"])

        return sorted(
            fused.values(),
            key=lambda item: item["rrf_score"],
            reverse=True,
        )[:final_k]


if __name__ == "__main__":
    retriever = HybridRetriever(top_k=5)
    results = retriever.search(
        "How can low soil organic carbon and low rainfall affect biodiversity?"
    )
    for index, result in enumerate(results, start=1):
        print(f"\n[{index}] {result['metadata']['topic']}")
        print(f"Source: {result['metadata']['source']}")
        print(result["text"][:400] + "...")
