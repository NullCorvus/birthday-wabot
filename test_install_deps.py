import os
import sys
import ctypes
import subprocess
import urllib.request
import json
import tempfile
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_cmd(cmd, cwd=None, hide_output=False, shell=True):
    try:
        result = subprocess.run(
            cmd, cwd=cwd, shell=shell,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, encoding='utf-8', errors='replace'
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
    logging.info(f"  Intentando winget: {package_id} ...")
    code, out = run_cmd(f"winget install {package_id} --silent --accept-package-agreements --accept-source-agreements")
    if code == 0:
        logging.info(f"  [OK] {package_id} instalado con winget.")
        return True
    logging.warning(f"  winget falló para {package_id}, intentando descarga directa...")
    return False

def download_file(url, dest):
    logging.info(f"  Descargando: {url}")
    try:
        urllib.request.urlretrieve(url, dest)
        return True
    except Exception as e:
        logging.error(f"  Error en descarga: {e}")
        return False

def install_node():
    logging.info("--- [1/2] Verificando Node.js ---")
    code, out = run_cmd("node -v", hide_output=True)
    if code == 0:
        logging.info(f"  Node.js ya instalado: {out.strip()}  [OK]")
        return True

    logging.info("  Node.js NO instalado. Instalando...")
    if has_winget() and winget_install("OpenJS.NodeJS.LTS"):
        code, out = run_cmd("node -v", hide_output=True)
        if code == 0:
            logging.info(f"  Node.js instalado: {out.strip()}  [OK]")
            return True

    logging.info("  Descargando Node.js LTS desde nodejs.org...")
    try:
        with urllib.request.urlopen("https://nodejs.org/dist/index.json") as response:
            data = json.loads(response.read().decode())
            lts_version = next(item for item in data if item["lts"] is not False)["version"]
            url = f"https://nodejs.org/dist/{lts_version}/node-{lts_version}-x64.msi"
            dest = os.path.join(tempfile.gettempdir(), "node_installer.msi")
            if download_file(url, dest):
                logging.info("  Instalando Node.js (silencioso)...")
                run_cmd(f"msiexec.exe /i \"{dest}\" /quiet /norestart")
                os.remove(dest)
                code, out = run_cmd("node -v", hide_output=True)
                if code == 0:
                    logging.info(f"  Node.js instalado: {out.strip()}  [OK]")
                    return True
    except Exception as e:
        logging.error(f"  Fallo instalación Node.js: {e}")
        return False
    return True

def install_chrome():
    logging.info("--- [2/2] Verificando Google Chrome ---")
    paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
    ]
    if any(os.path.exists(p) for p in paths):
        logging.info("  Google Chrome ya instalado.  [OK]")
        return True

    logging.info("  Chrome NO instalado. Instalando...")
    if has_winget() and winget_install("Google.Chrome"):
        if any(os.path.exists(p) for p in paths):
            logging.info("  Chrome instalado correctamente.  [OK]")
            return True

    logging.info("  Descargando Chrome desde Google...")
    url = "https://dl.google.com/chrome/install/latest/chrome_installer.exe"
    dest = os.path.join(tempfile.gettempdir(), "chrome_installer.exe")
    if download_file(url, dest):
        logging.info("  Instalando Chrome (silencioso)...")
        run_cmd(f"\"{dest}\" /silent /install")
        os.remove(dest)
        if any(os.path.exists(p) for p in paths):
            logging.info("  Chrome instalado correctamente.  [OK]")
        else:
            logging.warning("  Chrome instalado (no se pudo verificar presencia).  [AVISO]")
        return True

    logging.error("  No se pudo instalar Chrome.  [ERROR]")
    return False

def main():
    print("\n" + "="*55)
    print("  TEST: Instalacion de dependencias (Node.js + Chrome)")
    print("="*55 + "\n")

    if not is_admin():
        logging.error("Este script debe ejecutarse como Administrador.")
        logging.error("Clic derecho > 'Ejecutar como administrador'")
        input("\nPresiona Enter para salir...")
        sys.exit(1)

    ok_node = install_node()
    ok_chrome = install_chrome()

    print("\n" + "="*55)
    print("  RESULTADO FINAL")
    print("="*55)
    print(f"  Node.js:  {'[OK]' if ok_node else '[ERROR]'}")
    print(f"  Chrome:   {'[OK]' if ok_chrome else '[ERROR]'}")

    if ok_node and ok_chrome:
        print("\n  TODO OK - Las dependencias estan listas.  [OK]")
    else:
        print("\n  Hubo errores. Revisa los logs arriba.  [ERROR]")

    print("="*55 + "\n")
    input("Presiona Enter para salir...")

if __name__ == "__main__":
    main()
