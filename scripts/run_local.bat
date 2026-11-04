@echo off
echo ========================================================
echo STARTING MARS NEWS LOCAL DEVELOPMENT STACK
echo ========================================================

start "Mars News Backend (FastAPI)" cmd /k "cd /d %~dp0..\backend && .venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"

timeout /t 2 >nul

start "Mars News Frontend (Next.js)" cmd /k "cd /d %~dp0..\frontend && npm run dev"

echo.
echo Mars News Public Portal: http://localhost:3000
echo Mars News Newsroom Desk: http://localhost:3000/admin
echo Backend Interactive Docs: http://127.0.0.1:8000/docs
echo ========================================================
