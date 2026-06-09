import os
import sys
import ctypes
import subprocess
import urllib.request
import zipfile
import shutil
import json
import logging
import tempfile
import time
from urllib.error import URLError

os.environ["PUPPETEER_SKIP_DOWNLOAD"] = "true"

# ==========================================
# CONFIGURACION
# ==========================================
INSTALL_DIR = r"C:\Program Files\BirthdayWabot"
REPO_URL = "https://github.com/NullCorvus/birthday-wabot.git"
NSSM_URL = "https://nssm.cc/release/nssm-2.24.zip"
LOG_FILE = os.path.join(tempfile.gettempdir(), "birthday-wabot-install.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_cmd(cmd, cwd=None, hide_output=False, shell=True):
    """Ejecuta un comando y devuelve (exit_code, stdout)."""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            shell=shell,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        if not hide_output and result.stdout:
            for line in result.stdout.splitlines():
                logging.debug(f"  > {line}")
        return result.returncode, result.stdout
    except Exception as e:
        logging.error(f"Error ejecutando '{cmd}': {e}")
        return 1, str(e)

def has_winget():
    code, _ = run_cmd("where winget", hide_output=True)
    return code == 0

def winget_install(package_id):
    logging.info(f"Intentando instalar {package_id} usando winget...")
    code, out = run_cmd(f"winget install {package_id} --silent --accept-package-agreements --accept-source-agreements")
    if code == 0:
        logging.info(f"[{package_id}] Instalado correctamente con winget.")
        return True
    else:
        logging.warning(f"Winget falló para {package_id}. Se intentará descarga directa.")
        return False

def download_file(url, dest):
    logging.info(f"Descargando: {url}")
    try:
        urllib.request.urlretrieve(url, dest)
        return True
    except Exception as e:
        logging.error(f"Error en la descarga: {e}")
        return False

# ==========================================
# PASOS DE INSTALACION
# ==========================================

def step_node():
    logging.info("--- [1/10] Verificando Node.js ---")
    code, out = run_cmd("node -v", hide_output=True)
    if code == 0:
        logging.info(f"Node.js ya está instalado: {out.strip()}")
        return True

    logging.info("Node.js NO está instalado.")
    if has_winget() and winget_install("OpenJS.NodeJS.LTS"):
        return True

    # Descarga directa fallback
    logging.info("Obteniendo última versión LTS de Node.js...")
    try:
        with urllib.request.urlopen("https://nodejs.org/dist/index.json") as response:
            data = json.loads(response.read().decode())
            lts_version = next(item for item in data if item["lts"] is not False)["version"]
            url = f"https://nodejs.org/dist/{lts_version}/node-{lts_version}-x64.msi"
            dest = os.path.join(tempfile.gettempdir(), "node_installer.msi")
            if download_file(url, dest):
                logging.info("Instalando Node.js (silencioso)...")
                run_cmd(f"msiexec.exe /i \"{dest}\" /quiet /norestart")
                os.remove(dest)
    except Exception as e:
        logging.error(f"Fallo instalación directa de Node: {e}")
        return False
    return True

def step_git():
    logging.info("--- [2/10] Verificando Git ---")
    code, out = run_cmd("git --version", hide_output=True)
    if code == 0:
        logging.info(f"Git ya está instalado: {out.strip()}")
        return True

    logging.info("Git NO está instalado.")
    if has_winget() and winget_install("Git.Git"):
        return True

    logging.info("Obteniendo última versión de Git...")
    try:
        with urllib.request.urlopen("https://api.github.com/repos/git-for-windows/git/releases/latest") as response:
            data = json.loads(response.read().decode())
            asset = next(a for a in data["assets"] if a["name"].endswith("64-bit.exe"))
            url = asset["browser_download_url"]
            dest = os.path.join(tempfile.gettempdir(), "git_installer.exe")
            if download_file(url, dest):
                logging.info("Instalando Git (silencioso)...")
                run_cmd(f"\"{dest}\" /VERYSILENT /NORESTART /SP-")
                os.remove(dest)
    except Exception as e:
        logging.error(f"Fallo instalación directa de Git: {e}")
        return False
    return True

def step_chrome():
    logging.info("--- [3/10] Verificando Google Chrome ---")
    paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
    ]
    if any(os.path.exists(p) for p in paths):
        logging.info("Google Chrome ya está instalado.")
        return True

    logging.info("Chrome NO está instalado. (Requerido por WhatsApp Web)")
    if has_winget() and winget_install("Google.Chrome"):
        return True

    url = "https://dl.google.com/chrome/install/latest/chrome_installer.exe"
    dest = os.path.join(tempfile.gettempdir(), "chrome_installer.exe")
    if download_file(url, dest):
        logging.info("Instalando Chrome (silencioso)...")
        run_cmd(f"\"{dest}\" /silent /install")
        os.remove(dest)
    
    return True

