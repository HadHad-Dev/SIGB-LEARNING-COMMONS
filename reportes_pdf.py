import io
import os
from datetime import datetime
from fpdf import FPDF


def generar_pdf_dashboard(ruta_salida, periodo, kpis, fig_uso, fig_carreras, registros, resumen_general=None):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    ruta_logo = os.path.join("img", "UTRLOGO.png")
    if os.path.exists(ruta_logo):
        pdf.image(ruta_logo, x=10, y=8, w=25)

    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "SIGB Learning Commons - Reporte Histórico", ln=True, align="C")

    pdf.set_font("Helvetica", "", 10)
    fecha_gen = datetime.now().strftime("%d/%m/%Y %H:%M")
    pdf.cell(0, 6, f"Periodo: {periodo}   |   Generado: {fecha_gen}", ln=True, align="C")
    pdf.ln(8)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Resumen del periodo", ln=True)
    pdf.set_font("Helvetica", "", 11)

    resumen = [
        ("Usos registrados (Mujeres)", str(kpis["mujeres"])),
        ("Usos registrados (Hombres)", str(kpis["hombres"])),
        ("Cuatrimestre con mayor frecuencia", str(kpis["quarter_top"])),
    ]
    for etiqueta, valor in resumen:
        pdf.cell(90, 8, etiqueta, border=1)
        pdf.cell(50, 8, valor, border=1, ln=True, align="C")

    if resumen_general:
        pdf.ln(6)
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, "Detalle general de uso", ln=True)
        pdf.set_font("Helvetica", "", 10)
        for indicador, dato in resumen_general:
            pdf.cell(90, 7, indicador, border=1)
            pdf.cell(50, 7, dato[:35], border=1, ln=True, align="C")

    pdf.ln(6)

    if fig_uso is not None:
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, "Uso de recursos por tipo de usuario", ln=True)
        buf_uso = io.BytesIO()
        fig_uso.savefig(buf_uso, format="png", dpi=150, bbox_inches="tight")
        buf_uso.seek(0)
        pdf.image(buf_uso, x=12, w=175)
        pdf.ln(4)

    pdf.add_page()

    if fig_carreras is not None:
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, "Ranking por carrera", ln=True)
        buf_carreras = io.BytesIO()
        fig_carreras.savefig(buf_carreras, format="png", dpi=150, bbox_inches="tight")
        buf_carreras.seek(0)
        pdf.image(buf_carreras, x=12, w=150)
        pdf.ln(8)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Movimientos recientes", ln=True)

    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(25, 8, "Hora", border=1, align="C")
    pdf.cell(125, 8, "Actividad", border=1)
    pdf.cell(40, 8, "Estado", border=1, align="C", ln=True)

    pdf.set_font("Helvetica", "", 9)
    if not registros:
        pdf.cell(190, 8, "Sin movimientos registrados.", border=1, align="C", ln=True)
    else:
        for hora, actividad, estado in registros:
            pdf.cell(25, 7, hora, border=1, align="C")
            pdf.cell(125, 7, actividad[:68], border=1)
            pdf.cell(40, 7, estado, border=1, align="C", ln=True)

    pdf.output(ruta_salida)



def generar_pdf_prestamos_libros(ruta_salida, kpis, prestamos):

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    ruta_logo = os.path.join("img", "UTRLOGO.png")
    if os.path.exists(ruta_logo):
        pdf.image(ruta_logo, x=10, y=8, w=25)

    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "SIGB Learning Commons-Reporte de Préstamos de Libros", ln=True, align="C")

    pdf.set_font("Helvetica", "", 10)
    fecha_gen = datetime.now().strftime("%d/%m/%Y %H:%M")
    pdf.cell(0, 6, f"Generado: {fecha_gen}", ln=True, align="C")
    pdf.ln(8)

    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(63, 8, f"Activos: {kpis['activos']}", border=1, align="C")
    pdf.cell(63, 8, f"Atrasados: {kpis['atrasados']}", border=1, align="C")
    pdf.cell(64, 8, f"Devueltos (7 días): {kpis['devueltos_semana']}", border=1, align="C", ln=True)
    pdf.ln(6)

    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(20, 8, "Folio", border=1, align="C")
    pdf.cell(52, 8, "Estudiante", border=1)
    pdf.cell(63, 8, "Libro", border=1)
    pdf.cell(32, 8, "Vencimiento", border=1, align="C")
    pdf.cell(23, 8, "Estado", border=1, align="C", ln=True)

    pdf.set_font("Helvetica", "", 8)
    if not prestamos:
        pdf.cell(190, 8, "Sin préstamos registrados.", border=1, align="C", ln=True)
    else:
        for p in prestamos:
            venc = p["due_at"].strftime("%d/%m/%Y %H:%M") if p["due_at"] else "-"
            pdf.cell(20, 7, str(p["folio"]), border=1, align="C")
            pdf.cell(52, 7, str(p["estudiante"])[:28], border=1)
            pdf.cell(63, 7, str(p["libro"])[:35], border=1)
            pdf.cell(32, 7, venc, border=1, align="C")
            pdf.cell(23, 7, str(p["estado"]), border=1, align="C", ln=True)

    pdf.output(ruta_salida)