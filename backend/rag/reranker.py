from __future__ import annotations

from collections import Counter

from backend.config import Settings
from backend.utils.cleaners import tokenize_for_search


class Reranker:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._cross_encoder = None
        self._fallback_mode = False

        try:
            from sentence_transformers import CrossEncoder

            self._cross_encoder = CrossEncoder(settings.reranker_model_name)
        except Exception:
            self._fallback_mode = True

    def rerank(self, query: str, candidates: list[dict]) -> list[dict]:
        if not candidates:
            return []

        if self._fallback_mode or self._cross_encoder is None:
            scored = []
            for candidate in candidates:
                score = self._fallback_score(query, candidate["text"])
                item = dict(candidate)
                item["rerank_score"] = score
                scored.append(item)
        else:
            pairs = [(query, candidate["text"]) for candidate in candidates]
            scores = self._cross_encoder.predict(pairs)
            scored = []
            for candidate, score in zip(candidates, scores):
                item = dict(candidate)
                item["rerank_score"] = float(score)
                scored.append(item)

        scored.sort(key=lambda item: item["rerank_score"], reverse=True)
        filtered = [item for item in scored if item["rerank_score"] >= self.settings.rerank_min_score]
        if not filtered:
            filtered = scored
        return filtered[: self.settings.rerank_top_k]

    @staticmethod
    def _fallback_score(query: str, text: str) -> float:
        query_tokens = tokenize_for_search(query)
        text_tokens = tokenize_for_search(text)
        if not query_tokens or not text_tokens:
            return 0.0
        query_counter = Counter(query_tokens)
        text_counter = Counter(text_tokens)
        overlap = sum(min(query_counter[token], text_counter[token]) for token in query_counter)
        return overlap / max(len(set(query_tokens)), 1)
