FROM nvidia/cuda:12.3.1-devel-ubuntu22.04 AS base

WORKDIR /app/app

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN apt-get update && \
    apt-get install -y apt-transport-https && \
    python3 -m pip install --upgrade pip

COPY . .

RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python3 -m pip install -r requirements.txt

EXPOSE 5050

CMD ["gunicorn", "-c", "gunicorn_config.py", "app.main:app"]
