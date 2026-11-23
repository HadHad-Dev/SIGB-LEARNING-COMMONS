import tkinter as tk
from config import COLORES, FUENTES
from PIL import Image, ImageTk

def load_image(path, size):
    return ImageTk.PhotoImage(Image.open(path).resize(size, Image.ADAPTIVE))

def crear_tarjeta_kpi(parent, titulo, valor, subtitulo):
    """Crea las 3 tarjetas superiores de datos rápidos (KPIs)"""
    card = tk.Frame(parent, bg=COLORES["gris_claro"], padx=15, pady=15, 
                    highlightbackground=COLORES["gris_linea"], highlightthickness=1)
    
    tk.Label(card, text=titulo, bg=COLORES["gris_claro"], fg=COLORES["texto_ayuda"], 
             font=FUENTES["etiqueta"], anchor="w").pack(fill="x")
             
    tk.Label(card, text=valor, bg=COLORES["gris_claro"], fg=COLORES["texto_principal"], 
             font=FUENTES["subtitulo"], anchor="w").pack(fill="x", pady=5)
             
    tk.Label(card, text=subtitulo, bg=COLORES["gris_claro"], fg=COLORES["texto_ayuda"], 
             font=FUENTES["texto_ayuda"], anchor="w").pack(fill="x")
             
    return card

def crear_tarjeta_base(parent, pad_x=0, pad_y=0):
    card = tk.Frame(parent, bg=COLORES["gris_claro"], padx=pad_x, pady=pad_y,
                    highlightbackground=COLORES["gris_linea"], highlightthickness=1)
    return card