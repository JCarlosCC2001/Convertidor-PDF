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
    """Ejecuta PyInstaller para compilar la aplicación y luego su instalador."""
    preparar_iconos()
    print("Iniciando compilación del ejecutable principal con PyInstaller...")

    python_exe = sys.executable  # Usa el python del entorno actual
    pyinstaller_cmd = [
        python_exe, "-m", "PyInstaller",
        "--onefile",               # Empaquetar en un único archivo
        "--noconsole",             # No mostrar ventana negra de terminal
        f"--icon={RUTA_LOGO_ICO}", # Icono del ejecutable
        "--name=ConvertidorPDF",   # Nombre del ejecutable
        "--collect-all", "reportlab",
        "--collect-all", "docx",
        "--collect-all", "pypdf",
        RUTA_MAIN
    ]

    print(f"Comando de compilación principal: {' '.join(pyinstaller_cmd)}")
    result = subprocess.run(pyinstaller_cmd, cwd=DIR_PROYECTO)

    if result.returncode != 0:
        print("Error al compilar la aplicación principal.")
        sys.exit(1)

    print("\n" + "="*50)
    print("¡APLICACIÓN PRINCIPAL COMPILADA!")
    print("="*50 + "\n")

    # --- PASO 2: COMPILAR EL INSTALADOR GRÁFICO AUTÓNOMO ---
    print("Iniciando compilación del instalador gráfico...")

    ruta_installer_script = os.path.join(DIR_PROYECTO, "setup_installer.py")
    
    # Sintaxis de --add-data en Windows: "origen;destino_dentro_del_exe"
    add_data_exe = f"dist/ConvertidorPDF.exe;."
    add_data_logo = f"logo.ico;."

    pyinstaller_installer_cmd = [
        python_exe, "-m", "PyInstaller",
        "--onefile",
        "--noconsole",             # El instalador gráfico de Tkinter no necesita consola
        f"--icon={RUTA_LOGO_ICO}",
        "--add-data", add_data_exe,
        "--add-data", add_data_logo,
        "--name=Instalador_ConvertidorPDF",
        ruta_installer_script
    ]

    print(f"Comando de compilación del instalador: {' '.join(pyinstaller_installer_cmd)}")
    result_installer = subprocess.run(pyinstaller_installer_cmd, cwd=DIR_PROYECTO)

    if result_installer.returncode == 0:
        print("\n" + "="*60)
        print("¡PROCESO COMPLETADO EXITOSAMENTE!")
        print("Archivos generados en la carpeta 'dist/':")
        print(f" 1. Aplicación: {os.path.join(DIR_PROYECTO, 'dist', 'ConvertidorPDF.exe')}")
        print(f" 2. Instalador único: {os.path.join(DIR_PROYECTO, 'dist', 'Instalador_ConvertidorPDF.exe')}")
        print("\n* IMPORTANTE: Puedes enviar solo el 'Instalador_ConvertidorPDF.exe' a cualquier")
        print("  computadora y al ejecutarlo instalará y configurará todo automáticamente.")
        print("="*60 + "\n")
    else:
        print("Error al compilar el instalador.")
        sys.exit(1)


if __name__ == "__main__":
    compilar()

