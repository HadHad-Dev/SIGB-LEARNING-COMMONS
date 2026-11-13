# vistas/dashboard.py
import tkinter as tk
from tkinter import ttk
from config import COLORES, FUENTES, ESTADOS
from utils import crear_tarjeta_kpi, crear_tarjeta_base

class DashboardView(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=COLORES["blanco_fondo"])
        self.setup_ui()

    def setup_ui(self):
        header = tk.Frame(self, bg=COLORES["blanco_fondo"], pady=10, padx=20)
        header.pack(fill="x")
        
        tk.Label(header, text="Dashboard general", font=FUENTES["titulo"], 
                 fg=COLORES["texto_principal"], bg=COLORES["blanco_fondo"]).pack(side="left")

        header_right = tk.Frame(header, bg=COLORES["blanco_fondo"])
        header_right.pack(side="right")

        opciones_fecha = ["Semana actual", "Cuatrimestre actual", "Cuatrimestre anterior"]
        selector = ttk.Combobox(header_right, values=opciones_fecha, state="readonly", width=20)
        selector.current(0) # Selecciona la primera opción por defecto
        #veririfcar que son los states de una combobox
        selector.pack(side="left", padx=10)

        btn_notificaciones = tk.Button(header_right, text="🔔", font=("Arial", 14), bd=0, 
                                       bg=COLORES["blanco_fondo"], cursor="hand1")
        btn_notificaciones.pack(side="left", padx=5)


        kpi_frame = tk.Frame(self, bg=COLORES["blanco_fondo"], padx=20)
        kpi_frame.pack(fill="x", pady=10)
        
        kpis = [
            ("RESERVAS DE CUBÍCULOS", "186", "En el periodo"),
            ("HORAS DE USO", "231 h", "Acumuladas en el periodo"),
            ("ESTUDIANTES POR CUBÍCULO", "3.2", "Promedio · capacidad de 6")
        ]
        for i, (t, v, s) in enumerate(kpis):
            crear_tarjeta_kpi(kpi_frame, t, v, s).grid(row=0, column=i, padx=5, sticky="ew")
            kpi_frame.grid_columnconfigure(i, weight=1)


        charts_frame = tk.Frame(self, bg=COLORES["blanco_fondo"], padx=20)
        charts_frame.pack(fill="x", pady=(10, 0))

        bar_chart = crear_tarjeta_base(charts_frame)
        bar_chart.pack(fill="x", expand=True)
        
        tk.Label(bar_chart, text="Uso de cubículos (Horas reservadas por día)", font=FUENTES["texto_ayuda"], 
                 bg=COLORES["gris_claro"], fg=COLORES["texto_ayuda"], anchor="w").pack(fill="x", padx=10, pady=5)

        canvas_main = tk.Canvas(bar_chart, bg=COLORES["gris_claro"], height=180, highlightthickness=0)
        canvas_main.pack(fill="x", padx=10, pady=10)
        
        #Datos simuldos de altura , pendiente integrar libreria que haga las graficas con los datos obtenidos de la conexion ala base de datos 
        datos_uso = [("28 oct", 80), ("29 oct", 100), ("30 oct", 120), 
                     ("31 oct", 90), ("1 nov", 140), ("2 nov", 70), ("3 nov", 50)]
        
        x = 50
        for dia, altura in datos_uso:
            # Verificar necesidad de los 4 numeros
            canvas_main.create_rectangle(x, 150 - altura, x + 30, 150, 
                                         fill=COLORES["rojo_principal"], outline="")
            canvas_main.create_text(x + 15, 165, text=dia, fill=COLORES["texto_ayuda"], font=FUENTES["etiqueta"])
            x += 80

        btn_frame = tk.Frame(self, bg=COLORES["blanco_fondo"], padx=20)
        btn_frame.pack(fill="x", pady=5)
        
        btn_historico = tk.Button(btn_frame, text="Generar histórico", bg=COLORES["blanco_fondo"], 
                                  fg=COLORES["texto_principal"], font=FUENTES["texto_normal"], 
                                  relief="solid", bd=1, padx=15, pady=5, cursor="hand2")
        # Lo alineamos a la derecha bajo la gráfica
        btn_historico.pack(side="right")
        #Verificar porque usar la propiedas side en lugar de otras ejemplo sticky en caso de aplicar

        # Inferior a la grafica
        bottom_frame = tk.Frame(self, bg=COLORES["blanco_fondo"], padx=20)
        bottom_frame.pack(fill="both", expand=True, pady=(10, 20))
        #Ranking por carrera  
              
        ranking_card = crear_tarjeta_base(bottom_frame)
        ranking_card.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        tk.Label(ranking_card, text="Ranking por carrera", font=FUENTES["subtitulo"], 
                 bg=COLORES["gris_claro"], fg=COLORES["texto_principal"], anchor="w").pack(fill="x", padx=15, pady=10)

        canvas_ranking = tk.Canvas(ranking_card, bg=COLORES["gris_claro"], height=150, highlightthickness=0)
        canvas_ranking.pack(fill="both", expand=True, padx=15)

        datos_carreras = [("TICS", 180), ("Mercadotecnia", 120), ("Mecatrónica", 90)]
        y = 20

        for carrera, ancho in datos_carreras:
            canvas_ranking.create_text(0, y, text=carrera, fill=COLORES["texto_principal"], font=FUENTES["etiqueta"], anchor="w")
            # Dibuja la barra horizontal rosa claro
            canvas_ranking.create_rectangle(120, y - 8, 120 + ancho, y + 8, 
                                            fill=COLORES["rosa_claro"], outline="")
            # Dibuja la línea indicadora roja encima
            canvas_ranking.create_rectangle(120, y - 8, 120 + (ancho*0.8), y + 8, 
                                            fill=COLORES["rojo_principal"], outline="")
            y += 40

        # --- Tarjeta Derecha: Registro reciente (Lista tabular) ---
        registro_card = crear_tarjeta_base(bottom_frame)
        registro_card.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        tk.Label(registro_card, text="Registro reciente", font=FUENTES["subtitulo"], 
                 bg=COLORES["gris_claro"], fg=COLORES["texto_principal"], anchor="w").pack(fill="x", padx=15, pady=10)

        registros = [
            ("10:42", "Reserva C02 · Ana López", "Confirmada", ESTADOS["disponible_texto"]),
            ("10:18", "Audífonos · Diego Ruiz", "Entregado", ESTADOS["disponible_texto"]),
            ("09:56", "Reserva C06 · Sofía Pérez", "En uso", ESTADOS["ocupado_texto"])
        ]

        #grid interno para los datos tipo tabla 
        tabla_frame = tk.Frame(registro_card, bg=COLORES["gris_claro"])
        tabla_frame.pack(fill="both", expand=True, padx=15)

        for fila, (hora, actividad, estado, color_estado) in enumerate(registros):
            tk.Label(tabla_frame, text=hora, bg=COLORES["gris_claro"], fg=COLORES["texto_ayuda"], 
                     font=FUENTES["texto_ayuda"]).grid(row=fila, column=0, sticky="w", pady=10, padx=(0, 20))
                     
            tk.Label(tabla_frame, text=actividad, bg=COLORES["gris_claro"], fg=COLORES["texto_principal"], 
                     font=FUENTES["texto_normal"]).grid(row=fila, column=1, sticky="w", pady=10)
                     
            tk.Label(tabla_frame, text=estado, bg=COLORES["gris_claro"], fg=color_estado, 
                     font=FUENTES["texto_ayuda"]).grid(row=fila, column=2, sticky="e", pady=10, padx=(40, 0))
            
            #Verificar para que son los datos dentro del grid configure , de weight y el 1 solo
            tabla_frame.grid_columnconfigure(1, weight=1)