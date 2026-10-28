@echo off
title OSINT Brazuca Ultimate - Testes Automatizados
echo ========================================================
echo   EXECUTANDO BATERIA DE TESTES PYTEST
echo ========================================================
echo.
python -m pytest backend/tests -v
echo.
pause

