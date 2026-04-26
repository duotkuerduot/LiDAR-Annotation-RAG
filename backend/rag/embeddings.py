from __future__ import annotations

from typing import Sequence

import numpy as np

from backend.config import Settings


class EmbeddingModel:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as exc:
            raise ImportError(
                "Install sentence-transformers to generate embeddings."
            ) from exc

        self.model = SentenceTransformer(settings.embedding_model_name)

    def embed_documents(self, texts: Sequence[str]) -> np.ndarray:
        embeddings = self.model.encode(
            list(texts),
            batch_size=self.settings.embedding_batch_size,
            normalize_embeddings=True,
            show_progress_bar=False,
            convert_to_numpy=True,
        )
        return embeddings.astype("float32")

    def embed_query(self, text: str) -> np.ndarray:
        embedding = self.model.encode(
            [text],
            normalize_embeddings=True,
            show_progress_bar=False,
            convert_to_numpy=True,
        )
        return embedding.astype("float32")[0]
