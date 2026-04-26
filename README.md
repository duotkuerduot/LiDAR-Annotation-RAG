# Cruise Annotation RAG Backend

Production-oriented Retrieval-Augmented Generation backend for Cruise LiDAR annotation support. The system ingests internal project documentation, performs hybrid retrieval across semantic and keyword indexes, reranks evidence, and returns grounded answers with citations so frontline labelers can resolve policy questions without escalating to QA.

## Architecture

1. `scripts/run_ingestion.py` loads source files from `data/raw_docs/`.
2. `backend/rag/ingest.py` extracts structured text from PDF, DOCX, and TXT files.
3. `backend/rag/chunking.py` uses structure-aware chunking to split by headings, rules, examples, and bullet points instead of fixed token windows.
4. `backend/rag/embeddings.py` creates dense vectors for chunks.
5. `backend/rag/vectorstore.py` stores embeddings and chunk metadata in FAISS.
6. `backend/rag/keyword_index.py` builds a BM25 keyword index.
7. `backend/rag/retriever.py` runs hybrid retrieval over FAISS and BM25, then fuses the results.
8. `backend/rag/reranker.py` reranks retrieved chunks with a lightweight cross-encoder, with a lexical fallback if the cross-encoder is unavailable.
9. `backend/rag/prompt.py` builds a grounded prompt with explicit citation requirements.
10. `backend/rag/generator.py` calls the Groq API for final answer generation.
11. `backend/rag/pipeline.py` orchestrates the full query flow.
12. `backend/main.py` exposes the system through FastAPI.

## Project Layout

```text
MSL Cruise/
├── backend/
│   ├── config.py
│   ├── main.py
│   ├── rag/
│   │   ├── chunking.py
│   │   ├── embeddings.py
│   │   ├── generator.py
│   │   ├── ingest.py
│   │   ├── keyword_index.py
│   │   ├── pipeline.py
│   │   ├── prompt.py
│   │   ├── reranker.py
│   │   ├── retriever.py
│   │   └── vectorstore.py
│   └── utils/
│       ├── cleaners.py
│       └── logger.py
├── data/
│   └── raw_docs/
├── scripts/
│   └── run_ingestion.py
├── README.md
└── requirements.txt
```

## Requirements

Install Python 3.10+ and the dependencies below:

```bash
pip install fastapi uvicorn pydantic sentence-transformers faiss-cpu rank-bm25 groq pypdf python-docx numpy
```

Set your Groq API key:

```bash
set GROQ_API_KEY=your_groq_api_key
```

Optional configuration:

```bash
set GROQ_MODEL_NAME=llama-3.1-8b-instant
set EMBEDDING_MODEL_NAME=sentence-transformers/all-MiniLM-L6-v2
set RERANKER_MODEL_NAME=cross-encoder/ms-marco-MiniLM-L-6-v2
```

## Add Documentation

Place the 26 Cruise project files inside:

```text
data/raw_docs/
```

Supported formats:

- PDF
- DOCX
- TXT

## Run Ingestion

From the project root:

```bash
python scripts/run_ingestion.py
```

This creates:

- `data/processed_chunks.json`
- `data/faiss.index`
- `data/faiss_metadata.json`
- `data/keyword_index.pkl`

## Run The API

From the project root:

```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

## Example Request

```bash
curl -X POST "http://127.0.0.1:8000/query" ^
  -H "Content-Type: application/json" ^
  -d "{\"question\":\"When should I mark an object as occluded?\"}"
```

Example response:

```json
{
  "answer": "Answer:\nMark an object as occluded when...\n\nSources:\n* Document: lidar_rules.pdf | Section: Occlusion Handling",
  "sources": [
    {
      "document_name": "lidar_rules.pdf",
      "section_title": "Occlusion Handling",
      "page_number": 14,
      "chunk_type": "rule"
    }
  ]
}
```

## Notes

- The answer path is grounded only in retrieved documentation context.
- If the answer is not present in the indexed documents, the system returns `Not found in documentation`.
- Retrieval quality depends heavily on the quality and consistency of source documents.
