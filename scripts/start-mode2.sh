#!/bin/bash
# =============================================================================
# Mode 2: Frontend local (Vite), Backend + PostgreSQL in Docker/Podman
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

echo "Starting Mode 2: Backend + DB in Docker, Frontend local..."
echo ""

# Detect container runtime
if command -v podman-compose &> /dev/null; then
    COMPOSE_CMD="podman-compose"
elif command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
elif command -v docker &> /dev/null && docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
else
    echo "Error: Neither podman-compose nor docker-compose found"
    exit 1
fi

echo "Using: $COMPOSE_CMD"
echo ""

# Start backend and database
$COMPOSE_CMD -f docker-compose.dev.yml up -d --build

echo ""
echo "============================================="
echo "Backend and database started!"
echo ""
echo "Now run the frontend:"
echo "  cd frontend && npm run dev"
echo ""
echo "Access:"
echo "  Frontend:    http://localhost:5173"
echo "  Backend API: http://localhost:8000"
echo "  API Docs:    http://localhost:8000/docs"
echo "============================================="
