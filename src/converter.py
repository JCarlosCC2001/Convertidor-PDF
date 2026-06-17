"""
Módulo principal de conversión de archivos a PDF.

Orquesta la conversión de imágenes y documentos Word, clasificando
los archivos por tipo y delegando al procesador correspondiente.
"""
import os
import logging
from PIL import Image, ImageOps
from src.config import (
    CALIDADES, guardar_configuracion, clasificar_archivo,
    es_archivo_valido, EXTENSIONES_IMAGEN
)
from src.word_converter import convertir_word_a_pdf

logger = logging.getLogger(__name__)


def procesar_imagen(ruta_img, modo_color, calidad_elegida, orientacion_auto=True):
    """Procesa una imagen para convertirla a PDF.
    
    Si orientacion_auto es True, detecta si la imagen es horizontal
    y genera la página en modo apaisado. De lo contrario, fuerza A4 vertical.
    """
    config_calidad = CALIDADES[calidad_elegida]
    ancho_base = config_calidad["ancho"]
    alto_base = config_calidad["alto"]

    with Image.open(ruta_img) as img:
        # Aplicar la orientación EXIF antes de cualquier operación
        img = ImageOps.exif_transpose(img)

        # Detección de orientación automática
        if orientacion_auto and img.width > img.height:
            # Imagen horizontal → página apaisada (intercambiar ancho y alto)
            ancho, alto = alto_base, ancho_base
            logger.debug("Imagen horizontal detectada: %s → página apaisada", os.path.basename(ruta_img))
        else:
            ancho, alto = ancho_base, alto_base

        # Aplicar modo de color
        if modo_color == "Blanco y Negro":
            img_rgb = img.convert("L").convert("RGB")
        else:
            img_rgb = img.convert("RGB")

        # ImageOps.fit recorta inteligentemente para llenar el tamaño exacto
        img_final = ImageOps.fit(img_rgb, (ancho, alto), method=Image.Resampling.LANCZOS)

        # Forzar la carga de los píxeles en memoria para no depender del archivo original
        img_final.load()
        return img_final


def _validar_archivos(rutas):
    """Valida todos los archivos antes de iniciar la conversión.
    
    Returns:
        list: Lista de mensajes de error. Vacía si todo está OK.
    """
    errores = []
    for ruta in rutas:
        valido, mensaje = es_archivo_valido(ruta)
        if not valido:
            errores.append(mensaje)
    return errores


def _determinar_ruta_salida(ruta_archivo, directorio_salida, nombre_personalizado=None, sufijo=""):
    """Determina la ruta de salida para un archivo PDF generado.
    
    Args:
        ruta_archivo: Ruta del archivo origen (para obtener la carpeta si no se especifica).
        directorio_salida: Carpeta destino. Si está vacía, usa la carpeta del origen.
        nombre_personalizado: Nombre del PDF (sin extensión). Si está vacío, usa el del archivo.
        sufijo: Sufijo a añadir al nombre (ej. "_bw" para blanco y negro).
    """
    if not directorio_salida:
        directorio_salida = os.path.dirname(ruta_archivo)

    if nombre_personalizado:
        nombre = nombre_personalizado + sufijo
    else:
        nombre = os.path.splitext(os.path.basename(ruta_archivo))[0] + sufijo

    return os.path.join(directorio_salida, f"{nombre}.pdf")


