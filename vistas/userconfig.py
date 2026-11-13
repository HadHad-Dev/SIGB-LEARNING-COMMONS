# vistas/userconfig.py
import tkinter as tk
from tkinter import ttk
from config import COLORES, FUENTES, ESTADOS
from utils import crear_tarjeta_base


class UserconfigView(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=COLORES["blanco_fondo"])
        self.configurar_estilos()
        self.setup_ui()

    def configurar_estilos(self):
        # Mismo estilo de pestañas que libros.py
        style = ttk.Style()
        style.theme_use("default")
        style.configure("TNotebook", background=COLORES["blanco_fondo"], borderwidth=0)
        style.configure("TNotebook.Tab", background=COLORES["gris_claro"], foreground=COLORES["texto_ayuda"],
                        font=FUENTES["texto_normal"], padding=[15, 5])
        style.map("TNotebook.Tab", background=[("selected", COLORES["blanco_fondo"])],
                  foreground=[("selected", COLORES["rojo_principal"])])

    def setup_ui(self):
        # HEADER
        header = tk.Frame(self, bg=COLORES["blanco_fondo"], pady=10, padx=20)
        header.pack(fill="x")
        tk.Label(header, text="Configuración del Sistema", font=FUENTES["titulo"],
                 fg=COLORES["texto_principal"], bg=COLORES["blanco_fondo"]).pack(side="left")
        tk.Label(header, text="Perfil, ajustes generales y base de datos", font=FUENTES["texto_ayuda"],
                 fg=COLORES["texto_ayuda"], bg=COLORES["blanco_fondo"]).pack(side="right")

        # PESTAÑAS
        main_content = tk.Frame(self, bg=COLORES["blanco_fondo"], padx=20, pady=10)
        main_content.pack(fill="both", expand=True)
        self.notebook = ttk.Notebook(main_content)
        self.notebook.pack(fill="both", expand=True)

        for texto, constructor in [("Perfil de Usuario", self.construir_perfil),
                                   ("Ajustes Generales", self.construir_ajustes),
                                   ("Apariencia y Base de Datos", self.construir_bd)]:
            frame = tk.Frame(self.notebook, bg=COLORES["blanco_fondo"],
                             highlightbackground=COLORES["gris_linea"], highlightthickness=1)
            self.notebook.add(frame, text=texto)
            constructor(frame)

    # ---------- Helpers de UI ----------
    def _tarjeta(self, parent, titulo):
        """Tarjeta base con título; devuelve el cuerpo donde se colocan los campos."""
        card = crear_tarjeta_base(parent)
        card.pack(fill="x", padx=15, pady=(15, 0))
        tk.Label(card, text=titulo, font=FUENTES["subtitulo"], bg=COLORES["gris_claro"],
                 fg=COLORES["texto_principal"], anchor="w").pack(fill="x", padx=15, pady=10)
        cuerpo = tk.Frame(card, bg=COLORES["gris_claro"])
        cuerpo.pack(fill="x", padx=15, pady=(0, 15))
        cuerpo.grid_columnconfigure(1, weight=1)
        return cuerpo

    def _campo(self, cuerpo, fila, etiqueta, valor="", show=None, solo_lectura=False):
        tk.Label(cuerpo, text=etiqueta.upper(), bg=COLORES["gris_claro"], fg=COLORES["texto_ayuda"],
                 font=FUENTES["etiqueta"]).grid(row=fila, column=0, sticky="w", pady=8, padx=(0, 20))
        entry = tk.Entry(cuerpo, font=FUENTES["texto_normal"], relief="solid", bd=1, show=show,
                         bg=COLORES["blanco_fondo"], fg=COLORES["texto_principal"],
                         readonlybackground=COLORES["gris_tenue"])
        entry.insert(0, valor)
        if solo_lectura:
            entry.config(state="readonly")
        entry.grid(row=fila, column=1, sticky="ew", pady=8, ipady=4)
        return entry

    def _combo(self, cuerpo, fila, etiqueta, valores, actual):
        tk.Label(cuerpo, text=etiqueta.upper(), bg=COLORES["gris_claro"], fg=COLORES["texto_ayuda"],
                 font=FUENTES["etiqueta"]).grid(row=fila, column=0, sticky="w", pady=8, padx=(0, 20))
        combo = ttk.Combobox(cuerpo, values=valores, state="readonly", width=20)
        combo.set(actual)
        combo.grid(row=fila, column=1, sticky="w", pady=8)

    def _boton_primario(self, parent, texto):
        return tk.Button(parent, text=texto, bg=COLORES["rojo_principal"], fg=COLORES["blanco_fondo"],
                         font=FUENTES["texto_normal"], bd=0, padx=15, pady=10, cursor="hand2",
                         activebackground=COLORES["rojo_oscuro"], activeforeground=COLORES["blanco_fondo"])

    def _boton_secundario(self, parent, texto):
        return tk.Button(parent, text=texto, bg=COLORES["blanco_fondo"], fg=COLORES["texto_principal"],
                         font=FUENTES["texto_normal"], relief="solid", bd=1, padx=15, pady=8, cursor="hand2")

    # ---------- Pestaña 1: Perfil ----------
    def construir_perfil(self, parent):
        datos = self._tarjeta(parent, "Datos del administrador")
        self._campo(datos, 0, "Nombre completo", "Administrador UTR")
        self._campo(datos, 1, "Correo institucional", "admin@utr.edu.mx")
        self._campo(datos, 2, "Rol", "Administrador", solo_lectura=True)

        clave = self._tarjeta(parent, "Cambiar contraseña")
        self._campo(clave, 0, "Contraseña actual", show="*")
        self._campo(clave, 1, "Nueva contraseña", show="*")
        self._campo(clave, 2, "Confirmar contraseña", show="*")

        botones = tk.Frame(parent, bg=COLORES["blanco_fondo"])
        botones.pack(fill="x", padx=15, pady=15)
        self._boton_primario(botones, "Guardar cambios").pack(side="right")
        self._boton_secundario(botones, "Cancelar").pack(side="right", padx=10)

    # ---------- Pestaña 2: Ajustes generales ----------
    def construir_ajustes(self, parent):
        horario = self._tarjeta(parent, "Horario de la biblioteca")
        horas = [f"{h:02d}:00" for h in range(6, 23)]
        self._combo(horario, 0, "Hora de apertura", horas, "08:00")
        self._combo(horario, 1, "Hora de cierre", horas, "20:00")

        reservas = self._tarjeta(parent, "Reservas de cubículos")
        self._combo(reservas, 0, "Tolerancia (minutos)", ["5", "10", "15", "20", "30"], "15")

        notif = self._tarjeta(parent, "Notificaciones")
        self.var_notif = tk.BooleanVar(value=True)
        tk.Checkbutton(notif, text="Activar notificaciones del sistema", variable=self.var_notif,
                       font=FUENTES["texto_normal"], bg=COLORES["gris_claro"],
                       activebackground=COLORES["gris_claro"], selectcolor=COLORES["blanco_fondo"],
                       fg=COLORES["texto_principal"], cursor="hand2").grid(row=0, column=0, columnspan=2, sticky="w")

        botones = tk.Frame(parent, bg=COLORES["blanco_fondo"])
        botones.pack(fill="x", padx=15, pady=15)
        self._boton_primario(botones, "Guardar ajustes").pack(side="right")

    # ---------- Pestaña 3: Apariencia y BD ----------
    def construir_bd(self, parent):
        info = self._tarjeta(parent, "Sistema y base de datos")
        filas = [("Versión del software", "v1.0.0", COLORES["texto_principal"]),
                 ("Motor de base de datos", "SQLite (local)", COLORES["texto_principal"]),
                 ("Estado de la conexión", "Conectado", ESTADOS["disponible_texto"]),
                 ("Último respaldo", "12 Nov 2026 · 18:30", COLORES["texto_principal"])]
        for fila, (campo, valor, color) in enumerate(filas):
            tk.Label(info, text=campo.upper(), bg=COLORES["gris_claro"], fg=COLORES["texto_ayuda"],
                     font=FUENTES["etiqueta"]).grid(row=fila, column=0, sticky="w", pady=8, padx=(0, 20))
            tk.Label(info, text=valor, bg=COLORES["gris_claro"], fg=color,
                     font=FUENTES["texto_normal"]).grid(row=fila, column=1, sticky="w", pady=8)

        botones = tk.Frame(parent, bg=COLORES["blanco_fondo"])
        botones.pack(fill="x", padx=15, pady=15)
        self._boton_primario(botones, "Respaldar base de datos").pack(side="right")
        self._boton_secundario(botones, "Probar conexión").pack(side="right", padx=10)