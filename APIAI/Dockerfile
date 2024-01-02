FROM nvidia/cuda:12.3.1-devel-ubuntu22.04 AS base

WORKDIR /app/app

ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/app" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN apt-get update && \
    apt-get install -y apt-transport-https && \
    python3 -m pip install --upgrade pip

RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python3 -m pip install -r requirements.txt

USER root

RUN mkdir -p /app/.cache/huggingface && chmod -R 755 /app/.cache/huggingface

RUN chown -R appuser:appuser /app/.cache

ENV HF_HOME=/app/.cache/huggingface

USER appuser

COPY . .


EXPOSE 5050

CMD ["gunicorn", "-c", "gunicorn_config.py", "app.main:app"]
