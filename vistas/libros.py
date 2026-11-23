import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from config import COLORES, FUENTES
from utils import crear_tarjeta_kpi
from database.recursos_db import (
    obtener_libros,
    obtener_kpis_libros,
    agregar_libro,
    editar_libro,
    eliminar_libro,
    obtener_prestamos_libros,
    obtener_kpis_prestamos_libros,
    marcar_libro_devuelto,
)
from reportes_pdf import generar_pdf_prestamos_libros
from reportes_excel import exportar_tabla_excel


class LibrosView(tk.Frame):
    def __init__(self, parent, admin_id=1001):
        super().__init__(parent, bg=COLORES["blanco_fondo"])
        self.admin_id = admin_id
        self.datos_libros = []
        self.datos_prestamos = []
        self.kpis_prestamos = {"activos": 0, "atrasados": 0, "devueltos_semana": 0}

        self.configurar_estilos_tabla()
        self.setup_ui()
        self.cargar_datos()

    def configurar_estilos_tabla(self):
        style = ttk.Style()
        style.theme_use("default")

        style.configure("TNotebook", background=COLORES["blanco_fondo"], borderwidth=0)
        style.configure(
            "TNotebook.Tab", background=COLORES["gris_claro"],
            foreground=COLORES["texto_ayuda"], font=FUENTES["texto_normal"], padding=[15, 5]
        )
        style.map(
            "TNotebook.Tab",
            background=[("selected", COLORES["blanco_fondo"])],
            foreground=[("selected", COLORES["rojo_principal"])]
        )

        style.configure(
            "Treeview", background=COLORES["blanco_fondo"],
            foreground=COLORES["texto_principal"], rowheight=38,
            fieldbackground=COLORES["blanco_fondo"], font=FUENTES["texto_normal"], borderwidth=0
        )
        style.configure(
            "Treeview.Heading", background=COLORES["gris_claro"],
            foreground=COLORES["texto_ayuda"], font=FUENTES["etiqueta"], borderwidth=0
        )
        style.map(
            "Treeview",
            background=[("selected", COLORES["rosa_claro"])],
            foreground=[("selected", COLORES["rojo_principal"])]
        )

    def setup_ui(self):
        header = tk.Frame(self, bg=COLORES["blanco_fondo"], pady=10, padx=20)
        header.pack(fill="x")
        tk.Label(
            header, text="Acervo de libros y Préstamos", font=FUENTES["titulo"],
            fg=COLORES["texto_principal"], bg=COLORES["blanco_fondo"]
        ).pack(side="left")

        main_content = tk.Frame(self, bg=COLORES["blanco_fondo"], padx=20, pady=10)
        main_content.pack(fill="both", expand=True)

        self.panel_botones = tk.Frame(main_content, bg=COLORES["blanco_fondo"], width=200)
        self.panel_botones.pack(side="right", fill="y", padx=(20, 0))
        tk.Label(
            self.panel_botones, text="Acciones", font=FUENTES["subtitulo"],
            bg=COLORES["blanco_fondo"], fg=COLORES["texto_principal"]
        ).pack(anchor="w", pady=(0, 15))

        self.btn_agregar = tk.Button(
            self.panel_botones, text="Agregar ejemplar", bg=COLORES["rojo_principal"],
            fg=COLORES["blanco_fondo"], font=FUENTES["texto_normal"], bd=0,
            padx=15, pady=10, cursor="hand2", command=self.abrir_modal_agregar
        )

        self.btn_editar = tk.Button(
            self.panel_botones, text="Editar ejemplar", bg=COLORES["blanco_fondo"],
            fg=COLORES["texto_principal"], font=FUENTES["texto_normal"], relief="solid",
            bd=1, padx=15, pady=8, cursor="hand2", command=self.abrir_modal_editar
        )

        self.btn_eliminar = tk.Button(
            self.panel_botones, text="Eliminar ejemplar", bg=COLORES["blanco_fondo"],
            fg=COLORES["texto_principal"], font=FUENTES["texto_normal"], relief="solid",
            bd=1, padx=15, pady=8, cursor="hand2", command=self.accion_eliminar
        )

        self.btn_marcar_devuelto = tk.Button(
            self.panel_botones, text="Marcar como Devuelto", bg=COLORES["rojo_principal"],
            fg=COLORES["blanco_fondo"], font=FUENTES["texto_normal"], bd=0,
            padx=15, pady=10, cursor="hand2", command=self.accion_marcar_devuelto
        )
        self.btn_reporte_prestamos = tk.Button(
            self.panel_botones, text="Reporte de préstamos (PDF)", bg=COLORES["blanco_fondo"],
            fg=COLORES["texto_principal"], font=FUENTES["texto_normal"], relief="solid",
            bd=1, padx=15, pady=8, cursor="hand2", command=self.accion_reporte_pdf
        )

        self.btn_exportar = tk.Button(
            self.panel_botones, text="Exportar en .xlsx", bg=COLORES["blanco_fondo"],
            fg=COLORES["texto_principal"], font=FUENTES["texto_normal"], relief="solid",
            bd=1, padx=15, pady=8, cursor="hand2", command=self.accion_exportar_excel
        )

        self.notebook = ttk.Notebook(main_content)
        self.notebook.pack(side="left", fill="both", expand=True)

        frame_inventario = tk.Frame(
            self.notebook, bg=COLORES["blanco_fondo"],
            highlightbackground=COLORES["gris_linea"], highlightthickness=1
        )
        self.notebook.add(frame_inventario, text="Inventario de Ejemplares")
        self.construir_pestana_inventario(frame_inventario)

        # Pestaña 2: Préstamos
        frame_prestamos = tk.Frame(
            self.notebook, bg=COLORES["blanco_fondo"],
            highlightbackground=COLORES["gris_linea"], highlightthickness=1
        )
        self.notebook.add(frame_prestamos, text="Gestión de Préstamos")
        self.construir_pestana_prestamos(frame_prestamos)

        self.notebook.bind("<<NotebookTabChanged>>", self.actualizar_botones)
        self.actualizar_botones(None)

    def actualizar_botones(self, event):
        """Muestra solo los botones correspondientes a la pestaña activa."""
        pestana_actual = self.notebook.index("current")

        for widget in [
            self.btn_agregar, self.btn_editar, self.btn_eliminar,
            self.btn_marcar_devuelto, self.btn_reporte_prestamos, self.btn_exportar
        ]:
            widget.pack_forget()

        if pestana_actual == 0:
            self.btn_agregar.pack(fill="x", pady=5)
            self.btn_editar.pack(fill="x", pady=5)
            self.btn_eliminar.pack(fill="x", pady=5)
        elif pestana_actual == 1:
            self.btn_marcar_devuelto.pack(fill="x", pady=5)
            self.btn_reporte_prestamos.pack(fill="x", pady=5)

        self.btn_exportar.pack(fill="x", pady=(20, 5))

    def construir_pestana_inventario(self, parent):
        self.kpi_inv_frame = tk.Frame(parent, bg=COLORES["blanco_fondo"], padx=15, pady=15)
        self.kpi_inv_frame.pack(fill="x")

        frame_tabla = tk.Frame(parent, bg=COLORES["blanco_fondo"])
        frame_tabla.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        columnas = ("Código", "Título", "Autor", "Ubicación", "Estado")
        self.tabla_libros = ttk.Treeview(frame_tabla, columns=columnas, show="headings")

        anchos = [95, 250, 170, 120, 110]
        for col, ancho in zip(columnas, anchos):
            self.tabla_libros.heading(col, text=col.upper())
            self.tabla_libros.column(col, width=ancho, anchor="w")

        scrollbar = ttk.Scrollbar(frame_tabla, orient="vertical", command=self.tabla_libros.yview)
        self.tabla_libros.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.tabla_libros.pack(side="left", fill="both", expand=True)

    def construir_pestana_prestamos(self, parent):
        self.kpi_pres_frame = tk.Frame(parent, bg=COLORES["blanco_fondo"], padx=15, pady=15)
        self.kpi_pres_frame.pack(fill="x")

        frame_tabla = tk.Frame(parent, bg=COLORES["blanco_fondo"])
        frame_tabla.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        columnas = ("Folio", "Estudiante", "Libro", "Vencimiento", "Estado")
        self.tabla_prestamos = ttk.Treeview(frame_tabla, columns=columnas, show="headings")

        anchos = [85, 210, 230, 130, 100]
        for col, ancho in zip(columnas, anchos):
            self.tabla_prestamos.heading(col, text=col.upper())
            self.tabla_prestamos.column(col, width=ancho, anchor="w")

        scrollbar = ttk.Scrollbar(frame_tabla, orient="vertical", command=self.tabla_prestamos.yview)
        self.tabla_prestamos.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.tabla_prestamos.pack(side="left", fill="both", expand=True)

  
    def cargar_datos(self):
        self._cargar_inventario()
        self._cargar_prestamos()

    def _limpiar_frame(self, frame):
        for widget in frame.winfo_children():
            widget.destroy()

    def _cargar_inventario(self):
        kpis = obtener_kpis_libros()
        self._limpiar_frame(self.kpi_inv_frame)
        tarjetas = [
            ("TOTAL DE EJEMPLARES", str(kpis["total"]), "Acervo general"),
            ("DISPONIBLES", str(kpis["disponibles"]), "Listos para préstamo"),
            ("PRESTADOS", str(kpis["prestados"]), "Actualmente en uso"),
        ]
        for i, (t, v, s) in enumerate(tarjetas):
            crear_tarjeta_kpi(self.kpi_inv_frame, t, v, s).grid(row=0, column=i, padx=5, sticky="ew")
            self.kpi_inv_frame.grid_columnconfigure(i, weight=1)

        self.datos_libros = obtener_libros()
        for item in self.tabla_libros.get_children():
            self.tabla_libros.delete(item)

        for lib in self.datos_libros:
            self.tabla_libros.insert("", tk.END, values=(
                lib["bar_code"],
                lib["description_title"],
                lib["author"] or "-",
                lib["shelf_location"] or "-",
                lib["status"],
            ))

    def _cargar_prestamos(self):
        self.kpis_prestamos = obtener_kpis_prestamos_libros()
        self._limpiar_frame(self.kpi_pres_frame)
        tarjetas = [
            ("PRÉSTAMOS ACTIVOS", str(self.kpis_prestamos["activos"]), "Aún no devueltos"),
            ("ATRASADOS", str(self.kpis_prestamos["atrasados"]), "Requieren seguimiento"),
            ("DEVUELTOS ESTA SEMANA", str(self.kpis_prestamos["devueltos_semana"]), "Histórico reciente"),
        ]
        for i, (t, v, s) in enumerate(tarjetas):
            crear_tarjeta_kpi(self.kpi_pres_frame, t, v, s).grid(row=0, column=i, padx=5, sticky="ew")
            self.kpi_pres_frame.grid_columnconfigure(i, weight=1)

        self.datos_prestamos = obtener_prestamos_libros()
        for item in self.tabla_prestamos.get_children():
            self.tabla_prestamos.delete(item)

        for p in self.datos_prestamos:
            venc = p["due_at"].strftime("%d/%m/%Y %H:%M") if p["due_at"] else "-"
            self.tabla_prestamos.insert("", tk.END, values=(
                p["folio"],
                p["estudiante"],
                p["libro"],
                venc,
                p["estado"],
            ))


    def abrir_modal_agregar(self):
        self._abrir_modal_libro(modo="agregar")

    def abrir_modal_editar(self):
        seleccion = self.tabla_libros.selection()
        if not seleccion:
            messagebox.showwarning("Sin selección", "Selecciona un ejemplar de la tabla para editarlo.")
            return
        valores = self.tabla_libros.item(seleccion[0], "values")
        self._abrir_modal_libro(modo="editar", valores_iniciales=valores)

    def _abrir_modal_libro(self, modo, valores_iniciales=None):
        modal = tk.Toplevel(self)
        modal.title("Agregar ejemplar" if modo == "agregar" else "Editar ejemplar")
        modal.geometry("420x360")
        modal.configure(bg=COLORES["blanco_fondo"])
        modal.transient(self)
        modal.grab_set()

        frame = tk.Frame(modal, bg=COLORES["blanco_fondo"], padx=20, pady=15)
        frame.pack(fill="both", expand=True)

        tk.Label(frame, text="Código de barras *", bg=COLORES["blanco_fondo"], font=FUENTES["etiqueta"]).pack(anchor="w")
        entry_codigo = tk.Entry(frame, font=FUENTES["texto_normal"])
        entry_codigo.pack(fill="x", pady=(2, 10))

        tk.Label(frame, text="Título *", bg=COLORES["blanco_fondo"], font=FUENTES["etiqueta"]).pack(anchor="w")
        entry_titulo = tk.Entry(frame, font=FUENTES["texto_normal"])
        entry_titulo.pack(fill="x", pady=(2, 10))

        tk.Label(frame, text="Autor", bg=COLORES["blanco_fondo"], font=FUENTES["etiqueta"]).pack(anchor="w")
        entry_autor = tk.Entry(frame, font=FUENTES["texto_normal"])
        entry_autor.pack(fill="x", pady=(2, 10))

        tk.Label(frame, text="Ubicación (Estante)", bg=COLORES["blanco_fondo"], font=FUENTES["etiqueta"]).pack(anchor="w")
        entry_ubicacion = tk.Entry(frame, font=FUENTES["texto_normal"])
        entry_ubicacion.pack(fill="x", pady=(2, 10))

        tk.Label(frame, text="Estado", bg=COLORES["blanco_fondo"], font=FUENTES["etiqueta"]).pack(anchor="w")
        estados = ["disponible", "en_uso", "mantenimiento", "extraviado"]
        combo_estado = ttk.Combobox(frame, values=estados, state="readonly")
        combo_estado.current(0)
        combo_estado.pack(fill="x", pady=(2, 15))

        if modo == "editar" and valores_iniciales:
            codigo, titulo, autor, ubicacion, estado = valores_iniciales
            entry_codigo.insert(0, codigo)
            entry_codigo.config(state="disabled")  
            entry_titulo.insert(0, titulo)
            entry_autor.insert(0, "" if autor == "-" else autor)
            entry_ubicacion.insert(0, "" if ubicacion == "-" else ubicacion)
            if estado in estados:
                combo_estado.set(estado)

        def guardar():
            codigo = entry_codigo.get().strip()
            titulo = entry_titulo.get().strip()
            autor = entry_autor.get().strip()
            ubicacion = entry_ubicacion.get().strip()
            estado = combo_estado.get()

            if not codigo or not titulo:
                messagebox.showwarning("Campos obligatorios", "El código de barras y el título son obligatorios.")
                return

            if modo == "agregar":
                ok, msg = agregar_libro(codigo, titulo, autor, ubicacion, estado)
            else:
                ok, msg = editar_libro(codigo, titulo, autor, ubicacion, estado)

            if ok:
                messagebox.showinfo("Éxito", msg)
                modal.destroy()
                self.cargar_datos()
            else:
                messagebox.showerror("Error", msg)

        tk.Button(
            frame, text="Guardar", bg=COLORES["rojo_principal"], fg=COLORES["blanco_fondo"],
            font=FUENTES["texto_normal"], bd=0, pady=8, cursor="hand2", command=guardar
        ).pack(fill="x")

    def accion_eliminar(self):
        seleccion = self.tabla_libros.selection()
        if not seleccion:
            messagebox.showwarning("Sin selección", "Selecciona un ejemplar para eliminar.")
            return

        codigo, titulo = self.tabla_libros.item(seleccion[0], "values")[:2]
        confirmar = messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Seguro que deseas eliminar '{titulo}' ({codigo})?"
        )
        if not confirmar:
            return

        ok, msg = eliminar_libro(codigo)
        if ok:
            messagebox.showinfo("Eliminado", msg)
            self.cargar_datos()
        else:
            messagebox.showerror("No se pudo eliminar", msg)

  

    def accion_marcar_devuelto(self):
        seleccion = self.tabla_prestamos.selection()
        if not seleccion:
            messagebox.showwarning("Sin selección", "Selecciona un préstamo activo para marcarlo como devuelto.")
            return

        folio, estudiante, libro, _, estado = self.tabla_prestamos.item(seleccion[0], "values")
        if not str(folio).startswith("ACT-"):
            messagebox.showinfo("Ya devuelto", "Este préstamo ya se encuentra cerrado en el historial.")
            return

        confirmar = messagebox.askyesno(
            "Confirmar devolución",
            f"¿Confirmas la recepción física de:\n{libro}\nprestado a {estudiante}?"
        )
        if not confirmar:
            return

        usage_id = int(str(folio).replace("ACT-", ""))
        ok, msg = marcar_libro_devuelto(usage_id, self.admin_id)
        if ok:
            messagebox.showinfo("Devolución registrada", msg)
            self.cargar_datos()
        else:
            messagebox.showerror("Error", msg)

    def accion_reporte_pdf(self):
        ruta = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("Archivo PDF", "*.pdf")],
            initialfile="reporte_prestamos_libros.pdf",
            title="Guardar reporte de préstamos"
        )
        if not ruta:
            return

        try:
            generar_pdf_prestamos_libros(ruta, self.kpis_prestamos, self.datos_prestamos)
            messagebox.showinfo("Reporte generado", f"PDF guardado en:\n{ruta}")
        except Exception as e:
            messagebox.showerror("Error al generar PDF", str(e))

    def accion_exportar_excel(self):
        pestana = self.notebook.index("current")
        if pestana == 0:
            nombre_archivo = "inventario_libros.xlsx"
            nombre_hoja = "Inventario Libros"
            encabezados = ["Código", "Título", "Autor", "Ubicación", "Estado"]
            filas = [
                (l["bar_code"], l["description_title"], l["author"] or "", l["shelf_location"] or "", l["status"])
                for l in self.datos_libros
            ]
        else:
            nombre_archivo = "prestamos_libros.xlsx"
            nombre_hoja = "Préstamos Libros"
            encabezados = ["Folio", "Estudiante", "Libro", "Vencimiento", "Estado"]
            filas = [
                (
                    p["folio"], p["estudiante"], p["libro"],
                    p["due_at"].strftime("%d/%m/%Y %H:%M") if p["due_at"] else "",
                    p["estado"]
                )
                for p in self.datos_prestamos
            ]

        ruta = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Archivo Excel", "*.xlsx")],
            initialfile=nombre_archivo,
            title="Exportar a Excel"
        )
        if not ruta:
            return

        try:
            exportar_tabla_excel(ruta, nombre_hoja, encabezados, filas)
            messagebox.showinfo("Exportación exitosa", f"Archivo Excel guardado en:\n{ruta}")
        except Exception as e:
            messagebox.showerror("Error al exportar", str(e))