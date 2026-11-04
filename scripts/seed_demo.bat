@echo off
echo ========================================================
echo SEEDING MARS NEWS DEMO DATA & RUNNING PIPELINE
echo ========================================================

cd /d %~dp0..\backend
.venv\Scripts\python.exe -m app.db_seed
.venv\Scripts\python.exe -m app.seed_stories
echo.
echo Database and news pipeline seeded successfully!
pause
