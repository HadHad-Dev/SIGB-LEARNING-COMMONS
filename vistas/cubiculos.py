# vistas/cubiculos.py
import tkinter as tk
from config import COLORES, FUENTES, ESTADOS
from utils import crear_tarjeta_kpi, crear_tarjeta_base


class CubiculosView(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=COLORES["blanco_fondo"])

        # Datos simulados (mockup): nombre -> (capacidad, estado, usuario, inicio, fin)
        # El orden de escritura define la posición en la cuadrícula del mapa
        self.datos_cubiculos = {
            "Oceania": (4, "ocupado", "Ana López", "09:00", "11:00"),
            "Asia": (4, "disponible", "—", "—", "—"),
            "Europa": (6, "llave", "Diego Ruiz", "10:30", "12:30"),
            "America": (6, "disponible", "—", "—", "—"),
            "Africa": (8, "ocupado", "Luis Gómez", "09:30", "11:30")
        }
        # Etiqueta visible, color de texto y color de fondo por estado
        self.estilos_estado = {
            "disponible": ("Disponible", ESTADOS["disponible_texto"], ESTADOS["disponible_fondo"]),
            "ocupado": ("Ocupado", ESTADOS["ocupado_texto"], ESTADOS["ocupado_fondo"]),
            "llave": ("Falta entregar llave", ESTADOS["llave_texto"], ESTADOS["llave_fondo"]),
        }
        self.celdas = {}
        self.seleccionado = None
        self.setup_ui()
        self.seleccionar(next(iter(self.datos_cubiculos)))  # selecciona el primero

    def setup_ui(self):
        # HEADER
        header = tk.Frame(self, bg=COLORES["blanco_fondo"], pady=10, padx=20)
        header.pack(fill="x")
        tk.Label(header, text="Gestión de Cubículos", font=FUENTES["titulo"],
                 fg=COLORES["texto_principal"], bg=COLORES["blanco_fondo"]).pack(side="left")
        tk.Label(header, text="2 de 6 cubículos disponibles ahora", font=FUENTES["texto_ayuda"],
                 fg=COLORES["texto_ayuda"], bg=COLORES["blanco_fondo"]).pack(side="right")

        # KPIs
        kpi_frame = tk.Frame(self, bg=COLORES["blanco_fondo"], padx=20)
        kpi_frame.pack(fill="x", pady=10)
        kpis = [
            ("TOTAL DE CUBÍCULOS", "6", "Capacidad total de 36"),
            ("DISPONIBLES", "2", "Listos para reservar"),
            ("OCUPADOS", "4", "1 requiere entrega de llave"),
            ("HORAS DE USO HOY", "18 h", "Acumuladas en el día"),
        ]
        for i, (t, v, s) in enumerate(kpis):
            crear_tarjeta_kpi(kpi_frame, t, v, s).grid(row=0, column=i, padx=5, sticky="ew")
            kpi_frame.grid_columnconfigure(i, weight=1)

        # CUERPO: mapa (izquierda) + detalles (derecha)
        bottom_frame = tk.Frame(self, bg=COLORES["blanco_fondo"], padx=20)
        bottom_frame.pack(fill="both", expand=True, pady=(10, 20))

        self.construir_mapa(bottom_frame)
        self.construir_detalles(bottom_frame)

    # ---------- MAPA ----------
    def construir_mapa(self, parent):
        mapa_card = crear_tarjeta_base(parent)
        mapa_card.pack(side="left", fill="both", expand=True, padx=(0, 10))

        tk.Label(mapa_card, text="Mapa de la biblioteca", font=FUENTES["subtitulo"],
                 bg=COLORES["gris_claro"], fg=COLORES["texto_principal"], anchor="w"
                 ).pack(fill="x", padx=15, pady=10)

        # Leyenda de colores semánticos
        leyenda = tk.Frame(mapa_card, bg=COLORES["gris_claro"])
        leyenda.pack(fill="x", padx=15)
        for clave in ("disponible", "ocupado", "llave"):
            nombre, color, _ = self.estilos_estado[clave]
            tk.Label(leyenda, text="● " + nombre, font=FUENTES["etiqueta"],
                     bg=COLORES["gris_claro"], fg=color).pack(side="left", padx=(0, 15))

        # Cuadrícula 2 x 3 con la posición física de los cubículos
        grid_frame = tk.Frame(mapa_card, bg=COLORES["gris_claro"])
        grid_frame.pack(fill="both", expand=True, padx=15, pady=15)

        for indice, nombre in enumerate(self.datos_cubiculos):
            fila, col = divmod(indice, 3)
            grid_frame.grid_columnconfigure(col, weight=1, uniform="cub")
            grid_frame.grid_rowconfigure(fila, weight=1, uniform="cub")

            capacidad, estado = self.datos_cubiculos[nombre][:2]
            _, color, fondo = self.estilos_estado[estado]

            celda = tk.Frame(grid_frame, bg=fondo, cursor="hand2",
                             highlightbackground=COLORES["gris_linea"], highlightthickness=1)
            celda.grid(row=fila, column=col, sticky="nsew", padx=6, pady=6)

            lbl_num = tk.Label(celda, text=nombre, font=FUENTES["subtitulo"], bg=fondo, fg=color)
            lbl_num.pack(expand=True, pady=(15, 0))
            lbl_cap = tk.Label(celda, text=f"{capacidad} personas", font=FUENTES["etiqueta"],
                               bg=fondo, fg=COLORES["texto_ayuda"])
            lbl_cap.pack(expand=True, pady=(0, 15))

            # Clic en cualquier parte de la celda
            for w in (celda, lbl_num, lbl_cap):
                w.bind("<Button-1>", lambda e, n=nombre: self.seleccionar(n))
            self.celdas[nombre] = celda

    # ---------- DETALLES ----------
    def construir_detalles(self, parent):
        det_card = crear_tarjeta_base(parent)
        det_card.pack(side="right", fill="both", expand=True, padx=(10, 0))

        tk.Label(det_card, text="Detalles del cubículo", font=FUENTES["subtitulo"],
                 bg=COLORES["gris_claro"], fg=COLORES["texto_principal"], anchor="w"
                 ).pack(fill="x", padx=15, pady=10)

        tabla = tk.Frame(det_card, bg=COLORES["gris_claro"])
        tabla.pack(fill="x", padx=15)
        tabla.grid_columnconfigure(1, weight=1)

        self.det_valores = {}
        for fila, campo in enumerate(["Cubículo", "Capacidad", "Estado", "Usuario", "Inicio", "Fin"]):
            tk.Label(tabla, text=campo.upper(), bg=COLORES["gris_claro"], fg=COLORES["texto_ayuda"],
                     font=FUENTES["etiqueta"]).grid(row=fila, column=0, sticky="w", pady=6, padx=(0, 20))
            lbl = tk.Label(tabla, bg=COLORES["gris_claro"], fg=COLORES["texto_principal"],
                           font=FUENTES["texto_normal"])
            lbl.grid(row=fila, column=1, sticky="w", pady=6)
            self.det_valores[campo] = lbl

        # Botones de acción (mismo estilo que libros.py)
        acciones = tk.Frame(det_card, bg=COLORES["gris_claro"])
        acciones.pack(fill="x", padx=15, pady=15, side="bottom")

        btn_reserva = tk.Button(acciones, text="Registrar reserva manual", bg=COLORES["rojo_principal"],
                                fg=COLORES["blanco_fondo"], font=FUENTES["texto_normal"], bd=0,
                                padx=15, pady=10, cursor="hand2",
                                activebackground=COLORES["rojo_oscuro"], activeforeground=COLORES["blanco_fondo"])
        btn_reserva.pack(fill="x", pady=5)
        for texto in ("Extender tiempo", "Liberar cubículo"):
            tk.Button(acciones, text=texto, bg=COLORES["blanco_fondo"], fg=COLORES["texto_principal"],
                      font=FUENTES["texto_normal"], relief="solid", bd=1, padx=15, pady=8,
                      cursor="hand2").pack(fill="x", pady=5)

    # ---------- INTERACCIÓN VISUAL ----------
    def seleccionar(self, nombre_sel):
        """Resalta la celda elegida y actualiza el panel de detalles."""
        self.seleccionado = nombre_sel
        for n, celda in self.celdas.items():
            if n == nombre_sel:
                celda.config(highlightbackground=COLORES["SELECTED_BORDER"], highlightthickness=3)
            else:
                celda.config(highlightbackground=COLORES["gris_linea"], highlightthickness=1)

        capacidad, estado, usuario, inicio, fin = self.datos_cubiculos[nombre_sel]
        etiqueta, color, _ = self.estilos_estado[estado]
        self.det_valores["Cubículo"].config(text=nombre_sel)
        self.det_valores["Capacidad"].config(text=f"{capacidad} personas")
        self.det_valores["Estado"].config(text=etiqueta, fg=color)
        self.det_valores["Usuario"].config(text=usuario)
        self.det_valores["Inicio"].config(text=inicio)
        self.det_valores["Fin"].config(text=fin)