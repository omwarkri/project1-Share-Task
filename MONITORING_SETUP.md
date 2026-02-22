# Prometheus & Grafana Monitoring Setup

This guide explains how to set up and use Prometheus and Grafana monitoring with your Django application.

## What Was Added

### 1. **prometheus.yml**
Configuration file for Prometheus that defines:
- Django app metrics collection
- Redis exporter metrics
- PostgreSQL exporter metrics

### 2. **prometheus_middleware.py**
Django middleware that:
- Tracks HTTP request count by method, endpoint, and status code
- Measures request latency
- Exposes metrics at the `/metrics` endpoint

### 3. **Docker Compose Updates**
Added services:
- **prometheus**: Collects and stores metrics
- **grafana**: Visualizes metrics with dashboards
- **redis-exporter**: Exports Redis metrics
- **postgres-exporter**: Exports PostgreSQL metrics

### 4. **requirements.txt**
Added `prometheus-client==0.20.0` for metrics collection

## Quick Start

### Option 1: Using the Startup Script
```bash
chmod +x start-monitoring.sh
./start-monitoring.sh
```

### Option 2: Manual Docker Compose
```bash
docker-compose up -d
```

## Integrating Prometheus Middleware with Django

To enable metrics collection in your Django app:

### Step 1: Update Django Settings
Edit `todolist/todolist/settings.py` and add the middleware:

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    # ... other middleware ...
    'prometheus_middleware.PrometheusMiddleware',  # Add this line
]
```

### Step 2: Add Metrics URLs
Edit `todolist/todolist/urls.py`:

```python
from django.urls import path
from prometheus_middleware import metrics_view

urlpatterns = [
    # ... existing patterns ...
    path('metrics', metrics_view, name='prometheus_metrics'),
]
```

Or add it to any app's urls.py if preferred.

### Step 3: Restart Django
```bash
docker-compose restart web
```

## Access the Services

| Service | URL | Notes |
|---------|-----|-------|
| Grafana | http://localhost:3001 | Username: admin, Password: admin |
| Prometheus | http://localhost:9090 | Query metrics directly |
| Django App | http://localhost:8000 | Main application |
| Metrics Endpoint | http://localhost:8000/metrics | Raw Prometheus metrics |
| Redis Exporter | http://localhost:9121 | Exported metrics only |
| PostgreSQL Exporter | http://localhost:9187 | Exported metrics only |

## Setting Up Grafana Dashboard

### 1. Add Prometheus Data Source
1. Go to Grafana: http://localhost:3001
2. Login: admin / admin
3. Go to **Configuration** → **Data Sources**
4. Click **Add data source**
5. Select **Prometheus**
6. URL: `http://prometheus:9090`
7. Click **Save & Test**

### 2. Create a Dashboard
1. Go to **Dashboards** → **New Dashboard**
2. Click **Add panel**
3. Use these PromQL queries:

**Request Rate:**
```
rate(django_http_requests_total[5m])
```

**Request Duration:**
```
django_http_request_duration_seconds
```

**Requests in Progress:**
```
django_http_requests_in_progress
```

**Redis Memory Usage:**
```
redis_memory_used_bytes
```

**PostgreSQL Connections:**
```
pg_stat_activity_count
```

## Monitoring Metrics

### Django Application Metrics
- `django_http_requests_total`: Total HTTP requests by method, endpoint, and status
- `django_http_request_duration_seconds`: Request duration histogram
- `django_http_requests_in_progress`: Currently processing requests

### Redis Metrics
- `redis_memory_used_bytes`: Memory used by Redis
- `redis_connected_clients`: Number of connected clients
- `redis_commands_processed_total`: Total commands processed

### PostgreSQL Metrics
- `pg_up`: Whether PostgreSQL is up
- `pg_stat_activity_count`: Active database connections
- `pg_database_size_bytes`: Database size

## Docker Compose Commands

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f prometheus
docker-compose logs -f grafana
docker-compose logs -f web

# Stop all services
docker-compose down

# Rebuild and restart
docker-compose up -d --build
```

## PromQL Query Examples

```sql
# Requests per second in last 5 minutes
rate(django_http_requests_total[5m])

# 95th percentile request duration
histogram_quantile(0.95, django_http_request_duration_seconds)

# Error rate
rate(django_http_requests_total{status=~"5.."}[5m])

# Average request duration per endpoint
avg by (endpoint) (django_http_request_duration_seconds_sum / django_http_request_duration_seconds_count)
```

## Troubleshooting

### Prometheus can't scrape Django metrics
- Ensure `prometheus_middleware.PrometheusMiddleware` is in Django settings
- Check that `/metrics` endpoint is accessible
- View logs: `docker-compose logs web`

### Grafana won't connect to Prometheus
- Check Prometheus is running: `docker-compose logs prometheus`
- Ensure URL is `http://prometheus:9090` (not localhost)
- Check Docker network: `docker network ls`

### High memory usage
- Prometheus stores time-series data; increase `prometheus_data` volume size
- Reduce retention: Add `--storage.tsdb.retention.time=7d` to Prometheus command

## Performance Tips

1. **Adjust scrape intervals** in prometheus.yml based on your needs
2. **Set appropriate retention** to manage disk space
3. **Use Grafana alerts** for critical metrics
4. **Regular backups** of Grafana dashboards and saved state

## Next Steps

- Create custom dashboards for your specific use cases
- Set up alerting rules in Prometheus
- Export metrics to long-term storage if needed
- Fine-tune scrape intervals and retention policies
