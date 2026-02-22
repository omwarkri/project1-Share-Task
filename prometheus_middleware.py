"""
Prometheus metrics middleware for Django
Exposes application metrics at /metrics endpoint
"""

from prometheus_client import Counter, Histogram, generate_latest
from prometheus_client.core import CollectorRegistry
import time
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponse
import re

# Create a registry for metrics
REGISTRY = CollectorRegistry()

# Define metrics
REQUEST_COUNT = Counter(
    'django_http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status'],
    registry=REGISTRY
)

REQUEST_LATENCY = Histogram(
    'django_http_request_duration_seconds',
    'HTTP request latency in seconds',
    ['method', 'endpoint'],
    registry=REGISTRY
)

REQUESTS_IN_PROGRESS = Counter(
    'django_http_requests_in_progress',
    'HTTP requests in progress',
    ['method', 'endpoint'],
    registry=REGISTRY
)


class PrometheusMiddleware(MiddlewareMixin):
    """
    Middleware to track HTTP requests and expose metrics
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)

    def process_request(self, request):
        request.start_time = time.time()
        endpoint = self._get_endpoint(request)
        REQUESTS_IN_PROGRESS.labels(
            method=request.method,
            endpoint=endpoint
        ).inc()

    def process_response(self, request, response):
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            endpoint = self._get_endpoint(request)
            
            REQUEST_COUNT.labels(
                method=request.method,
                endpoint=endpoint,
                status=response.status_code
            ).inc()
            
            REQUEST_LATENCY.labels(
                method=request.method,
                endpoint=endpoint
            ).observe(duration)
            
            REQUESTS_IN_PROGRESS.labels(
                method=request.method,
                endpoint=endpoint
            ).dec()

        return response

    @staticmethod
    def _get_endpoint(request):
        """Extract endpoint name from request path"""
        path = request.path
        # Simplify path for metrics (remove IDs)
        path = re.sub(r'/\d+/', '/id/', path)
        return path[:100]  # Limit length


def metrics_view(request):
    """
    View to expose Prometheus metrics
    Add to your urls.py: path('metrics', views.metrics_view),
    """
    return HttpResponse(generate_latest(REGISTRY), content_type='text/plain; charset=utf-8')
