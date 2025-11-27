import customtkinter as ctk
from models.mensaje import MensajeModel

class MainController:
    def __init__(self):
        self.model = MensajeModel()
        self.app = ctk.CTk()
        self.app.title("Mi Aplicación")
        self.app.geometry("500x400")
        
        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("green")
        
        self.container = ctk.CTkFrame(self.app)
        self.container.pack(fill="both", expand=True)
        
        # Inicializar mensaje predeterminado
        mensaje_default = "¡Feliz cumpleaños, {nombre}! Espero que tengas un día maravilloso lleno de alegría y sorpresas. 🎉🎂"
        if not self.model.obtener_mensaje():
            self.model.guardar_mensaje(mensaje_default)

    def cambiar_vista(self, vista_class, container, cambiar_vista, app):
        for widget in self.container.winfo_children():
            widget.destroy()
        
        # Determinar qué controlador usar según la vista
        if vista_class.__name__ == "ContactosView":
            from controllers.contactos_controller import ContactosController
            controller = ContactosController()
            vista = vista_class(container, cambiar_vista, app, controller)
        elif vista_class.__name__ == "InputView":
            from controllers.mensajes_controller import MensajesController
            controller = MensajesController()
            vista = vista_class(container, cambiar_vista, app, controller)
        elif vista_class.__name__ == "LogView":
            from controllers.log_controller import LogController
            controller = LogController()
            vista = vista_class(container, cambiar_vista, app, controller)
        else:
            # Para MainView no necesitamos controlador
            vista = vista_class(container, cambiar_vista, app)
        
        vista.pack(fill="both", expand=True)

    def run(self):
        from views.main_view import MainView
        self.cambiar_vista(MainView, self.container, self.cambiar_vista, self.app)
        self.app.mainloop()