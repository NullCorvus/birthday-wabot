@echo off
setlocal enabledelayedexpansion

title Birthday WaBot - Instalador Completo
color 0B

set "INSTALL_DIR=C:\Program Files\BirthdayWabot"
set "REPO_URL=https://github.com/NullCorvus/birthday-wabot.git"
set "NSSM_URL=https://nssm.cc/release/nssm-2.24.zip"
set "LOG_FILE=%TEMP%\birthday-wabot-install.log"
set "TOTAL_STEPS=11"
set "STEP=0"
set "HAS_WINGET=0"
set "NODE_PATH="

:: Iniciar log
echo [%date% %time%] === INICIO DE INSTALACION === > "%LOG_FILE%"
echo [%date% %time%] OS: %OS% Arch: %PROCESSOR_ARCHITECTURE% >> "%LOG_FILE%"

echo.
echo  +=====================================================+
echo  :                                                     :
echo  :    Birthday WaBot - Instalador Completo             :
echo  :                                                     :
echo  :    Este script instalara TODO lo necesario:          :
echo  :      - Node.js, Git, Chrome (si no estan)           :
echo  :      - NSSM, dependencias, servicio Windows         :
echo  :                                                     :
echo  +=====================================================+
echo.
echo  Log: %LOG_FILE%
echo.

:: ==============================================================
:: PASO 1: Verificar Administrador
:: ==============================================================
set /a STEP+=1
echo  [Paso !STEP!/%TOTAL_STEPS%] Verificando permisos de administrador...
echo [%date% %time%] PASO !STEP!: Verificando admin >> "%LOG_FILE%"
net session >nul 2>&1
if !errorlevel! neq 0 (
    echo.
    echo    [ERROR] Este script DEBE ejecutarse como Administrador.
    echo    Clic derecho sobre install.bat ^> "Ejecutar como administrador"
    echo [%date% %time%] ERROR: Sin permisos de admin >> "%LOG_FILE%"
    goto :error_exit
)
echo           OK
echo [%date% %time%] Admin: OK >> "%LOG_FILE%"

:: Detectar winget
echo [%date% %time%] Buscando winget... >> "%LOG_FILE%"
where winget >nul 2>&1
if !errorlevel! equ 0 (
    set "HAS_WINGET=1"
    echo           Winget detectado.
    echo [%date% %time%] Winget: disponible >> "%LOG_FILE%"
) else (
    echo           Winget no disponible, se usara descarga directa.
    echo [%date% %time%] Winget: no disponible >> "%LOG_FILE%"
)

:: ==============================================================
:: PASO 2: Node.js
:: ==============================================================
set /a STEP+=1
echo.
echo  [Paso !STEP!/%TOTAL_STEPS%] Verificando Node.js...
echo [%date% %time%] PASO !STEP!: Verificando Node.js >> "%LOG_FILE%"

where node >nul 2>&1
if !errorlevel! equ 0 (
    for /f "tokens=*" %%v in ('node -v 2^>nul') do set "NODE_VER=%%v"
    echo           OK - Node.js !NODE_VER! ya instalado.
    echo [%date% %time%] Node.js: !NODE_VER! ya instalado >> "%LOG_FILE%"
    goto :node_ready
)

echo           Node.js NO encontrado. Instalando...
echo [%date% %time%] Node.js: no encontrado, instalando >> "%LOG_FILE%"

if "!HAS_WINGET!"=="1" (
    echo           Usando winget (puede tardar unos minutos)...
    echo [%date% %time%] Intentando winget install Node.js >> "%LOG_FILE%"
    winget install OpenJS.NodeJS.LTS --silent --accept-package-agreements --accept-source-agreements >> "%LOG_FILE%" 2>&1
    if !errorlevel! equ 0 (
        echo           Winget: Node.js instalado.
        echo [%date% %time%] winget Node.js: OK >> "%LOG_FILE%"
        goto :node_check_after_install
    )
    echo           Winget fallo, intentando descarga directa...
    echo [%date% %time%] winget Node.js: fallo, usando descarga directa >> "%LOG_FILE%"
)

