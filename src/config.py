import os
import json
import logging

logger = logging.getLogger(__name__)

# --- Versión de la Aplicación ---
VERSION = "1.0.0"

# --- Extensiones de archivos soportados ---
EXTENSIONES_IMAGEN = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tiff", ".tif"}
EXTENSIONES_WORD = {".docx"}
EXTENSIONES_SOPORTADAS = EXTENSIONES_IMAGEN | EXTENSIONES_WORD

# --- Ruta del archivo de configuración (relativa al script, no al CWD) ---
_DIR_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARCHIVO_CONFIG = os.path.join(_DIR_BASE, "configuracion_pdf.json")

# --- Calidades de salida (Formato A4) ---
CALIDADES = {
    "Baja": {
        "ancho": 595,
        "alto": 842,
        "dpi": 72.0,
        "compresion": 70,
        "label": "Baja (72 DPI)",
        "descripcion": "Archivo liviano, ideal para lectura en pantalla"
    },
    "Media": {
        "ancho": 1240,
        "alto": 1754,
        "dpi": 150.0,
        "compresion": 85,
        "label": "Media (150 DPI)",
        "descripcion": "Equilibrio entre calidad y tamaño de archivo"
    },
    "Alta": {
        "ancho": 2480,
        "alto": 3508,
        "dpi": 300.0,
        "compresion": 100,
        "label": "Alta (300 DPI)",
        "descripcion": "Máxima calidad, ideal para impresión profesional"
    }
}

# --- Valores por defecto de la configuración ---
CONFIG_DEFECTO = {
    "union": "Unido",
    "color": "A Colores",
    "calidad": "Alta",
    "carpeta_salida": "",       # Vacío = misma carpeta del archivo origen
    "nombre_archivo": "",       # Vacío = nombre automático
    "orientacion_auto": True    # Detectar orientación horizontal/vertical
}


def cargar_configuracion():
    """Carga la última configuración guardada o usa los valores por defecto."""
    if os.path.exists(ARCHIVO_CONFIG):
        try:
            with open(ARCHIVO_CONFIG, "r", encoding="utf-8") as f:
                config_guardada = json.load(f)
            # Mezclar con los valores por defecto para que los campos nuevos siempre existan
            config_completa = {**CONFIG_DEFECTO, **config_guardada}
            logger.info("Configuración cargada desde %s", ARCHIVO_CONFIG)
            return config_completa
        except (json.JSONDecodeError, OSError) as e:
            logger.warning("No se pudo leer la configuración: %s. Usando valores por defecto.", e)
    return dict(CONFIG_DEFECTO)


def guardar_configuracion(**kwargs):
    """Guarda las selecciones actuales para la próxima vez.
    
    Acepta argumentos con nombre para guardar solo los campos proporcionados,
    manteniendo los demás valores existentes.
    """
    config_actual = cargar_configuracion()
    config_actual.update(kwargs)
    try:
        with open(ARCHIVO_CONFIG, "w", encoding="utf-8") as f:
            json.dump(config_actual, f, indent=4, ensure_ascii=False)
        logger.info("Configuración guardada exitosamente.")
    except OSError as e:
        logger.error("No se pudo guardar la configuración: %s", e)


def clasificar_archivo(ruta):
    """Clasifica un archivo como 'imagen', 'word' o None según su extensión."""
    ext = os.path.splitext(ruta)[1].lower()
    if ext in EXTENSIONES_IMAGEN:
        return "imagen"
    elif ext in EXTENSIONES_WORD:
        return "word"
    return None


def es_archivo_valido(ruta):
    """Verifica que un archivo exista, sea legible y tenga una extensión soportada."""
    if not os.path.isfile(ruta):
        return False, f"El archivo no existe: {os.path.basename(ruta)}"
    if not os.access(ruta, os.R_OK):
        return False, f"Sin permisos de lectura: {os.path.basename(ruta)}"
    if clasificar_archivo(ruta) is None:
        ext = os.path.splitext(ruta)[1]
        return False, f"Formato no soportado ({ext}): {os.path.basename(ruta)}"
    return True, ""
