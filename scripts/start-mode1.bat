@echo off
REM =============================================================================
REM Mode 1: All services in Docker/Podman (Production-like)
REM =============================================================================

cd /d "%~dp0.."

echo Starting Mode 1: All services in Docker/Podman...
echo.

podman-compose -f docker-compose.yml up -d --build

echo.
echo =============================================
echo All services started!
echo.
echo Access:
echo   Frontend:    http://localhost:80
echo   Backend API: http://localhost:8000
echo   API Docs:    http://localhost:8000/docs
echo =============================================
