# 1. Colores principales del sistema web
COLORES = {
    "rojo_principal": "#B3261E",   # Barra superior y botón principal de acción
    "rojo_oscuro": "#8F1D17",      # Color al pasar el cursor sobre el botón principal
    "rosa_claro": "#FDECEA",       # Fondo de opción activa en el menú lateral
    "blanco_fondo": "#FFFFFF",     # Fondo general del 70% de las pantallas
    "gris_claro": "#FAF6F5",       # Fondo del menú lateral y de las tarjetas
    "gris_linea": "#EADFDD",       # Bordes de tarjetas y líneas de separación
    "texto_principal": "#1F1A1A",  # Casi negro para textos principales
    "texto_ayuda": "#6B5F5E",      # Gris para textos secundarios, fechas y detalles
    "gris_tenue" : "#F1F1F1",      # Gris para el topbar
    "OCCUPIED_BG": "#E3E3E3",
    "SELECTED_BORDER": "#333333",
    "CARD_BG": "#FFFFFF",
    "CARD_BORDER": "#D0D0D0",
    "CARD_BORDER": "#D0D0D0"
}

# 2. Colores semánticos para indicadores y estados
ESTADOS = {
    "disponible_texto": "#1F7A4D", # Verde (Cubículo libre o acción completada)
    "disponible_fondo": "#E3F4EA",
    "ocupado_texto": "#B3261E",    # Rojo (Cubículo en uso o error)
    "ocupado_fondo": "#FDECEA",
    "llave_texto": "#8A4F00",      # Ámbar (Falta entregar llave)
    "llave_fondo": "#FDF1DC"
}

# 3. Tipografía oficial (Requiere tener instaladas estas Google Fonts)
#  por lo cual al querer quitar complejidad en el deployment no agregaremos dichas fonts y habra un fallback interno sin marcar errror donde tkinter lo interpretara como sus propias fuentes default
FUENTES = {
    "titulo": ("Archivo", 28, "bold"),
    "subtitulo": ("Archivo", 20, "bold"),          # En Tkinter 'bold' suple a seminegrita
    "texto_normal": ("Public Sans", 16, "normal"),
    "texto_ayuda": ("Public Sans", 14, "normal"),
    "etiqueta": ("Public Sans", 12, "normal"),     # Recuerda aplicar .upper() en la vista
    "matricula": ("JetBrains Mono", 14, "normal")
}

# 4. Sistema de espaciado y bordes (radios en píxeles)
#A este diccionario no se accedera por el hecho de ser tkinter default y no tiene personalizacion de bordes
BORDES = {
    "etiqueta": 4,
    "boton": 8,
    "tarjeta": 8,
    "login": 16
}