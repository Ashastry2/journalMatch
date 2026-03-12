# JournalMatch — Docker image
# Used for Hugging Face Spaces deployment (free hosting, no credit card required).
# HF Spaces expects port 7860; locally Flask defaults to 5000 via run.bat / run.sh.

FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first (cached layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download SPECTER model into the image so the first request is fast
RUN python -c "from sentence_transformers import SentenceTransformer; \
    SentenceTransformer('allenai-specter'); print('SPECTER model cached.')"

# Copy application code
COPY . .

# HF Spaces listens on 7860; local runs use PORT env var (default 5000)
EXPOSE 7860

ENV PORT=7860

CMD ["python", "app.py"]
