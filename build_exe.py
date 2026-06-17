import os
import sys
import shutil
import subprocess
from PIL import Image

# Rutas principales
DIR_PROYECTO = os.path.dirname(os.path.abspath(__file__))
RUTA_LOGO_PNG = os.path.join(DIR_PROYECTO, "logo.png")
RUTA_LOGO_ICO = os.path.join(DIR_PROYECTO, "logo.ico")
RUTA_MAIN = os.path.join(DIR_PROYECTO, "main.py")

# Imagen de origen (se definió una por defecto si no existe logo.png)
RUTA_LOGO_ORIGEN = r"C:\Users\Documentación\.gemini\antigravity-ide\brain\18a7bdb4-4e48-4de2-8e6f-3bc69edd4daf\pdf_converter_logo_1781730243589.png"


def preparar_iconos():
    """Copia el logo PNG y genera el logo ICO necesario para la compilación."""
    print("Preparando logos de la aplicación...")
    # Si existe el logo generado por el agente, copiarlo
    if os.path.exists(RUTA_LOGO_ORIGEN):
        shutil.copy(RUTA_LOGO_ORIGEN, RUTA_LOGO_PNG)
        print(f"Copiado logo PNG desde {RUTA_LOGO_ORIGEN}")

    # Si tenemos el PNG pero no el ICO, crearlo
    if os.path.exists(RUTA_LOGO_PNG):
        try:
            img = Image.open(RUTA_LOGO_PNG)
            # Redimensionar a tamaños estándar de icono de Windows
            img.save(RUTA_LOGO_ICO, format="ICO", sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])
            print("Archivo logo.ico generado con éxito a partir de logo.png")
        except Exception as e:
            print(f"Error al generar logo.ico: {e}")
    else:
        # Generar un logo de respaldo básico en caso de que no existan
        print("No se encontró el logo PNG de origen. Creando un icono básico...")
        img = Image.new("RGB", (256, 256), color="#002060")
        img.save(RUTA_LOGO_ICO, format="ICO", sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])
        img.save(RUTA_LOGO_PNG, format="PNG")
        print("Logos básicos creados.")


def compilar():
    """Ejecuta PyInstaller para compilar el ejecutable sin consola."""
    preparar_iconos()
    print("Iniciando compilación del ejecutable con PyInstaller...")

    # Ejecutar PyInstaller en el entorno virtual
    python_exe = sys.executable  # Usa el python del entorno actual
    pyinstaller_cmd = [
        python_exe, "-m", "PyInstaller",
        "--onefile",               # Empaquetar todo en un único archivo
        "--noconsole",             # No mostrar ventana negra de terminal
        f"--icon={RUTA_LOGO_ICO}", # Icono del ejecutable
        "--name=ConvertidorPDF",   # Nombre del ejecutable
        # Añadir dependencias opcionales de reportlab y docx que pyinstaller podría omitir
        "--collect-all", "reportlab",
        "--collect-all", "docx",
        RUTA_MAIN
    ]

    print(f"Comando de compilación: {' '.join(pyinstaller_cmd)}")
    result = subprocess.run(pyinstaller_cmd, cwd=DIR_PROYECTO)

    if result.returncode == 0:
        print("\n" + "="*50)
        print("¡COMPILACIÓN FINALIZADA CON ÉXITO!")
        print(f"El ejecutable se encuentra en: {os.path.join(DIR_PROYECTO, 'dist', 'ConvertidorPDF.exe')}")
        print("="*50 + "\n")
    else:
        print("Error al compilar la aplicación.")
        sys.exit(1)


if __name__ == "__main__":
    compilar()
