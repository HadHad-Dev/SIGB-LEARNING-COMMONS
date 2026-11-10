# main.py
import tkinter as tk
from config import COLORS

from vistas.dashboard import DashboardView
from vistas.objetos import ObjetosView

class AppPrincipal(tk.Tk):
    def __init__(self):
        # se genera la ventana principal
        super().__init__()
        self.title("Mockup - Sistema de Gestión")
        self.geometry("1200x800")
        self.configure(bg=COLORS["bg"])
        
        self.vista_actual = None 
        self.construir_layout()

    def construir_layout(self):
#Aqui construimos nuestro menu sidebar
        sidebar = tk.Frame(self, bg=COLORS["sidebar"], width=250)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)
    #Etiqueta en el top  antes de la side bar pero estando dentro de ella
        tk.Label(sidebar, text="LOGO UTR\nGestión", bg=COLORS["sidebar"], fg="white", pady=20).pack(fill="x")

        # Botones del menú
        # Usamos lambda para pasarle a cambiar_vista la clase que queremos instanciar
        btn_dash = tk.Button(sidebar, text="Dashboard", bg=COLORS["sidebar"], fg="white", bd=0, anchor="w", padx=20, pady=10, 
                             command=lambda: self.cambiar_vista(DashboardView))
        btn_dash.pack(fill="x", pady=2)

        btn_obj = tk.Button(sidebar, text="Objetos Perdidos", bg=COLORS["sidebar"], fg="white", bd=0, anchor="w", padx=20, pady=10, 
                            command=lambda: self.cambiar_vista(ObjetosView))
        btn_obj.pack(fill="x", pady=2)

        #Aqui seguiria el mismo patron para agregar los botones de las demas pantallas

        # --- CONTENEDOR PRINCIPAL ---
        self.main_container = tk.Frame(self, bg=COLORS["bg"])
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