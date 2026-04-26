from __future__ import annotations

import pickle
from pathlib import Path
from typing import Sequence

import numpy as np

from backend.utils.cleaners import tokenize_for_search
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class KeywordIndex:
    def __init__(self) -> None:
        try:
            from rank_bm25 import BM25Okapi
        except ImportError as exc:
            raise ImportError("Install rank-bm25 to use keyword retrieval.") from exc

        self.BM25Okapi = BM25Okapi
        self.bm25 = None
        self.metadata: list[dict] = []
        self.tokenized_corpus: list[list[str]] = []

    def build(self, texts: Sequence[str], metadata: Sequence[dict]) -> None:
        self.tokenized_corpus = [tokenize_for_search(text) for text in texts]
        self.bm25 = self.BM25Okapi(self.tokenized_corpus)
        self.metadata = [dict(item) for item in metadata]

    def save(self, path: Path) -> None:
        if self.bm25 is None:
            raise RuntimeError("Cannot save an empty keyword index.")
        payload = {
            "tokenized_corpus": self.tokenized_corpus,
            "metadata": self.metadata,
        }
        path.write_bytes(pickle.dumps(payload))
        logger.info("Saved keyword index", extra={"extra_data": {"path": str(path)}})

    def load(self, path: Path) -> None:
        payload = pickle.loads(path.read_bytes())
        self.tokenized_corpus = payload["tokenized_corpus"]
        self.metadata = payload["metadata"]
        self.bm25 = self.BM25Okapi(self.tokenized_corpus)

    def search(self, query: str, top_k: int) -> list[dict]:
        if self.bm25 is None:
            raise RuntimeError("Keyword index is not loaded.")
        query_tokens = tokenize_for_search(query)
        scores = np.asarray(self.bm25.get_scores(query_tokens), dtype=float)
        if scores.size == 0:
            return []
        top_indices = scores.argsort()[::-1][:top_k]
        results: list[dict] = []
        for rank, idx in enumerate(top_indices, start=1):
            score = float(scores[idx])
            if score <= 0:
                continue
            payload = dict(self.metadata[int(idx)])
            payload["keyword_score"] = score
            payload["keyword_rank"] = rank
            results.append(payload)
        return results
