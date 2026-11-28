FROM python:3.11-slim@sha256:61e01f72680f86a5279ad510818ab7b2ee9f049822589d4e34e33e044360356c

# Install system dependencies (ffmpeg is essential for audio normalization)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install uv for fast, reliable dependency installation
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# Copy package specifications
COPY pyproject.toml README.md ./
COPY src/ ./src/

# Install application and production dependencies
RUN uv venv /opt/venv && \
    . /opt/venv/bin/activate && \
    uv pip install .

ENV PATH="/opt/venv/bin:$PATH"
ENV HOST=0.0.0.0
ENV PORT=8000
ENV DATABASE_PATH=/app/data/sureword.db

# Non-root user
RUN groupadd -r sureword -g 1001 && \
    useradd -r -u 1001 -g sureword -d /app -m sureword && \
    mkdir -p /app/data && \
    chown -R sureword:sureword /app

USER sureword

# Expose port
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/healthz || exit 1

# Run FastAPI via uvicorn
CMD ["uvicorn", "sureword.app:app", "--host", "0.0.0.0", "--port", "8000"]
