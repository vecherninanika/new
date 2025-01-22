import time

from fastapi import Request, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

# REQUEST_COUNT = Counter("app_requests_total", "Total number of requests", ["method", "endpoint"])
# REQUEST_LATENCY = Histogram("app_request_latency_seconds", "Request latency", ["endpoint"])


# class MetricsMiddleware(BaseHTTPMiddleware):
#     async def dispatch(self, request: Request, call_next):
#         start_time = time.time()
#         REQUEST_COUNT.labels(method=request.method, endpoint=request.url.path).inc()
#         response = await call_next(request)
#         request_latency = time.time() - start_time
#         REQUEST_LATENCY.labels(endpoint=request.url.path).observe(request_latency)
#         return response


DEFAULT_BUCKETS = (
    0.005,
    0.01,
    0.025,
    0.05,
    0.075,
    0.1,
    0.125,
    0.15,
    0.175,
    0.2,
    0.25,
    0.3,
    0.5,
    0.75,
    1.0,
    2.5,
    5.0,
    7.5,
    float("+inf"),
)

# histogram_quantile(0.99, sum(rate(sirius_deps_latency_seconds_bucket[1m])) by (le, endpoint))
# среднее время обработки за 1 мин
DEPS_LATENCY = Histogram(
    "sirius_deps_latency_seconds",
    "",
    ["endpoint"],
    buckets=DEFAULT_BUCKETS,
)


async def metrics(request: Request):
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


# гистограмма для измерения времени выполнения каждой ручки
API_REQUEST_LATENCY = Histogram(
    "api_request_latency_seconds",
    "Время выполнения каждой ручки в секундах",
    ["method", "endpoint"],
    buckets=DEFAULT_BUCKETS,
)

# гистограмма для измерения времени выполнения всех интеграционных методов
INTEGRATION_METHOD_LATENCY = Histogram(
    "integration_method_latency_seconds",
    "Время выполнения всех интеграционных методов в секундах",
    ["method", "integration_point"],
    buckets=DEFAULT_BUCKETS,
)

# счетчик для отслеживания исходящих запросов
OUTGOING_REQUESTS_COUNTER = Counter(
    "sirius_api_outgoing_requests_total",
    "Общее количество исходящих запросов от API",
    ["method", "destination"],
)
# счетчик для отслеживания запросов
REQUESTS_COUNTER = Counter(
    "sirius_api_requests_total",
    "Общее количество запросов к API",
    ["method", "endpoint", "http_status"],
)

# счетчики для успешных запросов
SUCCESSFUL_REQUESTS_COUNTER = Counter(
    "sirius_api_successful_requests_total",
    "Общее количество успешных запросов к API",
    ["method", "endpoint", "http_status"],
)

# счетчики для неуспешных запросов
UNSUCCESSFUL_REQUESTS_COUNTER = Counter(
    "sirius_api_unsuccessful_requests_total",
    "Общее количество неудачных запросов к API",
    ["method", "endpoint", "http_status"],
)


class MeasureLatencyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        endpoint = request.url.path
        method = request.method
        start_time = time.time()

        response = await call_next(request)

        process_time = time.time() - start_time
        DEPS_LATENCY.labels(endpoint=endpoint).observe(process_time)
        API_REQUEST_LATENCY.labels(method=method, endpoint=endpoint).observe(
            process_time,
        )

        # увеличиваем счетчик
        REQUESTS_COUNTER.labels(
            method=request.method,
            endpoint=endpoint,
            http_status=response.status_code,
        ).inc()

        # увеличиваем счетчик успешных/неуспешных запросов
        if 200 <= response.status_code < 400:
            SUCCESSFUL_REQUESTS_COUNTER.labels(
                method=request.method,
                endpoint=endpoint,
                http_status=response.status_code,
            ).inc()
        else:
            UNSUCCESSFUL_REQUESTS_COUNTER.labels(
                method=request.method,
                endpoint=endpoint,
                http_status=response.status_code,
            ).inc()

        return response
