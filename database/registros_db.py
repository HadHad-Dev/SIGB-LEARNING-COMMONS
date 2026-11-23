from datetime import datetime, timedelta
from database.conexion import obtener_conexion


def obtener_rango_fechas(periodo):
    hoy = datetime.now()

    if periodo == "Semana actual":
        inicio = (hoy - timedelta(days=6)).replace(hour=0, minute=0, second=0, microsecond=0)
        return inicio, hoy

    if hoy.month <= 4:
        mes_inicio = 1
    elif hoy.month <= 8:
        mes_inicio = 5
    else:
        mes_inicio = 9

    if periodo == "Cuatrimestre actual":
        inicio = datetime(hoy.year, mes_inicio, 1, 0, 0, 0)
        return inicio, hoy

    if mes_inicio == 1:
        inicio = datetime(hoy.year - 1, 9, 1, 0, 0, 0)
        fin = datetime(hoy.year - 1, 12, 31, 23, 59, 59)
    else:
        inicio = datetime(hoy.year, mes_inicio - 4, 1, 0, 0, 0)
        fin = datetime(hoy.year, mes_inicio, 1, 0, 0, 0) - timedelta(seconds=1)

    return inicio, fin


def _traer_usos_del_periodo(cursor, inicio, fin):
    sql_historial = """
        SELECT u.user_type, u.major, u.gender, u.quarter
        FROM usage_history h
        JOIN user u ON u.user_id = h.user_id
        WHERE h.starting_date BETWEEN %s AND %s
    """
    cursor.execute(sql_historial, (inicio, fin))
    historial = cursor.fetchall()

    sql_activos = """
        SELECT u.user_type, u.major, u.gender, u.quarter
        FROM active_usage a
        JOIN user u ON u.user_id = a.user_id
        WHERE a.starting_date BETWEEN %s AND %s
    """
    cursor.execute(sql_activos, (inicio, fin))
    activos = cursor.fetchall()

    return historial + activos


def _nombre_recurso(fila):
    """Función auxiliar: reemplaza a COALESCE usando un if normal."""
    if fila["description_title"]:
        return fila["description_title"]
    elif fila["name_category"]:
        return fila["name_category"]
    else:
        return "Recurso"


def _obtener_total(elemento):
    """Función auxiliar para ordenar listas de (nombre, total) por el total."""
    return elemento[1]


def obtener_kpis_dashboard(periodo):
    inicio, fin = obtener_rango_fechas(periodo)
    conexion = obtener_conexion()
    if conexion is None:
        return {"mujeres": 0, "hombres": 0, "quarter_top": "Sin datos"}

    cursor = conexion.cursor(dictionary=True)
    try:
        usos = _traer_usos_del_periodo(cursor, inicio, fin)

        mujeres = 0
        hombres = 0
        conteo_quarters = {}

        for u in usos:
            genero = str(u["gender"] or "").strip().lower()
            if genero in ("mujer", "femenino", "f"):
                mujeres += 1
            elif genero in ("hombre", "masculino", "m"):
                hombres += 1

            cuatri = u["quarter"]
            if cuatri is not None and str(cuatri).strip() != "":
                conteo_quarters[cuatri] = conteo_quarters.get(cuatri, 0) + 1

        quarter_top = "Sin datos"
        max_visitas = 0
        for cuatri, visitas in conteo_quarters.items():
            if visitas > max_visitas:
                max_visitas = visitas
                quarter_top = f"{cuatri}° ({visitas})"

        return {
            "mujeres": mujeres,
            "hombres": hombres,
            "quarter_top": quarter_top,
        }
    finally:
        cursor.close()
        conexion.close()


def obtener_usos_por_tipo_usuario(periodo):
    inicio, fin = obtener_rango_fechas(periodo)
    conexion = obtener_conexion()
    if conexion is None:
        return []

    cursor = conexion.cursor(dictionary=True)
    try:
        usos = _traer_usos_del_periodo(cursor, inicio, fin)

        conteo = {}
        for u in usos:
            tipo = u["user_type"] or "Sin tipo"
            conteo[tipo] = conteo.get(tipo, 0) + 1

        resultado = []
        for tipo, total in conteo.items():
            resultado.append((tipo, total))

        resultado.sort(key=_obtener_total, reverse=True)
        return resultado
    finally:
        cursor.close()
        conexion.close()

def obtener_ranking_carreras(periodo):
    inicio, fin = obtener_rango_fechas(periodo)
    conexion = obtener_conexion()
    if conexion is None:
        return []

    cursor = conexion.cursor(dictionary=True)
    try:
        usos = _traer_usos_del_periodo(cursor, inicio, fin)

        conteo = {}
        for u in usos:
            carrera = u["major"]
            if carrera is not None and carrera != "":
                conteo[carrera] = conteo.get(carrera, 0) + 1

        resultado = []
        for carrera, total in conteo.items():
            resultado.append((carrera, total))

        resultado.sort(key=_obtener_total, reverse=True)
        return resultado[:5]
    finally:
        cursor.close()
        conexion.close()

