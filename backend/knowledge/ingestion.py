"""Build the local ChromaDB index from GaiaScout's curated knowledge corpus."""

import os
import sys
from pathlib import Path
from typing import Dict, List

from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
import chromadb

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = PROJECT_ROOT / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from knowledge.knowledge_base import ALL_CHUNKS, get_all_chunks  # noqa: E402

load_dotenv(PROJECT_ROOT / ".env")

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
DEFAULT_CHROMA_DIR = BACKEND_DIR / "data" / "chroma_db"


def resolve_path(value: str | None, default: Path) -> Path:
    path = Path(value) if value else default
    return path if path.is_absolute() else PROJECT_ROOT / path


CHROMA_DIR = resolve_path(os.getenv("CHROMA_PERSIST_DIR"), DEFAULT_CHROMA_DIR)


def build_chroma_index() -> int:
    """Embed all curated chunks locally and upsert them into 5 Chroma collections."""
    chunks = get_all_chunks()
    if not chunks:
        raise RuntimeError("Knowledge corpus is empty.")

    print(f"Loading embedding model: {MODEL_NAME}")
    model = SentenceTransformer(MODEL_NAME)
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))

    total_indexed = 0

    for domain, domain_chunks in ALL_CHUNKS.items():
        collection = client.get_or_create_collection(
            name=domain,
            metadata={"description": f"GaiaScout {domain} scientific knowledge"},
        )

        documents = [chunk["text"].strip() for chunk in domain_chunks]
        embeddings = model.encode(documents, normalize_embeddings=True).tolist()
        ids = [f"{domain}_{i}" for i in range(len(domain_chunks))]
        metadatas: List[Dict] = []

        for chunk in domain_chunks:
            metadatas.append(
                {
                    "domain": chunk["domain"],
                    "topic": chunk["topic"],
                    "source": chunk["source"],
                    "year": int(chunk["year"]),
                    "source_url": chunk["source_url"],
                }
            )

        collection.upsert(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
        )

        print(f"{domain}: {len(domain_chunks)} chunks indexed")
        total_indexed += len(domain_chunks)

    print(f"ChromaDB ready: {CHROMA_DIR}")
    print(f"Total chunks indexed: {total_indexed}")
    return total_indexed


if __name__ == "__main__":
    build_chroma_index()