echo           Descargando Node.js LTS desde nodejs.org...
echo [%date% %time%] Descargando Node.js directamente >> "%LOG_FILE%"
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
    "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; ^
    try { ^
        Write-Host '           Buscando ultima version LTS...'; ^
        $idx = Invoke-RestMethod -Uri 'https://nodejs.org/dist/index.json' -TimeoutSec 30; ^
        $lts = ($idx | Where-Object { $_.lts -ne $false } | Select-Object -First 1); ^
        $ver = $lts.version; ^
        Write-Host \"           Version: $ver\"; ^
        $url = \"https://nodejs.org/dist/$ver/node-$ver-x64.msi\"; ^
        $out = Join-Path $env:TEMP 'node-lts-install.msi'; ^
        Write-Host '           Descargando...'; ^
        Invoke-WebRequest -Uri $url -OutFile $out -TimeoutSec 180; ^
        Write-Host '           Instalando (silencioso)...'; ^
        $proc = Start-Process msiexec.exe -ArgumentList \"/i `\"$out`\" /quiet /norestart\" -Wait -PassThru; ^
        Write-Host \"           Resultado: $($proc.ExitCode)\"; ^
        Remove-Item $out -Force -ErrorAction SilentlyContinue; ^
    } catch { ^
        Write-Host \"ERROR: $_\"; exit 1; ^
    }"
echo [%date% %time%] Descarga directa Node.js completada >> "%LOG_FILE%"

:node_check_after_install
:: Agregar rutas conocidas de Node.js al PATH de esta sesion
set "PATH=!PATH!;C:\Program Files\nodejs;%APPDATA%\npm"
echo [%date% %time%] PATH actualizado con rutas de Node.js >> "%LOG_FILE%"

where node >nul 2>&1
if !errorlevel! neq 0 (
    echo.
    echo    [ERROR] Node.js no se pudo instalar automaticamente.
    echo    Instalalo manualmente desde: https://nodejs.org
    echo    Luego ejecuta este script de nuevo.
    echo [%date% %time%] ERROR: Node.js no accesible despues de instalar >> "%LOG_FILE%"
    goto :error_exit
)

for /f "tokens=*" %%v in ('node -v 2^>nul') do set "NODE_VER=%%v"
echo           OK - Node.js !NODE_VER! instalado.
echo [%date% %time%] Node.js !NODE_VER! listo >> "%LOG_FILE%"

:node_ready
:: Guardar ruta de node.exe
for /f "tokens=*" %%p in ('where node 2^>nul') do (
    set "NODE_PATH=%%p"
    goto :node_path_set
)
:node_path_set
echo           Ruta: !NODE_PATH!
echo [%date% %time%] Node path: !NODE_PATH! >> "%LOG_FILE%"

:: ==============================================================
:: PASO 3: Git
:: ==============================================================
set /a STEP+=1
echo.
echo  [Paso !STEP!/%TOTAL_STEPS%] Verificando Git...
echo [%date% %time%] PASO !STEP!: Verificando Git >> "%LOG_FILE%"

where git >nul 2>&1
if !errorlevel! equ 0 (
    for /f "tokens=*" %%v in ('git --version 2^>nul') do set "GIT_VER=%%v"
    echo           OK - !GIT_VER! ya instalado.
    echo [%date% %time%] Git: !GIT_VER! ya instalado >> "%LOG_FILE%"
    goto :git_ready
)

echo           Git NO encontrado. Instalando...
echo [%date% %time%] Git: no encontrado, instalando >> "%LOG_FILE%"

if "!HAS_WINGET!"=="1" (
    echo           Usando winget...
    echo [%date% %time%] Intentando winget install Git >> "%LOG_FILE%"
    winget install Git.Git --silent --accept-package-agreements --accept-source-agreements >> "%LOG_FILE%" 2>&1
    if !errorlevel! equ 0 (
        echo           Winget: Git instalado.
        echo [%date% %time%] winget Git: OK >> "%LOG_FILE%"
        goto :git_check_after_install
    )
    echo           Winget fallo, intentando descarga directa...
    echo [%date% %time%] winget Git: fallo >> "%LOG_FILE%"
)

