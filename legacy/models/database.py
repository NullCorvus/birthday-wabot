import os
import sqlite3
import sys

def get_resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class Database:
    def __init__(self):
        self.db_path = get_resource_path(os.path.join("data", "fechasCumple.db"))
        self.crear_tablas()

    def crear_tablas(self):
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS contactos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    numero TEXT NOT NULL,
                    fecha_nacimiento TEXT NOT NULL,
                    UNIQUE(nombre, numero, fecha_nacimiento)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT,
                    numero TEXT,
                    mensaje TEXT,
                    fecha_hora_envio TEXT,
                    estado TEXT,
                    detalle TEXT,
                    UNIQUE(numero, fecha_hora_envio, estado)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS mensajetxt (
                    key TEXT PRIMARY KEY,
                    texto TEXT
                )
            ''')
            
            conn.commit()
        except sqlite3.Error as e:
            print(f"Error al crear tablas: {e}")
        finally:
            if conn:
                conn.close()

    def ejecutar_consulta(self, query, params=()):
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor
        except sqlite3.Error as e:
            print(f"Error en consulta: {e}")
            return None
        finally:
            if conn:
                conn.close()

    def obtener_registros(self, query, params=()):
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error al obtener registros: {e}")
            return []
        finally:
            if conn:
                conn.close()