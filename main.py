import tkinter as tk
from config import COLORES, FUENTES
from utils import load_image

from vistas.login import LoginView
from vistas.cubnew import CubiculosView
from vistas.dashboard import DashboardView
from vistas.objetos import ObjetosView
from vistas.libros import LibrosView
from vistas.userconfig import UserconfigView
from vistas.ayuda import AyudaView
class AppPrincipal(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Gestión - Biblioteca UTR")
        self.geometry("1200x900")
        self.configure(bg=COLORES["blanco_fondo"])

        self.usuario_actual = None
        self.vista_actual = None
        self.main_container = None

        self.contenedor_principal = tk.Frame(self, bg=COLORES["blanco_fondo"])
        self.contenedor_principal.pack(fill="both", expand=True)

        self.mostrar_login()

    def _limpiar_contenedor_principal(self):
        for widget in self.contenedor_principal.winfo_children():
            widget.destroy()
        self.vista_actual = None
        self.main_container = None

    def mostrar_login(self):
        self.usuario_actual = None
        self._limpiar_contenedor_principal()
        login = LoginView(self.contenedor_principal, on_login_success=self.al_iniciar_sesion)
        login.pack(fill="both", expand=True)

    def al_iniciar_sesion(self, usuario):
        self.usuario_actual = usuario
        self.construir_layout()

    def construir_layout(self):
        self._limpiar_contenedor_principal()

        self.sidebar = tk.Frame(
            self.contenedor_principal,
            bg=COLORES["rojo_principal"],
            width=250,
            highlightbackground=COLORES["gris_linea"],
            highlightthickness=1,
        )
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        self.image = load_image("img/UTRLOGO.png", (200, 100))
        tk.Label(self.sidebar, image=self.image, bg=COLORES["rojo_principal"]).pack(pady=10)

        # Info del usuario autenticado
        if self.usuario_actual:
            tk.Label(
                self.sidebar,
                text=self.usuario_actual["full_name"],
                bg=COLORES["rojo_principal"],
                fg=COLORES["blanco_fondo"],
                font=FUENTES["etiqueta"],
                wraplength=210,
            ).pack(padx=15, pady=(0, 2))
            tk.Label(
                self.sidebar,
                text=self.usuario_actual["user_type"].capitalize(),
                bg=COLORES["rojo_principal"],
                fg=COLORES["blanco_fondo"],
                font=FUENTES["texto_ayuda"],
            ).pack(pady=(0, 10))

        botones_menu = [
            ("Dashboard", lambda: self.cambiar_vista(DashboardView)),
            ("Cubículos", lambda: self.cambiar_vista(CubiculosView)),
            ("Objetos Perdidos", lambda: self.cambiar_vista(ObjetosView)),
            ("Libros", lambda: self.cambiar_vista(LibrosView)),
            ("Configuracion", lambda: self.cambiar_vista(UserconfigView)),
        ]

        for texto, comando in botones_menu:
            tk.Button(
                self.sidebar,
                text=texto,
                bg=COLORES["rojo_principal"],
                fg=COLORES["blanco_fondo"],
                font=FUENTES["texto_normal"],
                bd=0,
                anchor="w",
                padx=20,
                pady=10,
                activebackground=COLORES["rosa_claro"],
                command=comando,
            ).pack(fill="x", pady=0)

        # Cerrar sesión + Centro de ayuda abajo
        tk.Button(
            self.sidebar,
            text="Cerrar sesión",
            bg=COLORES["rojo_principal"],
            fg=COLORES["blanco_fondo"],
            font=FUENTES["texto_normal"],
            bd=0,
            anchor="w",
            padx=20,
            pady=10,
            activebackground=COLORES["rosa_claro"],
            command=self.mostrar_login,
        ).pack(fill="x", side="bottom")

        tk.Button(
            self.sidebar,
            text="Centro de ayuda",
            bg=COLORES["rojo_principal"],
            fg=COLORES["blanco_fondo"],
            font=FUENTES["texto_normal"],
            bd=0,
            anchor="w",
            padx=20,
            pady=10,
            activebackground=COLORES["rosa_claro"],
            command=None,
        ).pack(fill="x", side="bottom")

        self.main_container = tk.Frame(self.contenedor_principal, bg=COLORES["blanco_fondo"])
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