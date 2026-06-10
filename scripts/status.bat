@echo off
title Birthday WaBot - Estado

set "INSTALL_DIR=C:\Program Files\BirthdayWabot"

echo =============================================
echo  Birthday WaBot - Estado del Servicio
echo =============================================
echo.

if exist "%INSTALL_DIR%\nssm.exe" (
    "%INSTALL_DIR%\nssm.exe" status BirthdayWabot
    echo.
    "%INSTALL_DIR%\nssm.exe" list
) else (
    sc query BirthdayWabot
)

echo.
echo  Logs: %INSTALL_DIR%\bot\logs\
echo.
pause
