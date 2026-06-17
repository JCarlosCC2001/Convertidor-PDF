import sys
import os
import json
from PIL import Image, ImageOps
import tkinter as tk
from tkinter import messagebox
import traceback

# Archivo donde se guardarán tus preferencias
ARCHIVO_CONFIG = "configuracion_pdf.json"

# Diccionario con las resoluciones según la calidad elegida
CALIDADES = {
    "Baja": {"ancho": 595, "alto": 842, "dpi": 72.0, "compresion": 70},   # Calidad original
    "Media": {"ancho": 1240, "alto": 1754, "dpi": 150.0, "compresion": 85}, # Calidad intermedia
    "Alta": {"ancho": 2480, "alto": 3508, "dpi": 300.0, "compresion": 100}  # Máxima calidad
}

def cargar_configuracion():
    """Carga la última configuración guardada o usa los valores por defecto."""
    if os.path.exists(ARCHIVO_CONFIG):
        try:
            with open(ARCHIVO_CONFIG, "r") as f:
                return json.load(f)
        except:
            pass
    return {"union": "Unido", "color": "A Colores", "calidad": "Alta"}

def guardar_configuracion(union, color, calidad):
    """Guarda las selecciones actuales para la próxima vez."""
    config = {"union": union, "color": color, "calidad": calidad}
    try:
        with open(ARCHIVO_CONFIG, "w") as f:
            json.dump(config, f)
    except Exception as e:
        print(f"No se pudo guardar la configuración: {e}")

def mostrar_error(titulo, error):
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror(titulo, f"Detalle del error técnico:\n\n{error}")
    root.destroy()

def procesar_imagen(ruta_img, modo_color, calidad_elegida):
    """Procesa la imagen para que llene completamente el A4 sin dejar márgenes."""
    config_calidad = CALIDADES[calidad_elegida]
    ancho = config_calidad["ancho"]
    alto = config_calidad["alto"]
    
    img = Image.open(ruta_img)
    
    if modo_color == "Blanco y Negro":
        img = img.convert("L").convert("RGB")
    else:
        img = img.convert("RGB")
    
    # ImageOps.fit recorta la imagen de forma inteligente para que llene el tamaño A4 
    # exacto (ancho y alto) sin estirarse ni deformarse, eliminando los márgenes.
    img_sin_margen = ImageOps.fit(img, (ancho, alto), method=Image.Resampling.LANCZOS)
    
    return img_sin_margen

def ejecutar_conversion(rutas_imagenes, opcion_union, opcion_color, calidad_elegida):
    """Genera los PDFs y guarda las preferencias del usuario."""
    try:
        # Guardar la configuración para la próxima vez que se abra el programa
        guardar_configuracion(opcion_union, opcion_color, calidad_elegida)
        
        directorio_salida = os.path.dirname(rutas_imagenes[0])
        config_calidad = CALIDADES[calidad_elegida]
        
        if opcion_union == "Unido":
            imagenes_listas = [procesar_imagen(r, opcion_color, calidad_elegida) for r in rutas_imagenes]
            ruta_final = os.path.join(directorio_salida, "imagenes_unidas.pdf")
            
            imagenes_listas[0].save(
                ruta_final, 
                "PDF", 
                save_all=True, 
                append_images=imagenes_listas[1:],
                resolution=config_calidad["dpi"],
                quality=config_calidad["compresion"]
            )
            
        else: # Divididos
            for r in rutas_imagenes:
                img_procesada = procesar_imagen(r, opcion_color, calidad_elegida)
                nombre_base = os.path.splitext(os.path.basename(r))[0]
                ruta_final = os.path.join(directorio_salida, f"{nombre_base}.pdf")
                
                img_procesada.save(
                    ruta_final, 
                    "PDF",
                    resolution=config_calidad["dpi"],
                    quality=config_calidad["compresion"]
                )
                
        messagebox.showinfo("Éxito", f"¡Conversión completada!\nCalidad utilizada: {calidad_elegida}")
        sys.exit(0)
        
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error: {str(e)}")

def lanzar_interfaz(rutas_imagenes):
    ventana = tk.Tk()
    ventana.title("Convertidor PDF")
    ventana.geometry("380x360")
    ventana.resizable(False, False)
    
    try:
        ventana.iconbitmap("logo.ico")
    except:
        pass
        
    # Cargar las opciones previas
    config_guardada = cargar_configuracion()
    
    # Variables de Tkinter para los Radiobuttons
    var_union = tk.StringVar(value=config_guardada.get("union", "Unido"))
    var_color = tk.StringVar(value=config_guardada.get("color", "A Colores"))
    var_calidad = tk.StringVar(value=config_guardada.get("calidad", "Alta"))
    
    tk.Label(ventana, text=f"Archivos seleccionados: {len(rutas_imagenes)}", font=("Arial", 10, "bold")).pack(pady=10)
    
    # --- SECCIÓN: FORMATO DE SALIDA ---
    marco_union = tk.LabelFrame(ventana, text="Formato de salida")
    marco_union.pack(fill="x", padx=20, pady=5)
    tk.Radiobutton(marco_union, text="Unido (Un solo PDF)", variable=var_union, value="Unido").pack(anchor="w", padx=10)
    tk.Radiobutton(marco_union, text="Dividido (Un PDF por imagen)", variable=var_union, value="Dividido").pack(anchor="w", padx=10)
    
    # --- SECCIÓN: COLOR ---
    marco_color = tk.LabelFrame(ventana, text="Configuración de Color")
    marco_color.pack(fill="x", padx=20, pady=5)
    tk.Radiobutton(marco_color, text="A Colores", variable=var_color, value="A Colores").pack(anchor="w", padx=10)
    tk.Radiobutton(marco_color, text="Blanco y Negro", variable=var_color, value="Blanco y Negro").pack(anchor="w", padx=10)

    # --- SECCIÓN: CALIDAD ---
    marco_calidad = tk.LabelFrame(ventana, text="Calidad del PDF (A4 Vertical)")
    marco_calidad.pack(fill="x", padx=20, pady=5)
    # Organizamos los radiobuttons de calidad en una línea horizontal
    frame_radios_calidad = tk.Frame(marco_calidad)
    frame_radios_calidad.pack(pady=5)
    tk.Radiobutton(frame_radios_calidad, text="Baja", variable=var_calidad, value="Baja").pack(side="left", padx=10)
    tk.Radiobutton(frame_radios_calidad, text="Media", variable=var_calidad, value="Media").pack(side="left", padx=10)
    tk.Radiobutton(frame_radios_calidad, text="Alta (300 DPI)", variable=var_calidad, value="Alta").pack(side="left", padx=10)
    
    # --- BOTÓN DE ACCIÓN ---
    btn_convertir = tk.Button(
        ventana, 
        text="Transformar a PDF", 
        bg="#4CAF50", 
        fg="white", 
        font=("Arial", 11, "bold"),
        command=lambda: ejecutar_conversion(rutas_imagenes, var_union.get(), var_color.get(), var_calidad.get())
    )
    btn_convertir.pack(pady=15)
    
    ventana.mainloop()

if __name__ == "__main__":
    try:
        archivos = sys.argv[1:]
        if not archivos:
            root = tk.Tk()
            root.withdraw()
            messagebox.showwarning("Advertencia", "No se arrastró ni seleccionó ninguna imagen.")
            root.destroy()
        else:
            lanzar_interfaz(archivos)
            
    except Exception:
        error_completo = traceback.format_exc()
        mostrar_error("Error Crítico de Inicio", error_completo)