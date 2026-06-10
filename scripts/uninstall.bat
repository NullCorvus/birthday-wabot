@echo off
title Birthday WaBot - Desinstalador
color 0C

set "INSTALL_DIR=C:\Program Files\BirthdayWabot"

echo =============================================
echo  Birthday WaBot - Desinstalacion
echo =============================================
echo.

:: ─── Verificar Administrador ───
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Este script debe ejecutarse como Administrador.
    pause
    exit /b 1
)

:: ─── Confirmar ───
set /p "CONFIRM= Esto eliminara el servicio y todos los archivos. Continuar? (S/N): "
if /i not "%CONFIRM%"=="S" (
    echo Cancelado.
    pause
    exit /b 0
)

:: ─── Detener y eliminar servicio ───
echo [*] Deteniendo servicio...
if exist "%INSTALL_DIR%\nssm.exe" (
    "%INSTALL_DIR%\nssm.exe" stop BirthdayWabot >nul 2>&1
    timeout /t 2 /nobreak >nul
    "%INSTALL_DIR%\nssm.exe" remove BirthdayWabot confirm >nul 2>&1
    echo     Servicio eliminado.
) else (
    echo     NSSM no encontrado. Intentando detener con sc...
    sc stop BirthdayWabot >nul 2>&1
    sc delete BirthdayWabot >nul 2>&1
)

:: ─── Eliminar archivos ───
echo [*] Eliminando archivos...
if exist "%INSTALL_DIR%" (
    rmdir /s /q "%INSTALL_DIR%" >nul 2>&1
    if %errorlevel% equ 0 (
        echo     Archivos eliminados correctamente.
    ) else (
        echo [WARN] Algunos archivos no pudieron ser eliminados.
        echo     Cierra cualquier proceso y vuelve a intentar.
    )
)

echo.
echo =============================================
echo  Desinstalacion completada.
echo =============================================
pause
exit /b 0
