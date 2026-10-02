@echo off
title Push to GitHub - DBSE Project
echo ========================================================
echo   Pushing AgriTech DBSE Project to GitHub
echo ========================================================
set "PATH=C:\Users\HP\AppData\Local\Programs\Git\cmd;C:\Users\HP\AppData\Local\Programs\Git\mingw64\bin;%PATH%"
cd /d "%~dp0"
echo Remote Repository:
git remote -v
echo.
echo Running git push -u origin main...
git push -u origin main
echo.
if %ERRORLEVEL% equ 0 (
    echo ========================================================
    echo   SUCCESS! All files have been pushed to GitHub.
    echo ========================================================
) else (
    echo ========================================================
    echo   If prompted, please sign in with your GitHub account
    echo   in the browser popup.
    echo ========================================================
)
pause
