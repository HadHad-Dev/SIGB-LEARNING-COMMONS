import tkinter as tk
from config import COLORES
from utils import crear_tarjeta_kpi

class LoginView(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=COLORES["blanco_fondo"])
        self.setup_ui()

    def setup_ui(self):
        # Header
        header = tk.Frame(self, bg=COLORES["blanco_fondo"], pady=10, padx=20)
        header.pack(fill="x")
        tk.Label(header, text="Iniciar Sesión", font=("Arial", 18, "bold"), bg=COLORES["blanco_fondo"]).pack(side="left")

        # Formulario de inicio de sesión
        form_frame = tk.Frame(self, bg=COLORES["blanco_fondo"], padx=20, pady=20)
        form_frame.pack(fill="both", expand=True)

        tk.Label(form_frame, text="Usuario:", font=("Arial", 12), bg=COLORES["blanco_fondo"]).grid(row=0, column=0, sticky="w", pady=5)
        self.entry_usuario = tk.Entry(form_frame, font=("Arial", 12))
        self.entry_usuario.grid(row=0, column=1, pady=5)

        tk.Label(form_frame, text="Contraseña:", font=("Arial", 12), bg=COLORES["blanco_fondo"]).grid(row=1, column=0, sticky="w", pady=5)
        self.entry_contrasena = tk.Entry(form_frame, font=("Arial", 12), show="*")
        self.entry_contrasena.grid(row=1, column=1, pady=5)

        tk.Button(form_frame, text="Iniciar Sesión", bg=COLORES["gris_tenue"], fg="white", bd=0, padx=15, pady=5).grid(row=2, columnspan=2, pady=10)