import os
import sys
import subprocess
import threading
import time
import shutil
import json
import customtkinter as ctk
from tkinter import messagebox
from tkinter import Canvas
from PIL import Image, ImageDraw

# ---------------------------------------------------------------------------
# Helpers de ruta
# ---------------------------------------------------------------------------
APP_CONFIG_DIR = os.path.join(os.environ.get('APPDATA', os.path.expanduser('~')), 'BirthdayWabot')

def get_exe_dir():
    os.makedirs(APP_CONFIG_DIR, exist_ok=True)
    return APP_CONFIG_DIR

def get_bundle_dir():
    if getattr(sys, 'frozen', False):
        if hasattr(sys, '_MEIPASS'):
            return sys._MEIPASS
        return os.path.dirname(sys.executable)
    return os.path.abspath(os.path.dirname(__file__))

def is_admin():
    import ctypes
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

INSTALL_DIR = r"C:\Program Files\BirthdayWabot"

# ---------------------------------------------------------------------------
# Colores - Dashboard Web
# ---------------------------------------------------------------------------
COLOR_BG = "#050505"
COLOR_CARD = "#141414"
COLOR_CARD_HOVER = "#1c1c1c"
COLOR_PURPLE = "#a855f7"
COLOR_PURPLE_HOVER = "#9333ea"
COLOR_RED = "#ef4444"
COLOR_RED_HOVER = "#dc2626"
COLOR_GREEN = "#22c55e"
COLOR_TEXT = "#f8fafc"
COLOR_TEXT_MUTED = "#94a3b8"
COLOR_BORDER = "#27272a"

ctk.set_appearance_mode("dark")

