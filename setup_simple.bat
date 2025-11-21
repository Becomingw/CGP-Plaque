@echo off
echo === WSL Network Access Setup ===
echo.

set WSL_IP=172.19.220.112
set PORT=5001

echo WSL IP: %WSL_IP%
echo Port: %PORT%
echo.

echo Configuring port forwarding...
netsh interface portproxy delete v4tov4 listenport=%PORT% >nul 2>&1
netsh interface portproxy add v4tov4 listenport=%PORT% listenaddress=0.0.0.0 connectport=%PORT% connectaddress=%WSL_IP%

if %errorlevel% equ 0 (
    echo [SUCCESS] Port forwarding configured
) else (
    echo [ERROR] Configuration failed
)

echo.
echo Current port forwarding rules:
netsh interface portproxy show all

echo.
echo === Setup Complete ===
echo.
echo To access from local network:
echo 1. Find your Windows IP: ipconfig
echo 2. Access via: http://[YOUR_WINDOWS_IP]:5001
echo.
echo Make sure WSL app is running: python run_production.py
echo.
pause
