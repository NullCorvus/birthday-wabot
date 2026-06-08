@echo off
title Birthday WaBot - Logs

set "LOG_DIR=C:\Program Files\BirthdayWabot\bot\logs"

if not exist "%LOG_DIR%" (
    echo No hay logs disponibles.
    pause
    exit /b 1
)

echo =============================================
echo  Birthday WaBot - Visualizador de Logs
echo =============================================
echo.
echo  1) Ver logs de salida
echo  2) Ver logs de error
echo  3) Ver logs en tiempo real (seguir)
echo  4) Abrir carpeta de logs
echo  5) Salir
echo.

set /p "OPT= Selecciona una opcion (1-5): "

if "%OPT%"=="1" (
    if exist "%LOG_DIR%\service-out.log" (
        type "%LOG_DIR%\service-out.log"
    ) else (
        echo No hay logs de salida.
    )
    echo.
    pause
    start logs.bat
)
if "%OPT%"=="2" (
    if exist "%LOG_DIR%\service-err.log" (
        type "%LOG_DIR%\service-err.log"
    ) else (
        echo No hay logs de error.
    )
    echo.
    pause
    start logs.bat
)
if "%OPT%"=="3" (
    echo Mostrando logs en tiempo real...
    echo Presiona Ctrl+C para salir.
    echo.
    powershell -Command "Get-Content '%LOG_DIR%\service-out.log' -Wait -Tail 20"
)
if "%OPT%"=="4" (
    explorer "%LOG_DIR%"
    start logs.bat
)
if "%OPT%"=="5" exit /b 0
