import customtkinter as ctk

class MainView(ctk.CTkFrame):
    def __init__(self, container, cambiar_vista, app):
        super().__init__(container)
        self.container = container
        self.cambiar_vista = cambiar_vista
        self.app = app
        
        self.mostrar()

    def mostrar(self):
        self.app.geometry("350x600")
        
        frame = ctk.CTkFrame(self)
        frame.pack(pady=20, padx=20, fill="both", expand=True)

        botones_config = [
            ("Agregar Contactos", "ContactosView"),
            ("Registro de Envios", "LogView"),
            ("Editar Mensaje", "InputView")
        ]

        for texto, vista_nombre in botones_config:
            boton = ctk.CTkButton(
                frame,
                text=texto,
                command=lambda vn=vista_nombre: self.cambiar_vista_nombre(vn),
                text_color="white",
                font=ctk.CTkFont(size=16, weight="bold"),
                fg_color="#2ecc71",
                hover_color="#27ae60",
                corner_radius=10,
                width=150,
                height=50
            )
            boton.pack(pady=30, padx=30)

    def cambiar_vista_nombre(self, vista_nombre):
        # Importamos aquí para evitar circular
        if vista_nombre == "ContactosView":
            from views.contactos_view import ContactosView
            self.cambiar_vista(ContactosView, self.container, self.cambiar_vista, self.app)
        elif vista_nombre == "InputView":
            from views.input_view import InputView
            self.cambiar_vista(InputView, self.container, self.cambiar_vista, self.app)
        elif vista_nombre == "LogView":
            from views.log_view import LogView
            self.cambiar_vista(LogView, self.container, self.cambiar_vista, self.app)