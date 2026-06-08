@echo off
setlocal enabledelayedexpansion

title Birthday WaBot - Instalador
color 0B

set "INSTALL_DIR=C:\Program Files\BirthdayWabot"
set "REPO_URL=https://github.com/NullCorvus/birthday-wabot.git"
set "NSSM_URL=https://nssm.cc/release/nssm-2.24.zip"
set "NSSM_FILE=nssm-2.24.zip"

echo =============================================
echo  Birthday WaBot - Instalacion para Windows
echo =============================================
echo.

:: ─── Verificar Administrador ───
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Este script debe ejecutarse como Administrador.
    echo Haga clic derecho y seleccione "Ejecutar como administrador".
    pause
    exit /b 1
)

:: ─── Verificar Node.js ───
echo [*] Verificando Node.js...
where node >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js no esta instalado.
    echo Descarguelo desde: https://nodejs.org (v18 o superior)
    pause
    exit /b 1
)

for /f "tokens=2" %%v in ('node -v 2^>nul') do set "NODE_VER=%%v"
echo     Node.js: %NODE_VER%

:: ─── Verificar Git ───
echo [*] Verificando Git...
where git >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Git no esta instalado.
    echo Descarguelo desde: https://git-scm.com
    pause
    exit /b 1
)

echo     Git: OK

:: ─── Crear directorio de instalacion ───
echo.
echo [*] Instalando en: %INSTALL_DIR%
if not exist "%INSTALL_DIR%" (
    mkdir "%INSTALL_DIR%"
    if !errorlevel! neq 0 (
        echo [ERROR] No se pudo crear el directorio de instalacion.
        pause
        exit /b 1
    )
)

:: ─── Clonar / Actualizar repositorio ───
echo [*] Descargando repositorio...
cd /d "%INSTALL_DIR%"

if exist ".git" (
    echo     Repositorio ya existe. Actualizando...
    git pull --rebase
) else (
    if exist "%INSTALL_DIR%\*" (
        echo     La carpeta no esta vacia.
        set /p "OVERWRITE=     Sobrescribir? (S/N): "
        if /i "!OVERWRITE!"=="S" (
            rmdir /s /q "%INSTALL_DIR%" 2>nul
            mkdir "%INSTALL_DIR%"
            cd /d "%INSTALL_DIR%"
            git clone "%REPO_URL%" "%INSTALL_DIR%"
        )
    ) else (
        git clone "%REPO_URL%" "%INSTALL_DIR%"
    )
)

cd /d "%INSTALL_DIR%"
if not exist ".git" (
    echo [ERROR] No se pudo clonar el repositorio.
    pause
    exit /b 1
)
echo     Repositorio descargado correctamente.

:: ─── Instalar dependencias ───
echo [*] Instalando dependencias...
echo     Instalando dependencias raiz...
call npm install
if %errorlevel% neq 0 (
    echo [WARN] Dependencias raiz con errores.
)

echo     Instalando dependencias del bot...
cd /d "%INSTALL_DIR%\bot"
call npm install
if %errorlevel% neq 0 (
    echo [WARN] Dependencias del bot con errores.
)

echo     Generando cliente de Prisma...
cd /d "%INSTALL_DIR%"
call npx prisma generate
if %errorlevel% neq 0 (
    echo [ERROR] No se pudo generar Prisma client.
    pause
    exit /b 1
)

:: ─── Configurar .env ───
echo.
echo [*] Configurando base de datos...
echo     Necesitas una base de datos PostgreSQL (recomendado Supabase).
if not exist "%INSTALL_DIR%\.env" (
    echo     Creando archivo .env...
    echo.
    echo IMPORTANTE: Ingresa tu DATABASE_URL de Supabase.
    echo Ejemplo: postgresql://postgres.proyecto:pass@host:6543/postgres?pgbouncer=true
    echo.
    set /p "DB_URL=     DATABASE_URL: "
    if "!DB_URL!"=="" (
        echo [ERROR] Debes ingresar una URL de base de datos.
        pause
        exit /b 1
    )
    set /p "DIRECT_URL=     DIRECT_URL (opcional, para migraciones): "
    if "!DIRECT_URL!"=="" set "DIRECT_URL="
    
    (
        echo # ─── Base de datos ───
        echo DATABASE_URL="!DB_URL!"
    ) > "%INSTALL_DIR%\.env"
    
    if not "!DIRECT_URL!"=="" (
        echo DIRECT_URL="!DIRECT_URL!" >> "%INSTALL_DIR%\.env"
    )
    
    echo     .env creado correctamente.
    
    echo.
    echo [*] Creando tablas en la base de datos...
    set /p "PUSH=     Ejecutar prisma db push ahora? (S/N): "
    if /i "!PUSH!"=="S" (
        cd /d "%INSTALL_DIR%"
        call npx prisma db push
        if !errorlevel! equ 0 (
            echo     Tablas creadas correctamente.
        ) else (
            echo [WARN] Puede que necesites usar DIRECT_URL para las migraciones.
            echo     Ejecuta manualmente: npx prisma db push
        )
    )
) else (
    echo     .env ya existe. Omitiendo...
)

