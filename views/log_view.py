import customtkinter as ctk

class LogView(ctk.CTkFrame):
    def __init__(self, container, cambiar_vista, app, controller):
        super().__init__(container)
        self.container = container
        self.cambiar_vista = cambiar_vista
        self.app = app
        self.controller = controller
        
        self.app.title("Log de Mensajes Enviados")
        self.app.geometry("800x600")
        
        self.crear_widgets()

    def crear_widgets(self):
        # Frame principal
        main_columns_container = ctk.CTkFrame(self)
        main_columns_container.pack(fill="both", expand=True)

        # Obtener log
        log = self.controller.obtener_log()

        # Frame scrollable para la tabla
        log_frame = ctk.CTkScrollableFrame(main_columns_container, label_text="")
        log_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Limpiar contenido anterior
        for widget in log_frame.winfo_children():
            widget.destroy()

        # Encabezados
        headers = ["ID", "Nombre", "Número", "Mensaje", "Fecha y Hora de Envío", "Estado", "Detalle"]
        for col, header in enumerate(headers):
            label = ctk.CTkLabel(log_frame, text=header, font=ctk.CTkFont(weight="bold"))
            label.grid(row=0, column=col, padx=5, pady=5, sticky="w")
            log_frame.grid_columnconfigure(col, weight=1)

        # Filas del log
        for row_index, fila in enumerate(log, start=1):
            id_contacto, nombre, numero, mensaje_e, fecha, estado, detalle = fila
            
            for col_index, valor in enumerate(fila):
                valor_str = str(valor) if valor is not None else ""
                label = ctk.CTkLabel(
                    log_frame,
                    text=valor_str[:100] + "..." if len(valor_str) > 103 else valor_str,
                    anchor="w", wraplength=200
                )
                label.grid(row=row_index, column=col_index, padx=5, pady=2, sticky="ew")

        # Botón volver
        boton_volver = ctk.CTkButton(
            main_columns_container,
            command=self.volver,
            text="Regresar",
            height=40,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="white", hover_color="#2ecc71",
            text_color="black", border_width=2,
            border_color="#2ecc71", corner_radius=8
        )
        boton_volver.pack(fill="x", expand=False, padx=10, pady=10)

    def volver(self):
        from views.main_view import MainView
        self.cambiar_vista(MainView, self.container, self.cambiar_vista, self.app)