# vistas/objetos.py
import tkinter as tk
from tkinter import ttk
from config import COLORES, FUENTES, ESTADOS
from utils import crear_tarjeta_kpi, crear_tarjeta_base

class ObjetosView(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=COLORES["blanco_fondo"])
        
        self.datos_objetos = [
            {"id": 1, "titulo": "Mochila negra", "estado": "En custodia", "ubicacion": "Learning commons - Planta baja", "fecha": "3 nov 2026 - 09:15", "reporto": "Mariana López", "img_src": "/ruta/img/mochila.jpg"},
            {"id": 2, "titulo": "Audífonos inalámbricos", "estado": "Entregado", "ubicacion": "Edificio B - Piso 1", "fecha": "2 nov 2026 - 16:40", "reporto": "Carlos Méndez", "img_src": "/ruta/img/audifonos.jpg"},
            {"id": 3, "titulo": "Botella térmica", "estado": "En custodia", "ubicacion": "Learning commons - Piso 2", "fecha": "2 nov 2026 - 14:20", "reporto": "Sofía Hernández", "img_src": "/ruta/img/botella.jpg"},
            {"id": 4, "titulo": "Calculadora científica", "estado": "En custodia", "ubicacion": "Edificio c - Estudio para diseño", "fecha": "1 nov 2026 - 12:10", "reporto": "Andrés García", "img_src": "/ruta/img/calculadora.jpg"},
            {"id": 5, "titulo": "Cuaderno de apuntes", "estado": "Entregado", "ubicacion": "Edificio D - Recepcion", "fecha": "31 oct 2026 - 18:05", "reporto": "Elena Martínez", "img_src": "/ruta/img/cuaderno.jpg"},
            {"id": 6, "titulo": "Lentes de armazón", "estado": "Entregado", "ubicacion": "Cafeteria", "fecha": "30 oct 2026 - 10:35", "reporto": "Pablo Sánchez", "img_src": "/ruta/img/lentes.jpg"},
            {"id": 7, "titulo": "Llaves de auto", "estado": "En custodia", "ubicacion": "Estacionamiento segunda fila primer seccion", "fecha": "3 nov 2026 - 08:00", "reporto": "Guardia Turno 1", "img_src": "/ruta/img/llaves.jpg"},
            {"id": 8, "titulo": "Sudadera gris", "estado": "Entregado", "ubicacion": "Salida al oxxo", "fecha": "2 nov 2026 - 13:15", "reporto": "Luis Torres", "img_src": "/ruta/img/sudadera.jpg"},
            {"id": 9, "titulo": "Mouse inalámbrico", "estado": "En custodia", "ubicacion": "Edificio D - Laboratorio con impresoras 3D", "fecha": "1 nov 2026 - 11:45", "reporto": "Ana Ruíz", "img_src": "/ruta/img/mouse.jpg"},
            {"id": 10, "titulo": "Termo Yeti", "estado": "En custodia", "ubicacion": "Edificio Vinculacion - Servicios de internalizacion", "fecha": "31 oct 2026 - 19:20", "reporto": "José López", "img_src": "/ruta/img/termo2.jpg"},
            {"id": 11, "titulo": "Memoria USB 64GB", "estado": "Entregado", "ubicacion": "Paraescolares", "fecha": "30 oct 2026 - 09:30", "reporto": "Mónica Silva", "img_src": "/ruta/img/usb.jpg"},
            {"id": 12, "titulo": "Cargador tipo C", "estado": "En custodia", "ubicacion": "Learning commons - cubiculo Africa", "fecha": "29 oct 2026 - 15:10", "reporto": "Daniel Castro", "img_src": "/ruta/img/cargador.jpg"}
        ]
        self.setup()

    def setup(self):

        header = tk.Frame(self, bg=COLORES["blanco_fondo"], pady=10, padx=20)
        header.pack(fill="x")
        
        tk.Label(header, text="Objetos perdidos", font=FUENTES["titulo"], 
                 fg=COLORES["texto_principal"], bg=COLORES["blanco_fondo"]).pack(side="left")
        
        tk.Label(header, text="Registra hallazgos y ayuda a cada objeto a volver con su dueño.", 
                 font=FUENTES["texto_ayuda"], fg=COLORES["texto_ayuda"], bg=COLORES["blanco_fondo"]).pack(side="left", padx=15)

        # Boton para registrar pendiente funcionalidad
        btn_registrar = tk.Button(header, text="Registrar objeto", bg=COLORES["rojo_principal"], 
                                  fg=COLORES["blanco_fondo"], font=FUENTES["texto_normal"], 
                                  bd=0, padx=20, pady=8, cursor="hand2")
        btn_registrar.pack(side="right")

        # Contenedor de data
        kpi_frame = tk.Frame(self, bg=COLORES["blanco_fondo"], padx=20)
        kpi_frame.pack(fill="x", pady=10)
        
        kpis = [
            ("Objetos registrados", "48", ""),
            ("En custodia", "12", ""),
            ("Entregados", "36", "")
        ]
        for i, (t, v, s) in enumerate(kpis):
            crear_tarjeta_kpi(kpi_frame, t, v, s).grid(row=0, column=i, padx=5, sticky="ew")
            kpi_frame.grid_columnconfigure(i, weight=1)

        search_frame = tk.Frame(self, bg=COLORES["blanco_fondo"], padx=25)
        search_frame.pack(fill="x", pady=5)
        
    # Barra de busqueda aun sin funcionalidad

        search_container = tk.Frame(search_frame, bg=COLORES["blanco_fondo"], 
                                    highlightbackground=COLORES["gris_linea"], highlightthickness=1, padx=5, pady=5)
        search_container.pack(side="left", fill="x", expand=True)
        
        tk.Label(search_container, bg=COLORES["blanco_fondo"], fg=COLORES["texto_ayuda"]).pack(side="left")
        entry_busqueda = tk.Entry(search_container, bg=COLORES["blanco_fondo"], bd=0, font=FUENTES["texto_normal"], width=50)
        entry_busqueda.insert(0, "Buscar por objeto, lugar o persona...")
        entry_busqueda.pack(side="left", fill="x", expand=True, padx=5)

       #No se puede hacer scroll por defaul en tkinter pipipi

        scroll_container = tk.Frame(self, bg=COLORES["blanco_fondo"], padx=20)
        scroll_container.pack(fill="both", expand=True, pady=15)
        #verificar porque algunas "variables" como esta no estan declaradas con self
        canvas = tk.Canvas(scroll_container, bg=COLORES["blanco_fondo"])
        scrollbar = ttk.Scrollbar(scroll_container, orient="vertical", command=canvas.yview)
        #verificar que es ttk
        self.grid_frame = tk.Frame(canvas, bg=COLORES["blanco_fondo"])

        #Checar funcionamiento de todo esto todo el frame de scroll
        # Actualizar la región de scroll cada vez que el grid cambie de tamaño
        self.grid_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.grid_frame, anchor="nw", width=canvas.winfo_width())
        # Ajustar el ancho interno cuando cambie el tamaño del canvas
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(canvas.find_withtag("all")[0], width=e.width))

        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.construir_cuadricula()

    def construir_cuadricula(self):
        #Checar porque maneja una lista de diccionarios en lugar de una  matriz 
        # checar que es enumerate
        for i, obj in enumerate(self.datos_objetos):
            row = i // 3
            col = i % 3
            #Operaacio necesaria para acomodar los elementos segun cantidad , verificarla para que la expliqeu 
            
            card = crear_tarjeta_base(self.grid_frame, pad_x=10, pad_y=10)
            card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            self.grid_frame.grid_columnconfigure(col, weight=1)
            
            img_placeholder = tk.Frame(card, bg="#D0D0D0", height=120)
            img_placeholder.pack(fill="x", pady=(0, 10))
            tk.Label(img_placeholder, text=f"[IMAGEN]\n{obj['img_src']}", bg="#D0D0D0", 
                     fg=COLORES["texto_ayuda"], font=FUENTES["etiqueta"]).pack(expand=True)
            
            header_card = tk.Frame(card, bg=COLORES["gris_claro"])
            header_card.pack(fill="x")
            
            tk.Label(header_card, text=obj["titulo"], font=FUENTES["texto_normal"], 
                     bg=COLORES["gris_claro"], fg=COLORES["texto_principal"], anchor="w").pack(side="left")
            
            # Asignar color según estado
            if obj["estado"] == "En custodia":
                color_estado = ESTADOS["llave_texto"]
            
            else:
                ESTADOS["disponible_texto"]
            tk.Label(header_card, text=obj["estado"], font=FUENTES["etiqueta"], 
                     bg=COLORES["gris_claro"], fg=color_estado).pack(side="right")
            
            # Detalles del objeto
            tk.Label(card, text=f"{obj['ubicacion']}", font=FUENTES["texto_ayuda"], 
                     bg=COLORES["gris_claro"], fg=COLORES["texto_ayuda"], anchor="w").pack(fill="x", pady=(5,0))
            tk.Label(card, text=f" {obj['fecha']}", font=FUENTES["texto_ayuda"], 
                     bg=COLORES["gris_claro"], fg=COLORES["texto_ayuda"], anchor="w").pack(fill="x")
            
            # Separador
            tk.Frame(card, bg=COLORES["gris_linea"], height=1).pack(fill="x", pady=8)
            tk.Label(card, text=f"👤 Reportó: {obj['reporto']}", font=FUENTES["texto_ayuda"], 
                     bg=COLORES["gris_claro"], fg=COLORES["texto_ayuda"], anchor="w").pack(fill="x")

            # HACER LA TARJETA CLICKEABLE:
            # Vinculamos el evento clic izquierdo ("<Button-1>") de la tarjeta y todos sus hijos al modal
            self.hacer_clickeable(card, obj)

    #buscar en que se hace la recursividad ,que expliqeu su funcionamiento
    def hacer_clickeable(self, widget, datos_objeto):
        widget.bind("<Button-1>", lambda e, data=datos_objeto: self.abrirventana(data))
        # que expliqe desde porque ees recursviva , que son los <> , los datos que tipo de variable son al igual que el widget
        widget.configure(cursor="hand2") 
        for child in widget.winfo_children():
            self.hacer_clickeable(child, datos_objeto)

    def abrirventana(self, obj):
        modal = tk.Toplevel(self)
        modal.title(f"Detalles - {obj['titulo']}")
        modal.geometry("500x500")
        modal.configure(bg=COLORES["blanco_fondo"])
        #Elimina interaccion con la pantalla mientras esta abierta la de info
        #investigar su funcionamiento 
        modal.transient(self.winfo_toplevel())
        modal.grab_set() 

        # Contenido
        tk.Label(modal, text=obj["titulo"], font=FUENTES["titulo"], 
                 bg=COLORES["blanco_fondo"], fg=COLORES["texto_principal"]).pack(pady=(20, 5))
        #investigar porque si bien se esta utilizando un diccioanrio, para acceder al emento se una comilla individual
        tk.Label(modal, text=f"Estado actual: {obj['estado']}", font=FUENTES["subtitulo"], 
                 bg=COLORES["blanco_fondo"], fg=COLORES["texto_ayuda"]).pack(pady=5)
                 
        datos_frame = tk.Frame(modal, bg=COLORES["gris_claro"], padx=20, pady=20, 
                               highlightbackground=COLORES["gris_linea"], highlightthickness=1)
        datos_frame.pack(fill="x", padx=30, pady=15)
        
        tk.Label(datos_frame, text=f" Ubicación original:\n{obj['ubicacion']}", font=FUENTES["texto_normal"], 
                 bg=COLORES["gris_claro"], fg=COLORES["texto_principal"], justify="left").pack(anchor="w", pady=5)
                 
        tk.Label(datos_frame, text=f"📅 Fecha y hora de registro:\n{obj['fecha']}", font=FUENTES["texto_normal"], 
                 bg=COLORES["gris_claro"], fg=COLORES["texto_principal"], justify="left").pack(anchor="w", pady=5)

        # Botones de acción
        tk.Label(modal, text="Cambiar estado del objeto:", font=FUENTES["etiqueta"], 
                 bg=COLORES["blanco_fondo"], fg=COLORES["texto_ayuda"]).pack(pady=(10,0))
                 
        botones_frame = tk.Frame(modal, bg=COLORES["blanco_fondo"])
        botones_frame.pack(pady=10)

        #Entregado
        tk.Button(botones_frame, text="Marcar como Entregado", bg=ESTADOS["disponible_texto"], 
                  fg=COLORES["blanco_fondo"], font=FUENTES["texto_normal"], bd=0, padx=10, pady=8).pack(side="left", padx=5)
        
        #Custodia
        tk.Button(botones_frame, text="Mantener En custodia", bg=ESTADOS["llave_texto"], 
                  fg=COLORES["blanco_fondo"], font=FUENTES["texto_normal"], bd=0, padx=10, pady=8).pack(side="left", padx=5)

        tk.Button(modal, text="Cerrar ventana", bg=COLORES["blanco_fondo"], fg=COLORES["texto_principal"], 
                  font=FUENTES["texto_normal"], bd=0, command=modal.destroy).pack(pady=10)