def ejecutar_conversion(
    rutas_archivos,
    opcion_union,
    opcion_color,
    calidad_elegida,
    directorio_salida="",
    nombre_personalizado="",
    orientacion_auto=True,
    callback_progreso=None,
):
    """Orquesta la conversión de todos los archivos a PDF.
    
    Clasifica los archivos por tipo (imagen/word) y enruta al procesador
    correspondiente. Soporta modo unido (un solo PDF) y dividido.
    
    Args:
        rutas_archivos: Lista de rutas a los archivos a convertir.
        opcion_union: "Unido" o "Dividido".
        opcion_color: "A Colores" o "Blanco y Negro".
        calidad_elegida: Clave de CALIDADES ("Baja", "Media", "Alta").
        directorio_salida: Carpeta de destino (vacío = misma del origen).
        nombre_personalizado: Nombre del PDF unido (vacío = automático).
        orientacion_auto: Si True, detectar orientación de imágenes.
        callback_progreso: Función callback(actual, total, mensaje).
    
    Returns:
        list: Lista de rutas de los PDFs generados.
    """
    if not rutas_archivos:
        raise ValueError("No se proporcionaron archivos para la conversión.")

    # Validar todos los archivos antes de empezar
    errores = _validar_archivos(rutas_archivos)
    if errores:
        raise ValueError("Archivos no válidos:\n• " + "\n• ".join(errores))

    # Guardar la configuración para la próxima vez
    guardar_configuracion(
        union=opcion_union,
        color=opcion_color,
        calidad=calidad_elegida,
        carpeta_salida=directorio_salida,
        nombre_archivo=nombre_personalizado,
        orientacion_auto=orientacion_auto,
    )

    # Clasificar archivos
    imagenes = []
    documentos_word = []
    for ruta in rutas_archivos:
        tipo = clasificar_archivo(ruta)
        if tipo == "imagen":
            imagenes.append(ruta)
        elif tipo == "word":
            documentos_word.append(ruta)

    config_calidad = CALIDADES[calidad_elegida]
    total_archivos = len(rutas_archivos)
    pdfs_generados = []
    contador = 0

    logger.info(
        "Iniciando conversión: %d imágenes, %d documentos Word | Modo: %s | Calidad: %s",
        len(imagenes), len(documentos_word), opcion_union, calidad_elegida
    )

    if opcion_union == "Unido":
        # --- MODO UNIDO: Todo en un solo PDF ---
        nombre_pdf = nombre_personalizado if nombre_personalizado else "archivos_unidos"
        if not directorio_salida:
            directorio_salida = os.path.dirname(rutas_archivos[0])
        ruta_final = os.path.join(directorio_salida, f"{nombre_pdf}.pdf")

        # Para modo unido, solo se soportan imágenes (Word tiene formato propio)
        if documentos_word and not imagenes:
            # Solo hay documentos Word → convertirlos individualmente
            for idx, ruta in enumerate(documentos_word, start=1):
                contador += 1
                if callback_progreso:
                    callback_progreso(contador, total_archivos, f"Convirtiendo Word {idx}/{len(documentos_word)}...")

                ruta_pdf = _determinar_ruta_salida(ruta, directorio_salida)
                convertir_word_a_pdf(ruta, ruta_pdf, callback_progreso, contador, total_archivos)
                pdfs_generados.append(ruta_pdf)

        elif imagenes:
            # Procesar primera imagen
            contador += 1
            if callback_progreso:
                callback_progreso(contador, total_archivos, f"Procesando imagen 1 de {len(imagenes)}...")

            primera_img = procesar_imagen(imagenes[0], opcion_color, calidad_elegida, orientacion_auto)

            # Generador perezoso para las imágenes restantes
            def generador_imagenes():
                nonlocal contador
                for idx, r in enumerate(imagenes[1:], start=2):
                    contador += 1
                    if callback_progreso:
                        callback_progreso(contador, total_archivos, f"Procesando imagen {idx} de {len(imagenes)}...")
                    yield procesar_imagen(r, opcion_color, calidad_elegida, orientacion_auto)

            primera_img.save(
                ruta_final,
                "PDF",
                save_all=True,
                append_images=generador_imagenes(),
                resolution=config_calidad["dpi"],
                quality=config_calidad["compresion"],
            )
            primera_img.close()
            pdfs_generados.append(ruta_final)

            # Convertir documentos Word aparte (no se pueden mezclar en el PDF de imágenes)
            for idx, ruta in enumerate(documentos_word, start=1):
                contador += 1
                if callback_progreso:
                    callback_progreso(contador, total_archivos, f"Convirtiendo Word {idx}/{len(documentos_word)}...")

                ruta_pdf = _determinar_ruta_salida(ruta, directorio_salida)
                convertir_word_a_pdf(ruta, ruta_pdf, callback_progreso, contador, total_archivos)
                pdfs_generados.append(ruta_pdf)

    else:
        # --- MODO DIVIDIDO: Un PDF por archivo ---
        for idx, ruta in enumerate(rutas_archivos, start=1):
            contador += 1
            tipo = clasificar_archivo(ruta)

            if tipo == "imagen":
                if callback_progreso:
                    callback_progreso(contador, total_archivos, f"Procesando imagen {idx} de {total_archivos}...")

                img_procesada = procesar_imagen(ruta, opcion_color, calidad_elegida, orientacion_auto)
                ruta_pdf = _determinar_ruta_salida(ruta, directorio_salida)

                img_procesada.save(
                    ruta_pdf,
                    "PDF",
                    resolution=config_calidad["dpi"],
                    quality=config_calidad["compresion"],
                )
                img_procesada.close()
                pdfs_generados.append(ruta_pdf)

            elif tipo == "word":
                if callback_progreso:
                    callback_progreso(contador, total_archivos, f"Convirtiendo Word {idx} de {total_archivos}...")

                ruta_pdf = _determinar_ruta_salida(ruta, directorio_salida)
                convertir_word_a_pdf(ruta, ruta_pdf, callback_progreso, contador, total_archivos)
                pdfs_generados.append(ruta_pdf)

    if callback_progreso:
        callback_progreso(total_archivos, total_archivos, "¡Conversión finalizada con éxito!")

    logger.info("Conversión completada. PDFs generados: %d", len(pdfs_generados))
    return pdfs_generados
