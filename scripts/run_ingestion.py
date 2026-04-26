from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.config import settings
from backend.rag.chunking import SmartChunker
from backend.rag.embeddings import EmbeddingModel
from backend.rag.ingest import DocumentIngestor
from backend.rag.keyword_index import KeywordIndex
from backend.rag.vectorstore import FaissVectorStore
from backend.utils.logger import configure_logging, get_logger


configure_logging(settings.log_level)
logger = get_logger(__name__)


def main() -> None:
    ingestor = DocumentIngestor()
    documents = ingestor.load_documents(settings.raw_docs_dir)
    if not documents:
        raise RuntimeError(f"No supported documents found in {settings.raw_docs_dir}")

    chunker = SmartChunker()
    chunks = chunker.chunk_documents(documents)
    if not chunks:
        raise RuntimeError("No chunks were produced from the input documents.")

    chunk_dicts = [chunk.to_dict() for chunk in chunks]
    settings.processed_chunks_path.write_text(json.dumps(chunk_dicts, indent=2), encoding="utf-8")

    texts = [chunk["text"] for chunk in chunk_dicts]
    embedding_model = EmbeddingModel(settings)
    embeddings = embedding_model.embed_documents(texts)

    vectorstore = FaissVectorStore()
    vectorstore.build(embeddings, chunk_dicts)
    vectorstore.save(settings.faiss_index_path, settings.faiss_metadata_path)

    keyword_index = KeywordIndex()
    keyword_index.build(texts, chunk_dicts)
    keyword_index.save(settings.keyword_index_path)

    logger.info(
        "Completed ingestion pipeline",
        extra={
            "extra_data": {
                "document_count": len(documents),
                "chunk_count": len(chunks),
                "processed_chunks_path": str(settings.processed_chunks_path),
            }
        },
    )


if __name__ == "__main__":
    main()