echo           Descargando Git desde GitHub...
echo [%date% %time%] Descargando Git directamente >> "%LOG_FILE%"
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
    "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; ^
    try { ^
        Write-Host '           Buscando ultima version...'; ^
        $rel = Invoke-RestMethod -Uri 'https://api.github.com/repos/git-for-windows/git/releases/latest' -TimeoutSec 30; ^
        $asset = $rel.assets | Where-Object { $_.name -match '64-bit\.exe$' } | Select-Object -First 1; ^
        Write-Host \"           Version: $($rel.tag_name)\"; ^
        $out = Join-Path $env:TEMP 'git-install.exe'; ^
        Write-Host '           Descargando...'; ^
        Invoke-WebRequest -Uri $asset.browser_download_url -OutFile $out -TimeoutSec 300; ^
        Write-Host '           Instalando (silencioso)...'; ^
        $proc = Start-Process $out -ArgumentList '/VERYSILENT /NORESTART /SP-' -Wait -PassThru; ^
        Write-Host \"           Resultado: $($proc.ExitCode)\"; ^
        Remove-Item $out -Force -ErrorAction SilentlyContinue; ^
    } catch { ^
        Write-Host \"ERROR: $_\"; exit 1; ^
    }"
echo [%date% %time%] Descarga directa Git completada >> "%LOG_FILE%"

:git_check_after_install
:: Agregar rutas conocidas de Git al PATH de esta sesion
set "PATH=!PATH!;C:\Program Files\Git\cmd;C:\Program Files\Git\bin"
echo [%date% %time%] PATH actualizado con rutas de Git >> "%LOG_FILE%"

where git >nul 2>&1
if !errorlevel! neq 0 (
    echo.
    echo    [ERROR] Git no se pudo instalar automaticamente.
    echo    Instalalo manualmente desde: https://git-scm.com
    echo    Luego ejecuta este script de nuevo.
    echo [%date% %time%] ERROR: Git no accesible despues de instalar >> "%LOG_FILE%"
    goto :error_exit
)

for /f "tokens=*" %%v in ('git --version 2^>nul') do set "GIT_VER=%%v"
echo           OK - !GIT_VER! instalado.
echo [%date% %time%] Git !GIT_VER! listo >> "%LOG_FILE%"

:git_ready

:: ==============================================================
:: PASO 4: Google Chrome
:: ==============================================================
set /a STEP+=1
echo.
echo  [Paso !STEP!/%TOTAL_STEPS%] Verificando Google Chrome...
echo [%date% %time%] PASO !STEP!: Verificando Chrome >> "%LOG_FILE%"

set "CHROME_OK=0"
if exist "C:\Program Files\Google\Chrome\Application\chrome.exe" set "CHROME_OK=1"

if "!CHROME_OK!"=="0" (
    if exist "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" set "CHROME_OK=1"
)

if "!CHROME_OK!"=="1" (
    echo           OK - Chrome ya instalado.
    echo [%date% %time%] Chrome: ya instalado >> "%LOG_FILE%"
    goto :chrome_ready
)

echo           Chrome NO encontrado. Instalando...
echo [%date% %time%] Chrome: no encontrado, instalando >> "%LOG_FILE%"

if "!HAS_WINGET!"=="1" (
    echo           Usando winget...
    echo [%date% %time%] Intentando winget install Chrome >> "%LOG_FILE%"
    winget install Google.Chrome --silent --accept-package-agreements --accept-source-agreements >> "%LOG_FILE%" 2>&1
    if !errorlevel! equ 0 (
        echo           Winget: Chrome instalado.
        echo [%date% %time%] winget Chrome: OK >> "%LOG_FILE%"
        goto :chrome_verify
    )
    echo           Winget fallo, intentando descarga directa...
    echo [%date% %time%] winget Chrome: fallo >> "%LOG_FILE%"
)

