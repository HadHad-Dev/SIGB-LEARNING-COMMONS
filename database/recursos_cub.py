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


def registrar_reserva_cubiculo(bar_code: str, user_id: int, attendees_count: int):
    conexion = obtener_conexion()
    if conexion is None:
        return False, "No se pudo conectar a la base de datos."

    cursor = conexion.cursor(dictionary=True)
    try:
        sql_info = """
            SELECT ir.bar_code, ir.status, ir.capacity, c.maximum_time_minute
            FROM inventory_resource ir
            JOIN category c ON ir.category_id = c.category_id
            WHERE ir.bar_code = %s AND c.name_category = 'Cubículo'
        """
        cursor.execute(sql_info, (bar_code,))
        cub = cursor.fetchone()
        if not cub:
            return False, "El cubículo no existe."

        if cub["status"] != "disponible":
            return False, f"El cubículo no está disponible (estado actual: {cub['status']})."

        if cub["capacity"] is not None and attendees_count > int(cub["capacity"]):
            return False, f"La cantidad de asistentes ({attendees_count}) supera la capacidad ({cub['capacity']})."

        cursor.execute("SELECT user_id FROM `user` WHERE user_id = %s", (user_id,))
        if not cursor.fetchone():
            return False, f"El usuario con ID {user_id} no existe."

        cursor.execute("SELECT usage_id FROM active_usage WHERE bar_code = %s", (bar_code,))
        if cursor.fetchone():
            return False, "Este cubículo ya cuenta con un uso activo."

        minutos = int(cub["maximum_time_minute"] or 120)

        sql_insert = """
            INSERT INTO active_usage (user_id, category_id, bar_code, attendees_count, starting_date, due_at)
            VALUES (%s, NULL, %s, %s, NOW(), DATE_ADD(NOW(), INTERVAL %s MINUTE))
        """
        cursor.execute(sql_insert, (user_id, bar_code, attendees_count, minutos))

        cursor.execute(
            "UPDATE inventory_resource SET status = 'en_uso' WHERE bar_code = %s",
            (bar_code,),
        )

        conexion.commit()
        return True, f"Reserva registrada ({minutos} min máx.)."
    except Exception as e:
        conexion.rollback()
        return False, f"Error al registrar reserva: {e}"
    finally:
        cursor.close()
        conexion.close()


def extender_tiempo_cubiculo(bar_code: str, minutos_extra: int):
    conexion = obtener_conexion()
    if conexion is None:
        return False, "No se pudo conectar a la base de datos."

    cursor = conexion.cursor(dictionary=True)
    try:
        sql_uso = """
            SELECT au.usage_id
            FROM active_usage au
            WHERE au.bar_code = %s
        """
        cursor.execute(sql_uso, (bar_code,))
        uso = cursor.fetchone()
        if not uso:
            return False, "El cubículo no tiene un uso activo para extender."

        cursor.execute(
            """
            UPDATE active_usage
            SET due_at = DATE_ADD(due_at, INTERVAL %s MINUTE)
            WHERE usage_id = %s
            """,
            (minutos_extra, uso["usage_id"]),
        )
        conexion.commit()
        return True, f"Tiempo extendido +{minutos_extra} minutos."
    except Exception as e:
        conexion.rollback()
        return False, f"Error al extender tiempo: {e}"
    finally:
        cursor.close()
        conexion.close()


def liberar_cubiculo(bar_code: str, closed_by_user_id=None):
    conexion = obtener_conexion()
    if conexion is None:
        return False, "No se pudo conectar a la base de datos."

    cursor = conexion.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT usage_id, user_id, bar_code, attendees_count, starting_date, due_at
            FROM active_usage
            WHERE bar_code = %s
            """,
            (bar_code,),
        )
        uso = cursor.fetchone()

        if uso:
            if closed_by_user_id is not None:
                cursor.execute(
                    """
                    INSERT INTO usage_history (
                        user_id, category_id, bar_code, attendees_count,
                        starting_date, due_at, end_date, close_reason, closed_by
                    )
                    VALUES (%s, NULL, %s, %s, %s, %s, NOW(), 'completado', %s)
                    """,
                    (
                        uso["user_id"],
                        uso["bar_code"],
                        uso["attendees_count"],
                        uso["starting_date"],
                        uso["due_at"],
                        closed_by_user_id,
                    ),
                )
            else:
                cursor.execute(
                    """
                    INSERT INTO usage_history (
                        user_id, category_id, bar_code, attendees_count,
                        starting_date, due_at, end_date, close_reason, closed_by
                    )
                    VALUES (%s, NULL, %s, %s, %s, %s, NOW(), 'cierre_automatico', NULL)
                    """,
                    (
                        uso["user_id"],
                        uso["bar_code"],
                        uso["attendees_count"],
                        uso["starting_date"],
                        uso["due_at"],
                    ),
                )

            cursor.execute("DELETE FROM active_usage WHERE usage_id = %s", (uso["usage_id"],))

        cursor.execute(
            "UPDATE inventory_resource SET status = 'disponible' WHERE bar_code = %s",
            (bar_code,),
        )

        conexion.commit()
        return True, "Cubículo liberado y guardado en historial."
    except Exception as e:
        conexion.rollback()
        return False, f"Error al liberar cubículo: {e}"
    finally:
        cursor.close()
        conexion.close()