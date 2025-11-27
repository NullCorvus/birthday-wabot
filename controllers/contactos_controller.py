from models.mensaje import MensajeModel

class ContactosController:
    def __init__(self):
        self.model = MensajeModel()
    
    def guardar_contacto(self, numero, nombre, fecha):
        return self.model.agregar_contacto(numero, nombre, fecha)
    
    def obtener_contactos(self):
        return self.model.obtener_contactos()
    
    def eliminar_contacto(self, id):
        return self.model.eliminar_contacto(id)
    
    def modificar_contacto(self, id, numero, nombre, fecha):
        return self.model.modificar_contacto(id, numero, nombre, fecha)
    
    def filtrar_contactos(self, texto):
        todos = self.model.obtener_contactos()
        return [c for c in todos if texto in c[1].lower() or texto in c[2]]