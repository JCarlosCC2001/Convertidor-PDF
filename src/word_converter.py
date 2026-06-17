"""
Módulo de conversión Word (.docx) → PDF.

Usa python-docx para leer el contenido del documento y reportlab
para generar el PDF con formato preservado (negritas, cursivas,
encabezados, tablas y listas con viñetas).
"""
import os
import logging

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
)
from reportlab.lib import colors

logger = logging.getLogger(__name__)

# Márgenes del PDF generado
MARGEN = 2 * cm


def _obtener_estilos():
    """Crea y retorna los estilos de párrafo para el PDF."""
    estilos = getSampleStyleSheet()

    estilos.add(ParagraphStyle(
        name="Cuerpo",
        parent=estilos["Normal"],
        fontName="Helvetica",
        fontSize=11,
        leading=15,
        spaceAfter=6,
    ))
    estilos.add(ParagraphStyle(
        name="Encabezado1",
        parent=estilos["Normal"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        spaceAfter=10,
        spaceBefore=12,
    ))
    estilos.add(ParagraphStyle(
        name="Encabezado2",
        parent=estilos["Normal"],
        fontName="Helvetica-Bold",
        fontSize=15,
        leading=19,
        spaceAfter=8,
        spaceBefore=10,
    ))
    estilos.add(ParagraphStyle(
        name="Encabezado3",
        parent=estilos["Normal"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=17,
        spaceAfter=6,
        spaceBefore=8,
    ))
    estilos.add(ParagraphStyle(
        name="ListaViñeta",
        parent=estilos["Normal"],
        fontName="Helvetica",
        fontSize=11,
        leading=15,
        spaceAfter=4,
        leftIndent=20,
        bulletIndent=10,
    ))

    return estilos


def _mapear_alineacion(alineacion_docx):
    """Convierte la alineación de Word a la de reportlab."""
    mapa = {
        WD_ALIGN_PARAGRAPH.LEFT: TA_LEFT,
        WD_ALIGN_PARAGRAPH.CENTER: TA_CENTER,
        WD_ALIGN_PARAGRAPH.RIGHT: TA_RIGHT,
        WD_ALIGN_PARAGRAPH.JUSTIFY: TA_JUSTIFY,
    }
    return mapa.get(alineacion_docx, TA_LEFT)


def _run_a_html(run):
    """Convierte un Run de python-docx a fragmento HTML para reportlab."""
    texto = run.text
    if not texto:
        return ""
    # Escapar caracteres especiales de XML/HTML
    texto = texto.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    if run.bold:
        texto = f"<b>{texto}</b>"
    if run.italic:
        texto = f"<i>{texto}</i>"
    if run.underline:
        texto = f"<u>{texto}</u>"

    return texto


def _es_elemento_lista(parrafo):
    """Detecta si un párrafo es un elemento de lista (tiene viñetas o numeración)."""
    pPr = parrafo._element.find(qn('w:pPr'))
    if pPr is not None:
        numPr = pPr.find(qn('w:numPr'))
        if numPr is not None:
            return True
    return False


def _procesar_parrafo(parrafo, estilos):
    """Convierte un párrafo de Word a un elemento Flowable de reportlab."""
    # Determinar el estilo según el nivel de encabezado
    nombre_estilo_docx = parrafo.style.name if parrafo.style else ""

    if nombre_estilo_docx.startswith("Heading 1") or nombre_estilo_docx.startswith("Título 1"):
        estilo = estilos["Encabezado1"]
    elif nombre_estilo_docx.startswith("Heading 2") or nombre_estilo_docx.startswith("Título 2"):
        estilo = estilos["Encabezado2"]
    elif nombre_estilo_docx.startswith("Heading 3") or nombre_estilo_docx.startswith("Título 3"):
        estilo = estilos["Encabezado3"]
    elif _es_elemento_lista(parrafo):
        estilo = estilos["ListaViñeta"]
    else:
        estilo = estilos["Cuerpo"]

    # Aplicar alineación del párrafo
    if parrafo.alignment is not None:
        estilo = ParagraphStyle(
            name=f"{estilo.name}_alineado",
            parent=estilo,
            alignment=_mapear_alineacion(parrafo.alignment),
        )

    # Construir el contenido HTML a partir de los runs
    contenido_html = "".join(_run_a_html(run) for run in parrafo.runs)

    if not contenido_html.strip():
        return Spacer(1, 6)

    # Agregar viñeta si es lista
    if _es_elemento_lista(parrafo):
        contenido_html = f"• {contenido_html}"

    return Paragraph(contenido_html, estilo)


def _procesar_tabla(tabla, estilos):
    """Convierte una tabla de Word a una Table de reportlab."""
    datos = []
    for fila in tabla.rows:
        fila_datos = []
        for celda in fila.cells:
            # Unir todos los párrafos de la celda
            texto_celda = "\n".join(p.text for p in celda.paragraphs)
            fila_datos.append(Paragraph(texto_celda, estilos["Cuerpo"]))
        datos.append(fila_datos)

    if not datos:
        return Spacer(1, 6)

    ancho_disponible = A4[0] - (2 * MARGEN)
    num_cols = max(len(fila) for fila in datos) if datos else 1
    ancho_col = ancho_disponible / num_cols

    tabla_pdf = Table(datos, colWidths=[ancho_col] * num_cols)
    tabla_pdf.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#002060")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#003399")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f0f4fa")]),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))

    return tabla_pdf


def convertir_word_a_pdf(ruta_docx, ruta_salida_pdf, callback_progreso=None, indice=1, total=1):
    """Convierte un archivo Word (.docx) a PDF preservando formato básico.
    
    Args:
        ruta_docx: Ruta al archivo .docx de entrada.
        ruta_salida_pdf: Ruta completa del PDF de salida.
        callback_progreso: Función callback(actual, total, mensaje) para reportar progreso.
        indice: Número del archivo actual (para el callback).
        total: Total de archivos (para el callback).
    """
    logger.info("Convirtiendo Word → PDF: %s", os.path.basename(ruta_docx))

    if callback_progreso:
        callback_progreso(indice, total, f"Leyendo documento Word: {os.path.basename(ruta_docx)}...")

    doc = Document(ruta_docx)
    estilos = _obtener_estilos()

    # Construir la lista de elementos flowable
    elementos = []

    for elemento in doc.element.body:
        tag = elemento.tag.split("}")[-1] if "}" in elemento.tag else elemento.tag

        if tag == "p":
            # Es un párrafo
            from docx.text.paragraph import Paragraph as DocxParagraph
            parrafo = DocxParagraph(elemento, doc)
            flowable = _procesar_parrafo(parrafo, estilos)
            elementos.append(flowable)

        elif tag == "tbl":
            # Es una tabla
            from docx.table import Table as DocxTable
            tabla = DocxTable(elemento, doc)
            elementos.append(Spacer(1, 6))
            elementos.append(_procesar_tabla(tabla, estilos))
            elementos.append(Spacer(1, 6))

    # Si el documento está vacío, agregar un espacio para evitar error
    if not elementos:
        elementos.append(Spacer(1, 12))

    if callback_progreso:
        callback_progreso(indice, total, f"Generando PDF: {os.path.basename(ruta_salida_pdf)}...")

    # Generar el PDF
    pdf = SimpleDocTemplate(
        ruta_salida_pdf,
        pagesize=A4,
        leftMargin=MARGEN,
        rightMargin=MARGEN,
        topMargin=MARGEN,
        bottomMargin=MARGEN,
        title=os.path.splitext(os.path.basename(ruta_docx))[0],
    )
    pdf.build(elementos)

    logger.info("PDF generado exitosamente: %s", ruta_salida_pdf)
