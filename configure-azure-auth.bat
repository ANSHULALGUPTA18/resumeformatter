@echo off
echo ========================================
echo Azure AD Authentication Configuration
echo ========================================
echo.

set /p CLIENT_ID="Enter your Azure Client ID: "
set /p TENANT_ID="Enter your Azure Tenant ID: "
set /p CLIENT_SECRET="Enter your Azure Client Secret: "

echo.
echo Configuring Frontend...
(
echo # Azure AD ^(Entra ID^) Configuration
echo # Generated on %date% at %time%
echo.
echo REACT_APP_AZURE_CLIENT_ID=%CLIENT_ID%
echo REACT_APP_AZURE_TENANT_ID=%TENANT_ID%
echo REACT_APP_AZURE_REDIRECT_URI=http://localhost:3000
) > frontend\.env

echo Configuring Backend...
(
echo # Azure AD Backend Configuration
echo # Generated on %date% at %time%
echo.
echo AZURE_CLIENT_ID=%CLIENT_ID%
echo AZURE_TENANT_ID=%TENANT_ID%
echo AZURE_CLIENT_SECRET=%CLIENT_SECRET%
) > Backend\.env

echo.
echo ========================================
echo ✅ Configuration Complete!
echo ========================================
echo.
echo Frontend .env created at: frontend\.env
echo Backend .env created at: Backend\.env
echo.
echo Next steps:
echo 1. Restart your backend server
echo 2. Restart your frontend server
echo 3. Open http://localhost:3000
echo 4. Sign in with your Microsoft account
echo.
echo ========================================
pause
