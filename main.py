import sys
import os
from PIL import Image, ImageOps
import tkinter as tk
from tkinter import messagebox, ttk

import traceback # Añade esto arriba con los otros imports

if __name__ == "__main__":
    try:
        archivos = sys.argv[1:]
        if not archivos:
            # Si se abre vacío, solo salimos
            sys.exit(0)
        lanzar_interfaz(archivos)
    except Exception as e:
        # Esto creará un archivo 'error_log.txt' en la misma carpeta si algo falla
        with open("error_log.txt", "w") as f:
            f.write(traceback.format_exc())
# Dimensiones estándar de A4 a 300 DPI (píxeles: 2480 x 3508)
# Para evitar PDFs gigantescos, usamos una escala estándar de 72 DPI: 595 x 842 puntos
A4_ANCHO, A4_ALTO = 595, 842

def procesar_imagen(ruta_img, modo_color):
    """Abre la imagen, la convierte al color deseado y la ajusta a A4 Vertical"""
    img = Image.open(ruta_img)
    
    # 1. Configurar color (Blanco y Negro o Colores)
    if modo_color == "Blanco y Negro":
        img = img.convert("L").convert("RGB")
    else:
        img = img.convert("RGB")
    
    # 2. Ajustar a tamaño A4 Vertical manteniendo la proporción (Letterbox/Proporcional)
    # Creamos un lienzo blanco tamaño A4
    lienzo_a4 = Image.new("RGB", (A4_ANCHO, A4_ALTO), "white")
    
    # Redimensionamos la imagen original para que quepa en el A4
    img.thumbnail((A4_ANCHO, A4_ALTO), Image.Resampling.LANCZOS)
    
    # Centrar la imagen en el lienzo A4
    x = (A4_ANCHO - img.width) // 2
    y = (A4_ALTO - img.height) // 2
    lienzo_a4.paste(img, (x, y))
    
    return lienzo_a4

def ejecutar_conversion(rutas_imagenes, opcion_union, opcion_color):
    try:
        directorio_salida = os.path.dirname(rutas_imagenes[0])
        
        if opcion_union == "Unido (Un solo PDF)":
            imagenes_listas = [procesar_imagen(r, opcion_color) for r in rutas_imagenes]
            ruta_final = os.path.join(directorio_salida, "imagenes_unidas.pdf")
            
            # Guardar todo en uno
            imagenes_listas[0].save(
                ruta_final, "PDF", save_all=True, append_images=imagenes_listas[1:]
            )
            
        else: # Divididos (Un PDF por cada imagen)
            for r in rutas_imagenes:
                img_procesada = procesar_imagen(r, opcion_color)
                nombre_base = os.path.splitext(os.path.basename(r))[0]
                ruta_final = os.path.join(directorio_salida, f"{nombre_base}.pdf")
                img_procesada.save(ruta_final, "PDF")
                
        messagebox.showinfo("Éxito", "¡Conversión completada con éxito!")
        sys.exit(0)
        
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error: {str(e)}")

def lanzar_interfaz(rutas_imagenes):
    # Crear ventana de opciones
    ventana = tk.Tk()
    ventana.title("Convertidor a PDF (A4 Vertical)")
    ventana.geometry("350x250")
    ventana.resizable(False, False)
    
    tk.Label(ventana, text=f"Archivos seleccionados: {len(rutas_imagenes)}", font=("Arial", 10, "bold")).pack(pady=10)
    
    # Opción de Unión/División
    tk.Label(ventana, text="¿Cómo deseas los archivos?").pack()
    combo_union = ttk.Combobox(ventana, values=["Unido (Un solo PDF)", "Dividido (Un PDF por imagen)"], state="readonly")
    combo_union.set("Unido (Un solo PDF)")
    combo_union.pack(pady=5)
    
    # Opción de Color
    tk.Label(ventana, text="Configuración de color:").pack()
    combo_color = ttk.Combobox(ventana, values=["A Colores", "Blanco y Negro"], state="readonly")
    combo_color.set("A Colores")
    combo_color.pack(pady=5)
    
    # Botón de acción
    btn_convertir = tk.Button(
        ventana, 
        text="Transformar a PDF", 
        bg="#4CAF50", 
        fg="white", 
        font=("Arial", 11, "bold"),
        command=lambda: ejecutar_conversion(rutas_imagenes, combo_union.get(), combo_color.get())
    )
    btn_convertir.pack(pady=20)
    
    ventana.mainloop()

if __name__ == "__main__":
    # Windows pasa los archivos seleccionados como argumentos de línea de comandos (sys.argv)
    # sys.argv[0] es la ruta del script, el resto son las imágenes
    archivos = sys.argv[1:]
    
    if not archivos:
        # Si se abre el script sin seleccionar archivos por error
        root = tk.Tk()
        root.withdraw()
        messagebox.showwarning("Advertencia", "No se seleccionó ninguna imagen.")
    else:
        lanzar_interfaz(archivos)