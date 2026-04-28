#!/bin/sh
set -eu

PORT="${PORT:-7860}"

required_artifacts="data/faiss.index data/faiss_metadata.json data/keyword_index.pkl"
missing_artifacts=0

for artifact in $required_artifacts
do
  if [ ! -f "$artifact" ]; then
    missing_artifacts=1
    break
  fi
done

if [ "$missing_artifacts" -eq 1 ]; then
  if find data/raw_docs -maxdepth 1 -type f ! -name '.gitkeep' | grep -q .; then
    echo "Required search artifacts are missing. Running ingestion before startup..."
    python scripts/run_ingestion.py
  else
    echo "Required search artifacts are missing and data/raw_docs is empty. Starting API in degraded mode."
  fi
fi

exec uvicorn backend.main:app --host 0.0.0.0 --port "$PORT"
