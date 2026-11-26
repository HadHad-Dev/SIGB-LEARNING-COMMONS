import tkinter as tk
from tkinter import ttk, messagebox

from config import COLORES, FUENTES, ESTADOS
from utils import crear_tarjeta_kpi, crear_tarjeta_base
from database.objetos_db import (
    obtener_kpis_objetos,
    obtener_objetos,
    registrar_objeto,
    marcar_objeto_entregado,
    regresar_objeto_custodia,
)

class ObjetosView(tk.Frame):
    PLACEHOLDER = "Buscar por objeto, lugar o persona..."

    def __init__(self, parent, admin_id=1001):
        super().__init__(parent, bg=COLORES["blanco_fondo"])
        self.admin_id = admin_id
        self.datos_objetos = []

        self.setup()
        self.cargar_datos()

    def setup(self):
        header = tk.Frame(self, bg=COLORES["blanco_fondo"], pady=10, padx=20)
        header.pack(fill="x")

        tk.Label(
            header, text="Objetos perdidos", font=FUENTES["titulo"],
            fg=COLORES["texto_principal"], bg=COLORES["blanco_fondo"]
        ).pack(side="left")

        tk.Label(
            header, text="Registra hallazgos y ayuda a cada objeto a volver con su dueño.",
            font=FUENTES["texto_ayuda"], fg=COLORES["texto_ayuda"], bg=COLORES["blanco_fondo"]
        ).pack(side="left", padx=15)

        btn_registrar = tk.Button(
            header, text="Registrar objeto", bg=COLORES["rojo_principal"],
            fg=COLORES["blanco_fondo"], font=FUENTES["texto_normal"],
            bd=0, padx=20, pady=8, cursor="hand2",
            command=self.abrir_modal_registro
        )
        btn_registrar.pack(side="right")

        self.kpi_frame = tk.Frame(self, bg=COLORES["blanco_fondo"], padx=20)
        self.kpi_frame.pack(fill="x", pady=10)

        search_frame = tk.Frame(self, bg=COLORES["blanco_fondo"], padx=25)
        search_frame.pack(fill="x", pady=5)

        search_container = tk.Frame(
            search_frame, bg=COLORES["blanco_fondo"],
            highlightbackground=COLORES["gris_linea"], highlightthickness=1, padx=8, pady=6
        )
        search_container.pack(side="left", fill="x", expand=True)

        self.entry_busqueda = tk.Entry(
            search_container, bg=COLORES["blanco_fondo"],
            fg=COLORES["texto_ayuda"], bd=0, font=FUENTES["texto_normal"]
        )
        self.entry_busqueda.insert(0, self.PLACEHOLDER)
        self.entry_busqueda.pack(side="left", fill="x", expand=True, padx=5)

        self.entry_busqueda.bind("<FocusIn>", self._quitar_placeholder)
        self.entry_busqueda.bind("<FocusOut>", self._poner_placeholder)
        self.entry_busqueda.bind("<KeyRelease>", self._filtrar_objetos)

        scroll_container = tk.Frame(self, bg=COLORES["blanco_fondo"], padx=20)
        scroll_container.pack(fill="both", expand=True, pady=15)

        self.canvas = tk.Canvas(scroll_container, bg=COLORES["blanco_fondo"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(scroll_container, orient="vertical", command=self.canvas.yview)
        self.grid_frame = tk.Frame(self.canvas, bg=COLORES["blanco_fondo"])

        self.grid_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas_window = self.canvas.create_window((0, 0), window=self.grid_frame, anchor="nw")
        self.canvas.bind(
            "<Configure>",
            lambda e: self.canvas.itemconfig(self.canvas_window, width=e.width)
        )
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.bind("<Enter>", lambda e: self.canvas.bind_all("<MouseWheel>", self._scroll_mouse))
        self.canvas.bind("<Leave>", lambda e: self.canvas.unbind_all("<MouseWheel>"))

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _scroll_mouse(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _quitar_placeholder(self, event):
        if self.entry_busqueda.get() == self.PLACEHOLDER:
            self.entry_busqueda.delete(0, tk.END)
            self.entry_busqueda.config(fg=COLORES["texto_principal"])

    def _poner_placeholder(self, event):
        if not self.entry_busqueda.get().strip():
            self.entry_busqueda.insert(0, self.PLACEHOLDER)
            self.entry_busqueda.config(fg=COLORES["texto_ayuda"])

    def _filtrar_objetos(self, event=None):
        texto = self.entry_busqueda.get()
        if texto == self.PLACEHOLDER:
            texto = ""
        self.datos_objetos = obtener_objetos(filtro=texto)
        self.construir_cuadricula()


    def cargar_datos(self):
        self._render_kpis()
        self._filtrar_objetos()

    def _limpiar_frame(self, frame):
        for widget in frame.winfo_children():
            widget.destroy()

    def _render_kpis(self):
        self._limpiar_frame(self.kpi_frame)
        kpis = obtener_kpis_objetos()
        tarjetas = [
            ("OBJETOS REGISTRADOS", str(kpis["total"]), "Total histórico"),
            ("EN CUSTODIA", str(kpis["en_custodia"]), "Esperando a su dueño"),
            ("ENTREGADOS", str(kpis["entregados"]), "Devueltos correctamente"),
        ]
        for i, (t, v, s) in enumerate(tarjetas):
            crear_tarjeta_kpi(self.kpi_frame, t, v, s).grid(row=0, column=i, padx=5, sticky="ew")
            self.kpi_frame.grid_columnconfigure(i, weight=1)

    def construir_cuadricula(self):
        self._limpiar_frame(self.grid_frame)

        if not self.datos_objetos:
            tk.Label(
                self.grid_frame, text="No se encontraron objetos registrados.",
                font=FUENTES["texto_normal"], bg=COLORES["blanco_fondo"],
                fg=COLORES["texto_ayuda"]
            ).pack(pady=40)
            return

        for col in range(3):
            self.grid_frame.grid_columnconfigure(col, weight=1, uniform="col_obj")

        for i, obj in enumerate(self.datos_objetos):
            row = i // 3
            col = i % 3

            card = crear_tarjeta_base(self.grid_frame, pad_x=12, pad_y=12)
            card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

            # Cabecera de tarjeta: Título + Estado
            header_card = tk.Frame(card, bg=COLORES["gris_claro"])
            header_card.pack(fill="x")

            tk.Label(
                header_card, text=obj["title"], font=FUENTES["subtitulo"],
                bg=COLORES["gris_claro"], fg=COLORES["texto_principal"],
                anchor="w", wraplength=180, justify="left"
            ).pack(side="left", fill="x", expand=True)

            if obj["status"] == "en_custodia":
                texto_estado = "En custodia"
                color_estado = ESTADOS["llave_texto"]
            else:
                texto_estado = "Entregado"
                color_estado = ESTADOS["disponible_texto"]

            tk.Label(
                header_card, text=texto_estado, font=FUENTES["etiqueta"],
                bg=COLORES["gris_claro"], fg=color_estado
            ).pack(side="right", anchor="n")

            # Descripción breve
            desc_corta = obj["description"]
            if len(desc_corta) > 95:
                desc_corta = desc_corta[:92] + "..."

            tk.Label(
                card, text=desc_corta, font=FUENTES["texto_normal"],
                bg=COLORES["gris_claro"], fg=COLORES["texto_principal"],
                anchor="w", justify="left", wraplength=250
            ).pack(fill="x", pady=(8, 6))

            # Ubicación y fecha
            ubicacion = obj["found_location"] or "Sin ubicación"
            fecha_txt = obj["found_date"].strftime("%d/%m/%Y - %H:%M")

            tk.Label(
                card, text=f"Lugar: {ubicacion}", font=FUENTES["texto_ayuda"],
                bg=COLORES["gris_claro"], fg=COLORES["texto_ayuda"], anchor="w"
            ).pack(fill="x")

            tk.Label(
                card, text=f"Fecha: {fecha_txt}", font=FUENTES["texto_ayuda"],
                bg=COLORES["gris_claro"], fg=COLORES["texto_ayuda"], anchor="w"
            ).pack(fill="x")

            # Separador y reportante
            tk.Frame(card, bg=COLORES["gris_linea"], height=1).pack(fill="x", pady=8)
            tk.Label(
                card, text=f"Reportó: {obj['reporto']}", font=FUENTES["texto_ayuda"],
                bg=COLORES["gris_claro"], fg=COLORES["texto_ayuda"], anchor="w"
            ).pack(fill="x")

            self.hacer_clickeable(card, obj)

    def hacer_clickeable(self, widget, datos_objeto):
        widget.bind("<Button-1>", lambda e, data=datos_objeto: self.abrir_ventana_detalle(data))
        widget.configure(cursor="hand2")
        for child in widget.winfo_children():
            self.hacer_clickeable(child, datos_objeto)

    # ========================================================================
    # MODAL: REGISTRAR NUEVO OBJETO
    # ========================================================================

    def abrir_modal_registro(self):
        modal = tk.Toplevel(self)
        modal.title("Registrar objeto perdido")
        modal.geometry("450x430")
        modal.configure(bg=COLORES["blanco_fondo"])
        modal.transient(self.winfo_toplevel())
        modal.grab_set()

        frame = tk.Frame(modal, bg=COLORES["blanco_fondo"], padx=20, pady=15)
        frame.pack(fill="both", expand=True)

        tk.Label(
            frame, text="Nuevo objeto encontrado", font=FUENTES["subtitulo"],
            bg=COLORES["blanco_fondo"], fg=COLORES["texto_principal"]
        ).pack(anchor="w", pady=(0, 12))

        tk.Label(frame, text="Nombre del objeto *", bg=COLORES["blanco_fondo"], font=FUENTES["etiqueta"]).pack(anchor="w")
        entry_titulo = tk.Entry(frame, font=FUENTES["texto_normal"])
        entry_titulo.pack(fill="x", pady=(2, 10))

        tk.Label(frame, text="Descripción *", bg=COLORES["blanco_fondo"], font=FUENTES["etiqueta"]).pack(anchor="w")
        txt_desc = tk.Text(frame, font=FUENTES["texto_normal"], height=4)
        txt_desc.pack(fill="x", pady=(2, 10))

        tk.Label(frame, text="Ubicación donde se encontró", bg=COLORES["blanco_fondo"], font=FUENTES["etiqueta"]).pack(anchor="w")
        entry_ubicacion = tk.Entry(frame, font=FUENTES["texto_normal"])
        entry_ubicacion.pack(fill="x", pady=(2, 10))

        tk.Label(
            frame, text="Quién lo reportó (ID de usuario o Nombre completo) *",
            bg=COLORES["blanco_fondo"], font=FUENTES["etiqueta"]
        ).pack(anchor="w")
        entry_reporto = tk.Entry(frame, font=FUENTES["texto_normal"])
        entry_reporto.pack(fill="x", pady=(2, 15))

        def guardar():
            titulo = entry_titulo.get().strip()
            desc = txt_desc.get("1.0", tk.END).strip()
            ubicacion = entry_ubicacion.get().strip()
            reporto = entry_reporto.get().strip()

            if not titulo or not desc or not reporto:
                messagebox.showwarning(
                    "Campos obligatorios",
                    "Completa el nombre del objeto, la descripción y quién lo reportó."
                )
                return

            ok, msg = registrar_objeto(titulo, desc, ubicacion, reporto)
            if ok:
                messagebox.showinfo("Éxito", msg)
                modal.destroy()
                self.cargar_datos()
            else:
                messagebox.showerror("Error", msg)

        tk.Button(
            frame, text="Guardar registro", bg=COLORES["rojo_principal"],
            fg=COLORES["blanco_fondo"], font=FUENTES["texto_normal"],
            bd=0, pady=10, cursor="hand2", command=guardar
        ).pack(fill="x")

    # ========================================================================
    # MODAL: DETALLE Y CAMBIO DE ESTADO
    # ========================================================================

    def abrir_ventana_detalle(self, obj):
        modal = tk.Toplevel(self)
        modal.title(f"Detalles - {obj['title']}")
        modal.geometry("500x500")
        modal.configure(bg=COLORES["blanco_fondo"])
        modal.transient(self.winfo_toplevel())
        modal.grab_set()

        estado_legible = "En custodia" if obj["status"] == "en_custodia" else "Entregado"

        tk.Label(
            modal, text=obj["title"], font=FUENTES["titulo"],
            bg=COLORES["blanco_fondo"], fg=COLORES["texto_principal"]
        ).pack(pady=(20, 5))

        tk.Label(
            modal, text=f"Estado actual: {estado_legible}", font=FUENTES["subtitulo"],
            bg=COLORES["blanco_fondo"], fg=COLORES["texto_ayuda"]
        ).pack(pady=2)

        datos_frame = tk.Frame(
            modal, bg=COLORES["gris_claro"], padx=20, pady=15,
            highlightbackground=COLORES["gris_linea"], highlightthickness=1
        )
        datos_frame.pack(fill="x", padx=30, pady=12)

        fecha_txt = obj["found_date"].strftime("%d/%m/%Y - %H:%M")
        ubicacion = obj["found_location"] or "Sin ubicación"

        info = [
            f"Descripción:\n{obj['description']}",
            f"Ubicación de hallazgo: {ubicacion}",
            f"Fecha de registro: {fecha_txt}",
            f"Reportó: {obj['reporto']}",
        ]
        if obj["status"] == "entregado":
            fecha_ent = obj["delivered_at"].strftime("%d/%m/%Y - %H:%M") if obj["delivered_at"] else "-"
            info.append(f"Entregado a: {obj['entregado_a']} ({fecha_ent})")

        for linea in info:
            tk.Label(
                datos_frame, text=linea, font=FUENTES["texto_normal"],
                bg=COLORES["gris_claro"], fg=COLORES["texto_principal"],
                justify="left", wraplength=400
            ).pack(anchor="w", pady=4)

        # --- Acciones según el estado actual ---
        acciones_frame = tk.Frame(modal, bg=COLORES["blanco_fondo"], padx=30)
        acciones_frame.pack(fill="x", pady=5)

        if obj["status"] == "en_custodia":
            tk.Label(
                acciones_frame, text="Entregado a (ID de usuario o Nombre completo):",
                font=FUENTES["etiqueta"], bg=COLORES["blanco_fondo"], fg=COLORES["texto_ayuda"]
            ).pack(anchor="w")

            entry_receptor = tk.Entry(acciones_frame, font=FUENTES["texto_normal"])
            entry_receptor.pack(fill="x", pady=(3, 10))

            def confirmar_entrega():
                receptor = entry_receptor.get().strip()
                if not receptor:
                    messagebox.showwarning(
                        "Dato obligatorio",
                        "Indica el ID o nombre de la persona que recibe el objeto."
                    )
                    return

                ok, msg = marcar_objeto_entregado(obj["item_id"], self.admin_id, receptor)
                if ok:
                    messagebox.showinfo("Entregado", msg)
                    modal.destroy()
                    self.cargar_datos()
                else:
                    messagebox.showerror("Error", msg)

            tk.Button(
                acciones_frame, text="Marcar como Entregado",
                bg=ESTADOS["disponible_texto"], fg=COLORES["blanco_fondo"],
                font=FUENTES["texto_normal"], bd=0, padx=15, pady=8,
                cursor="hand2", command=confirmar_entrega
            ).pack(fill="x")
        else:
            def devolver_a_custodia():
                confirmar = messagebox.askyesno(
                    "Confirmar cambio",
                    "¿Regresar este objeto al estado 'En custodia'?"
                )
                if not confirmar:
                    return
                ok, msg = regresar_objeto_custodia(obj["item_id"])
                if ok:
                    messagebox.showinfo("Actualizado", msg)
                    modal.destroy()
                    self.cargar_datos()
                else:
                    messagebox.showerror("Error", msg)

            tk.Button(
                acciones_frame, text="Regresar a En custodia",
                bg=ESTADOS["llave_texto"], fg=COLORES["blanco_fondo"],
                font=FUENTES["texto_normal"], bd=0, padx=15, pady=8,
                cursor="hand2", command=devolver_a_custodia
            ).pack(fill="x")

        tk.Button(
            modal, text="Cerrar ventana", bg=COLORES["blanco_fondo"],
            fg=COLORES["texto_principal"], font=FUENTES["texto_normal"],
            bd=0, cursor="hand2", command=modal.destroy
        ).pack(pady=10)