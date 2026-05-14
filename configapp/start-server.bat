@echo off
REM Quick start script for HTAP Config Tool
REM Double-click this file to start the server and open in browser

echo.
echo ========================================
echo  HTAP Run File Configuration Tool
echo ========================================
echo.
echo Starting server...
echo.

cd /d "%~dp0"

REM Start Python server
start /b python server.py

REM Wait a moment for server to start
timeout /t 2 /nobreak >nul

REM Open in default browser
start http://localhost:8000/index.html

echo.
echo Server is running at http://localhost:8000
echo Browser should open automatically.
echo.
echo Press any key to stop the server and close this window...
pause >nul

REM Kill Python server
taskkill /f /im python.exe /fi "WINDOWTITLE eq *server.py*" >nul 2>&1

echo Server stopped.
timeout /t 1 /nobreak >nul
