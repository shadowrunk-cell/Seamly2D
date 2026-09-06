FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# docker CLI — для рендера лекал сервис запускает контейнер seamly-renderer
# через демон хоста (см. docker-compose.yml, volume docker.sock).
# Debian 13 docker.io не поставляет бинарь docker — ставим static CLI.
RUN apt-get update && \
    apt-get install -y --no-install-recommends ca-certificates curl && \
    VER=$(curl -fsSL https://download.docker.com/linux/static/stable/x86_64/ | grep -oE 'docker-[0-9]+\.[0-9]+\.[0-9]+\.tgz' | sort -V | tail -1) && \
    curl -fsSL "https://download.docker.com/linux/static/stable/x86_64/${VER}" | tar -xz -C /tmp && \
    mv /tmp/docker/docker /usr/local/bin/docker && \
    rm -rf /tmp/docker && \
    apt-get purge -y curl && apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY templates ./templates
COPY providers.example.yaml .

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]