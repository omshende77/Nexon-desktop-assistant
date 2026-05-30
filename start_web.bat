@echo off
echo ============================================
echo   Nexon AI -- Web Interface Launcher
echo ============================================
echo.
echo Starting FastAPI backend on port 8000...
echo Starting React frontend on port 5173...
echo.
echo FastAPI docs: http://localhost:8000/docs
echo React UI:     http://localhost:5173
echo.

:: Start FastAPI in a new window
start "Nexon AI Backend" cmd /k "uvicorn server:app --port 8000"

:: Wait a moment for backend to start
timeout /t 3 /nobreak > nul

:: Start React dev server in a new window
start "Nexon AI Frontend" cmd /k "cd nexon-ui && npm run dev"

echo Both servers starting...
echo Close those windows to stop the servers.
pause
