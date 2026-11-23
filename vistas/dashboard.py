import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from config import COLORES, FUENTES, ESTADOS
from utils import crear_tarjeta_kpi, crear_tarjeta_base
from database.registros_db import (
    obtener_kpis_dashboard,
    obtener_usos_por_tipo_usuario,
    obtener_ranking_carreras,
    obtener_registros_recientes,
    obtener_notificaciones,
    obtener_resumen_general,
)
from reportes_pdf import generar_pdf_dashboard


class DashboardView(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=COLORES["blanco_fondo"])
        self.kpis_actuales = {"mujeres": 0, "hombres": 0, "quarter_top": "Sin datos"}
        self.registros_actuales = []
        self.resumen_actual = []
        self.fig_uso = None
        self.fig_carreras = None

        self.setup_ui()
        self.cargar_datos()

    def setup_ui(self):
        # --- Encabezado ---
        header = tk.Frame(self, bg=COLORES["blanco_fondo"], pady=10, padx=20)
        header.pack(fill="x")

        tk.Label(
            header, text="Dashboard general", font=FUENTES["titulo"],
            fg=COLORES["texto_principal"], bg=COLORES["blanco_fondo"]
        ).pack(side="left")

        header_right = tk.Frame(header, bg=COLORES["blanco_fondo"])
        header_right.pack(side="right")

        opciones_fecha = ["Semana actual", "Cuatrimestre actual", "Cuatrimestre anterior"]
        self.selector = ttk.Combobox(header_right, values=opciones_fecha, state="readonly", width=20)
        self.selector.current(0)
        self.selector.bind("<<ComboboxSelected>>", self._al_cambiar_periodo)
        self.selector.pack(side="left", padx=10)

        tk.Button(
            header_right, text="Generar histórico (PDF)", bg=COLORES["blanco_fondo"],
            fg=COLORES["texto_principal"], font=FUENTES["texto_normal"],
            relief="solid", bd=1, padx=12, pady=3, cursor="hand2",
            command=self.exportar_pdf
        ).pack(side="left", padx=5)

        self.btn_notificaciones = tk.Button(
            header_right, text="🔔", font=("Arial", 14), bd=0,
            bg=COLORES["blanco_fondo"], cursor="hand2",
            command=self.mostrar_notificaciones
        )
        self.btn_notificaciones.pack(side="left", padx=5)

        # --- Tarjetas KPI ---
        self.kpi_frame = tk.Frame(self, bg=COLORES["blanco_fondo"], padx=20)
        self.kpi_frame.pack(fill="x", pady=8)

        # --- Gráfica principal (Uso por tipo de usuario) ---
        charts_frame = tk.Frame(self, bg=COLORES["blanco_fondo"], padx=20)
        charts_frame.pack(fill="x", pady=(6, 0))

        bar_chart = crear_tarjeta_base(charts_frame)
        bar_chart.pack(fill="x", expand=True)

        tk.Label(
            bar_chart, text="Uso de recursos por tipo de usuario",
            font=FUENTES["texto_ayuda"], bg=COLORES["gris_claro"],
            fg=COLORES["texto_ayuda"], anchor="w"
        ).pack(fill="x", padx=10, pady=(8, 0))

        self.contenedor_grafica_uso = tk.Frame(bar_chart, bg=COLORES["gris_claro"], height=180)
        self.contenedor_grafica_uso.pack(fill="x", padx=10, pady=6)

        # --- Resumen general de uso ---
        resumen_frame = tk.Frame(self, bg=COLORES["blanco_fondo"], padx=20)
        resumen_frame.pack(fill="x", pady=(8, 4))

        resumen_card = crear_tarjeta_base(resumen_frame)
        resumen_card.pack(fill="x", expand=True)

        tk.Label(
            resumen_card, text="Resumen general de uso", font=FUENTES["subtitulo"],
            bg=COLORES["gris_claro"], fg=COLORES["texto_principal"], anchor="w"
        ).pack(fill="x", padx=15, pady=(8, 4))

        self.tabla_resumen_frame = tk.Frame(resumen_card, bg=COLORES["gris_claro"])
        self.tabla_resumen_frame.pack(fill="x", padx=15, pady=(0, 8))

        # --- Sección inferior (Ranking + Registro reciente) ---
        bottom_frame = tk.Frame(self, bg=COLORES["blanco_fondo"], padx=20)
        bottom_frame.pack(fill="both", expand=True, pady=(6, 15))

        # Tarjeta Izquierda: Ranking por carrera
        ranking_card = crear_tarjeta_base(bottom_frame)
        ranking_card.pack(side="left", fill="both", expand=True, padx=(0, 10))

        tk.Label(
            ranking_card, text="Ranking por carrera", font=FUENTES["subtitulo"],
            bg=COLORES["gris_claro"], fg=COLORES["texto_principal"], anchor="w"
        ).pack(fill="x", padx=15, pady=(10, 0))

        self.contenedor_ranking = tk.Frame(ranking_card, bg=COLORES["gris_claro"])
        self.contenedor_ranking.pack(fill="both", expand=True, padx=10, pady=10)

        # Tarjeta Derecha: Registro reciente
        registro_card = crear_tarjeta_base(bottom_frame)
        registro_card.pack(side="right", fill="both", expand=True, padx=(10, 0))

        tk.Label(
            registro_card, text="Registro reciente", font=FUENTES["subtitulo"],
            bg=COLORES["gris_claro"], fg=COLORES["texto_principal"], anchor="w"
        ).pack(fill="x", padx=15, pady=10)

        self.tabla_frame = tk.Frame(registro_card, bg=COLORES["gris_claro"])
        self.tabla_frame.pack(fill="both", expand=True, padx=15)

    def _al_cambiar_periodo(self, evento):
        self.cargar_datos()

    def cargar_datos(self):
        """Consulta MySQL según el periodo seleccionado y actualiza toda la vista."""
        periodo = self.selector.get()

        self.kpis_actuales = obtener_kpis_dashboard(periodo)
        datos_tipo_usuario = obtener_usos_por_tipo_usuario(periodo)
        self.resumen_actual = obtener_resumen_general(periodo)
        datos_carreras = obtener_ranking_carreras(periodo)
        self.registros_actuales = obtener_registros_recientes(limite=6)
        alertas = obtener_notificaciones()

        self._render_kpis(self.kpis_actuales)
        self._render_grafica_tipo_usuario(datos_tipo_usuario)
        self._render_resumen_general(self.resumen_actual)
        self._render_ranking_carreras(datos_carreras)
        self._render_registros(self.registros_actuales)

        if alertas:
            texto_campana = f"🔔 ({len(alertas)})"
        else:
            texto_campana = "🔔"
        self.btn_notificaciones.config(text=texto_campana)

    def _limpiar_frame(self, frame):
        for widget in frame.winfo_children():
            widget.destroy()

    def _render_kpis(self, kpis):
        self._limpiar_frame(self.kpi_frame)
        tarjetas = [
            ("MUJERES", str(kpis["mujeres"]), "Usos registrados en el periodo"),
            ("HOMBRES", str(kpis["hombres"]), "Usos registrados en el periodo"),
            ("CUATRIMESTRE TOP", str(kpis["quarter_top"]), "Mayor frecuencia de alumnos"),
        ]
        for i, (titulo, valor, subtitulo) in enumerate(tarjetas):
            crear_tarjeta_kpi(self.kpi_frame, titulo, valor, subtitulo).grid(
                row=0, column=i, padx=5, sticky="ew"
            )
            self.kpi_frame.grid_columnconfigure(i, weight=1)

    def _render_grafica_tipo_usuario(self, datos_tipo):
        self._limpiar_frame(self.contenedor_grafica_uso)

        fig = Figure(figsize=(8, 2.0), dpi=100)
        fig.patch.set_facecolor(COLORES["gris_claro"])
        ax = fig.add_subplot(111)
        ax.set_facecolor(COLORES["gris_claro"])

        if not datos_tipo:
            ax.text(
                0.5, 0.5, "Sin registros en este periodo",
                ha="center", va="center", color=COLORES["texto_ayuda"], fontsize=10
            )
            ax.axis("off")
        else:
            tipos = []
            totales = []
            for tipo, total in datos_tipo:
                tipos.append(tipo)
                totales.append(total)

            ax.bar(tipos, totales, color=COLORES["rojo_principal"], width=0.45)
            ax.set_ylabel("Usos", color=COLORES["texto_ayuda"], fontsize=9)
            ax.tick_params(axis="x", colors=COLORES["texto_principal"], labelsize=9)
            ax.tick_params(axis="y", colors=COLORES["texto_ayuda"], labelsize=8)
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)
            ax.spines["left"].set_color(COLORES["gris_linea"])
            ax.spines["bottom"].set_color(COLORES["gris_linea"])
            fig.tight_layout()

        self.fig_uso = fig
        canvas = FigureCanvasTkAgg(fig, master=self.contenedor_grafica_uso)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def _render_resumen_general(self, resumen):
        self._limpiar_frame(self.tabla_resumen_frame)

        if not resumen:
            tk.Label(
                self.tabla_resumen_frame, text="Sin datos disponibles.",
                bg=COLORES["gris_claro"], fg=COLORES["texto_ayuda"],
                font=FUENTES["texto_normal"]
            ).pack(pady=10)
            return

        for i, (indicador, valor) in enumerate(resumen):
            fila = i // 2
            col_base = (i % 2) * 2

            tk.Label(
                self.tabla_resumen_frame, text=f"{indicador}:",
                bg=COLORES["gris_claro"], fg=COLORES["texto_ayuda"],
                font=FUENTES["texto_ayuda"], anchor="w"
            ).grid(row=fila, column=col_base, sticky="w", pady=3, padx=(0, 8))

            tk.Label(
                self.tabla_resumen_frame, text=valor,
                bg=COLORES["gris_claro"], fg=COLORES["texto_principal"],
                font=FUENTES["texto_normal"], anchor="w"
            ).grid(row=fila, column=col_base + 1, sticky="w", pady=3, padx=(0, 30))

        self.tabla_resumen_frame.grid_columnconfigure(1, weight=1)
        self.tabla_resumen_frame.grid_columnconfigure(3, weight=1)

    def _render_ranking_carreras(self, datos_carreras):
        self._limpiar_frame(self.contenedor_ranking)

        fig = Figure(figsize=(4.5, 2.0), dpi=100)
        fig.patch.set_facecolor(COLORES["gris_claro"])
        ax = fig.add_subplot(111)
        ax.set_facecolor(COLORES["gris_claro"])

        if not datos_carreras:
            ax.text(
                0.5, 0.5, "Sin datos de carreras",
                ha="center", va="center", color=COLORES["texto_ayuda"], fontsize=10
            )
            ax.axis("off")
        else:
            carreras = []
            totales = []
            for carrera, total in reversed(datos_carreras):
                carreras.append(carrera)
                totales.append(total)

            ax.barh(carreras, totales, color=COLORES["rojo_principal"], height=0.55)
            ax.tick_params(axis="x", colors=COLORES["texto_ayuda"], labelsize=8)
            ax.tick_params(axis="y", colors=COLORES["texto_principal"], labelsize=8)
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)
            ax.spines["left"].set_color(COLORES["gris_linea"])
            ax.spines["bottom"].set_color(COLORES["gris_linea"])
            fig.tight_layout()

        self.fig_carreras = fig
        canvas = FigureCanvasTkAgg(fig, master=self.contenedor_ranking)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def _render_registros(self, registros):
        self._limpiar_frame(self.tabla_frame)

        if not registros:
            tk.Label(
                self.tabla_frame, text="No hay movimientos recientes.",
                bg=COLORES["gris_claro"], fg=COLORES["texto_ayuda"],
                font=FUENTES["texto_normal"]
            ).pack(pady=20)
            return

        for fila, (hora, actividad, estado) in enumerate(registros):
            if estado == "En uso":
                color_estado = ESTADOS["ocupado_texto"]
            else:
                color_estado = ESTADOS["disponible_texto"]

            tk.Label(
                self.tabla_frame, text=hora, bg=COLORES["gris_claro"],
                fg=COLORES["texto_ayuda"], font=FUENTES["texto_ayuda"]
            ).grid(row=fila, column=0, sticky="w", pady=6, padx=(0, 15))

            tk.Label(
                self.tabla_frame, text=actividad, bg=COLORES["gris_claro"],
                fg=COLORES["texto_principal"], font=FUENTES["texto_normal"]
            ).grid(row=fila, column=1, sticky="w", pady=6)

            tk.Label(
                self.tabla_frame, text=estado, bg=COLORES["gris_claro"],
                fg=color_estado, font=FUENTES["texto_ayuda"]
            ).grid(row=fila, column=2, sticky="e", pady=6, padx=(20, 0))

        self.tabla_frame.grid_columnconfigure(1, weight=1)

    def mostrar_notificaciones(self):
        """Abre una ventana modal con préstamos vencidos e incidencias pendientes."""
        alertas = obtener_notificaciones()
        modal = tk.Toplevel(self)
        modal.title("Notificaciones")
        modal.geometry("480x320")
        modal.configure(bg=COLORES["blanco_fondo"])
        modal.transient(self)
        modal.grab_set()

        tk.Label(
            modal, text="Alertas activas", font=FUENTES["subtitulo"],
            bg=COLORES["blanco_fondo"], fg=COLORES["texto_principal"]
        ).pack(anchor="w", padx=15, pady=(15, 10))

        if not alertas:
            tk.Label(
                modal, text="Todo en orden. No hay alertas pendientes.",
                bg=COLORES["blanco_fondo"], fg=COLORES["texto_ayuda"],
                font=FUENTES["texto_normal"]
            ).pack(pady=30)
        else:
            for texto in alertas:
                tk.Label(
                    modal, text=f"• {texto}", bg=COLORES["gris_claro"],
                    fg=COLORES["texto_principal"], font=FUENTES["texto_ayuda"],
                    anchor="w", padx=10, pady=6, wraplength=430, justify="left"
                ).pack(fill="x", padx=15, pady=3)

    def exportar_pdf(self):
        """Abre el diálogo para guardar el reporte histórico en PDF."""
        periodo = self.selector.get()
        nombre_sugerido = f"reporte_dashboard_{periodo.lower().replace(' ', '_')}.pdf"
        ruta = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("Archivo PDF", "*.pdf")],
            initialfile=nombre_sugerido,
            title="Guardar reporte histórico"
        )
        if not ruta:
            return

        try:
            generar_pdf_dashboard(
                ruta, periodo, self.kpis_actuales,
                self.fig_uso, self.fig_carreras, self.registros_actuales,
                self.resumen_actual
            )
            messagebox.showinfo("Reporte generado", f"El PDF se guardó correctamente en:\n{ruta}")
        except Exception as e:
            messagebox.showerror("Error al generar PDF", f"No se pudo crear el archivo:\n{e}")