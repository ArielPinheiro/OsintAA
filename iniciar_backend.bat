@echo off
title OSINT Brazuca Ultimate - Backend FastAPI
echo ========================================================
echo   OSINT BRAZUCA ULTIMATE - SERVIDOR BACKEND (127.0.0.1)
echo ========================================================
echo.
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
pause

