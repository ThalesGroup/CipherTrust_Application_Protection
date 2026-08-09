# CipherTrust Manager Metrics Viewer
#
# Security: never COPY .env, data/, certs, DBs, or _deploy*.py scripts.
# Secrets (SECRET_KEY, appliance passwords) are supplied at runtime via
# env vars / the UI and stored only under the /app/data volume.
FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_HOST=0.0.0.0 \
    FLASK_PORT=5050 \
    FLASK_DEBUG=false \
    FLASK_HTTPS=false \
    DATABASE_PATH=/app/data/cm_metrics.db \
    SSL_CERT_PATH=/app/data/certs/cert.pem \
    SSL_KEY_PATH=/app/data/certs/key.pem

WORKDIR /app

# Minimal OS deps (certs for outbound HTTPS to CM appliances)
RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Explicit allow-list only — do not COPY . or any secret-bearing paths.
COPY cm_metrics ./cm_metrics
COPY static ./static
COPY templates ./templates
COPY vendor ./vendor
COPY tools/ksctl-linux-amd64 ./tools/ksctl-linux-amd64
COPY run.py .

RUN chmod +x /app/tools/ksctl-linux-amd64 \
    && ln -sf /app/tools/ksctl-linux-amd64 /app/tools/ksctl \
    && mkdir -p /app/data/certs /app/data/healthcheck \
    && test ! -e /app/.env \
    && test ! -e /app/data/cm_metrics.db

VOLUME ["/app/data"]

EXPOSE 5050

# Optional HTTPS (set FLASK_HTTPS=true) also uses 5050; dual HTTP uses FLASK_HTTP_PORT.
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:5050/', timeout=3)" || exit 1

CMD ["python", "run.py"]
