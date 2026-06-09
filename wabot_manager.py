import os
import sys
import subprocess
import threading
import time
import shutil
import json
import customtkinter as ctk
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText
from PIL import Image

def is_admin():
    import ctypes
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

INSTALL_DIR = r"C:\Program Files\BirthdayWabot"
COLOR_PURPLE = "#6b21a8"
COLOR_PURPLE_HOVER = "#581c87"
COLOR_GREEN = "#16a34a"
COLOR_DARK_BG = "#1e1e1e"
COLOR_CARD_BG = "#2b2b2b"
COLOR_RED = "#991b1b"

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

class WabotManagerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Birthday Wabot Manager")
        self.geometry("1150x750")
        self.configure(fg_color=COLOR_DARK_BG)
        
        # Header / Tabview
        self.tabview = ctk.CTkTabview(self, segmented_button_selected_color=COLOR_PURPLE, 
                                      segmented_button_selected_hover_color=COLOR_PURPLE_HOVER,
                                      fg_color=COLOR_DARK_BG, bg_color=COLOR_DARK_BG)
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
        # Grid layout: Left (Config & Tasks) 70%, Right (Info) 30%
        self.tab_config.grid_columnconfigure(0, weight=7)
        self.tab_config.grid_columnconfigure(1, weight=3)
        self.tab_config.grid_rowconfigure(0, weight=1)
        
        # === LEFT PANEL ===
        left_panel = ctk.CTkFrame(self.tab_config, fg_color="transparent")
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        # Supabase Config Card
        card_db = ctk.CTkFrame(left_panel, fg_color=COLOR_CARD_BG, corner_radius=10)
        card_db.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(card_db, text="CONFIGURACIÓN DE SUPABASE", font=ctk.CTkFont(size=12, weight="bold"), text_color=COLOR_PURPLE).pack(anchor="w", padx=15, pady=(15, 5))
        ctk.CTkLabel(card_db, text="ℹ️ Ingresa las URLs de tu proyecto Supabase. Se guardarán en el archivo .env", font=ctk.CTkFont(size=11), text_color="gray").pack(anchor="w", padx=15, pady=(0, 15))
        
        inputs_frame = ctk.CTkFrame(card_db, fg_color="transparent")
        inputs_frame.pack(fill="x", padx=15, pady=(0, 15))
        inputs_frame.grid_columnconfigure(0, weight=1)
        inputs_frame.grid_columnconfigure(1, weight=1)
        
        # DB URL
        frame_db_url = ctk.CTkFrame(inputs_frame, fg_color="transparent")
        frame_db_url.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        ctk.CTkLabel(frame_db_url, text="DATABASE_URL (Puerto 6543)").pack(anchor="w")
        self.db_url_var = ctk.StringVar()
        ctk.CTkEntry(frame_db_url, textvariable=self.db_url_var, placeholder_text="postgresql://...:6543/...").pack(fill="x", pady=5)
        
        # DIRECT URL
        frame_direct_url = ctk.CTkFrame(inputs_frame, fg_color="transparent")
        frame_direct_url.grid(row=0, column=1, sticky="ew", padx=(5, 0))
        ctk.CTkLabel(frame_direct_url, text="DIRECT_URL (Puerto 5432)").pack(anchor="w")
        self.direct_url_var = ctk.StringVar()
        ctk.CTkEntry(frame_direct_url, textvariable=self.direct_url_var, placeholder_text="postgresql://...:5432/...").pack(fill="x", pady=5)
        
        self.load_env()
        
        btn_guardar = ctk.CTkButton(card_db, text="💾 Guardar Configuración", fg_color=COLOR_PURPLE, hover_color=COLOR_PURPLE_HOVER, command=self.save_env)
        btn_guardar.pack(anchor="e", padx=15, pady=(0, 15))
        
        # Action Buttons (ABOVE the task list so they're always visible)
        actions_frame = ctk.CTkFrame(left_panel, fg_color="transparent")
        actions_frame.pack(fill="x", pady=(0, 10))
        actions_frame.grid_columnconfigure(0, weight=1)
        actions_frame.grid_columnconfigure(1, weight=1)
        
        btn_install = ctk.CTkButton(actions_frame, text="📥 Instalar Bot", fg_color=COLOR_PURPLE, hover_color=COLOR_PURPLE_HOVER, height=45, font=ctk.CTkFont(size=14, weight="bold"), command=self.install_bot_thread)
        btn_install.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        
        btn_uninstall = ctk.CTkButton(actions_frame, text="🗑️ Desinstalar Bot", fg_color=COLOR_RED, hover_color="#7f1d1d", height=45, font=ctk.CTkFont(size=14, weight="bold"), command=self.uninstall_bot_thread)
        btn_uninstall.grid(row=0, column=1, sticky="ew", padx=(5, 0))
        
        # Install Tasks Card (below buttons)
        card_tasks = ctk.CTkFrame(left_panel, fg_color=COLOR_CARD_BG, corner_radius=10)
        card_tasks.pack(fill="both", expand=True)
        
        ctk.CTkLabel(card_tasks, text="PROGRESO DE INSTALACIÓN", font=ctk.CTkFont(size=12, weight="bold"), text_color=COLOR_PURPLE).pack(anchor="w", padx=15, pady=(15, 10))
        
        self.tasks_data = [
            {"title": "Copiando Archivos...", "desc": "Copia los archivos del bot a su ubicación."},
            {"title": "Instalando Librerías (NPM)...", "desc": "Ejecuta npm install para instalar dependencias."},
            {"title": "Generando Cliente Prisma...", "desc": "Prepara la conexión a la base de datos."},
            {"title": "Configurando Base de Datos (Push)...", "desc": "Sincroniza el esquema con Supabase."},
            {"title": "Iniciando Servicio Windows...", "desc": "Registra el bot para que corra siempre de fondo."}
        ]
        
        self.task_ui_elements = []
        for task in self.tasks_data:
            task_frame = ctk.CTkFrame(card_tasks, fg_color=COLOR_DARK_BG, corner_radius=8)
            task_frame.pack(fill="x", padx=15, pady=4)
            
            icon_lbl = ctk.CTkLabel(task_frame, text="⚫", font=ctk.CTkFont(size=14), width=25)
            icon_lbl.pack(side="left", padx=8, pady=8)
            
            text_frame = ctk.CTkFrame(task_frame, fg_color="transparent")
            text_frame.pack(side="left", fill="x", expand=True, pady=4)
            title_lbl = ctk.CTkLabel(text_frame, text=task["title"], font=ctk.CTkFont(weight="bold", size=12))
            title_lbl.pack(anchor="w")
            desc_lbl = ctk.CTkLabel(text_frame, text=task["desc"], text_color="gray", font=ctk.CTkFont(size=10))
            desc_lbl.pack(anchor="w")
            
            status_lbl = ctk.CTkLabel(task_frame, text="Pendiente", fg_color="#333333", corner_radius=5, padx=8, font=ctk.CTkFont(size=11))
            status_lbl.pack(side="right", padx=10)
            
            self.task_ui_elements.append({"icon": icon_lbl, "status": status_lbl, "frame": task_frame})
        
        # === RIGHT PANEL ===
        right_panel = ctk.CTkFrame(self.tab_config, fg_color="transparent")
        right_panel.grid(row=0, column=1, sticky="nsew")
        
        # Info Card
        card_info = ctk.CTkFrame(right_panel, fg_color=COLOR_CARD_BG, corner_radius=10)
        card_info.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(card_info, text="INFORMACIÓN DEL SISTEMA", font=ctk.CTkFont(size=12, weight="bold"), text_color=COLOR_PURPLE).pack(anchor="w", padx=15, pady=(15, 10))
        
        self.lbl_svc_status = self.add_info_row(card_info, "⚙️ Estado del Servicio:", "Buscando...")
        self.add_info_row(card_info, "💻 Sistema Operativo:", "Windows")
        self.add_info_row(card_info, "📁 Ruta del Proyecto:", INSTALL_DIR)
        
        # Help Card
        card_help = ctk.CTkFrame(right_panel, fg_color=COLOR_CARD_BG, corner_radius=10)
        card_help.pack(fill="both", expand=True)
        
        ctk.CTkLabel(card_help, text="ℹ️ ¿Problemas con Prisma?", font=ctk.CTkFont(size=12, weight="bold"), text_color=COLOR_PURPLE).pack(anchor="w", padx=15, pady=(15, 10))
        help_text = ("Al usar Supabase, asegúrate de colocar las URLs completas.\n\n"
                     "DATABASE_URL debe terminar en el puerto 6543 e incluir pgbouncer=true.\n\n"
                     "DIRECT_URL debe usar el puerto 5432 y es crucial para que el bot pueda crear las tablas sin quedarse atascado.")
        lbl_help = ctk.CTkLabel(card_help, text=help_text, justify="left", wraplength=250, text_color="gray", font=ctk.CTkFont(size=12))
        lbl_help.pack(anchor="w", padx=15, pady=5)
        
    def add_info_row(self, parent, label, value):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=15, pady=5)
        ctk.CTkLabel(frame, text=label).pack(side="left")
        val_lbl = ctk.CTkLabel(frame, text=value, text_color="gray")
        val_lbl.pack(side="right")
        return val_lbl

    def setup_tab_qr(self):
        self.tab_qr.grid_rowconfigure(0, weight=1)
        self.tab_qr.grid_columnconfigure(0, weight=1)
        
        card_qr = ctk.CTkFrame(self.tab_qr, fg_color=COLOR_CARD_BG, corner_radius=15)
        card_qr.grid(row=0, column=0, sticky="nsew", padx=100, pady=50)
        
        ctk.CTkLabel(card_qr, text="Estado de Conexión a WhatsApp", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(30, 10))
        btn_qr = ctk.CTkButton(card_qr, text="🔄 Solicitar Nuevo Código QR", fg_color=COLOR_PURPLE, hover_color=COLOR_PURPLE_HOVER, command=self.regenerate_qr)
        btn_qr.pack(pady=10)
        
        self.qr_label = ctk.CTkLabel(card_qr, text="\n\nSi no ves un código QR:\n1. El bot ya tiene la sesión iniciada correctamente.\n2. La instalación aún no termina.\n3. Acabas de solicitar uno y está cargando.", justify='center', font=ctk.CTkFont(size=13))
        self.qr_label.pack(expand=True, pady=20)
        
    def setup_tab_logs(self):
        # Note: CTkTextbox doesn't auto-scroll easily when appending, so we use regular Tkinter ScrolledText styled darkly
        self.log_text = ScrolledText(self.tab_logs, bg="#000000", fg="#00ff00", font=("Consolas", 10), insertbackground="white")
        self.log_text.pack(fill='both', expand=True, padx=10, pady=10)
        
    def load_env(self):
        if getattr(sys, 'frozen', False):
            src_dir = os.path.dirname(sys.executable)
            if os.path.basename(src_dir).lower() == 'dist':
                src_dir = os.path.dirname(src_dir)
        else:
            src_dir = os.path.abspath(os.path.dirname(__file__))
            
        env_path = os.path.join(src_dir, '.env')
        if os.path.exists(env_path):
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.startswith('DATABASE_URL='):
                        self.db_url_var.set(line.split('=', 1)[1].strip().strip('"').strip("'"))
                    elif line.startswith('DIRECT_URL='):
                        self.direct_url_var.set(line.split('=', 1)[1].strip().strip('"').strip("'"))
                        
    def save_env(self):
        if getattr(sys, 'frozen', False):
            src_dir = os.path.dirname(sys.executable)
            if os.path.basename(src_dir).lower() == 'dist':
                src_dir = os.path.dirname(src_dir)
        else:
            src_dir = os.path.abspath(os.path.dirname(__file__))
            
        env_path = os.path.join(src_dir, '.env')
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write(f'DATABASE_URL="{self.db_url_var.get()}"\n')
            f.write(f'DIRECT_URL="{self.direct_url_var.get()}"\n')
        messagebox.showinfo("Guardado", "Configuración de Base de Datos guardada exitosamente.")
            
    def log(self, msg):
        self.log_text.insert("end", f"{msg}\n")
        self.log_text.see("end")
        print(msg)
        
    def update_task_ui(self, index, status):
        # status: 'pending', 'running', 'done', 'error'
        if 0 <= index < len(self.task_ui_elements):
            ui = self.task_ui_elements[index]
            if status == 'pending':
                ui["icon"].configure(text="⚫", text_color="gray")
                ui["status"].configure(text="Pendiente", fg_color="#333333", text_color="white")
            elif status == 'running':
                ui["icon"].configure(text="⏳", text_color="#eab308")
                ui["status"].configure(text="En progreso", fg_color="#854d0e", text_color="white")
            elif status == 'done':
                ui["icon"].configure(text="✅", text_color=COLOR_GREEN)
                ui["status"].configure(text="Completado", fg_color="#14532d", text_color="white")
            elif status == 'error':
                ui["icon"].configure(text="❌", text_color=COLOR_RED)
                ui["status"].configure(text="Error", fg_color="#7f1d1d", text_color="white")
            self.update()

    def run_command(self, cmd, cwd=None, env=None):
        self.log(f"\n[Ejecutando]: {cmd}")
        # IMPORTANTE: stdin=subprocess.DEVNULL evita que npx se quede congelado esperando input
        process = subprocess.Popen(
            cmd, shell=True, cwd=cwd, env=env, 
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, 
            stdin=subprocess.DEVNULL, text=True, errors='replace'
        )
        while True:
            line = process.stdout.readline()
            if not line and process.poll() is not None:
                break
            if line:
                self.log_text.insert("end", line)
                self.log_text.see("end")
        return process.returncode

    def install_bot_thread(self):
        if not is_admin():
            messagebox.showerror("Error", "Debes ejecutar este programa como Administrador para instalar el bot.")
            return
            
        if not self.db_url_var.get() or not self.direct_url_var.get():
            messagebox.showerror("Error", "Debes configurar DATABASE_URL y DIRECT_URL primero.")
            return
            
        threading.Thread(target=self.install_bot, daemon=True).start()

    def install_bot(self):
        for i in range(len(self.task_ui_elements)):
            self.update_task_ui(i, 'pending')
            
        self.log("=== INICIANDO INSTALACIÓN ===")
        
        # Guardar ENV silenciosamente
        if getattr(sys, 'frozen', False):
            src_dir = os.path.dirname(sys.executable)
            if os.path.basename(src_dir).lower() == 'dist':
                src_dir = os.path.dirname(src_dir)
        else:
            src_dir = os.path.abspath(os.path.dirname(__file__))
        env_path = os.path.join(src_dir, '.env')
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write(f'DATABASE_URL="{self.db_url_var.get()}"\n')
            f.write(f'DIRECT_URL="{self.direct_url_var.get()}"\n')

        # 0. Copiando Archivos
        self.update_task_ui(0, 'running')
        if os.path.exists(INSTALL_DIR):
            subprocess.run('sc stop birthdaywabot.exe', shell=True, stdout=subprocess.DEVNULL)
            time.sleep(3)
            subprocess.run('taskkill /F /IM node.exe /FI "WINDOWTITLE eq BirthdayWabot*" 2>nul', shell=True)
            time.sleep(1)
        try:
            os.makedirs(INSTALL_DIR, exist_ok=True)
            shutil.copytree(src_dir, INSTALL_DIR, dirs_exist_ok=True, ignore=shutil.ignore_patterns('node_modules', '.git', '*.log', '.env'))
            if os.path.exists(os.path.join(src_dir, '.env')):
                shutil.copy2(os.path.join(src_dir, '.env'), os.path.join(INSTALL_DIR, '.env'))
            self.update_task_ui(0, 'done')
        except Exception as e:
            self.log(f"Error copiando: {e}")
            self.update_task_ui(0, 'error')
            return
        
        bot_dir = os.path.join(INSTALL_DIR, "bot")
        with open(os.path.join(bot_dir, "install-service.js"), "w", encoding="utf-8") as f:
            f.write("const Service = require('node-windows').Service;\nconst path = require('path');\nconst svc = new Service({ name: 'BirthdayWabot', description: 'Bot automatizado de WhatsApp', script: path.join(__dirname, 'index.js'), env: [{ name: 'NODE_ENV', value: 'production' }] });\nsvc.on('install', () => { svc.start(); console.log('Servicio iniciado!'); });\nsvc.install();")
        
        # 1. NPM Install Raíz
        self.update_task_ui(1, 'running')
        if self.run_command("npm install", cwd=INSTALL_DIR) != 0:
            self.update_task_ui(1, 'error')
            return
        self.update_task_ui(1, 'done')
        
        # 2. Prisma Generate
        self.update_task_ui(2, 'running')
        self.run_command("npm install @prisma/config --save-dev", cwd=INSTALL_DIR)
        if self.run_command("npx prisma generate", cwd=INSTALL_DIR) != 0:
            self.update_task_ui(2, 'error')
            return
        self.update_task_ui(2, 'done')
        
        # 3. Prisma DB Push (usar DIRECT_URL temporalmente como DATABASE_URL)
        self.update_task_ui(3, 'running')
        env = os.environ.copy()
        env['DATABASE_URL'] = self.direct_url_var.get()
        if self.run_command("npx prisma db push --accept-data-loss", cwd=INSTALL_DIR, env=env) != 0:
            self.update_task_ui(3, 'error')
            return
        self.update_task_ui(3, 'done')
        
        # 4. Servicio Windows
        self.update_task_ui(4, 'running')
        if self.run_command("npm install", cwd=bot_dir) != 0:
            self.update_task_ui(4, 'error')
            return
        self.run_command("npm install node-windows", cwd=bot_dir)
        if self.run_command("node install-service.js", cwd=bot_dir) != 0:
            self.update_task_ui(4, 'error')
            return
        self.update_task_ui(4, 'done')
        
        self.log("=== INSTALACIÓN COMPLETADA EXITOSAMENTE ===")
        messagebox.showinfo("Éxito", "El Bot se ha instalado correctamente. Ve a la pestaña 'Conexión WhatsApp' para escanear el QR.")

    def uninstall_bot_thread(self):
        if not is_admin():
            messagebox.showerror("Error", "Debes ser Administrador para desinstalar.")
            return
        res = messagebox.askyesno("Confirmar", "¿Eliminar el bot y todos sus datos?")
        if res:
            threading.Thread(target=self.uninstall_bot, daemon=True).start()
            
    def uninstall_bot(self):
        self.log("=== INICIANDO DESINSTALACIÓN ===")
        bot_dir = os.path.join(INSTALL_DIR, 'bot')
        if os.path.exists(os.path.join(bot_dir, 'uninstall-service.js')):
            self.run_command("node uninstall-service.js", cwd=bot_dir)
        time.sleep(3)
        self.run_command("sc delete birthdaywabot.exe")
        self.log("=== DESINSTALACIÓN COMPLETADA ===")
        messagebox.showinfo("Éxito", "El Bot ha sido desinstalado.")

    def regenerate_qr(self):
        self.log("Forzando nuevo QR...")
        self.qr_label.configure(image='', text="Reiniciando servicio y generando nuevo QR... Por favor espera 10 segundos.")
        threading.Thread(target=lambda: subprocess.run("sc stop birthdaywabot.exe && ping 127.0.0.1 -n 4 > nul && sc start birthdaywabot.exe", shell=True), daemon=True).start()

    def update_status(self):
        try:
            result = subprocess.run('sc query birthdaywabot.exe', shell=True, stdout=subprocess.PIPE, text=True)
            if "RUNNING" in result.stdout:
                self.lbl_svc_status.configure(text="🟢 EN EJECUCIÓN")
            elif "STOPPED" in result.stdout:
                self.lbl_svc_status.configure(text="🔴 DETENIDO")
            else:
                self.lbl_svc_status.configure(text="⚪ NO INSTALADO")
        except:
            self.lbl_svc_status.configure(text="⚪ NO INSTALADO")
        self.after(5000, self.update_status)

    def monitor_qr(self):
        qr_path = os.path.join(INSTALL_DIR, "bot", "qr.png")
        if os.path.exists(qr_path):
            try:
                img = Image.open(qr_path)
                ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(300, 300))
                self.qr_label.configure(image=ctk_img, text="")
                self.qr_image_tk = ctk_img # Keep ref
            except Exception as e:
                pass
        else:
            self.qr_image_tk = None
            if "Reiniciando servicio" not in self.qr_label.cget("text"):
                self.qr_label.configure(image='', text="\n\nSi no ves un código QR:\n1. El bot ya tiene la sesión iniciada correctamente.\n2. La instalación aún no termina.\n3. Acabas de solicitar uno y está cargando.")
        self.after(2000, self.monitor_qr)

    def monitor_status(self):
        status_file = os.path.join(INSTALL_DIR, "bot", "status.json")
        if os.path.exists(status_file):
            try:
                with open(status_file, "r") as f:
                    data = json.load(f)
                    current = data.get("status")
                    if current == "disconnected" and self.last_known_status != "disconnected":
                        self.after(0, self.show_disconnected_popup)
                    self.last_known_status = current
            except:
                pass
        self.after(3000, self.monitor_status)

    def show_disconnected_popup(self):
        res = messagebox.askyesno("¡Alerta de WhatsApp!", "Se ha cerrado la sesión de WhatsApp.\n\n¿Deseas abrir la pestaña de Código QR para escanearlo ahora mismo?", parent=self)
        if res:
            self.deiconify()
            self.lift()
            self.tabview.set("2. Conexión WhatsApp")
            self.regenerate_qr()

    def read_logs(self):
        service_log = os.path.join(INSTALL_DIR, "bot", "daemon", "birthdaywabot.out.log")
        if not os.path.exists(service_log):
            service_log = os.path.join(INSTALL_DIR, "bot", "daemon", "birthdaywabot.out.log")
            
        if os.path.exists(service_log):
            try:
                size = os.path.getsize(service_log)
                if size > self.last_log_size:
                    with open(service_log, 'r', encoding='utf-8', errors='replace') as f:
                        f.seek(self.last_log_size)
                        new_data = f.read()
                        if new_data:
                            self.log_text.insert("end", new_data)
                            self.log_text.see("end")
                    self.last_log_size = size
            except:
                pass
        self.after(1000, self.read_logs)

if __name__ == "__main__":
    app = WabotManagerApp()
    app.mainloop()
