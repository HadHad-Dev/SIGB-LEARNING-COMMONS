from database.conexion import obtener_conexion


def obtener_usuario_perfil(user_id=None):
    """
    Obtiene los datos del usuario indicado.
    Si user_id es None, devuelve el primer usuario registrado en la BD
    para que los campos siempre tengan datos reales por defecto.
    """
    conexion = obtener_conexion()
    if conexion is None:
        return None

    cursor = conexion.cursor(dictionary=True)
    try:
        if user_id is not None:
            sql = """
                SELECT
                    user_id,
                    full_name,
                    user_type,
                    gender,
                    major,
                    quarter,
                    teacher_type,
                    department_area,
                    phone
                FROM `user`
                WHERE user_id = %s
            """
            cursor.execute(sql, (user_id,))
        else:
            sql = """
                SELECT
                    user_id,
                    full_name,
                    user_type,
                    gender,
                    major,
                    quarter,
                    teacher_type,
                    department_area,
                    phone
                FROM `user`
                ORDER BY user_id ASC
                LIMIT 1
            """
            cursor.execute(sql)

        return cursor.fetchone()
    finally:
        cursor.close()
        conexion.close()


def guardar_perfil_en_bd(user_id: int, full_name: str, department_area=None, phone=None):
    """
    Actualiza full_name y, según el rol (user_type), department_area o phone
    respetando los CHECK constraints de la tabla `user`.
    """
    conexion = obtener_conexion()
    if conexion is None:
        return False, "No se pudo conectar a la base de datos."

    cursor = conexion.cursor(dictionary=True)
    try:
        cursor.execute("SELECT user_type FROM `user` WHERE user_id = %s", (user_id,))
        actual = cursor.fetchone()
        if not actual:
            return False, "El usuario ya no existe en la base de datos."

        rol = actual["user_type"]

        # Respetar chk_admin_area: solo 'administrativo' conserva department_area
        dept_limpio = department_area.strip() if (rol == "administrativo" and department_area and department_area.strip()) else None
        if rol == "administrativo" and not dept_limpio:
            return False, "Los usuarios administrativos deben tener un área departamental."

        phone_limpio = phone.strip() if (phone and phone.strip()) else None
        if rol == "externo" and not phone_limpio:
            return False, "Los usuarios externos deben tener un teléfono registrado."

        sql = """
            UPDATE `user`
            SET full_name = %s,
                department_area = %s,
                phone = %s
            WHERE user_id = %s
        """
        cursor.execute(sql, (full_name.strip(), dept_limpio, phone_limpio, user_id))
        conexion.commit()
        return True, "Cambios guardados correctamente en la base de datos."
    except Exception as e:
        conexion.rollback()
        return False, f"Error al guardar cambios: {e}"
    finally:
        cursor.close()
        conexion.close()


def actualizar_password_en_bd(user_id: int, password_actual: str, password_nueva: str):
    """Valida la contraseña actual y guarda la nueva en `user`."""
    conexion = obtener_conexion()
    if conexion is None:
        return False, "No se pudo conectar a la base de datos."

    cursor = conexion.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT user_type, password FROM `user` WHERE user_id = %s",
            (user_id,),
        )
        fila = cursor.fetchone()
        if not fila:
            return False, "Usuario no encontrado."

        if fila["user_type"] == "externo":
            return False, "Los usuarios externos no manejan contraseña."

        if fila["password"] != password_actual:
            return False, "La contraseña actual no coincide."

        cursor.execute(
            "UPDATE `user` SET password = %s WHERE user_id = %s",
            (password_nueva, user_id),
        )
        conexion.commit()
        return True, "Contraseña actualizada correctamente."
    except Exception as e:
        conexion.rollback()
        return False, f"Error al actualizar contraseña: {e}"
    finally:
        cursor.close()
        conexion.close()