class VerticalStepper(ctk.CTkFrame):
    def __init__(self, master, steps, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.steps = steps
        self.step_widgets = []
        
        for i, step_text in enumerate(steps):
            frame = ctk.CTkFrame(self, fg_color="transparent")
            frame.pack(fill="x", pady=8)
            
            # Status Indicator (Circle)
            status_canvas = Canvas(frame, width=24, height=24, bg=COLOR_CARD, highlightthickness=0)
            status_canvas.pack(side="left", padx=(5, 15))
            self._draw_circle(status_canvas, "pending")
            
            # Text
            lbl = ctk.CTkLabel(frame, text=step_text, font=ctk.CTkFont(size=14, weight="bold"), text_color=COLOR_TEXT_MUTED)
            lbl.pack(side="left")
            
            # Sub Status Text
            sub_lbl = ctk.CTkLabel(frame, text="Pendiente", font=ctk.CTkFont(size=12), text_color=COLOR_TEXT_MUTED)
            sub_lbl.pack(side="right", padx=10)
            
            self.step_widgets.append({
                "canvas": status_canvas,
                "label": lbl,
                "sub_label": sub_lbl,
                "frame": frame
            })
            
            # Draw line connecting to next
            if i < len(steps) - 1:
                line_canvas = Canvas(self, width=24, height=20, bg=COLOR_CARD, highlightthickness=0)
                line_canvas.pack(fill="none", anchor="w", padx=(5, 0))
                line_canvas.create_line(12, 0, 12, 20, fill=COLOR_BORDER, width=2, dash=(4, 4))

    def _draw_circle(self, canvas, status):
        canvas.delete("all")
        if status == "pending":
            canvas.create_oval(2, 2, 22, 22, outline=COLOR_TEXT_MUTED, width=2, dash=(2, 2))
        elif status == "running":
            canvas.create_oval(2, 2, 22, 22, outline=COLOR_PURPLE, width=3)
            canvas.create_oval(8, 8, 16, 16, fill=COLOR_PURPLE, outline="")
        elif status == "done":
            canvas.create_oval(2, 2, 22, 22, fill=COLOR_GREEN, outline="")
            # checkmark
            canvas.create_line(6, 12, 10, 16, 18, 8, fill="white", width=2)
        elif status == "error":
            canvas.create_oval(2, 2, 22, 22, fill=COLOR_RED, outline="")
            # X mark
            canvas.create_line(8, 8, 16, 16, fill="white", width=2)
            canvas.create_line(16, 8, 8, 16, fill="white", width=2)

    def set_step_status(self, index, status):
        widget = self.step_widgets[index]
        self._draw_circle(widget["canvas"], status)
        
        if status == "running":
            widget["label"].configure(text_color=COLOR_TEXT)
            widget["sub_label"].configure(text="Procesando...", text_color=COLOR_PURPLE)
        elif status == "done":
            widget["label"].configure(text_color=COLOR_TEXT)
            widget["sub_label"].configure(text="Completado", text_color=COLOR_GREEN)
        elif status == "error":
            widget["label"].configure(text_color=COLOR_RED)
            widget["sub_label"].configure(text="Error", text_color=COLOR_RED)
        else:
            widget["label"].configure(text_color=COLOR_TEXT_MUTED)
            widget["sub_label"].configure(text="Pendiente", text_color=COLOR_TEXT_MUTED)


class WabotManagerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Birthday Wabot Manager")
        self.geometry("1150x750")
        self.configure(fg_color=COLOR_BG)
        
        # Set Window Icon for Taskbar
        try:
            icon_path = os.path.join(get_bundle_dir(), "wabot_icon_blue.ico")
            if os.path.exists(icon_path):
                self.iconbitmap(icon_path)
            else:
                # Fallback to the current directory if running uncompiled
                local_icon = os.path.join(os.path.dirname(__file__), "wabot_icon_blue.ico")
                if os.path.exists(local_icon):
                    self.iconbitmap(local_icon)
        except:
            pass
            
        # Header / Tabview
        self.tabview = ctk.CTkTabview(self, segmented_button_selected_color=COLOR_PURPLE, 
                                      segmented_button_selected_hover_color=COLOR_PURPLE_HOVER,
                                      segmented_button_unselected_color=COLOR_CARD,
                                      segmented_button_unselected_hover_color=COLOR_CARD_HOVER,
                                      fg_color=COLOR_BG, bg_color=COLOR_BG, corner_radius=10)
        self.tabview.pack(padx=20, pady=10, fill="both", expand=True)
        
        self.tab_config = self.tabview.add("1. Configuración & Instalación")
        self.tab_qr = self.tabview.add("2. Conexión WhatsApp")
        self.tab_logs = self.tabview.add("3. Consola / Logs")
        
        self.last_log_size = 0
        self.qr_image_tk = None
        self.last_known_status = None
        
        self.setup_tab_config()
        self.setup_tab_qr()
        self.setup_tab_logs()
        
        self.update_status()
        self.read_logs()
        self.monitor_qr()
        self.monitor_status()
        
    def setup_tab_config(self):
        self.tab_config.grid_columnconfigure(0, weight=6)
        self.tab_config.grid_columnconfigure(1, weight=4)
        self.tab_config.grid_rowconfigure(0, weight=1)
        
        # === LEFT PANEL ===
        left_panel = ctk.CTkFrame(self.tab_config, fg_color="transparent")
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        # Supabase Config Card
        card_db = ctk.CTkFrame(left_panel, fg_color=COLOR_CARD, corner_radius=10, border_width=1, border_color=COLOR_BORDER)
        card_db.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(card_db, text="CONFIGURACIÓN DE SUPABASE", font=ctk.CTkFont(size=13, weight="bold"), text_color=COLOR_PURPLE).pack(anchor="w", padx=20, pady=(20, 5))
        ctk.CTkLabel(card_db, text="Ingresa las URLs de tu proyecto Supabase. Se guardarán en el archivo .env", font=ctk.CTkFont(size=12), text_color=COLOR_TEXT_MUTED).pack(anchor="w", padx=20, pady=(0, 15))
        
        inputs_frame = ctk.CTkFrame(card_db, fg_color="transparent")
        inputs_frame.pack(fill="x", padx=20, pady=(0, 15))
        inputs_frame.grid_columnconfigure(0, weight=1)
        inputs_frame.grid_columnconfigure(1, weight=1)
        
        frame_db_url = ctk.CTkFrame(inputs_frame, fg_color="transparent")
        frame_db_url.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        ctk.CTkLabel(frame_db_url, text="DATABASE_URL (Puerto 6543)", font=ctk.CTkFont(size=11, weight="bold")).pack(anchor="w")
        self.db_url_var = ctk.StringVar()
        ctk.CTkEntry(frame_db_url, textvariable=self.db_url_var, placeholder_text="postgresql://...", fg_color=COLOR_BG, border_color=COLOR_BORDER).pack(fill="x", pady=(5,0))
        
        frame_direct_url = ctk.CTkFrame(inputs_frame, fg_color="transparent")
        frame_direct_url.grid(row=0, column=1, sticky="ew", padx=(10, 0))
        ctk.CTkLabel(frame_direct_url, text="DIRECT_URL (Puerto 5432)", font=ctk.CTkFont(size=11, weight="bold")).pack(anchor="w")
        self.direct_url_var = ctk.StringVar()
        ctk.CTkEntry(frame_direct_url, textvariable=self.direct_url_var, placeholder_text="postgresql://...", fg_color=COLOR_BG, border_color=COLOR_BORDER).pack(fill="x", pady=(5,0))
        
        self.load_env()
        
        btn_guardar = ctk.CTkButton(card_db, text="Guardar Configuración", fg_color=COLOR_PURPLE, hover_color=COLOR_PURPLE_HOVER, corner_radius=6, command=self.save_env)
        btn_guardar.pack(anchor="e", padx=20, pady=(0, 20))
        
        # Action Buttons
        actions_frame = ctk.CTkFrame(left_panel, fg_color="transparent")
        actions_frame.pack(fill="x", pady=(0, 15))
        actions_frame.grid_columnconfigure(0, weight=1)
        actions_frame.grid_columnconfigure(1, weight=1)
        
        btn_install = ctk.CTkButton(actions_frame, text="Instalar Bot", fg_color=COLOR_PURPLE, hover_color=COLOR_PURPLE_HOVER, height=45, corner_radius=8, font=ctk.CTkFont(size=14, weight="bold"), command=self.install_bot_thread)
        btn_install.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        
        btn_uninstall = ctk.CTkButton(actions_frame, text="Desinstalar Bot", fg_color=COLOR_RED, hover_color=COLOR_RED_HOVER, height=45, corner_radius=8, font=ctk.CTkFont(size=14, weight="bold"), command=self.uninstall_bot_thread)
        btn_uninstall.grid(row=0, column=1, sticky="ew", padx=(5, 0))
        
        push_frame = ctk.CTkFrame(left_panel, fg_color="transparent")
        push_frame.pack(fill="x", pady=(0, 15), padx=5)
        self.push_var = ctk.BooleanVar(value=True)
        self.push_check = ctk.CTkCheckBox(
            push_frame, text="Ejecutar Prisma DB Push (Crear/Actualizar tablas)", 
            variable=self.push_var, onvalue=True, offvalue=False,
            font=ctk.CTkFont(size=12), fg_color=COLOR_PURPLE, hover_color=COLOR_PURPLE_HOVER,
            border_color=COLOR_BORDER, border_width=2
        )
        self.push_check.pack(side="left")
        
        # Vertical Stepper
        card_tasks = ctk.CTkFrame(left_panel, fg_color=COLOR_CARD, corner_radius=10, border_width=1, border_color=COLOR_BORDER)
        card_tasks.pack(fill="both", expand=True)
        
        ctk.CTkLabel(card_tasks, text="PROGRESO DE INSTALACIÓN", font=ctk.CTkFont(size=12, weight="bold"), text_color=COLOR_TEXT_MUTED).pack(anchor="w", padx=20, pady=(15, 10))
        
        steps = [
            "Copiando Archivos...",
            "Instalando Librerías Base (NPM)...",
            "Generando Cliente Prisma...",
            "Configurando Base de Datos (Push)...",
            "Iniciando Servicio Windows..."
        ]
        self.stepper = VerticalStepper(card_tasks, steps)
        self.stepper.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        
        # === RIGHT PANEL ===
        right_panel = ctk.CTkFrame(self.tab_config, fg_color="transparent")
        right_panel.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        
        # System Info Card
        card_info = ctk.CTkFrame(right_panel, fg_color=COLOR_CARD, corner_radius=10, border_width=1, border_color=COLOR_BORDER)
        card_info.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(card_info, text="INFORMACIÓN DEL SISTEMA", font=ctk.CTkFont(size=12, weight="bold"), text_color=COLOR_TEXT_MUTED).pack(anchor="w", padx=20, pady=(15, 10))
        
        self.lbl_svc_status = ctk.CTkLabel(card_info, text="Estado: DESCONOCIDO", font=ctk.CTkFont(size=13, weight="bold"))
        self.lbl_svc_status.pack(anchor="w", padx=20, pady=2)
        
        ctk.CTkLabel(card_info, text=f"Ruta: {INSTALL_DIR}", text_color=COLOR_TEXT_MUTED).pack(anchor="w", padx=20, pady=(2, 15))
        
        # Botones de Acción Rápida (Logs, Force Trigger)
        btn_trigger = ctk.CTkButton(card_info, text="⚡ Forzar Envío Manual", fg_color=COLOR_BG, hover_color=COLOR_CARD_HOVER, border_width=1, border_color=COLOR_BORDER, corner_radius=6, command=self.force_manual_trigger)
        btn_trigger.pack(fill="x", padx=20, pady=(0, 15))
        
        # Banner Prisma Help
        card_help = ctk.CTkFrame(right_panel, fg_color="#083344", corner_radius=10, border_width=1, border_color="#0e7490")
        card_help.pack(fill="x")
        
        ctk.CTkLabel(card_help, text="ℹ️ ¿Problemas con Prisma?", font=ctk.CTkFont(size=13, weight="bold"), text_color="#22d3ee").pack(anchor="w", padx=20, pady=(15, 5))
        help_text = (
            "Al usar Supabase, asegúrate de colocar las URLs correctas:\n\n"
            "• DATABASE_URL debe terminar en puerto 6543 e incluir pgbouncer=true.\n"
            "• DIRECT_URL debe usar el puerto 5432 y es crucial para crear tablas."
        )
        ctk.CTkLabel(card_help, text=help_text, justify="left", font=ctk.CTkFont(size=11), text_color="#cffafe", wraplength=250).pack(anchor="w", padx=20, pady=(0, 15))

    def setup_tab_qr(self):
        self.tab_qr.grid_columnconfigure(0, weight=1)
        self.tab_qr.grid_rowconfigure(0, weight=1)
        
        card_qr = ctk.CTkFrame(self.tab_qr, fg_color=COLOR_CARD, corner_radius=10, border_width=1, border_color=COLOR_BORDER)
        card_qr.grid(row=0, column=0, sticky="nsew", padx=50, pady=50)
        
        self.lbl_qr_status = ctk.CTkLabel(card_qr, text="Esperando QR...", font=ctk.CTkFont(size=18, weight="bold"), text_color=COLOR_TEXT_MUTED)
        self.lbl_qr_status.pack(pady=(40, 20))
        
        self.lbl_qr_image = ctk.CTkLabel(card_qr, text="")
        self.lbl_qr_image.pack(expand=True)
        
    def setup_tab_logs(self):
        self.tab_logs.grid_columnconfigure(0, weight=1)
        self.tab_logs.grid_rowconfigure(0, weight=1)
        
        import tkinter as tk
        card_log = ctk.CTkFrame(self.tab_logs, fg_color=COLOR_CARD, corner_radius=10, border_width=1, border_color=COLOR_BORDER)
        card_log.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        self.txt_logs = tk.Text(card_log, bg=COLOR_BG, fg=COLOR_TEXT, font=("Consolas", 10), bd=0, highlightthickness=0)
        self.txt_logs.pack(fill="both", expand=True, padx=10, pady=10)
        
        btn_clear = ctk.CTkButton(card_log, text="Limpiar Logs", width=120, fg_color=COLOR_BG, border_width=1, border_color=COLOR_BORDER, hover_color=COLOR_CARD_HOVER, command=lambda: self.txt_logs.delete(1.0, tk.END))
        btn_clear.pack(anchor="e", padx=10, pady=(0, 10))

    # -----------------------------------------------------------------------
    # Utilidades
    # -----------------------------------------------------------------------
    def load_env(self):
        env_path = os.path.join(APP_CONFIG_DIR, ".env")
        if not os.path.exists(env_path):
            env_path = os.path.join(get_bundle_dir(), ".env")
        if os.path.exists(env_path):
            with open(env_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                for line in lines:
                    if line.startswith("DATABASE_URL="):
                        self.db_url_var.set(line.split("=")[1].strip().strip('"').strip("'"))
                    elif line.startswith("DIRECT_URL="):
                        self.direct_url_var.set(line.split("=")[1].strip().strip('"').strip("'"))

    def save_env(self):
        env_path = os.path.join(APP_CONFIG_DIR, ".env")
        content = f'DATABASE_URL="{self.db_url_var.get()}"\nDIRECT_URL="{self.direct_url_var.get()}"\n'
        with open(env_path, "w", encoding="utf-8") as f:
            f.write(content)
        messagebox.showinfo("Guardado", "Configuración de Supabase guardada correctamente.")

    def log(self, msg):
        import tkinter as tk
        self.txt_logs.insert(tk.END, msg + "\n")
        self.txt_logs.see(tk.END)

    def run_command(self, cmd, cwd=None, env=None):
        self.log(f"\n[Ejecutando]: {cmd}")
        try:
            # stdin=subprocess.DEVNULL previene bloqueos de prompts (ej: Prisma)
            process = subprocess.Popen(
                cmd, cwd=cwd, shell=True, env=env,
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
                text=True, encoding="utf-8", errors="replace"
            )
            for line in process.stdout:
                self.log(line.strip())
            process.wait()
            return process.returncode
        except Exception as e:
            self.log(f"Error ejecutando comando: {e}")
            return 1

    # -----------------------------------------------------------------------
    # Lógica de Trigger Manual
    # -----------------------------------------------------------------------
    def force_manual_trigger(self):
        bot_dir = os.path.join(INSTALL_DIR, "bot")
        if not os.path.exists(bot_dir):
            messagebox.showerror("Error", "El bot no parece estar instalado.")
            return
            
        trigger_path = os.path.join(bot_dir, ".trigger_send")
        try:
            with open(trigger_path, "w") as f:
                f.write("trigger")
            messagebox.showinfo("Éxito", "Señal enviada. Revisa la pestaña de consola/logs para ver el progreso del envío.")
            self.tabview.set("3. Consola / Logs")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo enviar la señal: {e}")

    # -----------------------------------------------------------------------
    # Hilos y Lógica de Instalación
    # -----------------------------------------------------------------------
    def update_task_ui(self, index, status):
        # Corre en el main thread para actualizar la GUI
        self.after(0, lambda: self.stepper.set_step_status(index - 1, status))

    def install_bot_thread(self):
        if not is_admin():
            messagebox.showerror("Error", "Debes abrir el programa como Administrador para instalar.")
            return
        
        for i in range(5):
            self.update_task_ui(i+1, "pending")
        
        threading.Thread(target=self.install_bot, daemon=True).start()

    def install_bot(self):
        # 1. Copiar Archivos
        self.update_task_ui(1, 'running')
        if os.path.exists(INSTALL_DIR):
            self.log("Carpeta de destino ya existe, limpiando...")
            try:
                shutil.rmtree(INSTALL_DIR, ignore_errors=True)
            except Exception as e:
                self.log(f"Error limpiando carpeta: {e}")
                self.update_task_ui(1, 'error')
                return
        
        os.makedirs(INSTALL_DIR, exist_ok=True)
        bot_dir = os.path.join(INSTALL_DIR, "bot")
        os.makedirs(bot_dir, exist_ok=True)
        
        source_dir = get_bundle_dir()
        
        shutil.copy2(os.path.join(APP_CONFIG_DIR, ".env") if os.path.exists(os.path.join(APP_CONFIG_DIR, ".env")) else os.path.join(source_dir, ".env"), os.path.join(INSTALL_DIR, ".env"))
        
        for item in ["package.json", "package-lock.json", "prisma.config.ts"]:
            src = os.path.join(source_dir, item)
            if os.path.exists(src):
                shutil.copy2(src, os.path.join(INSTALL_DIR, item))
                
        shutil.copytree(os.path.join(source_dir, "prisma"), os.path.join(INSTALL_DIR, "prisma"))
        shutil.copytree(os.path.join(source_dir, "bot"), bot_dir, dirs_exist_ok=True)
        
        # Generar install-service.js
        install_js_code = """
const Service = require('node-windows').Service;
const path = require('path');

const svc = new Service({
    name: 'Birthday Wabot',
    description: 'Bot de WhatsApp para Cumpleanos',
    script: path.join(__dirname, 'index.js'),
    env: [{
        name: "NODE_ENV",
        value: "production"
    }]
});

svc.on('install', () => {
    console.log('Servicio instalado exitosamente en Windows!');
    svc.start();
    console.log('Servicio iniciado!');
});

svc.on('alreadyinstalled', () => {
    console.log('El servicio ya estaba instalado.');
    svc.start();
});

svc.on('error', (err) => {
    console.error('Error fatal instalando el servicio:', err);
    process.exit(1);
});

svc.install();
"""
        with open(os.path.join(bot_dir, "install-service.js"), "w", encoding="utf-8") as f:
            f.write(install_js_code)

        self.update_task_ui(1, 'done')

        # 2. NPM Install Raiz
        self.update_task_ui(2, 'running')
        if self.run_command("npm install", cwd=INSTALL_DIR) != 0:
            self.update_task_ui(2, 'error')
            return
        self.update_task_ui(2, 'done')

        # 3. Prisma Generate
        self.update_task_ui(3, 'running')
        self.run_command("npm install @prisma/config --save-dev", cwd=INSTALL_DIR)
        if self.run_command("npx prisma generate", cwd=INSTALL_DIR) != 0:
            self.update_task_ui(3, 'error')
            return
        self.update_task_ui(3, 'done')

        # 4. Prisma DB Push
        if self.push_var.get():
            self.update_task_ui(4, 'running')
            direct_url = self.direct_url_var.get()
            push_cmd = f'npx prisma db push --accept-data-loss --url="{direct_url}"'
            push_result = self.run_command(push_cmd, cwd=INSTALL_DIR)
            if push_result != 0:
                self.log("⚠️ El push falló. Si las tablas ya existen, puedes continuar.")
                res = messagebox.askyesno("Aviso", "El push de base de datos falló.\n¿Continuar de todos modos si las tablas ya existen?")
                if not res:
                    self.update_task_ui(4, 'error')
                    return
            self.update_task_ui(4, 'done')
        else:
            self.update_task_ui(4, 'done')
            self.stepper.step_widgets[3]["sub_label"].configure(text="Saltado")

        # 5. Servicio Windows
        self.update_task_ui(5, 'running')
        daemon_dir = os.path.join(bot_dir, "daemon")
        if os.path.exists(daemon_dir):
            shutil.rmtree(daemon_dir, ignore_errors=True)
            
        if self.run_command("npm install", cwd=bot_dir) != 0:
            self.update_task_ui(5, 'error')
            return
        self.run_command("npm install node-windows", cwd=bot_dir)
        if self.run_command("node install-service.js", cwd=bot_dir) != 0:
            self.update_task_ui(5, 'error')
            return
        self.update_task_ui(5, 'done')

        self.log("=== INSTALACION COMPLETADA EXITOSAMENTE ===")
        messagebox.showinfo("Éxito", "El Bot se ha instalado. Ve a la pestaña 'Conexión WhatsApp' para escanear el QR.")

    def uninstall_bot_thread(self):
        if not is_admin():
            messagebox.showerror("Error", "Debes ser Administrador para desinstalar.")
            return
        res = messagebox.askyesno("Confirmar", "¿Eliminar el bot y todos sus datos?")
        if res:
            threading.Thread(target=self.uninstall_bot, daemon=True).start()

    def uninstall_bot(self):
        self.log("=== INICIANDO DESINSTALACION ===")
        bot_dir = os.path.join(INSTALL_DIR, "bot")
        
        uninstall_js_code = """
const Service = require('node-windows').Service;
const path = require('path');
const svc = new Service({
    name: 'Birthday Wabot',
    description: 'Bot de WhatsApp para Cumpleanos',
    script: path.join(__dirname, 'index.js')
});
svc.on('uninstall', () => {
    console.log('Servicio desinstalado.');
});
svc.uninstall();
"""
        if os.path.exists(bot_dir):
            un_js_path = os.path.join(bot_dir, "uninstall-service.js")
            with open(un_js_path, "w", encoding="utf-8") as f:
                f.write(uninstall_js_code)
            self.run_command("node uninstall-service.js", cwd=bot_dir)
            time.sleep(3) # Wait for service to stop and uninstall
            
        try:
            self.run_command(f'taskkill /F /IM node.exe /FI "WINDOWTITLE eq birthday-wabot*" 2>nul')
        except:
            pass
            
        try:
            shutil.rmtree(INSTALL_DIR, ignore_errors=True)
            self.log("Carpeta de instalacion eliminada.")
        except Exception as e:
            self.log(f"No se pudo borrar todo: {e}")
            
        self.log("=== DESINSTALACION COMPLETADA ===")
        messagebox.showinfo("Éxito", "Desinstalación completa.")

    # -----------------------------------------------------------------------
    # Monitoreo
    # -----------------------------------------------------------------------
    def update_status(self):
        try:
            result = subprocess.run('sc query "birthdaywabot.exe"', shell=True, capture_output=True, text=True)
            if "RUNNING" in result.stdout:
                self.lbl_svc_status.configure(text="● EN EJECUCIÓN", text_color=COLOR_GREEN)
            elif "STOPPED" in result.stdout:
                self.lbl_svc_status.configure(text="● DETENIDO", text_color=COLOR_RED)
            else:
                self.lbl_svc_status.configure(text="● NO INSTALADO", text_color=COLOR_TEXT_MUTED)
        except:
            self.lbl_svc_status.configure(text="● DESCONOCIDO", text_color=COLOR_TEXT_MUTED)

    def monitor_status(self):
        self.update_status()
        self.after(5000, self.monitor_status)

    def read_logs(self):
        log_file = os.path.join(INSTALL_DIR, "bot", "daemon", "birthdaywabot.out.log")
        if os.path.exists(log_file):
            try:
                current_size = os.path.getsize(log_file)
                if current_size > self.last_log_size:
                    with open(log_file, "r", encoding="utf-8", errors="replace") as f:
                        f.seek(self.last_log_size)
                        new_data = f.read()
                        if new_data:
                            self.log(new_data.strip())
                    self.last_log_size = current_size
            except:
                pass
        self.after(2000, self.read_logs)

    def monitor_qr(self):
        qr_path = os.path.join(INSTALL_DIR, "bot", "qr.png")
        status_path = os.path.join(INSTALL_DIR, "bot", "status.json")
        
        current_status = None
        if os.path.exists(status_path):
            try:
                with open(status_path, "r") as f:
                    data = json.load(f)
                    current_status = data.get("state")
            except:
                pass
                
        if current_status != self.last_known_status:
            if current_status == "running":
                self.lbl_qr_status.configure(text="✅ Bot Conectado y Corriendo", text_color=COLOR_GREEN)
                self.lbl_qr_image.configure(image="")
            elif current_status == "disconnected":
                self.lbl_qr_status.configure(text="❌ Bot Desconectado", text_color=COLOR_RED)
                self.lbl_qr_image.configure(image="")
            
            self.last_known_status = current_status

        if os.path.exists(qr_path) and current_status != "running":
            self.lbl_qr_status.configure(text="Escanea el código QR:", text_color=COLOR_PURPLE)
            try:
                img = Image.open(qr_path)
                img = img.resize((300, 300))
                ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(300, 300))
                self.lbl_qr_image.configure(image=ctk_img)
                self.qr_image_tk = ctk_img
            except Exception as e:
                self.log(f"Error cargando QR: {e}")
        elif not os.path.exists(qr_path) and current_status != "running":
             self.lbl_qr_status.configure(text="Esperando QR o conexión...", text_color=COLOR_TEXT_MUTED)
             self.lbl_qr_image.configure(image="")

        self.after(3000, self.monitor_qr)

if __name__ == "__main__":
    app = WabotManagerApp()
    app.mainloop()
