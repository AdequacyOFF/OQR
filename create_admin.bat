@echo off
REM Script to create admin user

echo ======================================
echo   OlimpQR - Create Admin User
echo ======================================
echo.

set /p ADMIN_EMAIL="Enter admin email (or press Enter for admin@admin.com): "
if "%ADMIN_EMAIL%"=="1234" set ADMIN_EMAIL=admin@admin.com

set /p ADMIN_PASSWORD="Enter admin password: "
if "%ADMIN_PASSWORD%"=="" (
    echo Error: Password cannot be empty
    pause
    exit /b 1
)

echo.
echo Creating admin user...
docker-compose exec -e ADMIN_EMAIL=%ADMIN_EMAIL% -e ADMIN_PASSWORD=%ADMIN_PASSWORD% backend python scripts/init_admin.py

echo.
echo ======================================
echo   Admin Account Created!
echo ======================================
echo Email: %ADMIN_EMAIL%
echo Password: [hidden]
echo.
echo You can now login at http://localhost:5173
echo.
pause
