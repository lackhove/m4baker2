FROM python:3.12-slim AS builder

ENV PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

COPY pyproject.toml README.md uv.lock ./
COPY src ./src

RUN python -m pip install --upgrade pip build && python -m build --wheel

FROM python:3.12-slim

ENV PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install --yes --no-install-recommends ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /work

COPY --from=builder /app/dist/*.whl /tmp/

RUN python -m pip install /tmp/*.whl \
    && rm -f /tmp/*.whl

ENTRYPOINT ["m4baker"]
