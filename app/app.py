"""
Simple Flask Web Service – DevOps Case Study Demo App
Author: Bishwajeet S
"""

import time
import random
from flask import Flask, jsonify, Response
from prometheus_client import (
    Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
)

app = Flask(__name__)

# ──────────────────────────────────────────────────────────────
# Prometheus metrics
# ──────────────────────────────────────────────────────────────
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"]
)
REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["endpoint"]
)
ERROR_COUNT = Counter(
    "http_errors_total",
    "Total HTTP errors",
    ["endpoint"]
)
APP_INFO = Gauge(
    "app_info",
    "Application information",
    ["version", "environment"]
)
APP_INFO.labels(version="1.0.0", environment="production").set(1)

START_TIME = time.time()


# ──────────────────────────────────────────────────────────────
# Routes
# ──────────────────────────────────────────────────────────────
@app.route("/")
def index():
    start = time.time()
    REQUEST_COUNT.labels(method="GET", endpoint="/", status="200").inc()
    REQUEST_LATENCY.labels(endpoint="/").observe(time.time() - start)
    return jsonify({
        "message": "Hello from DevOps Case Study App!",
        "version": "1.0.0",
        "status": "running"
    })


@app.route("/health")
def health():
    REQUEST_COUNT.labels(method="GET", endpoint="/health", status="200").inc()
    return jsonify({
        "status": "healthy",
        "uptime_seconds": round(time.time() - START_TIME, 2)
    })


@app.route("/api/data")
def data():
    start = time.time()
    # Simulate variable latency
    latency = random.uniform(0.01, 0.15)
    time.sleep(latency)
    REQUEST_COUNT.labels(method="GET", endpoint="/api/data", status="200").inc()
    REQUEST_LATENCY.labels(endpoint="/api/data").observe(time.time() - start)
    return jsonify({
        "data": [
            {"id": 1, "name": "Netflix", "challenge": "Monolithic DB corruption 2008"},
            {"id": 2, "name": "Amazon", "challenge": "Outages from monolith in early 2000s"},
            {"id": 3, "name": "Capital One", "challenge": "6-9 month release cycles"},
        ],
        "latency_simulated_ms": round(latency * 1000, 2)
    })


@app.route("/api/error")
def simulate_error():
    ERROR_COUNT.labels(endpoint="/api/error").inc()
    REQUEST_COUNT.labels(method="GET", endpoint="/api/error", status="500").inc()
    return jsonify({"error": "Simulated error for monitoring demo"}), 500


@app.route("/metrics")
def metrics():
    """Prometheus scrape endpoint."""
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
