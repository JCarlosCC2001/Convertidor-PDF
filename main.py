import sys
import logging
import tkinter as tk
import traceback
from tkinter import messagebox
from src.config import EXTENSIONES_SOPORTADAS
from src.gui import ConvertidorGUI

# Configurar logging al inicio
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def filtrar_archivos_validos(rutas):
    """Filtra los archivos pasados por argumentos, manteniendo solo los soportados."""
    import os
    validos = []
    for ruta in rutas:
        ext = os.path.splitext(ruta)[1].lower()
        if ext in EXTENSIONES_SOPORTADAS and os.path.isfile(ruta):
            validos.append(ruta)
        else:
            logger.warning("Archivo ignorado (no soportado o no existe): %s", ruta)
    return validos


def mostrar_error_critico(titulo, error):
    """Muestra un mensaje de error si ocurre un problema al inicializar la aplicación."""
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror(titulo, f"Detalle del error técnico de inicio:\n\n{error}")
    root.destroy()


def main():
    """Punto de entrada principal de la aplicación."""
    try:
        # Recuperar archivos pasados como argumentos (ej. al arrastrar y soltar)
        archivos_raw = sys.argv[1:]
        archivos = filtrar_archivos_validos(archivos_raw)

        if archivos:
            logger.info("Archivos recibidos por argumento: %d", len(archivos))

        # Inicializar la interfaz gráfica de usuario
        root = tk.Tk()
        _app = ConvertidorGUI(root, rutas_iniciales=archivos)
        root.mainloop()

    except Exception:
        error_completo = traceback.format_exc()
        logger.critical("Error crítico de inicio:\n%s", error_completo)
        mostrar_error_critico("Error Crítico de Inicio", error_completo)


if __name__ == "__main__":
    main()