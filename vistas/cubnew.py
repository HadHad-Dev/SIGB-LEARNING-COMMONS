import tkinter as tk
from tkinter import messagebox, simpledialog
from config import COLORES, FUENTES, ESTADOS
from utils import crear_tarjeta_kpi, crear_tarjeta_base
from database.recursos_cub import (
    obtener_kpis_cubi,
    obtener_cubiculos_detalle,
    registrar_reserva_cubiculo,
    extender_tiempo_cubiculo,
    liberar_cubiculo,
)

def _estilo_seguro(clave_estado):
    """Obtiene (etiqueta, texto, fondo) de ESTADOS evitando KeyError si falta alguna clave."""
    mapa = {
        "disponible": ("Disponible", "disponible_texto", "disponible_fondo", "#166534", "#dcfce7"),
        "en_uso": ("Ocupado", "ocupado_texto", "ocupado_fondo", "#991b1b", "#fee2e2"),
        "mantenimiento": ("Mantenimiento", "llave_texto", "llave_fondo", "#92400e", "#fef3c7"),
        "extraviado": ("Extraviado", "ocupado_texto", "ocupado_fondo", "#991b1b", "#fee2e2"),
    }
    etiqueta, k_txt, k_bg, def_txt, def_bg = mapa.get(
        clave_estado,
        (clave_estado.capitalize(), "disponible_texto", "disponible_fondo", "#166534", "#dcfce7"),
    )
    txt = ESTADOS.get(k_txt, def_txt)
    bg = ESTADOS.get(k_bg, def_bg)
    return etiqueta, txt, bg


