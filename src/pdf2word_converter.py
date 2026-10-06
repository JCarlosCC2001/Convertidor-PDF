import os
import logging
from pdf2docx import Converter

logger = logging.getLogger(__name__)

def convertir_pdf_a_word_batch(rutas_archivos, directorio_salida, callback_progreso=None):
    """
    Convierte una lista de archivos PDF a formato Word (.docx).
    """
    archivos_generados = []
    total_archivos = len(rutas_archivos)
    
    for idx, ruta in enumerate(rutas_archivos, start=1):
        if callback_progreso:
            callback_progreso(idx, total_archivos, f"Convirtiendo a Word: {os.path.basename(ruta)}...")
            
        nombre = os.path.splitext(os.path.basename(ruta))[0]
        
        if not directorio_salida:
            dir_salida_actual = os.path.dirname(ruta)
        else:
            dir_salida_actual = directorio_salida
            
        ruta_salida = os.path.join(dir_salida_actual, f"{nombre}.docx")
        
        # Evitar sobreescribir el archivo original si tuviera la misma extensión (improbable, pero seguro)
        if os.path.abspath(ruta_salida) == os.path.abspath(ruta):
            ruta_salida = os.path.join(dir_salida_actual, f"{nombre}_convertido.docx")
            
        try:
            cv = Converter(ruta)
            cv.convert(ruta_salida, start=0, end=None)
            cv.close()
            archivos_generados.append(ruta_salida)
        except Exception as e:
            logger.error("Error convirtiendo %s a Word: %s", ruta, str(e))
            raise Exception(f"Error procesando {os.path.basename(ruta)}:\n{str(e)}")
            
    if callback_progreso:
        callback_progreso(total_archivos, total_archivos, "¡Conversión finalizada!")
        
    return archivos_generados
