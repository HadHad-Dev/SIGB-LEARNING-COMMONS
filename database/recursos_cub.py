import mysql.connector
from database.conexion import obtener_conexion


def obtener_kpis_cubi():
    conexion = obtener_conexion()
    if conexion is None:
        return {"total": 0, "disponibles": 0, "ocupados": 0}

    cursor = conexion.cursor(dictionary=True)
    try:
        sql = """
            SELECT
                COUNT(*) AS total,
                SUM(CASE WHEN ir.status = 'disponible' THEN 1 ELSE 0 END) AS disponibles,
                SUM(CASE WHEN ir.status = 'en_uso' THEN 1 ELSE 0 END) AS ocupados
            FROM inventory_resource ir
            JOIN category c ON ir.category_id = c.category_id
            WHERE c.name_category = 'Cubículo'
        """
        cursor.execute(sql)
        datos = cursor.fetchone() or {}
        return {
            "total": int(datos.get("total") or 0),
            "disponibles": int(datos.get("disponibles") or 0),
            "ocupados": int(datos.get("ocupados") or 0),
        }
    finally:
        cursor.close()
        conexion.close()


def obtener_cubiculos_detalle():
    """Devuelve la lista de cubículos con su estado y datos del uso activo si existe."""
    conexion = obtener_conexion()
    if conexion is None:
        return []

    cursor = conexion.cursor(dictionary=True)
    try:
        sql = """
            SELECT
                ir.bar_code,
                ir.description_title,
                ir.capacity,
                ir.status,
                ir.shelf_location,
                au.attendees_count,
                au.starting_date,
                au.due_at,
                u.full_name AS usuario_nombre
            FROM inventory_resource ir
            JOIN category c ON ir.category_id = c.category_id
            LEFT JOIN active_usage au ON ir.bar_code = au.bar_code
            LEFT JOIN `user` u ON au.user_id = u.user_id
            WHERE c.name_category = 'Cubículo'
            ORDER BY ir.bar_code ASC
        """
        cursor.execute(sql)
        return cursor.fetchall()
    finally:
        cursor.close()
        conexion.close()