class CubiculosView(tk.Frame):
    def __init__(self, parent, usuario_actual=None):
        super().__init__(parent, bg=COLORES["blanco_fondo"])
        self.usuario_actual = usuario_actual or {}
        self.cubiculos_por_codigo = {}
        self.celdas = {}
        self.seleccionado = None

        self.setup_ui()
        self.cargar_datos()

    def setup_ui(self):
        # 1. HEADER
        header = tk.Frame(self, bg=COLORES["blanco_fondo"], pady=10, padx=20)
        header.pack(fill="x")

        tk.Label(
            header,
            text="Gestión de Cubículos",
            font=FUENTES["titulo"],
            fg=COLORES["texto_principal"],
            bg=COLORES["blanco_fondo"],
        ).pack(side="left")

        self.lbl_resumen_header = tk.Label(
            header,
            text="0 de 0 cubículos disponibles ahora",
            font=FUENTES["texto_ayuda"],
            fg=COLORES["texto_ayuda"],
            bg=COLORES["blanco_fondo"],
        )
        self.lbl_resumen_header.pack(side="right")

        btn_refrescar = tk.Button(
            header,
            text="Actualizar",
            bg=COLORES["blanco_fondo"],
            fg=COLORES["texto_principal"],
            font=FUENTES["etiqueta"],
            relief="solid",
            bd=1,
            padx=10,
            pady=4,
            cursor="hand2",
            command=self.cargar_datos,
        )
        btn_refrescar.pack(side="right", padx=(0, 12))

        # 2. TARJETAS KPI
        self.kpi_frame = tk.Frame(self, bg=COLORES["blanco_fondo"], padx=20)
        self.kpi_frame.pack(fill="x", pady=8)

        # 3. CUERPO PRINCIPAL: MAPA (IZQUIERDA) + DETALLES (DERECHA)
        cuerpo = tk.Frame(self, bg=COLORES["blanco_fondo"], padx=20)
        cuerpo.pack(fill="both", expand=True, pady=(10, 20))

        self.construir_mapa(cuerpo)
        self.construir_detalles(cuerpo)

    def construir_mapa(self, parent):
        mapa_card = crear_tarjeta_base(parent)
        mapa_card.pack(side="left", fill="both", expand=True, padx=(0, 10))

        tk.Label(
            mapa_card,
            text="Mapa de cubículos",
            font=FUENTES["subtitulo"],
            bg=COLORES["gris_claro"],
            fg=COLORES["texto_principal"],
            anchor="w",
        ).pack(fill="x", padx=15, pady=(12, 6))

        # Leyenda
        leyenda = tk.Frame(mapa_card, bg=COLORES["gris_claro"])
        leyenda.pack(fill="x", padx=15)
        for clave in ("disponible", "en_uso", "mantenimiento"):
            etiqueta, color, _ = _estilo_seguro(clave)
            tk.Label(
                leyenda,
                text="● " + etiqueta,
                font=FUENTES["etiqueta"],
                bg=COLORES["gris_claro"],
                fg=color,
            ).pack(side="left", padx=(0, 15))

        # Contenedor dinámico para la cuadrícula
        self.grid_mapa_frame = tk.Frame(mapa_card, bg=COLORES["gris_claro"])
        self.grid_mapa_frame.pack(fill="both", expand=True, padx=15, pady=15)

    def construir_detalles(self, parent):
        det_card = crear_tarjeta_base(parent)
        det_card.pack(side="right", fill="both", expand=True, padx=(10, 0))

        tk.Label(
            det_card,
            text="Detalles del cubículo",
            font=FUENTES["subtitulo"],
            bg=COLORES["gris_claro"],
            fg=COLORES["texto_principal"],
            anchor="w",
        ).pack(fill="x", padx=15, pady=(12, 10))

        tabla = tk.Frame(det_card, bg=COLORES["gris_claro"])
        tabla.pack(fill="x", padx=15)
        tabla.grid_columnconfigure(1, weight=1)

        self.det_valores = {}
        campos = ["Cubículo", "Código", "Ubicación", "Capacidad", "Estado", "Usuario", "Inicio", "Fin"]
        for fila, campo in enumerate(campos):
            tk.Label(
                tabla,
                text=campo.upper(),
                bg=COLORES["gris_claro"],
                fg=COLORES["texto_ayuda"],
                font=FUENTES["etiqueta"],
            ).grid(row=fila, column=0, sticky="w", pady=5, padx=(0, 18))

            lbl = tk.Label(
                tabla,
                text="—",
                bg=COLORES["gris_claro"],
                fg=COLORES["texto_principal"],
                font=FUENTES["texto_normal"],
                anchor="w",
            )
            lbl.grid(row=fila, column=1, sticky="w", pady=5)
            self.det_valores[campo] = lbl

        # Botones de acción (listos para conectar handlers luego)
        acciones = tk.Frame(det_card, bg=COLORES["gris_claro"])
        acciones.pack(fill="x", padx=15, pady=15, side="bottom")

        self.btn_reserva = tk.Button(
            acciones,
            text="Registrar reserva manual",
            bg=COLORES["rojo_principal"],
            fg=COLORES["blanco_fondo"],
            font=FUENTES["texto_normal"],
            bd=0,
            padx=15,
            pady=10,
            cursor="hand2",
            activebackground=COLORES["rojo_oscuro"],
            activeforeground=COLORES["blanco_fondo"],
            command=self._accion_registrar_reserva,
        )
        self.btn_reserva.pack(fill="x", pady=5)

        self.btn_extender = tk.Button(
            acciones,
            text="Extender tiempo",
            bg=COLORES["blanco_fondo"],
            fg=COLORES["texto_principal"],
            font=FUENTES["texto_normal"],
            relief="solid",
            bd=1,
            padx=15,
            pady=8,
            cursor="hand2",
            command=self._accion_extender_tiempo,
        )
        self.btn_extender.pack(fill="x", pady=5)

        self.btn_liberar = tk.Button(
            acciones,
            text="Liberar cubículo",
            bg=COLORES["blanco_fondo"],
            fg=COLORES["texto_principal"],
            font=FUENTES["texto_normal"],
            relief="solid",
            bd=1,
            padx=15,
            pady=8,
            cursor="hand2",
            command=self._accion_liberar,
        )
        self.btn_liberar.pack(fill="x", pady=5)

        for texto in ("Extender tiempo", "Liberar cubículo"):
            tk.Button(
                acciones,
                text=texto,
                bg=COLORES["blanco_fondo"],
                fg=COLORES["texto_principal"],
                font=FUENTES["texto_normal"],
                relief="solid",
                bd=1,
                padx=15,
                pady=8,
                cursor="hand2",
            ).pack(fill="x", pady=5)

    def cargar_datos(self):
        kpis = obtener_kpis_cubi()
        cubiculos = obtener_cubiculos_detalle()

        # Actualizar header
        self.lbl_resumen_header.config(
            text=f"{kpis['disponibles']} de {kpis['total']} cubículos disponibles ahora"
        )

        # Actualizar KPIs
        self._limpiar_frame(self.kpi_frame)
        tarjetas = [
            ("TOTAL DE CUBÍCULOS", str(kpis["total"]), "Espacios registrados"),
            ("DISPONIBLES", str(kpis["disponibles"]), "Listos para uso"),
            ("OCUPADOS", str(kpis["ocupados"]), "Actualmente en uso"),
        ]
        for i, (t, v, s) in enumerate(tarjetas):
            crear_tarjeta_kpi(self.kpi_frame, t, v, s).grid(row=0, column=i, padx=5, sticky="ew")
            self.kpi_frame.grid_columnconfigure(i, weight=1)

        # Reconstruir mapa con datos reales
        self._limpiar_frame(self.grid_mapa_frame)
        self.celdas.clear()
        self.cubiculos_por_codigo.clear()

        if not cubiculos:
            tk.Label(
                self.grid_mapa_frame,
                text="No hay cubículos registrados en la base de datos.",
                font=FUENTES["texto_normal"],
                bg=COLORES["gris_claro"],
                fg=COLORES["texto_ayuda"],
            ).pack(expand=True)
            self.seleccionado = None
            return

        cols = 3
        for idx, cub in enumerate(cubiculos):
            codigo = cub["bar_code"]
            self.cubiculos_por_codigo[codigo] = cub

            fila, col = divmod(idx, cols)
            self.grid_mapa_frame.grid_columnconfigure(col, weight=1, uniform="cub")
            self.grid_mapa_frame.grid_rowconfigure(fila, weight=1, uniform="cub")

            _, color, fondo = _estilo_seguro(cub["status"])
            cap_texto = f"{cub['capacity']} personas" if cub.get("capacity") else "Sin capacidad"

            celda = tk.Frame(
                self.grid_mapa_frame,
                bg=fondo,
                cursor="hand2",
                highlightbackground=COLORES["gris_linea"],
                highlightthickness=1,
            )
            celda.grid(row=fila, column=col, sticky="nsew", padx=6, pady=6)

            lbl_titulo = tk.Label(
                celda,
                text=cub["description_title"],
                font=FUENTES["subtitulo"],
                bg=fondo,
                fg=color,
            )
            lbl_titulo.pack(expand=True, pady=(12, 0))

            lbl_cap = tk.Label(
                celda,
                text=cap_texto,
                font=FUENTES["etiqueta"],
                bg=fondo,
                fg=COLORES["texto_ayuda"],
            )
            lbl_cap.pack(expand=True, pady=(0, 12))

            for w in (celda, lbl_titulo, lbl_cap):
                w.bind("<Button-1>", lambda e, c=codigo: self.seleccionar(c))

            self.celdas[codigo] = celda

        # Mantener selección actual si sigue existiendo, o elegir el primero
        objetivo = self.seleccionado if self.seleccionado in self.cubiculos_por_codigo else cubiculos[0]["bar_code"]
        self.seleccionar(objetivo)

    def seleccionar(self, codigo_sel):
        cub = self.cubiculos_por_codigo.get(codigo_sel)
        if not cub:
            return

        self.seleccionado = codigo_sel
        borde_sel = COLORES.get("SELECTED_BORDER", COLORES["rojo_principal"])

        for codigo, celda in self.celdas.items():
            if codigo == codigo_sel:
                celda.config(highlightbackground=borde_sel, highlightthickness=3)
            else:
                celda.config(highlightbackground=COLORES["gris_linea"], highlightthickness=1)

        etiqueta, color, _ = _estilo_seguro(cub["status"])
        cap_texto = f"{cub['capacity']} personas" if cub.get("capacity") else "—"
        inicio_txt = str(cub["starting_date"]) if cub.get("starting_date") else "—"
        fin_txt = str(cub["due_at"]) if cub.get("due_at") else "—"
        usuario_txt = cub.get("usuario_nombre") or "—"

        self.det_valores["Cubículo"].config(text=cub["description_title"])
        self.det_valores["Código"].config(text=cub["bar_code"])
        self.det_valores["Ubicación"].config(text=cub.get("shelf_location") or "—")
        self.det_valores["Capacidad"].config(text=cap_texto)
        self.det_valores["Estado"].config(text=etiqueta, fg=color)
        self.det_valores["Usuario"].config(text=usuario_txt)
        self.det_valores["Inicio"].config(text=inicio_txt)
        self.det_valores["Fin"].config(text=fin_txt)

    def _limpiar_frame(self, frame):
        for widget in frame.winfo_children():
            widget.destroy()

    def _accion_registrar_reserva(self):
        if not self.seleccionado:
            messagebox.showwarning("Sin selección", "Selecciona un cubículo primero.")
            return

        cub = self.cubiculos_por_codigo.get(self.seleccionado)
        if not cub or cub["status"] != "disponible":
            messagebox.showwarning("No disponible", "Solo puedes registrar reserva en cubículos disponibles.")
            return

        raw_user = simpledialog.askstring(
            "Registrar reserva",
            f"Ingresa el ID / matrícula del usuario para {cub['description_title']}:",
            parent=self,
        )
        if raw_user is None:
            return
        raw_user = raw_user.strip()
        if not raw_user.isdigit():
            messagebox.showwarning("Dato inválido", "El ID de usuario debe ser numérico.")
            return

        cap_max = cub.get("capacity") or 6
        raw_asist = simpledialog.askinteger(
            "Asistentes",
            f"Número de asistentes (capacidad máx.: {cap_max}):",
            minvalue=1,
            maxvalue=int(cap_max),
            initialvalue=1,
            parent=self,
        )
        if raw_asist is None:
            return

        ok, msg = registrar_reserva_cubiculo(self.seleccionado, int(raw_user), int(raw_asist))
        if ok:
            messagebox.showinfo("Reserva registrada", msg)
            self.cargar_datos()
        else:
            messagebox.showerror("Error", msg)

    def _accion_extender_tiempo(self):
        if not self.seleccionado:
            messagebox.showwarning("Sin selección", "Selecciona un cubículo primero.")
            return

        cub = self.cubiculos_por_codigo.get(self.seleccionado)
        if not cub or cub["status"] != "en_uso":
            messagebox.showwarning("Sin uso activo", "El cubículo seleccionado no está en uso.")
            return

        minutos = simpledialog.askinteger(
            "Extender tiempo",
            f"¿Cuántos minutos deseas agregar a {cub['description_title']}?",
            minvalue=15,
            maxvalue=240,
            initialvalue=30,
            parent=self,
        )
        if minutos is None:
            return

        ok, msg = extender_tiempo_cubiculo(self.seleccionado, int(minutos))
        if ok:
            messagebox.showinfo("Tiempo extendido", msg)
            self.cargar_datos()
        else:
            messagebox.showerror("Error", msg)

    def _accion_liberar(self):
        if not self.seleccionado:
            messagebox.showwarning("Sin selección", "Selecciona un cubículo primero.")
            return

        cub = self.cubiculos_por_codigo.get(self.seleccionado)
        if not cub:
            return

        if cub["status"] == "disponible":
            messagebox.showinfo("Ya disponible", "Este cubículo ya está disponible.")
            return

        confirmar = messagebox.askyesno(
            "Liberar cubículo",
            f"¿Deseas liberar {cub['description_title']} ({cub['bar_code']}) y registrar su cierre en el historial?",
            parent=self,
        )
        if not confirmar:
            return

        closed_by = self.usuario_actual.get("user_id")
        ok, msg = liberar_cubiculo(self.seleccionado, closed_by_user_id=closed_by)
        if ok:
            messagebox.showinfo("Cubículo liberado", msg)
            self.cargar_datos()
        else:
            messagebox.showerror("Error", msg)