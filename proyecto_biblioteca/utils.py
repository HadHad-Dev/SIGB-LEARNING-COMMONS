# utils.py
import tkinter as tk
from config import COLORS

def crear_tarjeta_kpi(parent, titulo, valor, subtitulo):
    card = tk.Frame(parent, bg=COLORS["card"], padx=15, pady=15, relief="solid", bd=1)
    tk.Label(card, text=titulo, bg=COLORS["card"], fg=COLORS["text_muted"], font=("Arial", 10), anchor="w").pack(fill="x")
    tk.Label(card, text=valor, bg=COLORS["card"], fg=COLORS["text_main"], font=("Arial", 20, "bold"), anchor="w").pack(fill="x", pady=5)
    tk.Label(card, text=subtitulo, bg=COLORS["card"], fg=COLORS["text_muted"], font=("Arial", 9), anchor="w").pack(fill="x")
    return card