:: ─── NSSM: Instalar servicio ───
echo [*] Preparando NSSM...
cd /d "%INSTALL_DIR%"

if not exist "nssm.exe" (
    echo     Descargando NSSM...
    powershell -Command "(New-Object Net.WebClient).DownloadFile('%NSSM_URL%', '%NSSM_FILE%')" >nul 2>&1
    if exist "%NSSM_FILE%" (
        echo     Extrayendo NSSM...
        powershell -Command "Expand-Archive -Path '%NSSM_FILE%' -DestinationPath '%INSTALL_DIR%\nssm-temp' -Force" >nul 2>&1
        for /r "%INSTALL_DIR%\nssm-temp" %%f in (*.exe) do (
            if /i "%%~nxf"=="nssm.exe" copy /y "%%f" "%INSTALL_DIR%\nssm.exe" >nul
        )
        rmdir /s /q "%INSTALL_DIR%\nssm-temp" 2>nul
        del "%NSSM_FILE%" 2>nul
    ) else (
        echo [WARN] No se pudo descargar NSSM automaticamente.
        echo     Descargalo desde: https://nssm.cc/download
        echo     y coloca nssm.exe en: %INSTALL_DIR%
        pause
    )
)

if exist "nssm.exe" (
    echo     NSSM listo.
    
    echo.
    echo [*] Instalando servicio Windows...
    cd /d "%INSTALL_DIR%\bot"
    
    :: Crear carpeta de logs
    if not exist "logs" mkdir logs
    
    :: Detener y eliminar servicio si existe
    "%INSTALL_DIR%\nssm.exe" stop BirthdayWabot >nul 2>&1
    "%INSTALL_DIR%\nssm.exe" remove BirthdayWabot confirm >nul 2>&1
    
    :: Crear servicio
    "%INSTALL_DIR%\nssm.exe" install BirthdayWabot "C:\Program Files\nodejs\node.exe"
    "%INSTALL_DIR%\nssm.exe" set BirthdayWabot AppDirectory "%INSTALL_DIR%\bot"
    "%INSTALL_DIR%\nssm.exe" set BirthdayWabot AppParameters "index.js"
    "%INSTALL_DIR%\nssm.exe" set BirthdayWabot AppStdout "%INSTALL_DIR%\bot\logs\service-out.log"
    "%INSTALL_DIR%\nssm.exe" set BirthdayWabot AppStderr "%INSTALL_DIR%\bot\logs\service-err.log"
    "%INSTALL_DIR%\nssm.exe" set BirthdayWabot AppRotateFiles 1
    "%INSTALL_DIR%\nssm.exe" set BirthdayWabot AppRotateOnline 1
    "%INSTALL_DIR%\nssm.exe" set BirthdayWabot AppRotateSeconds 86400
    "%INSTALL_DIR%\nssm.exe" set BirthdayWabot AppRotateBytes 10485760
    "%INSTALL_DIR%\nssm.exe" set BirthdayWabot Start SERVICE_AUTO_START
    "%INSTALL_DIR%\nssm.exe" set BirthdayWabot AppRestartDelay 5000
    "%INSTALL_DIR%\nssm.exe" set BirthdayWabot ObjectName LocalSystem
    
    :: Iniciar servicio
    "%INSTALL_DIR%\nssm.exe" start BirthdayWabot
    
    if !errorlevel! equ 0 (
        echo     Servicio iniciado correctamente.
    ) else (
        echo     El servicio se ha creado pero puede que necesites iniciarlo manualmente.
        echo     Ejecuta: nssm start BirthdayWabot
    )
) else (
    echo [WARN] NSSM no encontrado. El servicio no se ha instalado.
    echo     Para ejecutar el bot manualmente: cd bot ^&^& node index.js
)

:: ─── Finalizar ───
echo.
echo =============================================
echo  Instalacion completada!
echo =============================================
echo.
echo  Rutas:
echo    Instalacion: %INSTALL_DIR%
echo    Logs:        %INSTALL_DIR%\bot\logs\
echo.
echo  Comandos utiles:
echo    Ver estado:   nssm status BirthdayWabot
echo    Ver logs:     %INSTALL_DIR%\logs.bat
echo    Desinstalar:  %INSTALL_DIR%\uninstall.bat
echo.
echo  IMPORTANTE: Si es la primera vez, el bot mostrara un QR
echo  en los logs. Escanealo con WhatsApp (Dispositivos Vinculados).
echo.
echo  Para ver el QR: type "%INSTALL_DIR%\bot\logs\service-out.log"
echo.
pause
exit /b 0
