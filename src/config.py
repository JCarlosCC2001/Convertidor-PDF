import os
import json

# Archivo donde se guardarán las preferencias del usuario
ARCHIVO_CONFIG = "configuracion_pdf.json"

# Diccionario con las resoluciones según la calidad elegida
CALIDADES = {
    "Baja": {
        "ancho": 595,
        "alto": 842,
        "dpi": 72.0,
        "compresion": 70,
        "label": "Baja (72 DPI)"
    },
    "Media": {
        "ancho": 1240,
        "alto": 1754,
        "dpi": 150.0,
        "compresion": 85,
        "label": "Media (150 DPI)"
    },
    "Alta": {
        "ancho": 2480,
        "alto": 3508,
        "dpi": 300.0,
        "compresion": 100,
        "label": "Alta (300 DPI)"
    }
}

def cargar_configuracion():
    """Carga la última configuración guardada o usa los valores por defecto."""
    if os.path.exists(ARCHIVO_CONFIG):
        try:
            with open(ARCHIVO_CONFIG, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    # Valores por defecto por si el archivo no existe o está corrupto
    return {"union": "Unido", "color": "A Colores", "calidad": "Alta"}

def guardar_configuracion(union, color, calidad):
    """Guarda las selecciones actuales para la próxima vez."""
    config = {"union": union, "color": color, "calidad": calidad}
    try:
        with open(ARCHIVO_CONFIG, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4)
    except Exception as e:
        print(f"No se pudo guardar la configuración: {e}")
