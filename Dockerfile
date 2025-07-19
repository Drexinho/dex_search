# Multi-stage build pro Dex Search aplikaci
FROM ubuntu:22.04 as base

# Nastavení prostředí
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV NODE_ENV=production

# Instalace systémových závislostí
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    git \
    python3 \
    python3-pip \
    python3-venv \
    nodejs \
    npm \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Instalace Ollama
RUN curl -fsSL https://ollama.ai/install.sh | sh

# Vytvoření uživatele pro aplikaci
RUN useradd -m -s /bin/bash dexuser
USER dexuser
WORKDIR /home/dexuser

# Kopírování backend souborů
COPY --chown=dexuser:dexuser backend/ ./backend/
COPY --chown=dexuser:dexuser requirements.txt ./requirements.txt

# Instalace Python závislostí
RUN python3 -m venv backend/venv
RUN backend/venv/bin/pip install --no-cache-dir -r requirements.txt

# Kopírování frontend souborů
COPY --chown=dexuser:dexuser frontend/ ./frontend/

# Instalace Node.js závislostí
RUN cd frontend && npm ci --only=production

# Build frontendu
RUN cd frontend && npm run build

# Vytvoření datových složek
RUN mkdir -p data/documents data/embeddings data/config

# Kopírování konfiguračních souborů
COPY --chown=dexuser:dexuser data/config/ ./data/config/

# Startup script
COPY --chown=dexuser:dexuser start.sh ./start.sh
RUN chmod +x start.sh

# Expose porty
EXPOSE 8000 3000 11434

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Spuštění aplikace
CMD ["./start.sh"] 