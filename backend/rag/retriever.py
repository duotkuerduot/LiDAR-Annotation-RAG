from __future__ import annotations

from backend.config import Settings
from backend.rag.embeddings import EmbeddingModel
from backend.rag.keyword_index import KeywordIndex
from backend.rag.vectorstore import FaissVectorStore


class HybridRetriever:
    def __init__(
        self,
        settings: Settings,
        embedding_model: EmbeddingModel,
        vectorstore: FaissVectorStore,
        keyword_index: KeywordIndex,
    ) -> None:
        self.settings = settings
        self.embedding_model = embedding_model
        self.vectorstore = vectorstore
        self.keyword_index = keyword_index

    def retrieve(self, query: str) -> list[dict]:
        query_embedding = self.embedding_model.embed_query(query)
        semantic_results = self.vectorstore.search(query_embedding, self.settings.semantic_top_k)
        keyword_results = self.keyword_index.search(query, self.settings.keyword_top_k)
        merged = self._merge_results(semantic_results, keyword_results)
        return merged[: self.settings.hybrid_top_k]

    def _merge_results(self, semantic_results: list[dict], keyword_results: list[dict]) -> list[dict]:
        fused: dict[str, dict] = {}

        for result in semantic_results:
            key = result["chunk_id"]
            payload = fused.setdefault(key, dict(result))
            payload["semantic_score"] = result.get("semantic_score", 0.0)
            payload["semantic_rank"] = result.get("semantic_rank")
            payload["hybrid_score"] = payload.get("hybrid_score", 0.0) + (
                self.settings.semantic_weight / (60 + result["semantic_rank"])
            )

        for result in keyword_results:
            key = result["chunk_id"]
            payload = fused.setdefault(key, dict(result))
            payload["keyword_score"] = result.get("keyword_score", 0.0)
            payload["keyword_rank"] = result.get("keyword_rank")
            payload["hybrid_score"] = payload.get("hybrid_score", 0.0) + (
                self.settings.keyword_weight / (60 + result["keyword_rank"])
            )

        merged = list(fused.values())
        merged.sort(
            key=lambda item: (
                item.get("hybrid_score", 0.0),
                item.get("semantic_score", 0.0),
                item.get("keyword_score", 0.0),
            ),
            reverse=True,
        )
        return merged