def step_repo():
    logging.info("--- [4/10] Preparando Repositorio ---")
    os.makedirs(INSTALL_DIR, exist_ok=True)
    
    git_dir = os.path.join(INSTALL_DIR, ".git")
    if os.path.exists(git_dir):
        logging.info("Actualizando repositorio existente...")
        code, _ = run_cmd("git pull --rebase", cwd=INSTALL_DIR)
        if code != 0:
            logging.warning("Fallo el pull, continuando con la versión actual.")
    else:
        # Si la carpeta tiene archivos que no son git, preguntar o limpiar
        if os.listdir(INSTALL_DIR):
            resp = input(f"La carpeta {INSTALL_DIR} no está vacía. ¿Sobrescribir? (s/n): ")
            if resp.lower() != 's':
                logging.error("Instalación cancelada por el usuario.")
                sys.exit(1)
            shutil.rmtree(INSTALL_DIR)
            os.makedirs(INSTALL_DIR)
            
        logging.info("Clonando repositorio...")
        code, _ = run_cmd(f"git clone \"{REPO_URL}\" \"{INSTALL_DIR}\"")
        if code != 0:
            logging.error("Fallo al clonar el repositorio.")
            return False
    return True

def step_npm():
    logging.info("--- [5/10] Instalando Dependencias NPM ---")
    
    # Reload path to pick up node/npm if newly installed
    os.environ["PATH"] += os.pathsep + r"C:\Program Files\nodejs"
    
    logging.info("Instalando dependencias raíz...")
    code, _ = run_cmd("npm install", cwd=INSTALL_DIR)
    
    # Fijar dependencia faltante de Prisma v7 para el config file
    logging.info("Instalando @prisma/config (requerido para Prisma v7)...")
    run_cmd("npm install @prisma/config --save-dev", cwd=INSTALL_DIR)
    
    bot_dir = os.path.join(INSTALL_DIR, "bot")
    if os.path.exists(bot_dir):
        logging.info("Instalando dependencias del bot...")
        code, _ = run_cmd("npm install", cwd=bot_dir)
    else:
        logging.error("No se encontró la carpeta 'bot'.")
        return False
    return True

def step_env():
    logging.info("--- [6/10] Configurando Base de Datos ---")
    env_file = os.path.join(INSTALL_DIR, ".env")
    
    if os.path.exists(env_file):
        logging.info("El archivo .env ya existe. Omitiendo.")
        return True

    print("\n" + "="*50)
    print("CONFIGURACION DE BASE DE DATOS")
    print("Se requiere una base de datos PostgreSQL (ej. Supabase)")
    print("Formato: postgresql://user:pass@host:6543/postgres")
    print("="*50 + "\n")
    
    db_url = input("DATABASE_URL: ").strip()
    if not db_url:
        logging.error("DATABASE_URL es obligatoria.")
        return False
        
    direct_url = input("DIRECT_URL (opcional, Enter para omitir): ").strip()
    
    with open(env_file, "w") as f:
        f.write("# --- Base de datos ---\n")
        f.write(f"DATABASE_URL=\"{db_url}\"\n")
        if direct_url:
            f.write(f"DIRECT_URL=\"{direct_url}\"\n")
            
    logging.info(".env creado exitosamente.")
    return True

