@echo off
echo ============================================================
echo Restarting All Services
echo ============================================================
echo.

echo Step 1: Stopping OnlyOffice container...
docker stop onlyoffice-documentserver
docker rm onlyoffice-documentserver

echo.
echo Step 2: Starting OnlyOffice with correct configuration...
docker-compose up -d

echo.
echo Step 3: Waiting for OnlyOffice to initialize (90 seconds)...
echo Please wait...
timeout /t 90 /nobreak

echo.
echo ============================================================
echo All Services Restarted!
echo ============================================================
echo.
echo Next steps:
echo 1. Restart your Flask backend (Ctrl+C and run: python app.py)
echo 2. Refresh your browser
echo 3. Try editing a document
echo.
pause
