from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment


def exportar_tabla_excel(ruta_salida, nombre_hoja, encabezados, filas):
    """Exporta una lista de filas a un archivo .xlsx con formato limpio."""
    wb = Workbook()
    ws = wb.active
    ws.title = nombre_hoja[:31] 

    relleno_header = PatternFill(start_color="B22222", end_color="B22222", fill_type="solid")
    fuente_header = Font(color="FFFFFF", bold=True)

    ws.append(encabezados)
    for celda in ws[1]:
        celda.fill = relleno_header
        celda.font = fuente_header
        celda.alignment = Alignment(horizontal="center")
    for fila in filas:
        ws.append(list(fila))
    for col in ws.columns:
        letra = col[0].column_letter
        largo_max = max(len(str(c.value or "")) for c in col)
        ws.column_dimensions[letra].width = min(largo_max + 4, 45)
    wb.save(ruta_salida)