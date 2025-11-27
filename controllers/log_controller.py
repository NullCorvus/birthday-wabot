from models.mensaje import MensajeModel

class LogController:
    def __init__(self):
        self.model = MensajeModel()
    
    def obtener_log(self):
        return self.model.obtener_log()