# VisionKYC - Streamlit app (EasyOCR + DeepFace) in a CPU-only image.
FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    TF_CPP_MIN_LOG_LEVEL=2 \
    HOME=/home/app

# System libraries OpenCV needs at runtime (libGL / glib are not in -slim).
RUN apt-get update \
    && apt-get install -y --no-install-recommends libgl1 libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Run as a normal user, not root.
RUN useradd --create-home --uid 1000 app
WORKDIR /app

# 1) CPU-only PyTorch first (~200 MB instead of ~2.5 GB with CUDA libraries).
RUN pip install --no-cache-dir torch==2.2.1 torchvision==0.17.1 \
    --extra-index-url https://download.pytorch.org/whl/cpu

# 2) The rest of the dependencies (cached unless requirements.txt changes).
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3) Application code.
COPY --chown=app:app . .
RUN mkdir -p logs data/02_intermediate_data \
    && chown -R app:app /app /home/app

USER app

# 4) Bake the model weights into the image so the first request is fast.
#    (If the download fails here, the app simply downloads them on first use.)
RUN python scripts/preload_models.py || echo "WARNING: model preload failed; models will download on first run"

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8501/_stcore/health')" || exit 1

CMD ["streamlit", "run", "app.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true", \
     "--server.fileWatcherType=none", \
     "--browser.gatherUsageStats=false"]
