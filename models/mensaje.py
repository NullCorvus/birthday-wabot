from models.database import Database
from models.validaciones import validar_numero
from datetime import datetime

class MensajeModel:
    def __init__(self):
        self.db = Database()

    def obtener_cumpleaños(self):
        hoy = datetime.now()
        mes_actual = hoy.strftime('%m')
        dia_actual = hoy.strftime('%d')
        
        return self.db.obtener_registros(
            "SELECT id, nombre, numero, fecha_nacimiento FROM contactos WHERE STRFTIME('%m', fecha_nacimiento) = ? AND STRFTIME('%d', fecha_nacimiento) = ?",
            (mes_actual, dia_actual)
        )

    def agregar_contacto(self, numero, nombre, fecha):
        if not nombre or not numero or not fecha:
            return False, "Todos los campos son obligatorios"
        
        if not validar_numero(numero):
            return False, "El número no tiene el formato internacional correcto"
        
        cursor = self.db.ejecutar_consulta(
            "INSERT OR IGNORE INTO contactos (nombre, numero, fecha_nacimiento) VALUES(?, ?, ?)",
            (nombre, numero, fecha)
        )
        
        if cursor and cursor.rowcount > 0:
            return True, f"Contacto '{nombre}' agregado exitosamente"
        else:
            return False, f"Contacto '{nombre}' ya existe en la base de datos"

    def eliminar_contacto(self, id):
        cursor = self.db.ejecutar_consulta("DELETE FROM contactos WHERE id = ?", (str(id),))
        return cursor.rowcount > 0 if cursor else False

    def modificar_contacto(self, id, numero=None, fecha=None, nombre=None):
        if nombre is None and fecha is None and numero is None:
            return False, "No se especificó ningún campo para modificar"
        
        updates = []
        params = []
        
        if numero is not None:
            updates.append("numero = ?")
            params.append(numero)
        if nombre is not None:
            updates.append("nombre = ?")
            params.append(nombre)
        if fecha is not None:
            updates.append("fecha_nacimiento = ?")
            params.append(fecha)
        
        params.append(id)
        query = f"UPDATE contactos SET {', '.join(updates)} WHERE id = ?"
        
        cursor = self.db.ejecutar_consulta(query, tuple(params))
        
        if cursor and cursor.rowcount > 0:
            return True, "Contacto modificado exitosamente"
        else:
            return False, "No se encontró el contacto para modificar"

    def obtener_contactos(self):
        return self.db.obtener_registros("SELECT id, nombre, numero, fecha_nacimiento FROM contactos ORDER BY id DESC")

    def obtener_log(self):
        return self.db.obtener_registros("SELECT id, nombre, numero, mensaje, fecha_hora_envio, estado, detalle FROM log ORDER BY fecha_hora_envio DESC")

    def agregar_log(self, id, nombre, numero, fecha_envio, mensaje, estado, detalle):
        self.db.ejecutar_consulta(
            "INSERT OR IGNORE INTO log (id, nombre, numero, mensaje, fecha_hora_envio, estado, detalle) VALUES(?, ?, ?, ?, ?, ?, ?)",
            (id, nombre, numero, mensaje, fecha_envio, estado, detalle)
        )

    def guardar_mensaje(self, texto):
        cursor = self.db.ejecutar_consulta(
            "INSERT OR REPLACE INTO mensajetxt (key, texto) VALUES (?,?)",
            ("1", texto)
        )
        return cursor is not None, "Mensaje guardado correctamente" if cursor else "Error al guardar el mensaje"

    def obtener_mensaje(self):
        resultado = self.db.obtener_registros("SELECT texto FROM mensajetxt WHERE key = ?", ("1",))
        return resultado[0][0] if resultado else None

    def verificar_envio_hoy(self, id):
        fecha_hoy = datetime.now().strftime("%Y-%m-%d")
        resultado = self.db.obtener_registros(
            "SELECT COUNT(*) FROM log WHERE id = ? AND estado = 'Enviado' AND STRFTIME('%Y-%m-%d', fecha_hora_envio) = ?",
            (id, fecha_hoy)
        )
        return resultado[0][0] > 0 if resultado else False