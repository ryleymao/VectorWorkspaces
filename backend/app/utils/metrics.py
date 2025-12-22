from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response


request_count = Counter(
    "http_requests_total",
    "Total number of HTTP requests",
    ["method", "endpoint", "status_code"]
)

request_duration = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"]
)

active_connections = Gauge(
    "active_connections",
    "Number of active database connections"
)

error_count = Counter(
    "errors_total",
    "Total number of errors",
    ["error_type", "endpoint"]
)


def get_metrics() -> Response:
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


def record_request(method: str, endpoint: str, status_code: int, duration: float):
    request_count.labels(method=method, endpoint=endpoint, status_code=status_code).inc()
    request_duration.labels(method=method, endpoint=endpoint).observe(duration)


def record_error(error_type: str, endpoint: str):
    error_count.labels(error_type=error_type, endpoint=endpoint).inc()
