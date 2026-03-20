#!/bin/bash
# =============================================================================
# Mode 3: Only PostgreSQL in Docker/Podman (Frontend + Backend local)
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

echo "Starting Mode 3: Only DB in Docker, Frontend + Backend local..."
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

# Start only database
$COMPOSE_CMD -f docker-compose.db.yml up -d

echo ""
echo "============================================="
echo "Database started!"
echo ""
echo "Now run the backend and frontend:"
echo ""
echo "Terminal 1 (Backend):"
echo "  cd backend"
echo "  source .venv/bin/activate  # or .venv\\Scripts\\activate on Windows"
echo "  uvicorn app.main:app --reload"
echo ""
echo "Terminal 2 (Frontend):"
echo "  cd frontend && npm run dev"
echo ""
echo "Access:"
echo "  Frontend:    http://localhost:5173"
echo "  Backend API: http://localhost:8000"
echo "  API Docs:    http://localhost:8000/docs"
echo ""
echo "Note: Backend uses DATABASE_URL from .env"
echo "      Make sure it points to localhost:5433"
echo "============================================="
