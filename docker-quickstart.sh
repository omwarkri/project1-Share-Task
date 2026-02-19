#!/bin/bash
# Quick Start Script for Docker Deployment

echo "════════════════════════════════════════════════════════════"
echo "  Share Task - Docker Deployment Quick Start"
echo "════════════════════════════════════════════════════════════"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}Current Container Status:${NC}"
docker compose ps

echo ""
echo -e "${BLUE}Access Points:${NC}"
echo -e "${GREEN}✓ Web Application${NC}     → http://localhost:8000"
echo -e "${GREEN}✓ Nginx Proxy${NC}        → http://localhost:3000"
echo -e "${GREEN}✓ Admin Panel${NC}        → http://localhost:8000/admin"

echo ""
echo -e "${BLUE}Quick Commands:${NC}"
echo ""
echo "  View Logs (all services):"
echo "  $ docker compose logs -f"
echo ""
echo "  View Logs (specific service):"
echo "  $ docker compose logs -f web"
echo "  $ docker compose logs -f celery"
echo "  $ docker compose logs -f db"
echo ""
echo "  Create Superuser:"
echo "  $ docker compose exec web python manage.py createsuperuser"
echo ""
echo "  Django Shell:"
echo "  $ docker compose exec web python manage.py shell"
echo ""
echo "  Connect to Database:"
echo "  $ docker compose exec db psql -U postgres -d todolist_db"
echo ""
echo "  Stop All Services:"
echo "  $ docker compose down"
echo ""
echo "  Restart Services:"
echo "  $ docker compose restart"
echo ""
echo -e "${YELLOW}Database Credentials:${NC}"
echo "  Host:     db (docker-compose network)"
echo "  User:     postgres"
echo "  Password: postgres"
echo "  Database: todolist_db"
echo ""
echo -e "${YELLOW}Redis Credentials:${NC}"
echo "  Host: redis (docker-compose network)"
echo "  Port: 6379"
echo ""
echo "════════════════════════════════════════════════════════════"
echo "For detailed documentation, see: DOCKER_SETUP.md"
echo "════════════════════════════════════════════════════════════"
