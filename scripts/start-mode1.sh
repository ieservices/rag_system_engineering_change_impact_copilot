#!/bin/bash
# =============================================================================
# Mode 1: All services in Docker/Podman (Production-like)
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

echo "Starting Mode 1: All services in Docker/Podman..."
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

$COMPOSE_CMD -f docker-compose.yml up -d --build

echo ""
echo "============================================="
echo "All services started!"
echo ""
echo "Access:"
echo "  Frontend:    http://localhost:80"
echo "  Backend API: http://localhost:8000"
echo "  API Docs:    http://localhost:8000/docs"
echo "============================================="
