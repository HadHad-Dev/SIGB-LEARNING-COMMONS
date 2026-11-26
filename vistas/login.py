import tkinter as tk
from tkinter import messagebox
from config import COLORES, FUENTES
from utils import load_image, crear_tarjeta_base
from database.autentificacion import autenticar_usuario


class LoginView(tk.Frame):
    def __init__(self, parent, on_login_success):
        super().__init__(parent, bg=COLORES["blanco_fondo"])
        self.on_login_success = on_login_success
        self._construir_ui()

    def _construir_ui(self):
        # Contenedor centrador
        centro = tk.Frame(self, bg=COLORES["blanco_fondo"])
        centro.place(relx=0.5, rely=0.5, anchor="center")

        card = crear_tarjeta_base(centro)
        card.config(padx=35, pady=30)
        card.pack()

        try:
            self.logo = load_image("img/UTRLOGO.png", (180, 90))
            tk.Label(card, image=self.logo, bg=COLORES["gris_claro"]).pack(pady=(0, 12))
        except Exception:
            pass

        tk.Label(
            card,
            text="Iniciar Sesión",
            font=FUENTES["titulo"],
            fg=COLORES["texto_principal"],
            bg=COLORES["gris_claro"],
        ).pack()

        tk.Label(
            card,
            text="Sistema de Gestión - Biblioteca UTR",
            font=FUENTES["texto_ayuda"],
            fg=COLORES["texto_ayuda"],
            bg=COLORES["gris_claro"],
        ).pack(pady=(2, 20))

        # Campo ID / Matrícula
        tk.Label(
            card,
            text="ID / MATRÍCULA",
            font=FUENTES["etiqueta"],
            fg=COLORES["texto_ayuda"],
            bg=COLORES["gris_claro"],
            anchor="w",
        ).pack(fill="x")

        self.entry_id = tk.Entry(
            card,
            font=FUENTES["texto_normal"],
            bg=COLORES["blanco_fondo"],
            fg=COLORES["texto_principal"],
            relief="solid",
            bd=1,
            width=28,
        )
        self.entry_id.pack(fill="x", pady=(4, 14), ipady=6)
        self.entry_id.focus_set()

        # Campo Contraseña
        tk.Label(
            card,
            text="CONTRASEÑA",
            font=FUENTES["etiqueta"],
            fg=COLORES["texto_ayuda"],
            bg=COLORES["gris_claro"],
            anchor="w",
        ).pack(fill="x")

        self.entry_pass = tk.Entry(
            card,
            font=FUENTES["texto_normal"],
            bg=COLORES["blanco_fondo"],
            fg=COLORES["texto_principal"],
            relief="solid",
            bd=1,
            show="*",
            width=28,
        )
        self.entry_pass.pack(fill="x", pady=(4, 20), ipady=6)

        btn_login = tk.Button(
            card,
            text="Entrar",
            bg=COLORES["rojo_principal"],
            fg=COLORES["blanco_fondo"],
            font=FUENTES["texto_normal"],
            bd=0,
            pady=10,
            cursor="hand2",
            activebackground=COLORES["rojo_oscuro"],
            activeforeground=COLORES["blanco_fondo"],
            command=self._intentar_login,
        )
        btn_login.pack(fill="x")

        # Permitir iniciar sesión con Enter
        self.entry_id.bind("<Return>", lambda e: self.entry_pass.focus_set())
        self.entry_pass.bind("<Return>", lambda e: self._intentar_login())

    def _intentar_login(self):
        raw_id = self.entry_id.get().strip()
        password = self.entry_pass.get()

        if not raw_id or not password:
            messagebox.showwarning("Campos incompletos", "Ingresa tu ID/matrícula y contraseña.")
            return

        if not raw_id.isdigit():
            messagebox.showwarning("ID inválido", "El ID/matrícula debe ser numérico.")
            return

        usuario, error = autenticar_usuario(int(raw_id), password)
        if error:
            messagebox.showerror("Error de acceso", error)
            return

        self.on_login_success(usuario)