echo           Descargando Chrome desde Google...
echo [%date% %time%] Descargando Chrome directamente >> "%LOG_FILE%"
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
    "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; ^
    try { ^
        $url = 'https://dl.google.com/chrome/install/latest/chrome_installer.exe'; ^
        $out = Join-Path $env:TEMP 'chrome_installer.exe'; ^
        Write-Host '           Descargando...'; ^
        Invoke-WebRequest -Uri $url -OutFile $out -TimeoutSec 120; ^
        Write-Host '           Instalando (silencioso)...'; ^
        Start-Process $out -ArgumentList '/silent /install' -Wait; ^
        Write-Host '           Listo.'; ^
        Remove-Item $out -Force -ErrorAction SilentlyContinue; ^
    } catch { ^
        Write-Host \"ERROR: $_\"; exit 1; ^
    }"
echo [%date% %time%] Descarga directa Chrome completada >> "%LOG_FILE%"

:chrome_verify
set "CHROME_OK=0"
if exist "C:\Program Files\Google\Chrome\Application\chrome.exe" set "CHROME_OK=1"
if "!CHROME_OK!"=="0" (
    if exist "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" set "CHROME_OK=1"
)

if "!CHROME_OK!"=="1" (
    echo           OK - Chrome instalado.
    echo [%date% %time%] Chrome: instalado >> "%LOG_FILE%"
) else (
    echo           [AVISO] Chrome no se pudo instalar. Descargalo de:
    echo           https://www.google.com/chrome
    echo [%date% %time%] AVISO: Chrome no se pudo instalar >> "%LOG_FILE%"
)

:chrome_ready

:: ==============================================================
:: PASO 5: Crear directorio de instalacion
:: ==============================================================
set /a STEP+=1
echo.
echo  [Paso !STEP!/%TOTAL_STEPS%] Preparando directorio...
echo [%date% %time%] PASO !STEP!: Directorio >> "%LOG_FILE%"

if not exist "%INSTALL_DIR%" (
    echo           Creando: %INSTALL_DIR%
    mkdir "%INSTALL_DIR%" 2>nul
    if !errorlevel! neq 0 (
        echo    [ERROR] No se pudo crear el directorio.
        echo [%date% %time%] ERROR: mkdir fallo >> "%LOG_FILE%"
        goto :error_exit
    )
    echo           OK - Carpeta creada.
) else (
    echo           OK - Carpeta ya existe.
)
echo [%date% %time%] Directorio listo >> "%LOG_FILE%"

:: ==============================================================
:: PASO 6: Clonar / Actualizar repositorio
:: ==============================================================
set /a STEP+=1
echo.
echo  [Paso !STEP!/%TOTAL_STEPS%] Descargando codigo desde GitHub...
echo [%date% %time%] PASO !STEP!: Git clone >> "%LOG_FILE%"
echo           URL: %REPO_URL%
cd /d "%INSTALL_DIR%"

if exist ".git" (
    echo           Repo ya existe. Actualizando...
    git pull --rebase >> "%LOG_FILE%" 2>&1
    if !errorlevel! neq 0 (
        echo           [AVISO] Update fallo. Usando version actual.
        echo [%date% %time%] AVISO: git pull fallo >> "%LOG_FILE%"
    ) else (
        echo           OK - Actualizado.
    )
    goto :repo_ready
)

:: Si la carpeta tiene archivos preguntar
dir /b /a-d "%INSTALL_DIR%" >nul 2>&1
if !errorlevel! equ 0 (
    echo           La carpeta tiene archivos.
    set /p "OVERWRITE=          Sobrescribir? (S/N): "
    if /i "!OVERWRITE!" neq "S" (
        echo           Cancelado.
        echo [%date% %time%] Cancelado por usuario >> "%LOG_FILE%"
        goto :error_exit
    )
    echo           Limpiando...
    rmdir /s /q "%INSTALL_DIR%" 2>nul
    mkdir "%INSTALL_DIR%"
    cd /d "%INSTALL_DIR%"
)

echo           Clonando (puede tardar unos minutos)...
git clone "%REPO_URL%" "%INSTALL_DIR%" >> "%LOG_FILE%" 2>&1

:repo_ready
cd /d "%INSTALL_DIR%"
if not exist ".git" (
    echo.
    echo    [ERROR] No se pudo descargar el repositorio.
    echo    Verifica tu conexion a internet.
    echo    Intenta manualmente: git clone %REPO_URL%
    echo [%date% %time%] ERROR: git clone fallo >> "%LOG_FILE%"
    goto :error_exit
)
echo           OK - Codigo listo.
echo [%date% %time%] Repositorio listo >> "%LOG_FILE%"

