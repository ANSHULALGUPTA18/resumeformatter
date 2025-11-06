@echo off
echo ============================================================
echo Starting OnlyOffice Document Server
echo ============================================================
echo.

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker is not running!
    echo Please start Docker Desktop and try again.
    echo.
    pause
    exit /b 1
)

echo Docker is running...
echo.

REM Check if container already exists
docker ps -a | findstr "onlyoffice-documentserver" >nul 2>&1
if %errorlevel% equ 0 (
    echo OnlyOffice container exists. Starting it...
    docker start onlyoffice-documentserver
) else (
    echo Creating new OnlyOffice container...
    docker run -i -t -d -p 8080:80 ^
        --name onlyoffice-documentserver ^
        -e JWT_ENABLED=false ^
        -e ALLOW_PRIVATE_IP_ADDRESS=true ^
        --add-host=host.docker.internal:host-gateway ^
        onlyoffice/documentserver
)

echo.
echo ============================================================
echo OnlyOffice Document Server is starting...
echo.
echo It will be available at: http://localhost:8080
echo.
echo Waiting for server to be ready (this may take 30-60 seconds)...
echo ============================================================
echo.

REM Wait for OnlyOffice to be ready
:wait_loop
timeout /t 5 /nobreak >nul
curl -s http://localhost:8080/healthcheck >nul 2>&1
if errorlevel 1 (
    echo Still starting...
    goto wait_loop
)

echo.
echo ============================================================
echo SUCCESS! OnlyOffice Document Server is ready!
echo ============================================================
echo.
echo You can now start the Resume Formatter application.
echo.
pause
