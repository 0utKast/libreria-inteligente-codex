@echo off
setlocal enabledelayedexpansion
echo ========================================
echo    Deteniendo Servidores de la Libreria
echo ========================================

set "found_frontend="
set "found_backend="

echo.
echo Buscando y deteniendo el Frontend (puerto 3000)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":3000" ^| findstr "LISTENING"') do (
    set "found_frontend=1"
    echo Cerrando proceso con PID %%a y sus subprocesos...
    taskkill /F /PID %%a /T >nul 2>nul
)
if not defined found_frontend echo No se encontraron procesos escuchando en 3000.

echo.
echo Buscando y deteniendo el Backend (puerto 8001)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8001" ^| findstr "LISTENING"') do (
    set "backend_pid=%%a"
    set "found_backend=1"
    echo Cerrando proceso del backend con PID !backend_pid! y sus subprocesos...
    taskkill /F /PID !backend_pid! /T >nul 2>nul

    rem Intentar cerrar también la ventana padre del cmd que lo lanzó
    for /f "tokens=2" %%x in ('wmic process where "ProcessId=!backend_pid!" get ParentProcessId ^| findstr /v "ParentProcessId"') do (
        set "parent_pid=%%x"
        if defined parent_pid (
            echo Cerrando proceso padre con PID !parent_pid!...
            taskkill /F /PID !parent_pid! /T >nul 2>nul
        )
    )
)
if not defined found_backend echo No se encontraron procesos escuchando en 8001.

echo.
echo Fallback: cerrando ventanas por titulo (Frontend/Backend)...
taskkill /F /FI "WINDOWTITLE eq Frontend" /T >nul 2>nul
taskkill /F /FI "WINDOWTITLE eq Backend" /T >nul 2>nul

echo Fallback: terminando procesos por comando si siguen activos...
wmic process where "CommandLine like '%%uvicorn%%main:app%%'" call terminate >nul 2>nul
wmic process where "CommandLine like '%%npm%%start%%'" call terminate >nul 2>nul

echo.
echo Todos los procesos objetivo han sido detenidos (si existian).
timeout /t 2 >nul
