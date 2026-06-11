import os
import sys
import ctypes
import subprocess
import shutil
import time
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

INSTALL_DIR = r"C:\Program Files\BirthdayWabot"
SERVICE_NAME = "BirthdayWabot"

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_cmd(cmd, hide_output=False):
    try:
        result = subprocess.run(
            cmd, shell=True,
            stdout=subprocess.PIPE if hide_output else None,
            stderr=subprocess.PIPE if hide_output else None,
            text=True, encoding='utf-8', errors='replace'
        )
        return result.returncode
    except:
        return 1

def check_service():
    try:
        result = subprocess.run(
            f'sc query "{SERVICE_NAME}"', shell=True,
            capture_output=True, text=True
        )
        return "RUNNING" in result.stdout or "STOPPED" in result.stdout
    except:
        return False

def stop_service():
    logging.info("  Deteniendo servicio...")
    run_cmd(f'sc stop {SERVICE_NAME}', hide_output=True)
    time.sleep(2)

def remove_service():
    logging.info("  Eliminando servicio...")
    run_cmd(f'sc delete {SERVICE_NAME}', hide_output=True)
    time.sleep(1)

def kill_node_processes():
    logging.info("  Matando procesos node.exe del bot...")
    try:
        subprocess.run(
            'wmic process where "name=\'node.exe\' and ExecutablePath like \'%BirthdayWabot%\'" call terminate',
            shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
    except:
        pass
    run_cmd("taskkill /F /IM node.exe /FI \"WINDOWTITLE eq birthday*\"", hide_output=True)
    time.sleep(1)

def delete_files():
    logging.info(f"  Eliminando carpeta: {INSTALL_DIR}")
    if os.path.exists(INSTALL_DIR):
        try:
            shutil.rmtree(INSTALL_DIR)
            logging.info("  Archivos eliminados correctamente.")
            return True
        except Exception as e:
            logging.error(f"  No se pudo eliminar: {e}")
            return False
    else:
        logging.info("  La carpeta ya no existe.  [OK]")
        return True

def main():
    print("\n" + "="*55)
    print("  TEST: Desinstalacion de Birthday WaBot")
    print("="*55 + "\n")

    if not is_admin():
        logging.error("Este script debe ejecutarse como Administrador.")
        input("\nPresiona Enter para salir...")
        sys.exit(1)

    print(f"  Directorio: {INSTALL_DIR}")
    print(f"  Servicio:   {SERVICE_NAME}\n")

    svc_exists = check_service()
    dir_exists = os.path.exists(INSTALL_DIR)

    print("  Estado actual:")
    print(f"    Servicio existe:  {'Si' if svc_exists else 'No'}")
    print(f"    Carpeta existe:   {'Si' if dir_exists else 'No'}")

    if not svc_exists and not dir_exists:
        print("\n  No hay nada que desinstalar.  [OK]")
        input("\nPresiona Enter para salir...")
        return

    resp = input("\n  Desinstalar? (s/n): ")
    if resp.lower() != 's':
        print("  Cancelado.")
        input("\nPresiona Enter para salir...")
        return

    print("\n" + "-"*55)

    if svc_exists:
        stop_service()
        kill_node_processes()
        remove_service()
        if check_service():
            logging.error("  No se pudo eliminar el servicio.  [ERROR]")
        else:
            logging.info("  Servicio eliminado.  [OK]")
    else:
        logging.info("  No hay servicio instalado.  [OK]")

    kill_node_processes()
    ok = delete_files()

    print("\n" + "="*55)
    print("  RESULTADO FINAL")
    print("="*55)
    print(f"  Servicio:  {'[OK] Eliminado' if not check_service() else '[ERROR] Aun existe'}")
    print(f"  Archivos:  {'[OK] Eliminados' if ok else '[ERROR] No se pudo borrar'}")

    if not check_service() and ok:
        print("\n  TODO OK - Desinstalacion completada.  [OK]")
    else:
        print("\n  Hubo errores. Revisa los logs arriba.  [ERROR]")

    print("="*55 + "\n")
    input("Presiona Enter para salir...")

if __name__ == "__main__":
    main()
