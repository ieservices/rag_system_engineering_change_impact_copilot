@echo off
REM Start the backend service using Podman
REM Run this from the project root directory

cd /d "%~dp0..\..\..\"

echo Starting Impact Copilot Backend with Podman...
podman-compose -f backend/docker/podman/docker-compose.yml up -d

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: podman-compose not found. Install it with:
    echo   pip install podman-compose
    exit /b 1
)

echo.
echo Backend started! Access at http://localhost:8000
echo View logs with: podman-compose -f backend/docker/podman/docker-compose.yml logs -f
