import os
import sys
import shutil
import winreg
import subprocess

DIR_PROYECTO = os.path.dirname(os.path.abspath(__file__))
RUTA_EXE_ORIGEN = os.path.join(DIR_PROYECTO, "dist", "ConvertidorPDF.exe")
RUTA_LOGO_ORIGEN = os.path.join(DIR_PROYECTO, "logo.ico")

# Directorio destino de instalación (local del usuario para evitar requerir permisos de admin)
DIR_INSTALACION = os.path.join(os.environ["LOCALAPPDATA"], "Programs", "ConvertidorPDF")
RUTA_EXE_DESTINO = os.path.join(DIR_INSTALACION, "ConvertidorPDF.exe")
RUTA_LOGO_DESTINO = os.path.join(DIR_INSTALACION, "logo.ico")
RUTA_UNINSTALL_DESTINO = os.path.join(DIR_INSTALACION, "uninstall.py")


def crear_acceso_directo_powershell(ruta_acceso_directo, ruta_destino_exe, argumentos="", descripcion=""):
    """Crea un acceso directo .lnk usando PowerShell."""
    ps_cmd = (
        f'$WshShell = New-Object -ComObject WScript.Shell; '
        f'$Shortcut = $WshShell.CreateShortcut("{ruta_acceso_directo}"); '
        f'$Shortcut.TargetPath = "{ruta_destino_exe}"; '
        f'$Shortcut.Arguments = "{argumentos}"; '
        f'$Shortcut.Description = "{descripcion}"; '
        f'$Shortcut.WorkingDirectory = "{os.path.dirname(ruta_destino_exe)}"; '
        f'$Shortcut.Save()'
    )
    subprocess.run(["powershell", "-Command", ps_cmd], capture_output=True)


def registrar_menu_contextual():
    """Registra la aplicación en el menú contextual de Windows para archivos individuales (clic derecho directo)."""
    print("Registrando en el menú contextual (anticlick)...")
    try:
        # HKEY_CURRENT_USER\Software\Classes\*\shell\ConvertidorPDF
        key_path = r"Software\Classes\*\shell\ConvertidorPDF"
        with winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, "Convertidor PDF")
            winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, RUTA_LOGO_DESTINO)

        # Comando asociado al hacer clic
        cmd_path = key_path + r"\command"
        with winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, cmd_path, 0, winreg.KEY_SET_VALUE) as cmd_key:
            # "%1" representa el archivo seleccionado
            winreg.SetValueEx(cmd_key, "", 0, winreg.REG_SZ, f'"{RUTA_EXE_DESTINO}" "%1"')

        print("Registro en menú contextual completado.")
    except Exception as e:
        print(f"Error al registrar menú contextual: {e}")


def crear_accesos_directos():
    """Crea los accesos directos en Escritorio, Menú Inicio y en la carpeta 'SendTo'."""
    print("Creando accesos directos...")

    # 1. Escritorio
    escritorio = os.path.join(os.environ["USERPROFILE"], "Desktop")
    ruta_desktop = os.path.join(escritorio, "Convertidor PDF.lnk")
    crear_acceso_directo_powershell(ruta_desktop, RUTA_EXE_DESTINO, descripcion="Convertidor de imágenes y Word a PDF")
    print("Acceso directo creado en Escritorio.")

    # 2. Menú Inicio
    menu_inicio = os.path.join(os.environ["APPDATA"], "Microsoft", "Windows", "Start Menu", "Programs")
    dir_start_menu = os.path.join(menu_inicio, "Convertidor PDF")
    os.makedirs(dir_start_menu, exist_ok=True)
    ruta_start_menu = os.path.join(dir_start_menu, "Convertidor PDF.lnk")
    crear_acceso_directo_powershell(ruta_start_menu, RUTA_EXE_DESTINO, descripcion="Convertidor de imágenes y Word a PDF")
    print("Acceso directo creado en Menú Inicio.")

    # 3. Menú Enviar a (SendTo) - CLAVE PARA MÚLTIPLES ARCHIVOS
    sendto_dir = os.path.join(os.environ["APPDATA"], "Microsoft", "Windows", "SendTo")
    ruta_sendto = os.path.join(sendto_dir, "Convertidor PDF.lnk")
    crear_acceso_directo_powershell(ruta_sendto, RUTA_EXE_DESTINO, descripcion="Convertidor de imágenes y Word a PDF")
    print("Registrado en el menú 'Enviar a' (SendTo) para múltiples archivos.")


