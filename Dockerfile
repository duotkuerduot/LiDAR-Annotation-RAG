FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=7860 \
    HF_HOME=/tmp/huggingface \
    TRANSFORMERS_CACHE=/tmp/huggingface/transformers \
    SENTENCE_TRANSFORMERS_HOME=/tmp/huggingface/sentence-transformers \
    NLTK_DATA=/app/nltk_data

WORKDIR /app

# 1. Install system dependencies (Still requires root)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    libgl1 \
    libglib2.0-0 \
    libmagic1 \
    tesseract-ocr \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# 2. Create the user first
RUN useradd -m -u 1000 user

# 3. Install Python dependencies as root (for system-wide access)
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 4. Pre-download NLTK data to the app directory
RUN python -m nltk.downloader -d /app/nltk_data punkt averaged_perceptron_tagger

# 5. Copy the rest of the application AND set ownership during copy
COPY --chown=user:user backend ./backend
COPY --chown=user:user data ./data
COPY --chown=user:user scripts ./scripts
COPY --chown=user:user README.md ./

# 6. Final permissions for the start script
RUN chmod +x scripts/start.sh && chown user:user scripts/start.sh

# Switch to non-root user
USER user

EXPOSE 7860

CMD ["/app/scripts/start.sh"]