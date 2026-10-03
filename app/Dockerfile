# ─────────────────────────────────────────────
# Stage 1 – Builder
# ─────────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ─────────────────────────────────────────────
# Stage 2 – Runtime
# ─────────────────────────────────────────────
FROM python:3.11-slim AS runtime

LABEL maintainer="Bishwajeet S <bishwajeet@devops-demo.local>"
LABEL version="1.0.0"
LABEL description="DevOps Case Study – Flask Microservice"

# Non-root user (UID 1000 matches Kubernetes securityContext.runAsUser)
RUN groupadd -r appgroup -g 1000 && useradd -r -u 1000 -g appgroup appuser

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application source
COPY app.py .

# Switch to non-root
USER appuser

EXPOSE 5000

# Health-check so k8s and compose can probe it
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')"

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "60", "app:app"]
