from database.conexion import obtener_conexion


def autenticar_usuario(user_id: int, password: str):
    """Valida credenciales contra la tabla `user` y devuelve el dict del usuario o None."""
    conexion = obtener_conexion()
    if conexion is None:
        return None, "No se pudo conectar a la base de datos."

    cursor = conexion.cursor(dictionary=True)
    try:
        sql = """
            SELECT user_id, full_name, user_type, department_area, major, quarter, teacher_type
            FROM `user`
            WHERE user_id = %s
              AND password = %s
              AND password IS NOT NULL
        """
        cursor.execute(sql, (user_id, password))
        usuario = cursor.fetchone()

        if not usuario:
            return None, "Matrícula/ID o contraseña incorrectos."

        # Opcional: restringir acceso al panel administrativo
        # if usuario["user_type"] not in ("administrador", "administrativo"):
        #     return None, "Tu rol no tiene permisos para acceder a este panel."

        return usuario, None
    finally:
        cursor.close()
        conexion.close()