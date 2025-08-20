@echo off
setlocal
echo ========================================
echo   Iniciando Libreria Inteligente Codex
echo ========================================

pushd %~dp0

rem --- Backend ---
cd backend
if not exist .venv\Scripts\python.exe (
  echo Creando entorno virtual de Python...
  python -m venv .venv
)
call .venv\Scripts\pip.exe install -r requirements.txt
START "Backend" cmd /c ".venv\Scripts\python.exe -m uvicorn main:app --reload --port 8001 --host 0.0.0.0"

rem --- Frontend ---
cd ..\frontend
if not exist node_modules (
  echo Instalando dependencias de frontend...
  npm install
)
START "Frontend" cmd /c "npm start"

popd
echo.
echo Servidores iniciados en segundo plano.
timeout /t 3 >nul
