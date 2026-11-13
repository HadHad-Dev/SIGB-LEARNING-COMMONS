# main.py
import tkinter as tk
import imagesxd
from config import COLORES

from vistas.cubiculos import CubiculosView
from vistas.dashboard import DashboardView
from vistas.objetos import ObjetosView

class AppPrincipal(tk.Tk):
    def __init__(self):
        # se genera la ventana principal
        super().__init__()
        self.title("Mockup - Sistema de Gestión")
        self.geometry("1200x800")
        self.configure(bg=COLORES["blanco_fondo"])
        
        self.vista_actual = None 
        self.construir_layout()

    def topbar(self):
        self.top_menu_frame = tk.Frame(self, bg=COLORES["blanco_fondo"], height=50)
        self.top_menu_frame.pack(side="top", fill="x")
        etiqueta1 = tk.Label(self.top_menu_frame, text="campus Retoño / cubiculos", bg=COLORES["blanco_fondo"]).pack(side="left",fill="y")

    def construir_layout(self):
#Aqui construimos nuestro menu sidebar
        self.sidebar = tk.Frame(self, bg=COLORES["rojo_principal"], width=250)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        self.topbar()
    #Etiqueta en el top  antes de la side bar pero estando dentro de ella

        self.image = imagesxd.load_image(r"proyecto_biblioteca\UTRLOGO.png", (200, 100))
        UTR_logo_label = tk.Label(self.sidebar, image=self.image, bg=COLORES["rojo_principal"])
        UTR_logo_label.pack(pady=10)

        # Botones del menú
        # Usamos lambda para pasarle a cambiar_vista la clase que queremos instanciar
        btn_dash = tk.Button(self.sidebar, text="Dashboard", bg=COLORES["rojo_principal"], fg="white", bd=0, anchor="w", padx=20, pady=10, 
                             command=lambda: self.cambiar_vista(DashboardView))
        btn_dash.pack(fill="x", pady=2)

        btn_obj = tk.Button(self.sidebar, text="Objetos Perdidos", bg=COLORES["rojo_principal"], fg="white", bd=0, anchor="w", padx=20, pady=10, 
                            command=lambda: self.cambiar_vista(ObjetosView))
        btn_obj.pack(fill="x", pady=2)

        btn_cub = tk.Button(self.sidebar, text="Cubículos", bg=COLORES["rojo_principal"], fg="white", bd=0, anchor="w", padx=20, pady=10, 
                            command=lambda: self.cambiar_vista(CubiculosView))
        btn_cub.pack(fill="x", pady=2)

        #Aqui seguiria el mismo patron para agregar los botones de las demas pantallas

        # --- CONTENEDOR PRINCIPAL ---
        self.main_container = tk.Frame(self, bg=COLORES["gris_tenue"])
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