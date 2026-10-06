FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    HF_HOME=/models_cache \
    KMP_DUPLICATE_LIB_OK=TRUE \
    CUDA_VISIBLE_DEVICES=-1

# System deps: gcc+libpq for psycopg2 (source build), libgomp1 for faiss/torch
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential libpq-dev libgomp1 curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# requirements.txt in the repo is UTF-16; convert to UTF-8 for pip
COPY requirements.txt /tmp/requirements.utf16.txt
RUN python -c "open('/tmp/requirements.txt','w',encoding='utf-8').write(open('/tmp/requirements.utf16.txt','rb').read().decode('utf-16'))" \
    && pip install --upgrade pip \
    && pip install -r /tmp/requirements.txt

# App source
COPY . /app

# Pre-download HF models so startup doesn't pay the download cost (baked into image)
RUN python -c "import model_loader; print('models cached')"

EXPOSE 8080
# --preload loads models once in master, workers share via copy-on-write (no code change)
CMD ["gunicorn", "--preload", "--workers", "2", "--bind", "0.0.0.0:8080", "--timeout", "120", "app:app"]
