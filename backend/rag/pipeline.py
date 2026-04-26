from __future__ import annotations

from backend.config import Settings
from backend.rag.embeddings import EmbeddingModel
from backend.rag.generator import GroqAnswerGenerator
from backend.rag.keyword_index import KeywordIndex
from backend.rag.prompt import build_messages
from backend.rag.reranker import Reranker
from backend.rag.retriever import HybridRetriever
from backend.rag.vectorstore import FaissVectorStore
from backend.utils.cleaners import clean_query
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class RAGPipeline:
    def __init__(
        self,
        settings: Settings,
        retriever: HybridRetriever,
        reranker: Reranker,
        generator: GroqAnswerGenerator,
    ) -> None:
        self.settings = settings
        self.retriever = retriever
        self.reranker = reranker
        self.generator = generator

    @classmethod
    def from_settings(cls, settings: Settings) -> "RAGPipeline":
        embedding_model = EmbeddingModel(settings)

        vectorstore = FaissVectorStore()
        vectorstore.load(settings.faiss_index_path, settings.faiss_metadata_path)

        keyword_index = KeywordIndex()
        keyword_index.load(settings.keyword_index_path)

        retriever = HybridRetriever(settings, embedding_model, vectorstore, keyword_index)
        reranker = Reranker(settings)
        generator = GroqAnswerGenerator(settings)
        return cls(settings, retriever, reranker, generator)

    def answer(self, question: str) -> dict:
        cleaned_question = clean_query(question)
        candidates = self.retriever.retrieve(cleaned_question)
        reranked = self.reranker.rerank(cleaned_question, candidates)
        selected = reranked[: self.settings.answer_top_k]

        logger.info(
            "Processed query retrieval",
            extra={
                "extra_data": {
                    "question": cleaned_question,
                    "candidate_count": len(candidates),
                    "selected_chunks": [
                        {
                            "chunk_id": item["chunk_id"],
                            "document_name": item["document_name"],
                            "section_title": item["section_title"],
                            "rerank_score": item.get("rerank_score"),
                        }
                        for item in selected
                    ],
                }
            },
        )

        if not selected:
            return {"answer": "Not found in documentation", "sources": []}

        messages = build_messages(cleaned_question, selected)
        answer = self.generator.generate(messages)
        sources = self._format_sources(selected)
        return {"answer": answer, "sources": sources}

    @staticmethod
    def _format_sources(chunks: list[dict]) -> list[dict]:
        unique: list[dict] = []
        seen: set[tuple[str, str, int | None]] = set()
        for chunk in chunks:
            key = (chunk["document_name"], chunk["section_title"], chunk.get("page_number"))
            if key in seen:
                continue
            seen.add(key)
            unique.append(
                {
                    "document_name": chunk["document_name"],
                    "section_title": chunk["section_title"],
                    "page_number": chunk.get("page_number"),
                    "chunk_type": chunk["chunk_type"],
                }
            )
        return unique
