@echo off
REM =============================================================================
REM Mode 2: Frontend local (Vite), Backend + PostgreSQL in Docker/Podman
REM =============================================================================

cd /d "%~dp0.."

echo Starting Mode 2: Backend + DB in Docker, Frontend local...
echo.

podman-compose -f docker-compose.dev.yml up -d --build

echo.
echo =============================================
echo Backend and database started!
echo.
echo Now run the frontend:
echo   cd frontend ^&^& npm run dev
echo.
echo Access:
echo   Frontend:    http://localhost:5173
echo   Backend API: http://localhost:8000
echo   API Docs:    http://localhost:8000/docs
echo =============================================
