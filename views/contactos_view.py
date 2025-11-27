import customtkinter as ctk
from tkinter import Menu, messagebox
import re
from datetime import date
from CTkDatePicker.ctk_date_picker import CTkDatePicker

class ContactosView(ctk.CTkFrame):
    def __init__(self, container, cambiar_vista, app, controller):
        super().__init__(container)
        self.container = container
        self.cambiar_vista = cambiar_vista
        self.app = app
        self.controller = controller
        
        self.app.title("Agregar contactos")
        self.app.geometry("800x600")
        
        self.crear_widgets()
        self.mostrar_contactos()

    def crear_widgets(self):
        # Frame principal
        self.main_columns_container = ctk.CTkFrame(self)
        self.main_columns_container.pack(fill="both", expand=True)

        # Frame derecho
        self.right_column_frame = ctk.CTkFrame(self.main_columns_container, width=900, fg_color="gray20")
        self.right_column_frame.pack(side="bottom", fill="x", expand=True)

        # Frame izquierdo
        self.left_column_frame = ctk.CTkFrame(self.main_columns_container, width=300, fg_color="transparent")
        self.left_column_frame.pack(side="top", fill="both", expand=True)

        self.contenido_frame = ctk.CTkFrame(self.left_column_frame)
        self.contenido_frame.pack(expand=True)

        self.crear_formulario()
        self.crear_busqueda_tabla()

    def crear_formulario(self):
        estilo_label = {
            "font": ctk.CTkFont(size=20, weight="bold", family="Arial"),
            "text_color": ("black", "white"),
            "corner_radius": 10,
            "width": 200,
            "height": 40,
            "anchor": "e"
        }

        # Labels
        self.label_nombre = ctk.CTkLabel(self.contenido_frame, text="Nombre", **estilo_label)
        self.label_num = ctk.CTkLabel(self.contenido_frame, text="Número", **estilo_label)
        self.label_fecha = ctk.CTkLabel(self.contenido_frame, text="Fecha Nacimiento", **estilo_label)

        # Entradas
        self.entry_nombre = ctk.CTkEntry(
            self.contenido_frame,
            placeholder_text="Nombre del contacto",
            height=35, width=200,
            font=ctk.CTkFont(size=15),
            fg_color=("white", "gray20"),
            text_color=("black", "white"),
            placeholder_text_color="gray60",
            border_width=2, corner_radius=8, border_color="black",
        )

        validador = self.app.register(self.solo_numeros)
        self.entry_numero = ctk.CTkEntry(
            self.contenido_frame,
            height=35, width=200,
            font=ctk.CTkFont(size=15),
            fg_color=("white", "gray20"),
            text_color=("black", "white"),
            placeholder_text_color="gray60",
            border_width=2, corner_radius=8, border_color="black",
            validate="key", validatecommand=(validador, "%P"),
        )

        self.entry_fecha = CTkDatePicker(self.contenido_frame)
        self.entry_fecha.set_date_format("%Y-%m-%d")
        self.entry_fecha.set_allow_manual_input(True)
        self.entry_fecha.set_localization("es_CO.UTF-8")
        self.entry_fecha.set_date(date.today())

        # Botones
        self.boton_guardar = ctk.CTkButton(
            self.contenido_frame,
            text="Guardar Contacto",
            height=40,
            font=ctk.CTkFont(size=16, weight="bold"),
            command=self.guardar_contacto
        )

        self.boton_volver = ctk.CTkButton(
            self.contenido_frame,
            command=self.volver,
            text="Regresar",
            height=40,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="white", hover_color="#2ecc71",
            text_color="black", border_width=2,
            border_color="#2ecc71", corner_radius=8
        )

        # Grid
        self.label_nombre.grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.label_num.grid(row=1, column=0, padx=5, pady=10, sticky="e")
        self.label_fecha.grid(row=2, column=0, padx=5, pady=10, sticky="e")

        self.entry_nombre.grid(row=0, column=1, padx=5, pady=10, sticky="w")
        self.entry_numero.grid(row=1, column=1, padx=5, pady=10, sticky="w")
        self.entry_fecha.grid(row=2, column=1, padx=(5, 20), pady=10, sticky="e")

        self.boton_guardar.grid(row=3, column=0, padx=5, pady=10, sticky="ew", columnspan=2)
        self.boton_volver.grid(row=4, column=0, padx=5, pady=10, sticky="ew", columnspan=2)

    def crear_busqueda_tabla(self):
        # Búsqueda
        self.entry_busqueda = ctk.CTkEntry(
            self.right_column_frame,
            placeholder_text="Buscar por nombre o número",
            width=400
        )
        self.entry_busqueda.pack(pady=(10, 0))
        self.entry_busqueda.bind("<KeyRelease>", self.filtrar_contactos)

        # Tabla
        self.log_frame = ctk.CTkScrollableFrame(self.right_column_frame, label_text="")
        self.log_frame.pack(fill="x", expand=True, padx=10, pady=10)

    def solo_numeros(self, texto):
        return bool(re.fullmatch(r'\+?\d*', texto)) or texto == ""

    def guardar_contacto(self):
        numero = self.entry_numero.get()
        nombre = self.entry_nombre.get()
        fecha = self.entry_fecha.get_date()

        exito, mensaje_resultado = self.controller.guardar_contacto(numero, nombre, fecha)

        if exito:
            messagebox.showinfo("Éxito", mensaje_resultado)
            self.entry_numero.delete(0, "end")
            self.entry_nombre.delete(0, "end")
            self.entry_fecha.set_date(date.today())
            self.mostrar_contactos()
        else:
            messagebox.showinfo("Error", mensaje_resultado)

    def filtrar_contactos(self, event):
        texto = self.entry_busqueda.get().lower().strip()
        contactos_filtrados = self.controller.filtrar_contactos(texto)
        self.mostrar_contactos(contactos_filtrados)

    def mostrar_contactos(self, contactos=None):
        # Limpiar contenido anterior
        for widget in self.log_frame.winfo_children():
            widget.destroy()

        contactos_mostrar = contactos if contactos is not None else self.controller.obtener_contactos()

        # Encabezados
        headers = ["ID", "Nombre", "Número", "Fecha de Nacimiento"]
        for col, header in enumerate(headers):
            label = ctk.CTkLabel(self.log_frame, text=header, font=ctk.CTkFont(weight="bold"))
            label.grid(row=0, column=col, padx=5, pady=5, sticky="w")
            self.log_frame.grid_columnconfigure(col, weight=1)

        # Filas
        for row_index, fila in enumerate(contactos_mostrar, start=1):
            widgets_fila = []
            id_contacto, nombre, numero, fecha = fila

            for col_index, valor in enumerate(fila):
                valor_str = str(valor) if valor is not None else ""
                label = ctk.CTkLabel(
                    self.log_frame,
                    text=valor_str[:100] + "..." if len(valor_str) > 103 else valor_str,
                    anchor="w", wraplength=200
                )
                label.grid(row=row_index, column=col_index, padx=5, pady=2, sticky="ew")
                widgets_fila.append(label)

            # Clic derecho
            for widget in widgets_fila:
                widget.bind(
                    "<Button-3>",
                    lambda e, id=id_contacto, nombre=nombre, numero=numero, 
                           fecha=fecha, widgets=widgets_fila:
                        self.on_right_click(e, id, nombre, numero, fecha, widgets)
                )

    def on_right_click(self, event, id_contacto, nombre, numero, fecha, widgets):
        # Resaltar fila
        for w in widgets:
            w.configure(fg_color="gray30")

        menu = self.crear_menu_contextual(id_contacto, nombre, numero, fecha, widgets)

        def quitar_resaltado(event):
            for w in widgets:
                w.configure(fg_color="transparent")

        menu.bind("<Unmap>", quitar_resaltado)
        menu.tk_popup(event.x_root, event.y_root)

    def crear_menu_contextual(self, id_contacto, nombre, numero, fecha, widgets):
        menu = Menu(self.log_frame, tearoff=0)
        menu.add_command(label="Modificar", 
                        command=lambda: self.modificar_contacto(id_contacto, nombre, numero, fecha))
        menu.add_command(label="Eliminar", 
                        command=lambda: self.eliminar_contacto(id_contacto, nombre, numero))
        return menu

    def modificar_contacto(self, id_contacto, nombre_actual, numero_actual, fecha_actual):
        ventana = VentanaModificarContacto(self, id_contacto, nombre_actual, 
                                         numero_actual, fecha_actual, self.actualizar_tabla)
        ventana.grab_set()

    def eliminar_contacto(self, id_contacto, nombre, numero):
        confirmar = messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Estás seguro de que deseas eliminar a '{nombre}' ({numero})?"
        )
        if confirmar:
            if self.controller.eliminar_contacto(id_contacto):
                messagebox.showinfo("Éxito", "Contacto eliminado")
                self.mostrar_contactos()
            else:
                messagebox.showinfo("Error", "No se pudo eliminar el contacto")

    def actualizar_tabla(self):
        self.mostrar_contactos()

    def volver(self):
        from views.main_view import MainView
        self.cambiar_vista(MainView, self.container, self.cambiar_vista, self.app)


