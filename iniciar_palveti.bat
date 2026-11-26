@echo off
cd /d "%~dp0"
title PALVETI - Panaderia Artesanal de Masa Madre

echo ========================================================
echo         INICIANDO SISTEMA PALVETI (LOCAL)
echo ========================================================
echo.

:: Detectar ejecutable de Python disponible
set PYTHON_CMD=
where python >nul 2>nul && set PYTHON_CMD=python
if "%PYTHON_CMD%"=="" where py >nul 2>nul && set PYTHON_CMD=py
if "%PYTHON_CMD%"=="" if exist "C:\Python315\python.exe" set PYTHON_CMD=C:\Python315\python.exe

if "%PYTHON_CMD%"=="" (
    echo [ERROR] No se encontro Python en tu sistema.
    echo Por favor instala Python o verifica que este en las variables de entorno.
    echo.
    pause
    exit /b 1
)

echo Usando ejecutable: %PYTHON_CMD%
echo Abriendo aplicacion en tu navegador...
echo.

:: Abrir navegador automaticamente despues de 2 segundos
start "" cmd /c "timeout /t 2 /nobreak >nul & start http://localhost:8501"

:: Iniciar servidor Streamlit
%PYTHON_CMD% -m streamlit run app.py --server.port 8501 --browser.gatherUsageStats false

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [AVISO] El servidor se ha detenido.
    pause
)