:: ==============================================================
:: PASO 7: Instalar dependencias npm
:: ==============================================================
set /a STEP+=1
echo.
echo  [Paso !STEP!/%TOTAL_STEPS%] Instalando dependencias npm...
echo [%date% %time%] PASO !STEP!: npm install >> "%LOG_FILE%"

echo           [7a] Dependencias raiz...
cd /d "%INSTALL_DIR%"
call npm install >> "%LOG_FILE%" 2>&1
if !errorlevel! neq 0 (
    echo                [AVISO] Hubo warnings (ver log).
) else (
    echo                OK
)

echo           [7b] Dependencias del bot...
cd /d "%INSTALL_DIR%\bot"
if not exist "package.json" (
    echo    [ERROR] bot/package.json no encontrado.
    echo [%date% %time%] ERROR: bot/package.json no existe >> "%LOG_FILE%"
    goto :error_exit
)
call npm install >> "%LOG_FILE%" 2>&1
if !errorlevel! neq 0 (
    echo                [AVISO] Hubo warnings (ver log).
) else (
    echo                OK
)
echo [%date% %time%] Dependencias instaladas >> "%LOG_FILE%"

:: ==============================================================
:: PASO 8: Configurar .env
:: ==============================================================
set /a STEP+=1
echo.
echo  [Paso !STEP!/%TOTAL_STEPS%] Configurando base de datos...
echo [%date% %time%] PASO !STEP!: Configurar .env >> "%LOG_FILE%"
cd /d "%INSTALL_DIR%"

if exist ".env" (
    echo           OK - Archivo .env ya existe. Omitiendo.
    echo [%date% %time%] .env ya existe >> "%LOG_FILE%"
    goto :env_ready
)

echo.
echo   +----------------------------------------------------+
echo   :  CONFIGURACION DE BASE DE DATOS                    :
echo   :                                                    :
echo   :  Necesitas una base de datos PostgreSQL.            :
echo   :  Puedes crear una gratis en https://supabase.com   :
echo   :                                                    :
echo   :  Formato:                                          :
echo   :  postgresql://user:pass@host:6543/postgres         :
echo   +----------------------------------------------------+
echo.
set /p "DB_URL=  DATABASE_URL: "
if "!DB_URL!"=="" (
    echo    [ERROR] DATABASE_URL es obligatorio.
    echo [%date% %time%] ERROR: DATABASE_URL vacia >> "%LOG_FILE%"
    goto :error_exit
)
echo.
set /p "DIRECT_URL=  DIRECT_URL (Enter para omitir): "

echo # --- Base de datos --- > "%INSTALL_DIR%\.env"
echo DATABASE_URL="!DB_URL!" >> "%INSTALL_DIR%\.env"

if not "!DIRECT_URL!"=="" (
    echo DIRECT_URL="!DIRECT_URL!" >> "%INSTALL_DIR%\.env"
)

echo           OK - .env creado.
echo [%date% %time%] .env creado >> "%LOG_FILE%"

echo.
set /p "DO_PUSH=  Crear tablas ahora? (S/N): "
if /i "!DO_PUSH!"=="S" (
    echo           Creando tablas...
    cd /d "%INSTALL_DIR%"
    call npx prisma db push >> "%LOG_FILE%" 2>&1
    if !errorlevel! equ 0 (
        echo           OK - Tablas creadas.
        echo [%date% %time%] prisma db push: OK >> "%LOG_FILE%"
    ) else (
        echo           [AVISO] No se pudieron crear tablas.
        echo           Puedes reintentar: npx prisma db push
        echo [%date% %time%] AVISO: prisma db push fallo >> "%LOG_FILE%"
    )
)

:env_ready

:: ==============================================================
:: PASO 9: Prisma generate
:: ==============================================================
set /a STEP+=1
echo.
echo  [Paso !STEP!/%TOTAL_STEPS%] Generando cliente Prisma...
echo [%date% %time%] PASO !STEP!: prisma generate >> "%LOG_FILE%"
cd /d "%INSTALL_DIR%"

