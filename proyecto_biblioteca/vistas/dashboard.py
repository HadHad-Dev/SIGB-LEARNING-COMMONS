# vistas/dashboard.py
import tkinter as tk
from config import COLORES
from utils import crear_tarjeta_kpi

class DashboardView(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=COLORES["gris_tenue"])
        self.setup_ui()
        
    def setup_ui(self):
        # Header
        header = tk.Frame(self, bg=COLORES["gris_tenue"], pady=10, padx=20)
        header.pack(fill="x")
        tk.Label(header, text="Dashboard general", font=("Arial", 18, "bold"), bg=COLORES["gris_tenue"]).pack(side="left")

        # Contenedor KPIs
        kpi_frame = tk.Frame(self, bg=COLORES["gris_tenue"], padx=20)
        kpi_frame.pack(fill="x", pady=10)
        
        kpis = [
            ("Objetos perdidos", "48", "36 entregados · 12 pendientes"),
            ("Reservas de cubículos", "186", "Últimos 7 días"),
            ("Horas de uso", "372 h", "Acumuladas en el periodo"),
            ("Estudiantes por cubículo", "3.2", "Promedio · capacidad de 4")
        ]
        
        for i, (t, v, s) in enumerate(kpis):
            crear_tarjeta_kpi(kpi_frame, t, v, s).grid(row=0, column=i, padx=5, sticky="ew")
            kpi_frame.grid_columnconfigure(i, weight=1)

        # Gráficas
        charts_frame = tk.Frame(self, bg=COLORES["gris_tenue"], padx=20)
        charts_frame.pack(fill="both", expand=True, pady=10)

        bar_chart = tk.Frame(charts_frame, bg=COLORES["gris_tenue"], relief="solid", bd=1)
        bar_chart.pack(side="left", fill="both", expand=True, padx=(0, 5))
        tk.Label(bar_chart, text="[Gráfica de Barras]", bg=COLORES["gris_tenue"], fg=COLORES["texto_principal"]).pack(expand=True)

        pie_chart = tk.Frame(charts_frame, bg=COLORES["gris_tenue"], width=300, relief="solid", bd=1)
        pie_chart.pack(side="right", fill="y", padx=(5, 0))
        pie_chart.pack_propagate(False)
        tk.Label(pie_chart, text="[Gráfica Circular]", bg=COLORES["gris_tenue"], fg=COLORES["texto_principal"]).pack(expand=True)