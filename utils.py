import tkinter as tk
from config import COLORES, FUENTES


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

#verificar duncioanmiento de los argumentos de pad_x y , estar seguro si inician como 0 o lo toman como default en caso de no mandar algun argumento 
def crear_tarjeta_base(parent, pad_x=0, pad_y=0):
    card = tk.Frame(parent, bg=COLORES["gris_claro"], padx=pad_x, pady=pad_y,
                    highlightbackground=COLORES["gris_linea"], highlightthickness=1)
    return card