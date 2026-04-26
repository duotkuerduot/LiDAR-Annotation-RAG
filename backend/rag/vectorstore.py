from __future__ import annotations

import json
from pathlib import Path
from typing import Sequence

import numpy as np

from backend.utils.logger import get_logger

logger = get_logger(__name__)


class FaissVectorStore:
    def __init__(self) -> None:
        try:
            import faiss
        except ImportError as exc:
            raise ImportError("Install faiss-cpu to use the FAISS vector store.") from exc

        self.faiss = faiss
        self.index = None
        self.metadata: list[dict] = []

    def build(self, embeddings: np.ndarray, metadata: Sequence[dict]) -> None:
        if embeddings.ndim != 2:
            raise ValueError("Embeddings must be a 2D array.")
        dimension = embeddings.shape[1]
        self.index = self.faiss.IndexFlatIP(dimension)
        self.index.add(embeddings)
        self.metadata = [dict(item) for item in metadata]

    def save(self, index_path: Path, metadata_path: Path) -> None:
        if self.index is None:
            raise RuntimeError("Cannot save an empty FAISS index.")
        index_path.parent.mkdir(parents=True, exist_ok=True)
        self.faiss.write_index(self.index, str(index_path))
        metadata_path.write_text(json.dumps(self.metadata, indent=2), encoding="utf-8")
        logger.info(
            "Saved FAISS index",
            extra={"extra_data": {"index_path": str(index_path), "metadata_path": str(metadata_path)}},
        )

    def load(self, index_path: Path, metadata_path: Path) -> None:
        self.index = self.faiss.read_index(str(index_path))
        self.metadata = json.loads(metadata_path.read_text(encoding="utf-8"))

    def search(self, query_embedding: np.ndarray, top_k: int) -> list[dict]:
        if self.index is None:
            raise RuntimeError("Vector store is not loaded.")
        query = np.asarray([query_embedding], dtype="float32")
        scores, indices = self.index.search(query, top_k)
        results: list[dict] = []
        for rank, (score, idx) in enumerate(zip(scores[0], indices[0]), start=1):
            if idx == -1:
                continue
            payload = dict(self.metadata[idx])
            payload["semantic_score"] = float(score)
            payload["semantic_rank"] = rank
            results.append(payload)
        return results
