# main.py
import tkinter as tk
from config import COLORES, FUENTES
from vistas.dashboard import DashboardView
from vistas.objetos import ObjetosView
from vistas.libros import LibrosView
from vistas.cubiculos import CubiculosView
#from vistas.userconfig import UserconfigView
class AppPrincipal(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Gestión - Biblioteca UTR")
        self.geometry("1200x900") 
        self.configure(bg=COLORES["blanco_fondo"]) 
        self.vista_actual = None
        self.construir_layout()

    def construir_layout(self):

        sidebar = tk.Frame(self, bg=COLORES["rojo_principal"], width=250, 
                           highlightbackground=COLORES["gris_linea"], highlightthickness=1)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        tk.Label(sidebar, text="LOGO UTR\nGestión", bg=COLORES["rojo_principal"], 
                 fg=COLORES["blanco_fondo"], font=FUENTES["subtitulo"], pady=20).pack(fill="x")

        # Lista actualizada de botones según la imagen
        botones_menu = [
            ("Dashboard", lambda: self.cambiar_vista(DashboardView)),
            ("Cubículos", lambda:self.cambiar_vista(CubiculosView)),
            ("Objetos Perdidos",lambda:self.cambiar_vista(ObjetosView)), # Cambia None por: lambda: self.cambiar_vista(ObjetosView)
            ("Libros", lambda:self.cambiar_vista(LibrosView)),
            ("Configuracion", lambda:self.cambiar_vista(UserconfigView))
        ]

        for texto, comando in botones_menu:
            btn = tk.Button(sidebar, text=texto, bg=COLORES["rojo_principal"], 
                            fg=COLORES["blanco_fondo"], font=FUENTES["texto_normal"], bd=0, anchor="w", 
                            padx=20, pady=10, activebackground=COLORES["rosa_claro"], 
                            command=comando)
            btn.pack(fill="x", pady=0)
        
        btn_ayuda=tk.Button(sidebar,text="Centro de ayuda",bg=COLORES["rojo_principal"],fg=COLORES["blanco_fondo"], font=FUENTES["texto_normal"], bd=0, anchor="w", 
                                    padx=20, pady=10, activebackground=COLORES["rosa_claro"], 
                                    command=None)
        btn_ayuda.pack(fill="x",pady=0,side="bottom")

        self.main_container = tk.Frame(self, bg=COLORES["blanco_fondo"])
        self.main_container.pack(side="right", fill="both", expand=True)

        self.cambiar_vista(DashboardView)

    def cambiar_vista(self, ClaseVista):
        if self.vista_actual is not None:
            self.vista_actual.destroy()
            
        self.vista_actual = ClaseVista(self.main_container)
        self.vista_actual.pack(fill="both", expand=True)

if __name__ == "__main__":
    app = AppPrincipal()
    app.mainloop()