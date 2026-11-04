@echo off
echo ========================================================
echo STARTING MARS NEWS AUTONOMOUS NEWSROOM SCHEDULER
echo ========================================================

cd /d %~dp0..\backend
.venv\Scripts\python.exe -m app.workers.scheduler
