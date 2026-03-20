#!/bin/bash
# =============================================================================
# Stop all Docker/Podman services
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

echo "Stopping all services..."

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

# Stop all possible compose files
$COMPOSE_CMD -f docker-compose.yml down 2>/dev/null || true
$COMPOSE_CMD -f docker-compose.dev.yml down 2>/dev/null || true
$COMPOSE_CMD -f docker-compose.db.yml down 2>/dev/null || true

echo "All services stopped."
