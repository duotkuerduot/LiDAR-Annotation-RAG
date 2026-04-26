from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from backend.config import settings
from backend.rag.pipeline import RAGPipeline
from backend.utils.logger import configure_logging, get_logger

configure_logging(settings.log_level)
logger = get_logger(__name__)


class QueryRequest(BaseModel):
    question: str = Field(min_length=1, description="Annotation question to answer from project documentation.")


class SourceResponse(BaseModel):
    document_name: str
    section_title: str
    page_number: int | None = None
    chunk_type: str


class QueryResponse(BaseModel):
    answer: str
    sources: list[SourceResponse]


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.pipeline = None
    try:
        app.state.pipeline = RAGPipeline.from_settings(settings)
        logger.info("RAG pipeline initialized")
    except Exception:
        logger.exception("Failed to initialize RAG pipeline")
    yield


app = FastAPI(
    title="Cruise Annotation RAG Backend",
    version="1.0.0",
    lifespan=lifespan,
)


@app.post("/query", response_model=QueryResponse)
async def query_assistant(payload: QueryRequest) -> QueryResponse:
    pipeline: RAGPipeline | None = app.state.pipeline
    if pipeline is None:
        raise HTTPException(status_code=503, detail="RAG pipeline is not available. Run ingestion and verify configuration.")

    try:
        result = pipeline.answer(payload.question)
        return QueryResponse(**result)
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception(
            "Query handling failed",
            extra={"extra_data": {"question": payload.question}},
        )
        raise HTTPException(status_code=500, detail=f"Failed to answer question: {exc}") from exc
