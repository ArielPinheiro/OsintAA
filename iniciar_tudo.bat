@echo off
title OSINT Brazuca Ultimate
echo ========================================================
echo   INICIANDO OSINT BRAZUCA ULTIMATE (BACKEND + FRONTEND)
echo ========================================================
echo.
echo Iniciando Backend em 127.0.0.1:8000...
start cmd /k "iniciar_backend.bat"

echo Aguardando 2 segundos...
timeout /t 2 /nobreak > nul

echo Iniciando Frontend em 127.0.0.1:5173...
start cmd /k "iniciar_frontend.bat"

echo.
echo ========================================================
echo   SISTEMA PRONTO!
echo   Acesse a interface no navegador:
echo   -> http://127.0.0.1:5173 (Desenvolvimento)
echo   ou
echo   -> http://127.0.0.1:8000 (Producao Integrada)
echo ========================================================

