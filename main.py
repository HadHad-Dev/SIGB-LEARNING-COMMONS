# main.py
import tkinter as tk
import imagesxd
from config import COLORES, FUENTES

from vistas.cubiculos import CubiculosView
from vistas.dashboard import DashboardView
from vistas.objetos import ObjetosView
from vistas.libros import LibrosView
from vistas.cubiculos import CubiculosView
from vistas.userconfig import UserconfigView
class AppPrincipal(tk.Tk):
    def __init__(self):
        # se genera la ventana principal
        super().__init__()
        self.title("Sistema de Gestión - Biblioteca UTR")
        self.geometry("1200x900") 
        self.configure(bg=COLORES["blanco_fondo"]) 
        self.vista_actual = None
        self.construir_layout()

    def topbar(self):
        self.top_menu_frame = tk.Frame(self, bg=COLORES["blanco_fondo"], height=50)
        self.top_menu_frame.pack(side="top", fill="x")
        etiqueta1 = tk.Label(self.top_menu_frame, text="campus Retoño / cubiculos", bg=COLORES["blanco_fondo"]).pack(side="left",fill="y")

    def construir_layout(self):

        self.sidebar = tk.Frame(self, bg=COLORES["rojo_principal"], width=250, 
                           highlightbackground=COLORES["gris_linea"], highlightthickness=1)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        self.image = imagesxd.load_image(r"proyecto_biblioteca/img/UTRLOGO.png", (200, 100))
        UTR_logo_label = tk.Label(self.sidebar, image=self.image, bg=COLORES["rojo_principal"])
        UTR_logo_label.pack(pady=10)

        # Lista actualizada de botones según la imagen
        botones_menu = [
            ("Dashboard", lambda: self.cambiar_vista(DashboardView)),
            ("Cubículos", lambda:self.cambiar_vista(CubiculosView)),
            ("Objetos Perdidos",lambda:self.cambiar_vista(ObjetosView)), # Cambia None por: lambda: self.cambiar_vista(ObjetosView)
            ("Libros", lambda:self.cambiar_vista(LibrosView)),
            ("Configuracion", lambda:self.cambiar_vista(UserconfigView))
        ]

        for texto, comando in botones_menu:
            btn = tk.Button(self.sidebar, text=texto, bg=COLORES["rojo_principal"], 
                            fg=COLORES["blanco_fondo"], font=FUENTES["texto_normal"], bd=0, anchor="w", 
                            padx=20, pady=10, activebackground=COLORES["rosa_claro"], 
                            command=comando)
            btn.pack(fill="x", pady=0)
        
        btn_ayuda=tk.Button(self.sidebar,text="Centro de ayuda",bg=COLORES["rojo_principal"],fg=COLORES["blanco_fondo"], font=FUENTES["texto_normal"], bd=0, anchor="w", 
                                    padx=20, pady=10, activebackground=COLORES["rosa_claro"], 
                                    command=None)
        btn_ayuda.pack(fill="x",pady=0,side="bottom")

        self.main_container = tk.Frame(self, bg=COLORES["blanco_fondo"])
        self.main_container.pack(side="right", fill="both", expand=True)

        # Cargar vista por defecto al iniciar
        self.cambiar_vista(DashboardView)

    def cambiar_vista(self, ClaseVista):
        #Destruye la pantalla actual y carga la nueva
        if self.vista_actual is not None:
            self.vista_actual.destroy()
            
        # Instancia la nueva clase pasándole main_container como padre
        self.vista_actual = ClaseVista(self.main_container)
        
        # Empaqueta el nuevo Frame para que llene el contenedor
        self.vista_actual.pack(fill="both", expand=True)

if __name__ == "__main__":
    app = AppPrincipal()
    app.mainloop()