def step_prisma():
    logging.info("--- [7/10] Generando Cliente Prisma ---")
    run_cmd("npx prisma generate", cwd=INSTALL_DIR)
    
    ans = input("\n¿Ejecutar 'prisma db push' para crear tablas ahora? (s/n): ")
    if ans.lower() == 's':
        logging.info("Creando tablas...")
        
        # Extraer DIRECT_URL del .env para usarlo en db push y evitar el error "prepared statement s1 already exists"
        direct_url = ""
        env_file = os.path.join(INSTALL_DIR, ".env")
        if os.path.exists(env_file):
            with open(env_file, "r") as f:
                for line in f:
                    if line.startswith("DIRECT_URL="):
                        direct_url = line.strip().split("=", 1)[1].strip('"').strip("'")
                        break
        
        cmd = "npx prisma db push --accept-data-loss"
        if direct_url:
            cmd += f" --url=\"{direct_url}\""
            
        code, _ = run_cmd(cmd, cwd=INSTALL_DIR)
        if code != 0:
            logging.warning("Fallo prisma db push. Revisa la URL en .env")
    return True

def step_service():
    logging.info("--- [8/8] Instalando Servicio Windows con node-windows ---")
    bot_dir = os.path.join(INSTALL_DIR, "bot")
    
    logging.info("Instalando node-windows...")
    code, out = run_cmd("npm install node-windows", cwd=bot_dir)
    if code != 0:
        logging.error(f"Fallo al instalar node-windows. Detalle del error:\\n{out}")
        return False

    service_script = os.path.join(bot_dir, "install-service.js")
    with open(service_script, "w", encoding="utf-8") as f:
        f.write("""const Service = require('node-windows').Service;
const path = require('path');

const svc = new Service({
  name: 'BirthdayWabot',
  description: 'Bot automatizado de WhatsApp (Birthday Wabot)',
  script: path.join(__dirname, 'index.js'),
  env: [{
    name: "NODE_ENV",
    value: "production"
  }]
});

svc.on('install', () => {
  svc.start();
  console.log('¡Servicio BirthdayWabot instalado y ejecutándose!');
});

svc.install();
""")

    uninstall_script = os.path.join(bot_dir, "uninstall-service.js")
    with open(uninstall_script, "w", encoding="utf-8") as f:
        f.write("""const Service = require('node-windows').Service;
const path = require('path');

const svc = new Service({
  name: 'BirthdayWabot',
  script: path.join(__dirname, 'index.js')
});

svc.on('uninstall', () => {
  console.log('Servicio BirthdayWabot desinstalado.');
});

svc.uninstall();
""")

    logging.info("Configurando e iniciando nuevo servicio...")
    # node-windows requires elevated privileges to install the service, but install.py is already running as admin.
    code, out = run_cmd("node install-service.js", cwd=bot_dir)
    if code != 0:
        logging.error(f"Fallo al configurar servicio con node-windows.")
        return False

    logging.info("Servicio iniciado correctamente con node-windows.")
    return True

def main():
    print(f"\\nLog detallado guardado en: {LOG_FILE}\\n")
    
    if not is_admin():
        logging.error("Este script DEBE ejecutarse como Administrador.")
        input("Presiona Enter para salir...")
        sys.exit(1)

    steps = [
        step_node,
        step_git,
        step_chrome,
        step_repo,
        step_npm,
        step_env,
        step_prisma,
        step_service
    ]

    for step in steps:
        if not step():
            logging.error(f"Instalación abortada en {step.__name__}")
            input("Presiona Enter para salir...")
            sys.exit(1)
            
    logging.info("\n" + "="*50)
    logging.info("INSTALACION COMPLETADA EXITOSAMENTE")
    logging.info("="*50)
    logging.info(f"Directorio: {INSTALL_DIR}")
    logging.info("Para ver el QR del bot, abre:")
    logging.info(f"  {os.path.join(INSTALL_DIR, 'bot', 'logs', 'service-out.log')}")
    input("\nPresiona Enter para salir...")

if __name__ == "__main__":
    main()