call npx prisma generate >> "%LOG_FILE%" 2>&1
if !errorlevel! neq 0 (
    echo           [AVISO] Prisma generate fallo.
    echo           Puedes reintentar: npx prisma generate
    echo [%date% %time%] AVISO: prisma generate fallo >> "%LOG_FILE%"
) else (
    echo           OK
    echo [%date% %time%] prisma generate: OK >> "%LOG_FILE%"
)

:: ==============================================================
:: PASO 10: Descargar NSSM
:: ==============================================================
set /a STEP+=1
echo.
echo  [Paso !STEP!/%TOTAL_STEPS%] Preparando NSSM...
echo [%date% %time%] PASO !STEP!: NSSM >> "%LOG_FILE%"
cd /d "%INSTALL_DIR%"

if exist "%INSTALL_DIR%\nssm.exe" (
    echo           OK - NSSM ya presente.
    echo [%date% %time%] NSSM ya existe >> "%LOG_FILE%"
    goto :nssm_ready
)

echo           Descargando NSSM...
echo [%date% %time%] Descargando NSSM >> "%LOG_FILE%"
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
    "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; ^
    try { ^
        $zip = Join-Path $env:TEMP 'nssm.zip'; ^
        $tmp = Join-Path $env:TEMP 'nssm-extract'; ^
        Invoke-WebRequest -Uri '%NSSM_URL%' -OutFile $zip -TimeoutSec 60; ^
        Expand-Archive -Path $zip -DestinationPath $tmp -Force; ^
        $exe = Get-ChildItem -Path $tmp -Recurse -Filter 'nssm.exe' | Where-Object { $_.DirectoryName -match 'win64' } | Select-Object -First 1; ^
        if (-not $exe) { $exe = Get-ChildItem -Path $tmp -Recurse -Filter 'nssm.exe' | Select-Object -First 1; } ^
        Copy-Item $exe.FullName '%INSTALL_DIR%\nssm.exe' -Force; ^
        Remove-Item $tmp -Recurse -Force -ErrorAction SilentlyContinue; ^
        Remove-Item $zip -Force -ErrorAction SilentlyContinue; ^
        Write-Host 'OK'; ^
    } catch { ^
        Write-Host \"ERROR: $_\"; exit 1; ^
    }"

if exist "%INSTALL_DIR%\nssm.exe" (
    echo           OK - NSSM descargado.
    echo [%date% %time%] NSSM descargado >> "%LOG_FILE%"
) else (
    echo           [AVISO] No se pudo descargar NSSM.
    echo           Descargalo de https://nssm.cc/download
    echo           Coloca nssm.exe en: %INSTALL_DIR%
    echo [%date% %time%] AVISO: NSSM fallo >> "%LOG_FILE%"
)

:nssm_ready

:: ==============================================================
:: PASO 11: Instalar servicio Windows
:: ==============================================================
set /a STEP+=1
echo.
echo [%date% %time%] PASO !STEP!: Servicio Windows >> "%LOG_FILE%"

if not exist "%INSTALL_DIR%\nssm.exe" (
    echo  [Paso !STEP!/%TOTAL_STEPS%] Servicio OMITIDO - NSSM no disponible.
    echo           Para ejecutar manualmente:
    echo             cd /d "%INSTALL_DIR%\bot"
    echo             node index.js
    echo [%date% %time%] Servicio omitido >> "%LOG_FILE%"
    goto :finish
)

echo  [Paso !STEP!/%TOTAL_STEPS%] Instalando servicio "BirthdayWabot"...

cd /d "%INSTALL_DIR%\bot"
if not exist "logs" mkdir logs

:: Limpiar servicio anterior
echo           Limpiando servicio anterior...
"%INSTALL_DIR%\nssm.exe" stop BirthdayWabot >nul 2>&1
timeout /t 2 /nobreak >nul
"%INSTALL_DIR%\nssm.exe" remove BirthdayWabot confirm >nul 2>&1
echo           OK

:: Crear servicio
echo           Creando servicio con:
echo             Node: !NODE_PATH!
echo             Dir:  %INSTALL_DIR%\bot
echo             App:  index.js

