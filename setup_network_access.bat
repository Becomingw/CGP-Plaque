@echo off
chcp 65001 >nul
echo === WSL Network Access Configuration ===
echo.

REM Set variables
set WSL_IP=172.19.220.112
set PORT1=5001
set PORT2=5002

echo WSL IP Address: %WSL_IP%
echo Application Ports: %PORT1% (Web UI), %PORT2% (Analysis Tool)
echo.

echo 1. Configuring port forwarding...
REM Delete existing rules
netsh interface portproxy delete v4tov4 listenport=%PORT1% >nul 2>&1
netsh interface portproxy delete v4tov4 listenport=%PORT2% >nul 2>&1

REM Add new port forwarding rules
netsh interface portproxy add v4tov4 listenport=%PORT1% listenaddress=0.0.0.0 connectport=%PORT1% connectaddress=%WSL_IP%
netsh interface portproxy add v4tov4 listenport=%PORT2% listenaddress=0.0.0.0 connectport=%PORT2% connectaddress=%WSL_IP%

if %errorlevel% equ 0 (
    echo [SUCCESS] Port forwarding configured for ports %PORT1% and %PORT2%
) else (
    echo [ERROR] Port forwarding configuration failed
)
echo.

echo 2. Current port forwarding configuration:
netsh interface portproxy show all
echo.

echo 3. Network access information:
echo Local network access address:
echo   http://[YOUR_WINDOWS_IP]:%PORT%
echo.
echo To find your Windows IP address, run: ipconfig
echo.

echo === Configuration Complete ===
echo Please ensure the WSL application is running: python run_production.py
echo.
pause
