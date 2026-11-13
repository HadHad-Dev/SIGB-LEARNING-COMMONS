# utils.py
import tkinter as tk
from config import COLORES

def crear_tarjeta_kpi(parent, titulo, valor, subtitulo):
    card = tk.Frame(parent, bg=COLORES["gris_tenue"], padx=15, pady=15, relief="solid", bd=1)
    tk.Label(card, text=titulo, bg=COLORES["gris_tenue"], fg=COLORES["texto_ayuda"], font=("Arial", 10), anchor="w").pack(fill="x")
    tk.Label(card, text=valor, bg=COLORES["gris_tenue"], fg=COLORES["texto_principal"], font=("Arial", 20, "bold"), anchor="w").pack(fill="x", pady=5)
    tk.Label(card, text=subtitulo, bg=COLORES["gris_tenue"], fg=COLORES["texto_ayuda"], font=("Arial", 9), anchor="w").pack(fill="x")
    return card