def obtener_registros_recientes(limite=6):
    conexion = obtener_conexion()
    if conexion is None:
        return []

    cursor = conexion.cursor(dictionary=True)
    try:
        sql_activos = """
            SELECT a.starting_date, ir.description_title, c.name_category, u.full_name
            FROM active_usage a
            JOIN user u ON u.user_id = a.user_id
            LEFT JOIN inventory_resource ir ON ir.bar_code = a.bar_code
            LEFT JOIN category c ON c.category_id = a.category_id
            ORDER BY a.starting_date DESC
            LIMIT %s
        """
        cursor.execute(sql_activos, (limite,))
        activos = cursor.fetchall()
        sql_historial = """
            SELECT h.starting_date, h.close_reason, ir.description_title, c.name_category, u.full_name
            FROM usage_history h
            JOIN user u ON u.user_id = h.user_id
            LEFT JOIN inventory_resource ir ON ir.bar_code = h.bar_code
            LEFT JOIN category c ON c.category_id = h.category_id
            ORDER BY h.starting_date DESC
            LIMIT %s
        """
        cursor.execute(sql_historial, (limite,))
        historial = cursor.fetchall()

        movimientos = []

        for f in activos:
            movimientos.append({
                "fecha": f["starting_date"],
                "recurso": _nombre_recurso(f),
                "usuario": f["full_name"],
                "estado": "En uso",
            })

        for f in historial:
            if f["close_reason"] == "completado":
                estado = "Completado"
            else:
                estado = "Cierre auto."

            movimientos.append({
                "fecha": f["starting_date"],
                "recurso": _nombre_recurso(f),
                "usuario": f["full_name"],
                "estado": estado,
            })

        # Ordenar todos juntos del más reciente al más antiguo y tomar solo el límite
        movimientos.sort(key=lambda m: m["fecha"], reverse=True)
        movimientos = movimientos[:limite]

        resultados = []
        for m in movimientos:
            hora = m["fecha"].strftime("%H:%M")
            actividad = f"{m['recurso']} · {m['usuario']}"
            resultados.append((hora, actividad, m["estado"]))

        return resultados
    finally:
        cursor.close()
        conexion.close()

def obtener_notificaciones():
    conexion = obtener_conexion()
    if conexion is None:
        return []

    cursor = conexion.cursor(dictionary=True)
    alertas = []
    try:
        sql_objetos = """
            SELECT title, found_location, found_date
            FROM lost_item
            WHERE status = 'en_custodia'
            ORDER BY found_date DESC
            LIMIT 10
        """
        cursor.execute(sql_objetos)
        for obj in cursor.fetchall():
            fecha = obj["found_date"].strftime("%d/%m")
            ubicacion = obj["found_location"] or "Sin ubicación"
            alertas.append(f"[En custodia] {obj['title']} ({ubicacion} · {fecha})")

        return alertas
    finally:
        cursor.close()
        conexion.close()


def obtener_resumen_general(periodo):
    inicio, fin = obtener_rango_fechas(periodo)
    conexion = obtener_conexion()
    if conexion is None:
        return []

    cursor = conexion.cursor(dictionary=True)
    try:
        sql_historial = """
            SELECT h.user_id, h.starting_date, h.end_date, h.close_reason,
                   ir.description_title, c.name_category
            FROM usage_history h
            LEFT JOIN inventory_resource ir ON ir.bar_code = h.bar_code
            LEFT JOIN category c ON c.category_id = h.category_id
            WHERE h.starting_date BETWEEN %s AND %s
        """
        cursor.execute(sql_historial, (inicio, fin))
        historial = cursor.fetchall()

        sql_activos = """
            SELECT a.user_id, a.starting_date,
                   ir.description_title, c.name_category
            FROM active_usage a
            LEFT JOIN inventory_resource ir ON ir.bar_code = a.bar_code
            LEFT JOIN category c ON c.category_id = a.category_id
            WHERE a.starting_date BETWEEN %s AND %s
        """
        cursor.execute(sql_activos, (inicio, fin))
        activos = cursor.fetchall()

        cursor.execute("SELECT COUNT(*) AS total FROM active_usage")
        activos_ahora = cursor.fetchone()["total"]

        ahora = datetime.now()
        usuarios_unicos = set()
        conteo_recursos = {}
        completados = 0
        cierres_auto = 0
        total_minutos = 0.0

        for h in historial:
            usuarios_unicos.add(h["user_id"])

            if h["close_reason"] == "completado":
                completados += 1
            else:
                cierres_auto += 1

            if h["starting_date"] and h["end_date"]:
                minutos = (h["end_date"] - h["starting_date"]).total_seconds() / 60
                if minutos > 0:
                    total_minutos += minutos

            recurso = _nombre_recurso(h)
            conteo_recursos[recurso] = conteo_recursos.get(recurso, 0) + 1

        for a in activos:
            usuarios_unicos.add(a["user_id"])

            if a["starting_date"]:
                minutos = (ahora - a["starting_date"]).total_seconds() / 60
                if minutos > 0:
                    total_minutos += minutos

            recurso = _nombre_recurso(a)
            conteo_recursos[recurso] = conteo_recursos.get(recurso, 0) + 1

        total_usos = len(historial) + len(activos)
        horas_totales = round(total_minutos / 60, 1)

        if total_usos > 0:
            promedio_min = round(total_minutos / total_usos, 1)
        else:
            promedio_min = 0

        recurso_top = "Sin datos"
        max_usos = 0
        for nombre, cantidad in conteo_recursos.items():
            if cantidad > max_usos:
                max_usos = cantidad
                recurso_top = f"{nombre} ({cantidad})"

        return [
            ("Total de usos en el periodo", str(total_usos)),
            ("Usuarios únicos atendidos", str(len(usuarios_unicos))),
            ("Usos activos ahora mismo", str(activos_ahora)),
            ("Préstamos completados", str(completados)),
            ("Cierres automáticos", str(cierres_auto)),
            ("Horas totales de uso", f"{horas_totales} h"),
            ("Duración promedio por uso", f"{promedio_min} min"),
            ("Recurso más solicitado", recurso_top),
        ]
    finally:
        cursor.close()
        conexion.close()