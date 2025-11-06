@echo off
echo ============================================================
echo OnlyOffice Diagnostic Tool
echo ============================================================
echo.

echo [1/5] Checking Docker container status...
docker ps | findstr onlyoffice
if errorlevel 1 (
    echo ❌ OnlyOffice container not running!
    pause
    exit /b 1
)
echo ✅ Container is running
echo.

echo [2/5] Checking OnlyOffice web interface...
curl -s http://localhost:8080/healthcheck
if errorlevel 1 (
    echo ❌ OnlyOffice not responding!
) else (
    echo ✅ OnlyOffice web interface is up
)
echo.

echo [3/5] Checking backend health...
curl -s http://localhost:5000/api/health
if errorlevel 1 (
    echo ❌ Backend not responding!
) else (
    echo ✅ Backend is healthy
)
echo.

echo [4/5] Testing download from inside Docker...
docker exec onlyoffice-documentserver curl -I http://host.docker.internal:5000/api/health
if errorlevel 1 (
    echo ❌ Docker cannot reach backend!
) else (
    echo ✅ Docker can reach backend
)
echo.

echo [5/5] Checking OnlyOffice document service logs...
docker logs onlyoffice-documentserver --tail 10 | findstr /C:"listening" /C:"error" /C:"failed"
echo.

echo ============================================================
echo Diagnostic Complete
echo ============================================================
echo.
echo If all checks pass but browser still fails:
echo 1. Clear browser cache (Ctrl+Shift+Delete)
echo 2. Wait 2 minutes for OnlyOffice to fully initialize
echo 3. Try in incognito/private window
echo 4. Check browser console (F12) for specific errors
echo.
pause
