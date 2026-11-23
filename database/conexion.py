import mysql.connector
from database.credenciales import DB_CONFIG

def obtener_conexion():
    try:
        conexion = mysql.connector.connect(**DB_CONFIG)
        return conexion
    except Exception as e:
        print("Error de conexión:", e)
        return None
