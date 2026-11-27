import tkinter as tk
from tkinter import ttk, messagebox
from config import COLORES, FUENTES
from utils import crear_tarjeta_base
from database.userconfiDB import (
    obtener_usuario_perfil,
    guardar_perfil_en_bd,
    actualizar_password_en_bd,
)


class UserconfigView(tk.Frame):
    def __init__(self, parent, usuario_actual=None, on_perfil_actualizado=None):
        super().__init__(parent, bg=COLORES["blanco_fondo"])
        self.usuario_actual = usuario_actual or {}
        self.user_id = self.usuario_actual.get("user_id")
        self.on_perfil_actualizado = on_perfil_actualizado
        self.datos_originales = {}

        self.configurar_estilos()
        self.setup_ui()
        self.cargar_datos_usuario()

    def configurar_estilos(self):
        style = ttk.Style()
        style.theme_use("default")
        style.configure("TNotebook", background=COLORES["blanco_fondo"], borderwidth=0)
        style.configure(
            "TNotebook.Tab",
            background=COLORES["gris_claro"],
            foreground=COLORES["texto_ayuda"],
            font=FUENTES["texto_normal"],
            padding=[15, 5],
        )
        style.map(
            "TNotebook.Tab",
            background=[("selected", COLORES["blanco_fondo"])],
            foreground=[("selected", COLORES["rojo_principal"])],
        )

    def setup_ui(self):
        # HEADER
        header = tk.Frame(self, bg=COLORES["blanco_fondo"], pady=10, padx=20)
        header.pack(fill="x")
        tk.Label(
            header,
            text="Configuración del Sistema",
            font=FUENTES["titulo"],
            fg=COLORES["texto_principal"],
            bg=COLORES["blanco_fondo"],
        ).pack(side="left")
        tk.Label(
            header,
            text="Perfil, ajustes generales y base de datos",
            font=FUENTES["texto_ayuda"],
            fg=COLORES["texto_ayuda"],
            bg=COLORES["blanco_fondo"],
        ).pack(side="right")

        # PESTAÑAS
        main_content = tk.Frame(self, bg=COLORES["blanco_fondo"], padx=20, pady=10)
        main_content.pack(fill="both", expand=True)
        self.notebook = ttk.Notebook(main_content)
        self.notebook.pack(fill="both", expand=True)

        for texto, constructor in [("Perfil de Usuario", self.construir_perfil)]:
            frame = tk.Frame(
                self.notebook,
                bg=COLORES["blanco_fondo"],
                highlightbackground=COLORES["gris_linea"],
                highlightthickness=1,
            )
            self.notebook.add(frame, text=texto)
            constructor(frame)

    # ---------- Helpers de UI ----------
    def _tarjeta(self, parent, titulo):
        card = crear_tarjeta_base(parent)
        card.pack(fill="x", padx=15, pady=(15, 0))
        tk.Label(
            card,
            text=titulo,
            font=FUENTES["subtitulo"],
            bg=COLORES["gris_claro"],
            fg=COLORES["texto_principal"],
            anchor="w",
        ).pack(fill="x", padx=15, pady=10)
        cuerpo = tk.Frame(card, bg=COLORES["gris_claro"])
        cuerpo.pack(fill="x", padx=15, pady=(0, 15))
        cuerpo.grid_columnconfigure(1, weight=1)
        return cuerpo

    def _campo(self, cuerpo, fila, etiqueta, valor="", show=None, solo_lectura=False):
        tk.Label(
            cuerpo,
            text=etiqueta.upper(),
            bg=COLORES["gris_claro"],
            fg=COLORES["texto_ayuda"],
            font=FUENTES["etiqueta"],
        ).grid(row=fila, column=0, sticky="w", pady=8, padx=(0, 20))

        entry = tk.Entry(
            cuerpo,
            font=FUENTES["texto_normal"],
            relief="solid",
            bd=1,
            show=show,
            bg=COLORES["blanco_fondo"],
            fg=COLORES["texto_principal"],
            readonlybackground=COLORES["gris_tenue"],
        )
        entry.insert(0, valor)
        if solo_lectura:
            entry.config(state="readonly")
        entry.grid(row=fila, column=1, sticky="ew", pady=8, ipady=4)
        return entry

    def _set_entry_valor(self, entry, texto, solo_lectura=False):
        entry.config(state="normal")
        entry.delete(0, tk.END)
        entry.insert(0, "" if texto is None else str(texto))
        if solo_lectura:
            entry.config(state="readonly")

    def _boton_primario(self, parent, texto, comando=None):
        return tk.Button(
            parent,
            text=texto,
            bg=COLORES["rojo_principal"],
            fg=COLORES["blanco_fondo"],
            font=FUENTES["texto_normal"],
            bd=0,
            padx=15,
            pady=10,
            cursor="hand2",
            activebackground=COLORES["rojo_oscuro"],
            activeforeground=COLORES["blanco_fondo"],
            command=comando,
        )

    def _boton_secundario(self, parent, texto, comando=None):
        return tk.Button(
            parent,
            text=texto,
            bg=COLORES["blanco_fondo"],
            fg=COLORES["texto_principal"],
            font=FUENTES["texto_normal"],
            relief="solid",
            bd=1,
            padx=15,
            pady=8,
            cursor="hand2",
            command=comando,
        )

    # ---------- Pestaña 1: Perfil ----------
    def construir_perfil(self, parent):
        datos = self._tarjeta(parent, "Datos del usuario")
        self.entry_id = self._campo(datos, 0, "ID / Matrícula", "", solo_lectura=True)
        self.entry_nombre = self._campo(datos, 1, "Nombre completo", "")
        self.entry_rol = self._campo(datos, 2, "Rol", "", solo_lectura=True)
        self.entry_extra = self._campo(datos, 3, "Área / Carrera / Teléfono", "", solo_lectura=True)

        clave = self._tarjeta(parent, "Cambiar contraseña")
        self.entry_pass_actual = self._campo(clave, 0, "Contraseña actual", show="*")
        self.entry_pass_nueva = self._campo(clave, 1, "Nueva contraseña", show="*")
        self.entry_pass_confirmar = self._campo(clave, 2, "Confirmar contraseña", show="*")

        botones = tk.Frame(parent, bg=COLORES["blanco_fondo"])
        botones.pack(fill="x", padx=15, pady=15)
        self._boton_primario(botones, "Guardar cambios", comando=self.guardar_cambios).pack(side="right")
        self._boton_secundario(botones, "Cancelar", comando=self.cancelar_cambios).pack(side="right", padx=10)

    def _aplicar_valores_a_campos(self, usuario):
        rol = usuario.get("user_type", "")
        self._set_entry_valor(self.entry_id, usuario.get("user_id", ""), solo_lectura=True)
        self._set_entry_valor(self.entry_nombre, usuario.get("full_name", ""), solo_lectura=False)
        self._set_entry_valor(self.entry_rol, rol.capitalize(), solo_lectura=True)

        if rol == "administrativo":
            self._set_entry_valor(self.entry_extra, usuario.get("department_area") or "", solo_lectura=False)
        elif rol == "externo":
            self._set_entry_valor(self.entry_extra, usuario.get("phone") or "", solo_lectura=False)
        else:
            info_fija = usuario.get("major") or usuario.get("teacher_type") or "—"
            self._set_entry_valor(self.entry_extra, info_fija, solo_lectura=True)

    def cargar_datos_usuario(self):
        usuario = obtener_usuario_perfil(self.user_id)
        if not usuario:
            return

        self.user_id = usuario["user_id"]
        self.usuario_actual.update(usuario)
        self.datos_originales = dict(usuario)
        self._aplicar_valores_a_campos(usuario)

    def cancelar_cambios(self):
        if self.datos_originales:
            self._aplicar_valores_a_campos(self.datos_originales)
        for campo in (self.entry_pass_actual, self.entry_pass_nueva, self.entry_pass_confirmar):
            campo.delete(0, tk.END)

    def guardar_cambios(self):
        if self.user_id is None:
            messagebox.showwarning("Sin usuario", "No se encontró un usuario registrado para actualizar.")
            return

        nuevo_nombre = self.entry_nombre.get().strip()
        if not nuevo_nombre:
            messagebox.showwarning("Campo vacío", "El nombre completo no puede estar vacío.")
            return

        rol = self.datos_originales.get("user_type", "")
        dept_area = self.datos_originales.get("department_area")
        phone = self.datos_originales.get("phone")

        if rol == "administrativo":
            dept_area = self.entry_extra.get().strip()
        elif rol == "externo":
            phone = self.entry_extra.get().strip()

        ok_perfil, msg_perfil = guardar_perfil_en_bd(
            user_id=self.user_id,
            full_name=nuevo_nombre,
            department_area=dept_area,
            phone=phone,
        )
        if not ok_perfil:
            messagebox.showerror("Error al guardar", msg_perfil)
            return

        # Si el usuario también llenó campos de contraseña, validar y guardar
        p_actual = self.entry_pass_actual.get()
        p_nueva = self.entry_pass_nueva.get()
        p_confirm = self.entry_pass_confirmar.get()

        if p_actual or p_nueva or p_confirm:
            if not p_actual or not p_nueva or not p_confirm:
                messagebox.showwarning(
                    "Campos incompletos",
                    "Completa contraseña actual, nueva contraseña y confirmación para cambiarla.",
                )
                return
            if p_nueva != p_confirm:
                messagebox.showwarning("No coinciden", "La nueva contraseña y la confirmación no coinciden.")
                return
            if len(p_nueva) < 4:
                messagebox.showwarning("Contraseña corta", "La nueva contraseña debe tener al menos 4 caracteres.")
                return

            ok_pass, msg_pass = actualizar_password_en_bd(self.user_id, p_actual, p_nueva)
            if not ok_pass:
                messagebox.showerror("Error de contraseña", msg_pass)
                return

            for campo in (self.entry_pass_actual, self.entry_pass_nueva, self.entry_pass_confirmar):
                campo.delete(0, tk.END)

        # Recargar desde la BD para asegurar que la UI refleje lo guardado
        self.cargar_datos_usuario()
        if self.on_perfil_actualizado:
            self.on_perfil_actualizado(self.usuario_actual)
        messagebox.showinfo("Éxito", msg_perfil)