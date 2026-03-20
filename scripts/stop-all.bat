@echo off
REM =============================================================================
REM Stop all Docker/Podman services
REM =============================================================================

cd /d "%~dp0.."

echo Stopping all services...

podman-compose -f docker-compose.yml down 2>nul
podman-compose -f docker-compose.dev.yml down 2>nul
podman-compose -f docker-compose.db.yml down 2>nul

echo All services stopped.
