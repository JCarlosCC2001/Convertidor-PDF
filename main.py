import sys
import tkinter as tk
import traceback
from tkinter import messagebox
from src.gui import ConvertidorGUI

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
        archivos = sys.argv[1:]
        
        # Inicializar la interfaz gráfica de usuario
        root = tk.Tk()
        _app = ConvertidorGUI(root, rutas_iniciales=archivos)
        root.mainloop()
        
    except Exception:
        error_completo = traceback.format_exc()
        mostrar_error_critico("Error Crítico de Inicio", error_completo)

if __name__ == "__main__":
    main()