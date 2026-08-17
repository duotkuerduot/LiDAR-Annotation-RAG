from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(slots=True)
class Settings:
    project_root: Path = field(default_factory=lambda: Path(__file__).resolve().parents[1])
    data_dir: Path = field(init=False)
    raw_docs_dir: Path = field(init=False)
    processed_chunks_path: Path = field(init=False)
    faiss_index_path: Path = field(init=False)
    faiss_metadata_path: Path = field(init=False)
    keyword_index_path: Path = field(init=False)

    embedding_model_name: str = field(
        default_factory=lambda: os.getenv(
            "EMBEDDING_MODEL_NAME",
            "sentence-transformers/all-MiniLM-L6-v2",
        )
    )
    reranker_model_name: str = field(
        default_factory=lambda: os.getenv(
            "RERANKER_MODEL_NAME",
            "cross-encoder/ms-marco-MiniLM-L-6-v2",
        )
    )
    groq_model_name: str = field(
        default_factory=lambda: os.getenv("GROQ_MODEL_NAME", "openai/gpt-oss-20b")
    )
    groq_api_key: str = field(default_factory=lambda: os.getenv("GROQ_API_KEY", ""))

    semantic_top_k: int = field(default_factory=lambda: int(os.getenv("SEMANTIC_TOP_K", "8")))
    keyword_top_k: int = field(default_factory=lambda: int(os.getenv("KEYWORD_TOP_K", "8")))
    hybrid_top_k: int = field(default_factory=lambda: int(os.getenv("HYBRID_TOP_K", "10")))
    rerank_top_k: int = field(default_factory=lambda: int(os.getenv("RERANK_TOP_K", "5")))
    answer_top_k: int = field(default_factory=lambda: int(os.getenv("ANSWER_TOP_K", "4")))

    semantic_weight: float = field(default_factory=lambda: float(os.getenv("SEMANTIC_WEIGHT", "0.55")))
    keyword_weight: float = field(default_factory=lambda: float(os.getenv("KEYWORD_WEIGHT", "0.45")))
    rerank_min_score: float = field(default_factory=lambda: float(os.getenv("RERANK_MIN_SCORE", "0.15")))

    embedding_batch_size: int = field(default_factory=lambda: int(os.getenv("EMBEDDING_BATCH_SIZE", "32")))
    llm_temperature: float = field(default_factory=lambda: float(os.getenv("LLM_TEMPERATURE", "0.1")))
    llm_max_tokens: int = field(default_factory=lambda: int(os.getenv("LLM_MAX_TOKENS", "700")))
    log_level: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO").upper())

    def __post_init__(self) -> None:
        self.data_dir = self.project_root / "data"
        self.raw_docs_dir = self.data_dir / "raw_docs"
        self.processed_chunks_path = self.data_dir / "processed_chunks.json"
        self.faiss_index_path = self.data_dir / "faiss.index"
        self.faiss_metadata_path = self.data_dir / "faiss_metadata.json"
        self.keyword_index_path = self.data_dir / "keyword_index.pkl"


settings = Settings()