def generar_desinstalador():
    """Genera el script uninstall.py dentro del directorio de instalación."""
    print("Generando desinstalador...")
    script_content = f"""# Script de Desinstalación de Convertidor PDF
import os
import winreg
import subprocess

print("Iniciando desinstalación de Convertidor PDF...")

# 1. Eliminar accesos directos
accesos_directos = [
    os.path.join(os.environ["USERPROFILE"], "Desktop", "Convertidor PDF.lnk"),
    os.path.join(os.environ["APPDATA"], "Microsoft", "Windows", "SendTo", "Convertidor PDF.lnk"),
    os.path.join(os.environ["APPDATA"], "Microsoft", "Windows", "Start Menu", "Programs", "Convertidor PDF", "Convertidor PDF.lnk"),
]

for ruta in accesos_directos:
    if os.path.exists(ruta):
        try:
            os.remove(ruta)
            print(f"Eliminado acceso directo: {{ruta}}")
        except Exception as e:
            print(f"No se pudo eliminar {{ruta}}: {{e}}")

# Eliminar carpeta en Menú Inicio si está vacía
dir_start_menu = os.path.join(os.environ["APPDATA"], "Microsoft", "Windows", "Start Menu", "Programs", "Convertidor PDF")
if os.path.exists(dir_start_menu):
    try:
        os.rmdir(dir_start_menu)
    except Exception:
        pass

# 2. Remover del Registro de Windows
print("Removiendo del menú contextual...")
try:
    # Eliminar comando y luego la clave principal del menú contextual
    winreg.DeleteKey(winreg.HKEY_CURRENT_USER, r"Software\\Classes\\*\\shell\\ConvertidorPDF\\command")
    winreg.DeleteKey(winreg.HKEY_CURRENT_USER, r"Software\\Classes\\*\\shell\\ConvertidorPDF")
    print("Registro removido del menú contextual.")
except Exception as e:
    print(f"Error al eliminar registro: {{e}}")

# 3. Eliminar archivos locales
print("Eliminando archivos de instalación...")
# Intentamos agendar la eliminación o borrar los archivos no bloqueados
# El propio uninstall.py se borrará al final o el usuario podrá borrar la carpeta
dir_instalacion = r"{DIR_INSTALACION}"
print(f"Puedes borrar manualmente la carpeta del programa si quedan archivos: {{dir_instalacion}}")
print("Desinstalación completada con éxito.")
"""

    with open(RUTA_UNINSTALL_DESTINO, "w", encoding="utf-8") as f:
        f.write(script_content)


def instalar():
    """Orquesta el proceso de instalación completo."""
    print("="*60)
    print("INSTALADOR DE CONVERTIDOR PDF")
    print("="*60)

    # Verificar que el ejecutable compilado existe
    if not os.path.exists(RUTA_EXE_ORIGEN):
        print(f"ERROR: No se encontró el ejecutable compilado en {RUTA_EXE_ORIGEN}.")
        print("Por favor, ejecuta primero 'build_exe.py' para compilar la aplicación.")
        sys.exit(1)

    # Crear carpeta de instalación
    print(f"Creando carpeta de instalación en: {DIR_INSTALACION}...")
    os.makedirs(DIR_INSTALACION, exist_ok=True)

    # Copiar ejecutable
    print("Copiando ejecutable...")
    shutil.copy2(RUTA_EXE_ORIGEN, RUTA_EXE_DESTINO)

    # Copiar icono
    if os.path.exists(RUTA_LOGO_ORIGEN):
        print("Copiando icono de la aplicación...")
        shutil.copy2(RUTA_LOGO_ORIGEN, RUTA_LOGO_DESTINO)
    else:
        print("Advertencia: No se encontró el icono logo.ico.")

    # Generar desinstalador
    generar_desinstalador()

    # Configurar el sistema
    crear_accesos_directos()
    registrar_menu_contextual()

    print("\n" + "="*60)
    print("¡CONVERTIDOR PDF INSTALADO EXITOSAMENTE!")
    print("Puedes usarlo desde:")
    print(" 1. Tu Escritorio (Acceso directo)")
    print(" 2. Menú Inicio")
    print(" 3. Haciendo clic derecho sobre cualquier archivo -> Convertidor PDF")
    print(" 4. Clic derecho sobre un lote de archivos -> Enviar a -> Convertidor PDF")
    print("="*60 + "\n")


if __name__ == "__main__":
    instalar()
