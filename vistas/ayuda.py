# vistas/ayuda.py
import tkinter as tk
from config import COLORES, FUENTES
from utils import crear_tarjeta_base


class AyudaView(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=COLORES["blanco_fondo"])
        self.setup_ui()

    def setup_ui(self):
        header = tk.Frame(self, bg=COLORES["blanco_fondo"], pady=10, padx=20)
        header.pack(fill="x")

        tk.Label(
            header, text="Centro de ayuda", font=FUENTES["titulo"],
            fg=COLORES["texto_principal"], bg=COLORES["blanco_fondo"]
        ).pack(side="left")

        contenedor = tk.Frame(self, bg=COLORES["blanco_fondo"], padx=20, pady=10)
        contenedor.pack(fill="both", expand=True)

        tarjeta = crear_tarjeta_base(contenedor, pad_x=25, pad_y=25)
        tarjeta.pack(fill="x")

        tk.Label(
            tarjeta, text="Acerca del sistema y soporte", font=FUENTES["subtitulo"],
            bg=COLORES["gris_claro"], fg=COLORES["texto_principal"], anchor="w"
        ).pack(fill="x", pady=(0, 10))

        texto_ayuda = (
            "Bienvenido al Sistema Integral de Gestión Bibliotecaria (SIGB) del "
            "Learning Commons. Desde este panel administrativo puedes consultar el "
            "resumen general de uso, administrar el acervo y préstamos de libros, "
            "y llevar el control de objetos perdidos.\n\n"
            "Si presentas algún problema técnico, dudas sobre el funcionamiento del "
            "sistema o requieres soporte adicional, comunícate con el equipo de desarrollo:"
        )

        tk.Label(
            tarjeta, text=texto_ayuda, font=FUENTES["texto_normal"],
            bg=COLORES["gris_claro"], fg=COLORES["texto_principal"],
            justify="left", anchor="w", wraplength=700
        ).pack(fill="x", pady=(0, 20))

        tk.Frame(tarjeta, bg=COLORES["gris_linea"], height=1).pack(fill="x", pady=(0, 15))

        tk.Label(
            tarjeta, text="CORREO DE CONTACTO", font=FUENTES["etiqueta"],
            bg=COLORES["gris_claro"], fg=COLORES["texto_ayuda"], anchor="w"
        ).pack(fill="x")

        tk.Label(
            tarjeta, text="soporte.ticsianos@utr.edu.mx", font=FUENTES["subtitulo"],
            bg=COLORES["gris_claro"], fg=COLORES["rojo_principal"], anchor="w"
        ).pack(fill="x", pady=(4, 0))