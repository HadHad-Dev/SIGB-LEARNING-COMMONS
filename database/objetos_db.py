import mysql.connector
from database.conexion import obtener_conexion


def _obtener_o_crear_usuario(cursor, texto):
    """
    Resuelve siempre un user_id válido para mantener trazabilidad en user:
    1. Si es número, busca por institutional_id o user_id.
    2. Si es nombre, busca si ya existe ese usuario por full_name;
       si no existe, lo inserta automáticamente como 'externo' y devuelve su user_id.
    """
    texto = texto.strip()

    if texto.isdigit():
        num = int(texto)
        cursor.execute(
            "SELECT user_id FROM user WHERE institutional_id = %s OR user_id = %s LIMIT 1",
            (num, num),
        )
        fila = cursor.fetchone()
        if fila:
            return fila[0]

    cursor.execute(
        "SELECT user_id FROM user WHERE LOWER(full_name) = LOWER(%s) LIMIT 1",
        (texto,),
    )
    fila = cursor.fetchone()
    if fila:
        return fila[0]

    cursor.execute(
        "INSERT INTO user (full_name, user_type) VALUES (%s, 'externo')",
        (texto,),
    )
    return cursor.lastrowid


def obtener_kpis_objetos():
    """Retorna total de objetos, en custodia y entregados."""
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
    """Retorna los objetos perdidos con el nombre del reportante y receptor desde user."""
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
                u_found.full_name AS reporto,
                u_deliv.full_name AS entregado_a
            FROM lost_item l
            JOIN user u_found ON l.found_by_user_id = u_found.user_id
            LEFT JOIN user u_deliv ON l.delivered_to_user_id = u_deliv.user_id
        """
        params = []
        filtro = filtro.strip()
        if filtro:
            sql += """
                WHERE l.title LIKE %s
                   OR l.description LIKE %s
                   OR l.found_location LIKE %s
                   OR u_found.full_name LIKE %s
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
    """Inserta un nuevo objeto perdido ligado siempre a un user_id."""
    conexion = obtener_conexion()
    if conexion is None:
        return False, "No hay conexión con la base de datos."

    cursor = conexion.cursor()
    try:
        found_by_id = _obtener_o_crear_usuario(cursor, reportado_por)
        sql = """
            INSERT INTO lost_item
                (title, description, found_location, found_by_user_id, status)
            VALUES (%s, %s, %s, %s, 'en_custodia')
        """
        cursor.execute(sql, (
            titulo.strip(),
            descripcion.strip(),
            ubicacion.strip() or None,
            found_by_id,
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
    """Cambia el objeto a 'entregado' guardando fecha, admin y user_id del receptor."""
    conexion = obtener_conexion()
    if conexion is None:
        return False, "No hay conexión con la base de datos."

    cursor = conexion.cursor()
    try:
        delivered_to_id = _obtener_o_crear_usuario(cursor, entregado_a)
        sql = """
            UPDATE lost_item
            SET status = 'entregado',
                delivered_at = NOW(),
                delivered_by = %s,
                delivered_to_user_id = %s
            WHERE item_id = %s
        """
        cursor.execute(sql, (admin_id, delivered_to_id, item_id))
        conexion.commit()
        return True, "Objeto marcado como entregado."
    except mysql.connector.Error as err:
        conexion.rollback()
        return False, f"Error de MySQL: {err.msg}"
    finally:
        cursor.close()
        conexion.close()


def regresar_objeto_custodia(item_id):
    """Regresa un objeto a 'en_custodia' limpiando los campos de entrega."""
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
                delivered_to_user_id = NULL
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