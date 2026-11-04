@echo off
echo ========================================================
echo RUNNING MARS NEWS TEST SUITE
echo ========================================================

cd /d %~dp0..\backend
.venv\Scripts\python.exe -m pytest
