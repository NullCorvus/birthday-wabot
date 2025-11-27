import customtkinter as ctk

class InputView(ctk.CTkFrame):
    def __init__(self, container, cambiar_vista, app, controller):
        super().__init__(container)
        self.container = container
        self.cambiar_vista = cambiar_vista
        self.app = app
        self.controller = controller
        
        self.app.title("Editar Mensaje Predeterminado")
        self.app.geometry("800x600")
        
        self.crear_widgets()

    def crear_widgets(self):
        # Frame principal
        main_columns_container = ctk.CTkFrame(self)
        main_columns_container.pack(fill="both", expand=True, padx=20, pady=20)

        # Sub-frame para el mensaje editable
        mensaje_frame = ctk.CTkFrame(main_columns_container)
        mensaje_frame.pack(fill="x", pady=10)

        # Etiqueta
        ctk.CTkLabel(mensaje_frame, text="Mensaje predeterminado:").pack(anchor="w")

        # Caja de texto (editable)
        self.input_text = ctk.CTkTextbox(mensaje_frame, height=100)
        self.input_text.pack(fill="x", pady=5)

        # Obtener mensaje actual
        mensaje_actual = self.controller.obtener_mensaje()
        if mensaje_actual:
            self.input_text.insert("1.0", mensaje_actual)

        # Botón para guardar
        ctk.CTkButton(mensaje_frame, text="Guardar mensaje", 
                     command=self.guardar_mensaje).pack(pady=5)
        
        ctk.CTkButton(
            mensaje_frame,
            command=self.volver,
            text="Regresar",
            height=40,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="white", hover_color="#2ecc71",
            text_color="black", border_width=2,
            border_color="#2ecc71", corner_radius=8
        ).pack(pady=5)

    def guardar_mensaje(self):
        nuevo_mensaje = self.input_text.get("1.0", "end").strip()
        exito, feedback = self.controller.guardar_mensaje(nuevo_mensaje)
        
        # Mostrar resultado
        if exito:
            mensaje_label = ctk.CTkLabel(self, text="✅ Mensaje actualizado correctamente", fg_color="transparent")
            mensaje_label.pack(pady=5)
        else:
            mensaje_label = ctk.CTkLabel(self, text=f"❌ Error: {feedback}", fg_color="transparent")
            mensaje_label.pack(pady=5)

    def volver(self):
        from views.main_view import MainView
        self.cambiar_vista(MainView, self.container, self.cambiar_vista, self.app)