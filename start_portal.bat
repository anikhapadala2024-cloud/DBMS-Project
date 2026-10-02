@echo off
title AgriTech Portal Runner
echo ========================================================
echo   Starting AgriTech Crop Batch Portal
echo ========================================================
cd /d "%~dp0"
if exist "%~dp0.venv\Scripts\python.exe" (
    "%~dp0.venv\Scripts\python.exe" run_app.py
) else if exist "C:\Users\HP\AppData\Local\Programs\Python\Python311\python.exe" (
    "C:\Users\HP\AppData\Local\Programs\Python\Python311\python.exe" run_app.py
) else (
    python run_app.py
)
pause

