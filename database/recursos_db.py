import mysql.connector
from database.conexion import obtener_conexion


def obtener_libros():
    conexion = obtener_conexion()
    if conexion is None:
        return []

    cursor = conexion.cursor(dictionary=True)
    try:
        sql = """
            SELECT ir.bar_code, ir.description_title, ir.author,
                   ir.shelf_location, ir.status
            FROM inventory_resource ir
            JOIN category c ON ir.category_id = c.category_id
            WHERE c.name_category = 'Libro'
            ORDER BY ir.bar_code ASC
        """
        cursor.execute(sql)
        return cursor.fetchall()
    finally:
        cursor.close()
        conexion.close()

def obtener_kpis_libros():
    conexion = obtener_conexion()
    if conexion is None:
        return {"total": 0, "disponibles": 0, "prestados": 0}

    cursor = conexion.cursor(dictionary=True)
    try:
        sql = """
            SELECT
                COUNT(*) AS total,
                SUM(CASE WHEN ir.status = 'disponible' THEN 1 ELSE 0 END) AS disponibles,
                SUM(CASE WHEN ir.status = 'en_uso' THEN 1 ELSE 0 END) AS prestados
            FROM inventory_resource ir
            JOIN category c ON ir.category_id = c.category_id
            WHERE c.name_category = 'Libro'
        """
        cursor.execute(sql)
        datos = cursor.fetchone()
        return {
            "total": int(datos["total"] or 0),
            "disponibles": int(datos["disponibles"] or 0),
            "prestados": int(datos["prestados"] or 0),
        }
    finally:
        cursor.close()
        conexion.close()


