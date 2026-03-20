@echo off
REM =============================================================================
REM Mode 3: Only PostgreSQL in Docker/Podman (Frontend + Backend local)
REM =============================================================================

cd /d "%~dp0.."

echo Starting Mode 3: Only DB in Docker, Frontend + Backend local...
echo.

podman-compose -f docker-compose.db.yml up -d

echo.
echo =============================================
echo Database started!
echo.
echo Now run the backend and frontend:
echo.
echo Terminal 1 (Backend):
echo   cd backend
echo   .venv\Scripts\activate
echo   uvicorn app.main:app --reload
echo.
echo Terminal 2 (Frontend):
echo   cd frontend ^&^& npm run dev
echo.
echo Access:
echo   Frontend:    http://localhost:5173
echo   Backend API: http://localhost:8000
echo   API Docs:    http://localhost:8000/docs
echo.
echo Note: Backend uses DATABASE_URL from .env
echo       Make sure it points to localhost:5433
echo =============================================