class VentanaModificarContacto(ctk.CTkToplevel):
    def __init__(self, parent, id_contacto, nombre_actual, numero_actual, fecha_actual, callback_actualizar):
        super().__init__(parent)
        self.parent = parent
        self.id_contacto = id_contacto
        self.callback_actualizar = callback_actualizar
        
        self.title("Modificar Contacto")
        self.geometry("400x300")
        self.grab_set()

        self.crear_widgets(nombre_actual, numero_actual, fecha_actual)

    def crear_widgets(self, nombre_actual, numero_actual, fecha_actual):
        estilo_entry = {
            "height": 35, "width": 200, "font": ctk.CTkFont(size=15),
            "fg_color": ("white", "gray20"), "text_color": ("black", "white"),
            "placeholder_text_color": "gray60", "border_width": 2,
            "corner_radius": 8, "border_color": "black",
        }

        estilo_label = {
            "font": ctk.CTkFont(size=18, weight="bold"),
            "text_color": ("black", "white"), "anchor": "w"
        }

        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.pack(expand=True, pady=20)

        # Nombre
        ctk.CTkLabel(frame, text="Nombre", **estilo_label).pack(pady=(5, 0))
        self.entry_nombre = ctk.CTkEntry(frame, **estilo_entry)
        self.entry_nombre.insert(0, nombre_actual)
        self.entry_nombre.pack(pady=5)

        # Número
        ctk.CTkLabel(frame, text="Número", **estilo_label).pack(pady=(10, 0))
        self.entry_numero = ctk.CTkEntry(frame, **estilo_entry)
        self.entry_numero.insert(0, numero_actual)
        self.entry_numero.pack(pady=5)

        # Fecha
        self.entry_fecha = CTkDatePicker(frame)
        self.entry_fecha.set_date_format("%Y-%m-%d")
        self.entry_fecha.set_allow_manual_input(True)
        self.entry_fecha.set_date(str(fecha_actual))
        self.entry_fecha.set_localization("es_CO.UTF-8")
        self.entry_fecha.pack(pady=5)

        # Botón guardar
        ctk.CTkButton(self, text="Guardar Cambios", 
                     command=self.guardar_modificacion).pack(pady=20)

    def guardar_modificacion(self):
        from tkinter import messagebox
        
        nuevo_nombre = self.entry_nombre.get()
        nuevo_numero = self.entry_numero.get()
        nueva_fecha = self.entry_fecha.get_date()

        if not nuevo_nombre.strip() or not nuevo_numero.strip():
            messagebox.showwarning("Datos incompletos", "Nombre y número no pueden estar vacíos.")
            return

        confirmacion = messagebox.askyesno(
            "Confirmar modificación?",
            f"¿Deseas modificar el contacto a:\n\nNombre: {nuevo_nombre}\nNúmero: {nuevo_numero}\nFecha: {nueva_fecha}?"
        )

        if not confirmacion:
            return
        
        exito, msg = self.parent.controller.modificar_contacto(
            self.id_contacto, nuevo_numero, nuevo_nombre, nueva_fecha
        )

        if exito:
            messagebox.showinfo("Éxito", msg)
            self.callback_actualizar()
            self.destroy()
        else:
            messagebox.showinfo("Error", msg)