def agregar_libro(bar_code, titulo, autor, ubicacion, status="disponible"):
    conexion = obtener_conexion()
    if conexion is None:
        return False, "No hay conexión con la base de datos."

    cursor = conexion.cursor(dictionary=True)
    try:
        cat_id = 5
        if cat_id is None:
            return False, "No existe la categoría 'Libro' en la base de datos."

        sql = """
            INSERT INTO inventory_resource
                (bar_code, category_id, description_title, author, status, shelf_location)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (bar_code, cat_id, titulo, autor or None, status, ubicacion or None))
        conexion.commit()
        return True, "Ejemplar agregado correctamente."
    except mysql.connector.Error as err:
        conexion.rollback()
        if err.errno == 1062:
            return False, f"Ya existe un recurso con el código '{bar_code}'."
        return False, f"Error de MySQL: {err.msg}"
    finally:
        cursor.close()
        conexion.close()


def editar_libro(bar_code, titulo, autor, ubicacion, status):
    conexion = obtener_conexion()
    if conexion is None:
        return False, "No hay conexión con la base de datos."

    cursor = conexion.cursor()
    try:
        sql = """
            UPDATE inventory_resource
            SET description_title = %s,
                author = %s,
                shelf_location = %s,
                status = %s
            WHERE bar_code = %s
        """
        cursor.execute(sql, (titulo, autor or None, ubicacion or None, status, bar_code))
        conexion.commit()
        return True, "Ejemplar actualizado correctamente."
    except mysql.connector.Error as err:
        conexion.rollback()
        return False, f"Error de MySQL: {err.msg}"
    finally:
        cursor.close()
        conexion.close()


def eliminar_libro(bar_code):
    conexion = obtener_conexion()
    if conexion is None:
        return False, "No hay conexión con la base de datos."

    cursor = conexion.cursor()
    try:
        cursor.execute("DELETE FROM inventory_resource WHERE bar_code = %s", (bar_code,))
        conexion.commit()
        return True, "Ejemplar eliminado correctamente."
    except mysql.connector.Error as err:
        conexion.rollback()
        if err.errno == 1451:
            return (
                False,
                "No se puede eliminar este libro porque tiene préstamos o incidencias en el historial.\n"
                "En su lugar, edítalo y cambia su estado a 'mantenimiento' o 'extraviado'."
            )
        return False, f"Error de MySQL: {err.msg}"
    finally:
        cursor.close()
        conexion.close()

def obtener_prestamos_libros():
    conexion = obtener_conexion()
    if conexion is None:
        return []

    cursor = conexion.cursor(dictionary=True)
    try:
        sql_activos = """
            SELECT
                CONCAT('ACT-', a.usage_id) AS folio,
                a.usage_id,
                CONCAT(COALESCE(u.institutional_id, u.user_id), ' - ', u.full_name) AS estudiante,
                CONCAT(ir.bar_code, ' - ', ir.description_title) AS libro,
                a.due_at,
                CASE
                    WHEN a.due_at < NOW() THEN 'Atrasado'
                    ELSE 'En tiempo'
                END AS estado
            FROM active_usage a
            JOIN inventory_resource ir ON a.bar_code = ir.bar_code
            JOIN category c ON ir.category_id = c.category_id
            JOIN user u ON a.user_id = u.user_id
            WHERE c.name_category = 'Libro'
            ORDER BY a.due_at ASC
        """
        cursor.execute(sql_activos)
        activos = cursor.fetchall()

        sql_historial = """
            SELECT
                CONCAT('HIS-', h.history_id) AS folio,
                CONCAT(u.user_id, ' - ', u.full_name) AS estudiante,
                CONCAT(ir.bar_code, ' - ', ir.description_title) AS libro,
                h.due_at,
                'Devuelto' AS estado
            FROM usage_history h
            JOIN inventory_resource ir ON h.bar_code = ir.bar_code
            JOIN category c ON ir.category_id = c.category_id
            JOIN user u ON h.user_id = u.user_id
            WHERE c.name_category = 'Libro'
            ORDER BY h.end_date DESC
            LIMIT 30
        """
        cursor.execute(sql_historial)
        historial = cursor.fetchall()

        return activos + historial
    finally:
        cursor.close()
        conexion.close()


def obtener_kpis_prestamos_libros():
    conexion = obtener_conexion()
    if conexion is None:
        return {"activos": 0, "atrasados": 0, "devueltos_semana": 0}

    cursor = conexion.cursor(dictionary=True)
    try:
        sql_activos = """
            SELECT
                COUNT(*) AS activos,
                SUM(CASE WHEN a.due_at < NOW() THEN 1 ELSE 0 END) AS atrasados
            FROM active_usage a
            JOIN inventory_resource ir ON a.bar_code = ir.bar_code
            JOIN category c ON ir.category_id = c.category_id
            WHERE c.name_category = 'Libro'
        """
        cursor.execute(sql_activos)
        datos_act = cursor.fetchone()

        sql_devueltos = """
            SELECT COUNT(*) AS devueltos
            FROM usage_history h
            JOIN inventory_resource ir ON h.bar_code = ir.bar_code
            JOIN category c ON ir.category_id = c.category_id
            WHERE c.name_category = 'Libro'
              AND h.end_date >= NOW() - INTERVAL 7 DAY
        """
        cursor.execute(sql_devueltos)
        datos_dev = cursor.fetchone()

        return {
            "activos": int(datos_act["activos"] or 0),
            "atrasados": int(datos_act["atrasados"] or 0),
            "devueltos_semana": int(datos_dev["devueltos"] or 0),
        }
    finally:
        cursor.close()
        conexion.close()


def marcar_libro_devuelto(usage_id, admin_id):

    conexion = obtener_conexion()
    if conexion is None:
        return False, "No hay conexión con la base de datos."

    cursor = conexion.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM active_usage WHERE usage_id = %s", (usage_id,))
        prestamo = cursor.fetchone()
        if prestamo is None:
            return False, "El préstamo ya no existe o ya fue cerrado."

        sql_insert = """
            INSERT INTO usage_history
                (user_id, category_id, bar_code, attendees_count,
                 starting_date, due_at, end_date, close_reason, closed_by)
            VALUES (%s, %s, %s, %s, %s, %s, NOW(), 'completado', %s)
        """
        cursor.execute(sql_insert, (
            prestamo["user_id"],
            prestamo["category_id"],
            prestamo["bar_code"],
            prestamo["attendees_count"],
            prestamo["starting_date"],
            prestamo["due_at"],
            admin_id,
        ))

        cursor.execute("DELETE FROM active_usage WHERE usage_id = %s", (usage_id,))

        if prestamo["bar_code"]:
            cursor.execute(
                "UPDATE inventory_resource SET status = 'disponible' WHERE bar_code = %s",
                (prestamo["bar_code"],),
            )

        conexion.commit()
        return True, "Libro marcado como devuelto correctamente."
    except mysql.connector.Error as err:
        conexion.rollback()
        return False, f"Error al procesar la devolución: {err.msg}"
    finally:
        cursor.close()
        conexion.close()