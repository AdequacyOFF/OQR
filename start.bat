@echo off
REM OlimpQR Startup Script for Windows
REM This script will start all services and set up the application

echo ======================================
echo   OlimpQR - Starting Application
echo ======================================
echo.

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo X Error: Docker is not running. Please start Docker Desktop first.
    pause
    exit /b 1
)

echo [OK] Docker is running
echo.

REM Start all services
echo [*] Starting Docker containers...
docker-compose up -d

REM Wait for services to be ready
echo.
echo [*] Waiting for services to be ready...
timeout /t 15 /nobreak >nul

REM Check backend health
echo.
echo [*] Checking backend health...
:check_backend
curl -s http://localhost:8000/health >nul 2>&1
if errorlevel 1 (
    timeout /t 2 /nobreak >nul
    goto check_backend
)
echo [OK] Backend is healthy

REM Apply database migrations
echo.
echo [*] Applying database migrations...
docker-compose exec -T backend alembic upgrade head

echo.
echo ======================================
echo   Application Started Successfully!
echo ======================================
echo.
echo Access the application at:
echo   Frontend:    http://localhost:5173
echo   Backend API: http://localhost:8000/docs
echo   MinIO:       http://localhost:9001 (minioadmin/minioadmin)
echo.
echo.
echo To create an admin user, run:
echo   docker-compose exec backend python scripts/init_admin.py
echo.
echo   Or with custom email:
echo   set ADMIN_EMAIL=your@email.com
echo   set ADMIN_PASSWORD=YourPassword123
echo   docker-compose exec backend python scripts/init_admin.py
echo.
echo Default admin credentials will be:
echo   Email: admin@admin.com
echo   Password: (from ADMIN_PASSWORD env var)
echo.
echo To view logs:
echo   docker-compose logs -f backend
echo   docker-compose logs -f frontend
echo.
echo To stop all services:
echo   docker-compose down
echo.
pause
