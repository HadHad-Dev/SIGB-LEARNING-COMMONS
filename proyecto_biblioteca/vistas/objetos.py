# vistas/objetos.py
import tkinter as tk
from config import COLORES
from utils import crear_tarjeta_kpi

class ObjetosView(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=COLORES["blanco_fondo"])
        self.setup_ui()

    def setup_ui(self):
        # Header
        header = tk.Frame(self, bg=COLORES["blanco_fondo"], pady=10, padx=20)
        header.pack(fill="x")
        tk.Label(header, text="Objetos perdidos", font=("Arial", 18, "bold"), bg=COLORES["blanco_fondo"]).pack(side="left")
        tk.Button(header, text="Registrar objeto", bg=COLORES["gris_tenue"], fg="white", bd=0, padx=15, pady=5).pack(side="right")

        # Catálogo Grid (código simplificado para ilustrar)
        grid_frame = tk.Frame(self, bg=COLORES["blanco_fondo"], padx=20)
        grid_frame.pack(fill="both", expand=True, pady=10)
        
        items = ["Mochila", "Audífonos", "Botella", "Calculadora", "Cuaderno", "Lentes"]

        for i, titulo in enumerate(items):
            row, col = i // 3, i % 3
            card = tk.Frame(grid_frame, bg=COLORES["gris_tenue"], relief="solid", bd=1, padx=10, pady=10)
            card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            grid_frame.grid_columnconfigure(col, weight=1)
            tk.Frame(card, bg="#D0D0D0", height=100).pack(fill="x", pady=(0, 10))
            tk.Label(card, text=titulo, font=("Arial", 11, "bold"), bg=COLORES["gris_tenue"]).pack(fill="x")