import mysql.connector
from database.conexion import obtener_conexion
def _resolver_usuario_o_nombre(cursor, texto):

    texto = texto.strip()
    if texto.isdigit():
        cursor.execute("SELECT user_id FROM user WHERE user_id = %s", (int(texto),))
        fila = cursor.fetchone()
        if fila:
            return int(texto), None
    return None, texto
def obtener_kpis_objetos():
    conexion = obtener_conexion()
    if conexion is None:
        return {"total": 0, "en_custodia": 0, "entregados": 0}

    cursor = conexion.cursor(dictionary=True)
    try:
        sql = """
            SELECT
                COUNT(*) AS total,
                SUM(CASE WHEN status = 'en_custodia' THEN 1 ELSE 0 END) AS en_custodia,
                SUM(CASE WHEN status = 'entregado' THEN 1 ELSE 0 END) AS entregados
            FROM lost_item
        """
        cursor.execute(sql)
        datos = cursor.fetchone()
        return {
            "total": int(datos["total"] or 0),
            "en_custodia": int(datos["en_custodia"] or 0),
            "entregados": int(datos["entregados"] or 0),
        }
    finally:
        cursor.close()
        conexion.close()


def obtener_objetos(filtro=""):
    conexion = obtener_conexion()
    if conexion is None:
        return []

    cursor = conexion.cursor(dictionary=True)
    try:
        sql = """
            SELECT
                l.item_id,
                l.title,
                l.description,
                l.found_location,
                l.found_date,
                l.status,
                l.delivered_at,
                COALESCE(u_found.full_name, l.finder_name) AS reporto,
                COALESCE(u_deliv.full_name, l.delivered_to_name) AS entregado_a
            FROM lost_item l
            LEFT JOIN user u_found ON l.found_by_user_id = u_found.user_id
            LEFT JOIN user u_deliv ON l.delivered_to_user_id = u_deliv.user_id
        """
        params = []
        filtro = filtro.strip()
        if filtro:
            sql += """
                WHERE l.title LIKE %s
                   OR l.description LIKE %s
                   OR l.found_location LIKE %s
                   OR COALESCE(u_found.full_name, l.finder_name) LIKE %s
            """
            patron = f"%{filtro}%"
            params = [patron, patron, patron, patron]

        sql += " ORDER BY (l.status = 'en_custodia') DESC, l.found_date DESC"
        cursor.execute(sql, params)
        return cursor.fetchall()
    finally:
        cursor.close()
        conexion.close()


def registrar_objeto(titulo, descripcion, ubicacion, reportado_por):
    conexion = obtener_conexion()
    if conexion is None:
        return False, "No hay conexión con la base de datos."

    cursor = conexion.cursor()
    try:
        user_id, nombre_libre = _resolver_usuario_o_nombre(cursor, reportado_por)
        sql = """
            INSERT INTO lost_item
                (title, description, found_location, found_by_user_id, finder_name, status)
            VALUES (%s, %s, %s, %s, %s, 'en_custodia')
        """
        cursor.execute(sql, (
            titulo.strip(),
            descripcion.strip(),
            ubicacion.strip() or None,
            user_id,
            nombre_libre,
        ))
        conexion.commit()
        return True, "Objeto registrado correctamente."
    except mysql.connector.Error as err:
        conexion.rollback()
        return False, f"Error de MySQL: {err.msg}"
    finally:
        cursor.close()
        conexion.close()


def marcar_objeto_entregado(item_id, admin_id, entregado_a):
    conexion = obtener_conexion()
    if conexion is None:
        return False, "No hay conexión con la base de datos."
    cursor = conexion.cursor()
    try:
        user_id, nombre_libre = _resolver_usuario_o_nombre(cursor, entregado_a)
        sql = """
            UPDATE lost_item
            SET status = 'entregado',
                delivered_at = NOW(),
                delivered_by = %s,
                delivered_to_user_id = %s,
                delivered_to_name = %s
            WHERE item_id = %s
        """
        cursor.execute(sql, (admin_id, user_id, nombre_libre, item_id))
        conexion.commit()
        return True, "Objeto marcado como entregado."
    except mysql.connector.Error as err:
        conexion.rollback()
        return False, f"Error de MySQL: {err.msg}"
    finally:
        cursor.close()
        conexion.close()
def regresar_objeto_custodia(item_id):
    conexion = obtener_conexion()
    if conexion is None:
        return False, "No hay conexión con la base de datos."
    cursor = conexion.cursor()
    try:
        sql = """
            UPDATE lost_item
            SET status = 'en_custodia',
                delivered_at = NULL,
                delivered_by = NULL,
                delivered_to_user_id = NULL,
                delivered_to_name = NULL
            WHERE item_id = %s
        """
        cursor.execute(sql, (item_id,))
        conexion.commit()
        return True, "El objeto volvió al estado 'En custodia'."
    except mysql.connector.Error as err:
        conexion.rollback()
        return False, f"Error de MySQL: {err.msg}"
    finally:
        cursor.close()
        conexion.close()