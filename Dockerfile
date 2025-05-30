#-- Build stage --#
FROM python:3-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    && rm -rf /var/lib/apt/lists/*

ARG USER_UID=1000
RUN useradd -m -u ${USER_UID} appuser
USER appuser

COPY --chown=appuser:appuser server/requirements.txt .

RUN python -m venv /home/appuser/venv && \
    . /home/appuser/venv/bin/activate && \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

#-- Runtime stage --#
FROM python:3-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libglib2.0-0 \
    libnss3 \
    libnspr4 \
    libdbus-1-3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libglib2.0-0 \
    libexpat1 \
    libatspi2.0-0 \
    libx11-6 \
    libxcomposite1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libxcb1 \
    libxkbcommon0 \
    libasound2 \
    && rm -rf /var/lib/apt/lists/*

ARG USER_UID=1000
RUN useradd -m -u ${USER_UID} appuser
USER appuser

COPY --chown=appuser:appuser --from=builder /home/appuser/venv /home/appuser/venv

ENV PATH="/home/appuser/venv/bin:$PATH"
RUN playwright install chromium

ENV PORT=8081
HEALTHCHECK --interval=5s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

CMD ["python", "server/main.py"] 
