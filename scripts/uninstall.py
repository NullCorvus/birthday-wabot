import os
import sys
import ctypes
import subprocess
import shutil
import time

INSTALL_DIR = r"C:\Program Files\BirthdayWabot"
SERVICE_NAME = "BirthdayWabot"

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_cmd(cmd):
    """Ejecuta un comando en modo silencioso y devuelve el codigo de salida."""
    try:
        result = subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return result.returncode
    except:
        return 1

def kill_node_processes():
    """Mata cualquier proceso de node.exe ejecutado desde el directorio de instalación para liberar archivos."""
    print("  > Cerrando procesos asociados...")
    try:
        # Intenta matar node si fue lanzado desde INSTALL_DIR
        subprocess.run(
            f'wmic process where "name=\'node.exe\' and ExecutablePath like \'%BirthdayWabot%\'" call terminate',
            shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
    except:
        pass

def main():
    print("=============================================")
    print("  Birthday WaBot - Desinstalación")
    print("=============================================\n")

    if not is_admin():
        print("[ERROR] Este script debe ejecutarse como Administrador.")
        input("Presiona Enter para salir...")
        sys.exit(1)

    print(f"ADVERTENCIA: Esto eliminará el servicio de Windows y borrará TODOS los archivos en:")
    print(f"  {INSTALL_DIR}")
    resp = input("\n¿Estás seguro que deseas continuar? (s/n): ")
    if resp.lower() != 's':
        print("Desinstalación cancelada.")
        input("Presiona Enter para salir...")
        sys.exit(0)

    print("\n[*] Deteniendo y eliminando el servicio de Windows...")
    
    bot_dir = os.path.join(INSTALL_DIR, "bot")
    uninstall_script = os.path.join(bot_dir, "uninstall-service.js")
    
    if os.path.exists(uninstall_script):
        print("  > Ejecutando desinstalador de node-windows...")
        run_cmd(f'node "{uninstall_script}"')
        time.sleep(3)
        print("  > Servicio eliminado correctamente.")
    else:
        print("  > Desinstalador nativo no encontrado. Intentando con sc...")
        run_cmd(f'sc stop {SERVICE_NAME}')
        time.sleep(2)
        run_cmd(f'sc delete {SERVICE_NAME}')
        print("  > Servicio eliminado con SC.")

    time.sleep(2)  # Dar tiempo al sistema para liberar el lock del servicio
    kill_node_processes()
    time.sleep(1)

    print("\n[*] Eliminando archivos...")
    if os.path.exists(INSTALL_DIR):
        try:
            shutil.rmtree(INSTALL_DIR)
            print("  > Archivos eliminados correctamente.")
        except Exception as e:
            print(f"  > [AVISO] Algunos archivos no pudieron ser eliminados. Error: {e}")
            print(f"  > Intenta borrar la carpeta manualmente: {INSTALL_DIR}")
    else:
        print("  > La carpeta ya no existe.")

    print("\n=============================================")
    print("  Desinstalación completada.")
    print("=============================================")
    input("\nPresiona Enter para salir...")

if __name__ == "__main__":
    main()
