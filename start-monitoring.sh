#!/bin/bash

# Prometheus & Grafana Quick Start Script
# This script starts all services including Prometheus and Grafana

set -e

echo "🚀 Starting Prometheus & Grafana Stack..."

# Check if prometheus.yml exists
if [ ! -f "prometheus.yml" ]; then
    echo "❌ Error: prometheus.yml not found!"
    echo "Please run this script from the project root directory"
    exit 1
fi

# Start services with Docker Compose
echo "📦 Building and starting services..."
docker-compose up -d

echo ""
echo "✅ Services started successfully!"
echo ""
echo "🌐 Access the following services:"
echo ""
echo "  📊 Grafana:      http://localhost:3001"
echo "     Username: admin"
echo "     Password: admin"
echo ""
echo "  📈 Prometheus:   http://localhost:9090"
echo ""
echo "  🌍 Django App:   http://localhost:8000"
echo ""
echo "  💬 API Metrics:  http://localhost:8000/metrics"
echo ""
echo "  ⚡ Redis:        http://localhost:9121 (exporter)"
echo ""
echo "  🗄️  PostgreSQL:   http://localhost:9187 (exporter)"
echo ""
echo "📝 To view logs: docker-compose logs -f <service-name>"
echo "🛑 To stop: docker-compose down"
echo ""
echo "📚 Next steps:"
echo "  1. Go to Grafana: http://localhost:3001"
echo "  2. Add Prometheus as a data source: http://prometheus:9090"
echo "  3. Create dashboards to visualize metrics"
echo ""
