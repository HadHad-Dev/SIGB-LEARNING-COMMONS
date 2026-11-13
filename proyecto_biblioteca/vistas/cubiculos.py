import tkinter as tk
from config import COLORES
from utils import crear_tarjeta_kpi

class CubiculosView(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=COLORES["blanco_fondo"])
        self.setup_ui()

    def setup_ui(self):
        self.content_frame = tk.Frame(self, bg=COLORES["rojo_oscuro"])
        self.content_frame.grid(row=1, column=1, sticky="nsew")

        self.title_label = tk.Label(self.content_frame, text="Gestion de Cubiculos", bg=COLORES["gris_tenue"], font=("Arial", 30))
        self.title_label.pack(side="top", anchor="w", pady=20, padx=20)

        self.body_frame = tk.Frame(self.content_frame, bg=COLORES["gris_tenue"])
        self.body_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        self.body_frame.grid_columnconfigure(0, weight=3)
        self.body_frame.grid_columnconfigure(1, weight=1, minsize=330)
        self.body_frame.grid_rowconfigure(0, weight=3)
        self.body_frame.grid_rowconfigure(1, weight=2)

        card = self.create_card(self.body_frame,"Pocicionamiento de cubiculos")
        card.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=(0, 10))

        mapa = tk.Frame(self.body_frame, bg=COLORES["blanco_fondo"], highlightbackground=COLORES["CARD_BORDER"], highlightthickness=1)
        mapa.grid(row=1,column=0,sticky="nsew", padx=20, pady=(0,10))

        for c in range(4):
            mapa.grid_columnconfigure(c, weight=1, uniform="cub")
        for r in range(2):
            mapa.grid_rowconfigure(r, weight=1)

        self.cubiculo_item(mapa, "Cubículo 1", 4, "Disponible", 0, 0)
        self.cubiculo_item(mapa, "Cubículo 2", 6, "Ocupado", 0, 1)
        self.cubiculo_item(mapa, "Cubículo 3", 4, "Disponible", 0, 2)
        self.cubiculo_item(mapa, "Cubículo 4", 8, "Disponible", 0, 3, selected=True)
        self.cubiculo_item(mapa, "Cubículo 5", 10, "Ocupado", 1, 0, colspan=2)
        self.cubiculo_item(mapa, "Cubículo 6", 12, "Disponible", 1, 2, colspan=2)

        tk.Label(card, text="Selecciona un cubículo para ver más detalles", bg=COLORES["blanco_fondo"],
                 fg=COLORES["texto_ayuda"], font=("Arial", 9)).pack(anchor="w", padx=20, pady=(0, 15))

        
    def create_card(self, parent, title):
            card = tk.Frame(parent, bg=COLORES["blanco_fondo"], highlightbackground=COLORES["rojo_oscuro"], highlightthickness=1)
            tk.Label(card, text=title, bg=COLORES["blanco_fondo"], font=("Arial", 13, "bold")).pack(anchor="w", padx=20, pady=(15, 10))
            return card

    def cubiculo_item(self, parent, nombre, capacidad, estado, row, col, colspan=1, selected=False):
        occupied = estado == "Ocupado"
        bg = COLORES.get("OCCUPIED_BG", "#ffdddd") if occupied else COLORES.get("CARD_BG", "#ffffff")
        border = COLORES.get("SELECTED_BORDER", "#0000ff") if selected else COLORES.get("CARD_BORDER", "#cccccc")
        thickness = 2 if selected else 1

        item_frame = tk.Frame(
            parent, 
            bg=bg, 
            highlightbackground=border, 
            highlightthickness=thickness
        )
        
        item_frame.grid(row=row, column=col, columnspan=colspan, sticky="nsew", padx=4, pady=4)

        lbl_nombre = tk.Label(item_frame, text=nombre, bg=bg, font=("Arial", 10, "bold"))
        lbl_nombre.pack(anchor="w", padx=8, pady=(8, 2))

        lbl_estado = tk.Label(item_frame, text=f"{estado} - Cap: {capacidad}", bg=bg, font=("Arial", 8), fg=COLORES.get("texto_ayuda", "#666666"))
        lbl_estado.pack(anchor="w", padx=8, pady=(0, 8))

        return item_frame