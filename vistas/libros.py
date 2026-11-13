# vistas/libros.py
import tkinter as tk
from tkinter import ttk
from config import COLORES, FUENTES
from utils import crear_tarjeta_kpi

class LibrosView(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=COLORES["blanco_fondo"])
        
        # Datos simulados: 25 Libros
        self.datos_libros = [
            (f"LIB-{str(i).zfill(3)}", f"Libro de Especialidad Vol. {i}", "Autor Anónimo", "Tecnología", "Disponible") for i in range(1, 21)
        ] + [
            (f"LIB-{str(i).zfill(3)}", f"Libro de Especialidad Vol. {i}", "Autor Anónimo", "Tecnología", "Prestado") for i in range(21, 26)
        ]

        # Datos simulados: 10 Préstamos
        self.datos_prestamos = [
            ("PR-001", "2201145 - Juan Pérez", "LIB-021 (Libro... Vol. 21)", "10 Nov 2026", "Atrasado"),
            ("PR-002", "2201146 - María Gómez", "LIB-022 (Libro... Vol. 22)", "13 Nov 2026", "En tiempo"),
            ("PR-003", "2201147 - Luis Torres", "LIB-023 (Libro... Vol. 23)", "14 Nov 2026", "En tiempo"),
            ("PR-004", "2201148 - Ana Ruíz", "LIB-024 (Libro... Vol. 24)", "15 Nov 2026", "En tiempo"),
            ("PR-005", "2201149 - Carlos Méndez", "LIB-025 (Libro... Vol. 25)", "15 Nov 2026", "En tiempo"),
            ("PR-006", "2201150 - Sofía Hernández", "LIB-010 (Fundamentos...)", "12 Nov 2026", "Devuelto"),
            ("PR-007", "2201151 - Elena Martínez", "LIB-015 (Redes...)", "11 Nov 2026", "Devuelto"),
            ("PR-008", "2201152 - Andrés García", "LIB-018 (Python...)", "09 Nov 2026", "Devuelto"),
            ("PR-009", "2201153 - Pablo Sánchez", "LIB-005 (Bases de datos)", "08 Nov 2026", "Devuelto"),
            ("PR-010", "2201154 - Mónica Silva", "LIB-002 (Cálculo...)", "05 Nov 2026", "Devuelto")
        ]

        self.configurar_estilos_tabla()
        self.setup_ui()

    def configurar_estilos_tabla(self):
        style = ttk.Style()
        style.theme_use("default")
        
        style.configure("TNotebook", background=COLORES["blanco_fondo"], borderwidth=0)
        style.configure("TNotebook.Tab", background=COLORES["gris_claro"], foreground=COLORES["texto_ayuda"], 
                        font=FUENTES["texto_normal"], padding=[15, 5])
        style.map("TNotebook.Tab", background=[("selected", COLORES["blanco_fondo"])], 
                  foreground=[("selected", COLORES["rojo_principal"])])

        style.configure("Treeview", background=COLORES["blanco_fondo"], foreground=COLORES["texto_principal"], 
                        rowheight=40, fieldbackground=COLORES["blanco_fondo"], font=FUENTES["texto_normal"], borderwidth=0)
        style.configure("Treeview.Heading", background=COLORES["gris_claro"], foreground=COLORES["texto_ayuda"], 
                        font=FUENTES["etiqueta"], borderwidth=0)
        style.map("Treeview", background=[("selected", COLORES["rosa_claro"])], foreground=[("selected", COLORES["rojo_principal"])])

    def setup_ui(self):
        # HEADER
        header = tk.Frame(self, bg=COLORES["blanco_fondo"], pady=10, padx=20)
        header.pack(fill="x")
        tk.Label(header, text="Acervo de libros y Préstamos", font=FUENTES["titulo"], 
                 fg=COLORES["texto_principal"], bg=COLORES["blanco_fondo"]).pack(side="left")

        # CONTENEDOR PRINCIPAL DIVIDIDO
        main_content = tk.Frame(self, bg=COLORES["blanco_fondo"], padx=20, pady=10)
        main_content.pack(fill="both", expand=True)

        # PANEL DERECHO (Botones)
        self.panel_botones = tk.Frame(main_content, bg=COLORES["blanco_fondo"], width=200)
        self.panel_botones.pack(side="right", fill="y", padx=(20, 0))
        tk.Label(self.panel_botones, text="Acciones", font=FUENTES["subtitulo"], 
                 bg=COLORES["blanco_fondo"], fg=COLORES["texto_principal"]).pack(anchor="w", pady=(0, 15))

        # Instanciar TODOS los botones (pero no empaquetarlos aún)
        self.btn_agregar = tk.Button(self.panel_botones, text="Agregar ejemplar", bg=COLORES["rojo_principal"], 
                                     fg=COLORES["blanco_fondo"], font=FUENTES["texto_normal"], bd=0, padx=15, pady=10, cursor="hand2")
        self.btn_editar = tk.Button(self.panel_botones, text="Editar ejemplar", bg=COLORES["blanco_fondo"], fg=COLORES["texto_principal"], 
                                    font=FUENTES["texto_normal"], relief="solid", bd=1, padx=15, pady=8, cursor="hand2")
        self.btn_eliminar = tk.Button(self.panel_botones, text="Eliminar ejemplar", bg=COLORES["blanco_fondo"], fg=COLORES["texto_principal"], 
                                      font=FUENTES["texto_normal"], relief="solid", bd=1, padx=15, pady=8, cursor="hand2")
        
        self.btn_marcar_devuelto = tk.Button(self.panel_botones, text="Marcar como Devuelto", bg=COLORES["rojo_principal"], 
                                             fg=COLORES["blanco_fondo"], font=FUENTES["texto_normal"], bd=0, padx=15, pady=10, cursor="hand2")
        self.btn_reporte_prestamos = tk.Button(self.panel_botones, text="Reporte de préstamos", bg=COLORES["blanco_fondo"], fg=COLORES["texto_principal"], 
                                               font=FUENTES["texto_normal"], relief="solid", bd=1, padx=15, pady=8, cursor="hand2")
        
        self.btn_exportar = tk.Button(self.panel_botones, text="Exportar en .xlsx", bg=COLORES["blanco_fondo"], fg=COLORES["texto_principal"], 
                                      font=FUENTES["texto_normal"], relief="solid", bd=1, padx=15, pady=8, cursor="hand2")

        # PANEL IZQUIERDO (Pestañas)
        self.notebook = ttk.Notebook(main_content)
        self.notebook.pack(side="left", fill="both", expand=True)

        # Pestaña 1: Inventario
        frame_inventario = tk.Frame(self.notebook, bg=COLORES["blanco_fondo"], highlightbackground=COLORES["gris_linea"], highlightthickness=1)
        self.notebook.add(frame_inventario, text="Inventario de Ejemplares")
        self.construir_pestaña_inventario(frame_inventario)

        # Pestaña 2: Préstamos
        frame_prestamos = tk.Frame(self.notebook, bg=COLORES["blanco_fondo"], highlightbackground=COLORES["gris_linea"], highlightthickness=1)
        self.notebook.add(frame_prestamos, text="Gestión de Préstamos")
        self.construir_pestaña_prestamos(frame_prestamos)

        # Conectar el evento de cambio de pestaña
        self.notebook.bind("<<NotebookTabChanged>>", self.actualizar_botones)
        
        # Forzar la actualización inicial
        self.actualizar_botones(None)

    def actualizar_botones(self, event):
        """Oculta todos los botones y muestra solo los de la pestaña actual"""
        pestana_actual = self.notebook.index("current")
        
        # 1. Limpiar el panel derecho (ocultar todo)
        for widget in [self.btn_agregar, self.btn_editar, self.btn_eliminar, 
                       self.btn_marcar_devuelto, self.btn_reporte_prestamos, self.btn_exportar]:
            widget.pack_forget()

        # 2. Empaquetar solo los correspondientes
        if pestana_actual == 0:  # Inventario
            self.btn_agregar.pack(fill="x", pady=5)
            self.btn_editar.pack(fill="x", pady=5)
            self.btn_eliminar.pack(fill="x", pady=5)
        elif pestana_actual == 1:  # Préstamos
            self.btn_marcar_devuelto.pack(fill="x", pady=5)
            self.btn_reporte_prestamos.pack(fill="x", pady=5)

        # 3. El botón de exportar siempre va al final, sin importar la pestaña
        self.btn_exportar.pack(fill="x", pady=(20, 5))

    def construir_pestaña_inventario(self, parent):
        # 1. KPIs del Inventario (Antes de la tabla)
        kpi_frame = tk.Frame(parent, bg=COLORES["blanco_fondo"], padx=15, pady=15)
        kpi_frame.pack(fill="x")
        
        kpis_inventario = [
            ("TOTAL DE EJEMPLARES", "25", "Acervo general"),
            ("DISPONIBLES", "20", "Listos para préstamo"),
            ("PRESTADOS", "5", "Actualmente en uso")
        ]
        for i, (t, v, s) in enumerate(kpis_inventario):
            crear_tarjeta_kpi(kpi_frame, t, v, s).grid(row=0, column=i, padx=5, sticky="ew")
            kpi_frame.grid_columnconfigure(i, weight=1)

        # 2. Tabla (Treeview)
        frame_tabla = tk.Frame(parent, bg=COLORES["blanco_fondo"])
        frame_tabla.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        columnas = ("ID", "Título", "Autor", "Categoría", "Estado")
        tabla = ttk.Treeview(frame_tabla, columns=columnas, show="headings")
        
        anchos = [80, 250, 180, 120, 100]
        for col, ancho in zip(columnas, anchos):
            tabla.heading(col, text=col.upper())
            tabla.column(col, width=ancho, anchor="w")

        scrollbar = ttk.Scrollbar(frame_tabla, orient="vertical", command=tabla.yview)
        tabla.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        tabla.pack(side="left", fill="both", expand=True)

        for libro in self.datos_libros:
            tabla.insert("", tk.END, values=libro)

    def construir_pestaña_prestamos(self, parent):
        # 1. KPIs de Préstamos (Antes de la tabla)
        kpi_frame = tk.Frame(parent, bg=COLORES["blanco_fondo"], padx=15, pady=15)
        kpi_frame.pack(fill="x")
        
        kpis_prestamos = [
            ("PRÉSTAMOS ACTIVOS", "5", "Aún no devueltos"),
            ("ATRASADOS", "1", "Requieren seguimiento"),
            ("DEVUELTOS ESTA SEMANA", "5", "Histórico reciente")
        ]
        for i, (t, v, s) in enumerate(kpis_prestamos):
            crear_tarjeta_kpi(kpi_frame, t, v, s).grid(row=0, column=i, padx=5, sticky="ew")
            kpi_frame.grid_columnconfigure(i, weight=1)

        # 2. Tabla (Treeview)
        frame_tabla = tk.Frame(parent, bg=COLORES["blanco_fondo"])
        frame_tabla.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        columnas = ("Folio", "Estudiante", "Libro", "Vencimiento", "Estado")
        tabla = ttk.Treeview(frame_tabla, columns=columnas, show="headings")
        
        anchos = [80, 220, 220, 120, 100]
        for col, ancho in zip(columnas, anchos):
            tabla.heading(col, text=col.upper())
            tabla.column(col, width=ancho, anchor="w")

        scrollbar = ttk.Scrollbar(frame_tabla, orient="vertical", command=tabla.yview)
        tabla.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        tabla.pack(side="left", fill="both", expand=True)

        for prestamo in self.datos_prestamos:
            tabla.insert("", tk.END, values=prestamo)