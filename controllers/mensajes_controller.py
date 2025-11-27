from models.mensaje import MensajeModel

class MensajesController:
    def __init__(self):
        self.model = MensajeModel()
    
    def guardar_mensaje(self, texto):
        return self.model.guardar_mensaje(texto)
    
    def obtener_mensaje(self):
        return self.model.obtener_mensaje()