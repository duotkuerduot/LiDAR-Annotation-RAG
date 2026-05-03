from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Response, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from backend.config import settings
from backend.rag.pipeline import RAGPipeline
from backend.utils.logger import configure_logging, get_logger

configure_logging(settings.log_level)
logger = get_logger(__name__)


class QueryRequest(BaseModel):
    question: str = Field(min_length=1, description="Annotation question to answer from project documentation.")


class QueryResponse(BaseModel):
    answer: str
    sources: list[str]


class ServiceStatusResponse(BaseModel):
    status: str
    ready: bool
    missing_artifacts: list[str]
    startup_error: str | None = None


def _missing_artifacts() -> list[str]:
    required_paths = (
        settings.faiss_index_path,
        settings.faiss_metadata_path,
        settings.keyword_index_path,
    )
    return [str(path.relative_to(settings.project_root)) for path in required_paths if not path.exists()]


def _service_status() -> ServiceStatusResponse:
    pipeline = getattr(app.state, "pipeline", None)
    startup_error = getattr(app.state, "startup_error", None)
    missing_artifacts = _missing_artifacts()
    ready = pipeline is not None
    return ServiceStatusResponse(
        status="ok",
        ready=ready,
        missing_artifacts=missing_artifacts,
        startup_error=startup_error,
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.pipeline = None
    app.state.startup_error = None
    try:
        app.state.pipeline = RAGPipeline.from_settings(settings)
        logger.info("RAG pipeline initialized")
    except Exception as exc:
        app.state.startup_error = str(exc)
        logger.exception("Failed to initialize RAG pipeline")
    yield


app = FastAPI(
    title="Cruise Annotation RAG Backend",
    version="1.0.0",
    lifespan=lifespan,
)

# --- CORS CONFIGURATION ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://msl-cruise-assistant.lovable.app"],
    allow_credentials=True,
    allow_methods=["POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)


@app.get("/", response_model=ServiceStatusResponse)
async def root() -> ServiceStatusResponse:
    return _service_status()


@app.get("/health", response_model=ServiceStatusResponse)
async def health(response: Response) -> ServiceStatusResponse:
    payload = _service_status()
    if not payload.ready:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return payload


@app.post("/query", response_model=QueryResponse)
async def query_assistant(payload: QueryRequest) -> QueryResponse:
    pipeline: RAGPipeline | None = app.state.pipeline
    if pipeline is None:
        raise HTTPException(
            status_code=503, 
            detail="RAG pipeline is not available. Run ingestion and verify configuration."
        )

    try:
        result = pipeline.answer(payload.question)
        
        # Format sources as a list of strings: "DocName (Page X)"
        formatted_sources = []
        for src in result.get("sources", []):
            source_str = f"{src['document_name']} | {src['section_title']}"
            if src.get("page_number"):
                source_str += f" (Page {src['page_number']})"
            formatted_sources.append(source_str)

        return QueryResponse(
            answer=result["answer"],
            sources=list(set(formatted_sources))  # Use set to remove duplicates
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception(
            "Query handling failed",
            extra={"extra_data": {"question": payload.question}},
        )
        raise HTTPException(status_code=500, detail=f"Failed to process query: {str(exc)}")