"%INSTALL_DIR%\nssm.exe" install BirthdayWabot "!NODE_PATH!" >> "%LOG_FILE%" 2>&1
if !errorlevel! neq 0 (
    echo    [ERROR] No se pudo crear el servicio.
    echo [%date% %time%] ERROR: nssm install fallo >> "%LOG_FILE%"
    goto :error_exit
)

"%INSTALL_DIR%\nssm.exe" set BirthdayWabot AppDirectory "%INSTALL_DIR%\bot" >nul 2>&1
"%INSTALL_DIR%\nssm.exe" set BirthdayWabot AppParameters "index.js" >nul 2>&1
"%INSTALL_DIR%\nssm.exe" set BirthdayWabot AppStdout "%INSTALL_DIR%\bot\logs\service-out.log" >nul 2>&1
"%INSTALL_DIR%\nssm.exe" set BirthdayWabot AppStderr "%INSTALL_DIR%\bot\logs\service-err.log" >nul 2>&1
"%INSTALL_DIR%\nssm.exe" set BirthdayWabot AppRotateFiles 1 >nul 2>&1
"%INSTALL_DIR%\nssm.exe" set BirthdayWabot AppRotateOnline 1 >nul 2>&1
"%INSTALL_DIR%\nssm.exe" set BirthdayWabot AppRotateSeconds 86400 >nul 2>&1
"%INSTALL_DIR%\nssm.exe" set BirthdayWabot AppRotateBytes 10485760 >nul 2>&1
"%INSTALL_DIR%\nssm.exe" set BirthdayWabot Start SERVICE_AUTO_START >nul 2>&1
"%INSTALL_DIR%\nssm.exe" set BirthdayWabot AppRestartDelay 5000 >nul 2>&1
"%INSTALL_DIR%\nssm.exe" set BirthdayWabot ObjectName LocalSystem >nul 2>&1
echo           OK - Servicio configurado.
echo [%date% %time%] Servicio configurado >> "%LOG_FILE%"

:: Iniciar
echo           Iniciando servicio...
"%INSTALL_DIR%\nssm.exe" start BirthdayWabot >> "%LOG_FILE%" 2>&1
if !errorlevel! equ 0 (
    echo           OK - Servicio ACTIVO.
    echo [%date% %time%] Servicio iniciado OK >> "%LOG_FILE%"
) else (
    echo           [AVISO] Servicio creado pero no arranco.
    echo           Revisa: type "%INSTALL_DIR%\bot\logs\service-err.log"
    echo           Iniciar: nssm start BirthdayWabot
    echo [%date% %time%] AVISO: servicio no arranco >> "%LOG_FILE%"
)

:: ==============================================================
:: FIN EXITOSO
:: ==============================================================
:finish
echo.
echo  +=====================================================+
echo  :    INSTALACION COMPLETADA!                          :
echo  +=====================================================+
echo.
echo  Rutas:
echo    Instalacion:  %INSTALL_DIR%
echo    Logs bot:     %INSTALL_DIR%\bot\logs\
echo    Log install:  %LOG_FILE%
echo.
echo  Comandos:
echo    Estado:      nssm status BirthdayWabot
echo    Logs:        "%INSTALL_DIR%\logs.bat"
echo    Reiniciar:   nssm restart BirthdayWabot
echo    Desinstalar: "%INSTALL_DIR%\uninstall.bat"
echo.
echo  SIGUIENTE PASO:
echo    El bot mostrara un QR en los logs.
echo    Escanea con WhatsApp ^> Dispositivos vinculados.
echo    Ver QR: type "%INSTALL_DIR%\bot\logs\service-out.log"
echo.
echo [%date% %time%] === INSTALACION COMPLETADA === >> "%LOG_FILE%"
pause
exit /b 0

:: ==============================================================
:: SALIDA POR ERROR
:: ==============================================================
:error_exit
echo.
echo  +=====================================================+
echo  :    INSTALACION NO COMPLETADA                        :
echo  +=====================================================+
echo.
echo  Revisa el error arriba.
echo  Log: %LOG_FILE%
echo.
echo [%date% %time%] === INSTALACION FALLIDA === >> "%LOG_FILE%"
pause
exit /b 1
