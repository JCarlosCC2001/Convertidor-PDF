import os
import logging
import fitz  # PyMuPDF
from src.config import CALIDADES

logger = logging.getLogger(__name__)

def convertir_pdf_a_imagen_batch(
    rutas_archivos, 
    calidad_elegida, 
    modo_color, 
    directorio_salida, 
    callback_progreso=None
):
    """
    Convierte las páginas de los PDFs en imágenes individuales (PNG o JPG).
    """
    archivos_generados = []
    
    # Obtener DPI configurado
    config_calidad = CALIDADES.get(calidad_elegida, CALIDADES["Media"])
    dpi = config_calidad["dpi"]
    
    # Configuración de color para PyMuPDF
    if modo_color == "Blanco y Negro":
        color_space = fitz.csGRAY
        formato_img = "png" # PNG es mejor para escala de grises limpio sin artefactos
    else:
        color_space = fitz.csRGB
        formato_img = "jpg"

    # Calcular el total de páginas de todos los PDFs para el progreso
    total_paginas = 0
    try:
        for ruta in rutas_archivos:
            with fitz.open(ruta) as doc:
                total_paginas += len(doc)
    except Exception as e:
        logger.error("Error al contar páginas: %s", e)
        raise Exception(f"No se pudo leer uno de los archivos PDF: {str(e)}")

    if total_paginas == 0:
        return []

    paginas_procesadas = 0

    for ruta in rutas_archivos:
        nombre_base = os.path.splitext(os.path.basename(ruta))[0]
        
        if not directorio_salida:
            dir_salida_actual = os.path.dirname(ruta)
        else:
            dir_salida_actual = directorio_salida
            
        try:
            doc = fitz.open(ruta)
            
            for num_pag in range(len(doc)):
                paginas_procesadas += 1
                
                if callback_progreso:
                    callback_progreso(
                        paginas_procesadas, 
                        total_paginas, 
                        f"Renderizando pág. {num_pag + 1} de {nombre_base}..."
                    )
                
                pagina = doc.load_page(num_pag)
                
                # Rasterizar página a píxeles
                pix = pagina.get_pixmap(colorspace=color_space, dpi=int(dpi))
                
                # Nombre de la imagen (ej: MiDocumento_pag_1.jpg)
                ruta_salida = os.path.join(dir_salida_actual, f"{nombre_base}_pag_{num_pag + 1}.{formato_img}")
                
                # Guardar
                pix.save(ruta_salida)
                archivos_generados.append(ruta_salida)
                
            doc.close()
            
        except Exception as e:
            logger.error("Error renderizando PDF %s a imagen: %s", ruta, str(e))
            raise Exception(f"Error procesando {os.path.basename(ruta)}:\n{str(e)}")
            
    if callback_progreso:
        callback_progreso(total_paginas, total_paginas, "¡Conversión de PDF a Imagen finalizada!")
        
    return archivos_generados
