import os
from PIL import Image, ImageOps
from src.config import CALIDADES, guardar_configuracion

def procesar_imagen(ruta_img, modo_color, calidad_elegida):
    """Procesa la imagen para que llene completamente el A4 sin dejar márgenes.
    
    Abre la imagen usando un administrador de contexto para asegurar que el archivo
    se cierre inmediatamente y carga los datos en memoria para evitar dependencias
    de archivo abierto.
    """
    config_calidad = CALIDADES[calidad_elegida]
    ancho = config_calidad["ancho"]
    alto = config_calidad["alto"]
    
    with Image.open(ruta_img) as img:
        # Orientación de la imagen: si está en horizontal, Pillow la rotará si es necesario
        # o podemos mantener la orientación estándar convirtiendo a RGB
        if modo_color == "Blanco y Negro":
            img_rgb = img.convert("L").convert("RGB")
        else:
            img_rgb = img.convert("RGB")
        
        # ImageOps.fit recorta inteligentemente para llenar el tamaño A4 exacto
        img_sin_margen = ImageOps.fit(img_rgb, (ancho, alto), method=Image.Resampling.LANCZOS)
        
        # Forzar la carga de los píxeles en memoria para que no dependa del archivo original
        img_sin_margen.load()
        return img_sin_margen

def ejecutar_conversion(rutas_imagenes, opcion_union, opcion_color, calidad_elegida, callback_progreso=None):
    """Genera los PDFs y guarda las preferencias del usuario.
    
    Usa procesamiento diferido (generador) para la opción "Unido", reduciendo
    drásticamente el consumo de RAM.
    """
    if not rutas_imagenes:
        raise ValueError("No se proporcionaron imágenes para la conversión.")
        
    # Guardar la configuración para la próxima vez
    guardar_configuracion(opcion_union, opcion_color, calidad_elegida)
    
    directorio_salida = os.path.dirname(rutas_imagenes[0])
    config_calidad = CALIDADES[calidad_elegida]
    total_imagenes = len(rutas_imagenes)
    
    if opcion_union == "Unido":
        ruta_final = os.path.join(directorio_salida, "imagenes_unidas.pdf")
        
        # Procesar y cargar la primera imagen
        if callback_progreso:
            callback_progreso(1, total_imagenes, f"Procesando imagen 1 de {total_imagenes}...")
            
        primera_img = procesar_imagen(rutas_imagenes[0], opcion_color, calidad_elegida)
        
        # Generador perezoso para procesar las imágenes subsecuentes una a una
        def generador_imagenes():
            for idx, r in enumerate(rutas_imagenes[1:], start=2):
                if callback_progreso:
                    callback_progreso(idx, total_imagenes, f"Procesando imagen {idx} de {total_imagenes}...")
                img_proc = procesar_imagen(r, opcion_color, calidad_elegida)
                yield img_proc
        
        # Guardar en PDF unificado
        primera_img.save(
            ruta_final, 
            "PDF", 
            save_all=True, 
            append_images=generador_imagenes(),
            resolution=config_calidad["dpi"],
            quality=config_calidad["compresion"]
        )
        primera_img.close()
        
    else:  # Divididos
        for idx, r in enumerate(rutas_imagenes, start=1):
            if callback_progreso:
                callback_progreso(idx, total_imagenes, f"Procesando imagen {idx} de {total_imagenes}...")
                
            img_procesada = procesar_imagen(r, opcion_color, calidad_elegida)
            nombre_base = os.path.splitext(os.path.basename(r))[0]
            ruta_final = os.path.join(directorio_salida, f"{nombre_base}.pdf")
            
            img_procesada.save(
                ruta_final, 
                "PDF",
                resolution=config_calidad["dpi"],
                quality=config_calidad["compresion"]
            )
            img_procesada.close()
            
    if callback_progreso:
        callback_progreso(total_imagenes, total_imagenes, "¡Conversión finalizada con éxito!")
