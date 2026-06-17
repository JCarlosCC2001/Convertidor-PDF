import os
import sys
import shutil
import winreg
import subprocess
import tkinter as tk
from tkinter import messagebox

# Paleta de colores consistente
COLOR_BG = "#001333"
COLOR_HEADER = "#002060"
COLOR_TEXT_PRIMARY = "#ffffff"
COLOR_TEXT_MUTED = "#8cadd3"
COLOR_ACCENT = "#007acc"
COLOR_ACCENT_HOVER = "#0099ff"
COLOR_CARD = "#001a40"
COLOR_CARD_BORDER = "#003399"

DIR_PROYECTO = os.path.dirname(os.path.abspath(__file__))

# Directorio destino de instalación (local del usuario para evitar requerir permisos de admin)
DIR_INSTALACION = os.path.join(os.environ["LOCALAPPDATA"], "Programs", "ConvertidorPDF")
RUTA_EXE_DESTINO = os.path.join(DIR_INSTALACION, "ConvertidorPDF.exe")
RUTA_LOGO_DESTINO = os.path.join(DIR_INSTALACION, "logo.ico")
RUTA_UNINSTALL_DESTINO = os.path.join(DIR_INSTALACION, "uninstall.py")


def obtener_ruta_recurso(nombre_archivo):
    """Obtiene la ruta absoluta de un recurso, compatible con empaquetado PyInstaller."""
    if hasattr(sys, "_MEIPASS"):
        # PyInstaller crea una carpeta temporal y guarda la ruta en sys._MEIPASS
        return os.path.join(sys._MEIPASS, nombre_archivo)
    # Si se ejecuta como script, buscar en carpetas de desarrollo
    if nombre_archivo == "ConvertidorPDF.exe":
        return os.path.join(DIR_PROYECTO, "dist", "ConvertidorPDF.exe")
    return os.path.join(DIR_PROYECTO, nombre_archivo)


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
    try:
        # HKEY_CURRENT_USER\Software\Classes\*\shell\ConvertidorPDF
        key_path = r"Software\Classes\*\shell\ConvertidorPDF"
        with winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, "Convertidor PDF")
            winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, RUTA_LOGO_DESTINO)

        # Comando asociado al hacer clic
        cmd_path = key_path + r"\command"
        with winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, cmd_path, 0, winreg.KEY_SET_VALUE) as cmd_key:
            winreg.SetValueEx(cmd_key, "", 0, winreg.REG_SZ, f'"{RUTA_EXE_DESTINO}" "%1"')
    except Exception as e:
        raise Exception(f"No se pudo configurar el menú contextual: {e}")


def crear_accesos_directos():
    """Crea los accesos directos en Escritorio, Menú Inicio y en la carpeta 'SendTo'."""
    # 1. Escritorio
    escritorio = os.path.join(os.environ["USERPROFILE"], "Desktop")
    ruta_desktop = os.path.join(escritorio, "Convertidor PDF.lnk")
    crear_acceso_directo_powershell(ruta_desktop, RUTA_EXE_DESTINO, descripcion="Convertidor de imágenes y Word a PDF")

    # 2. Menú Inicio
    menu_inicio = os.path.join(os.environ["APPDATA"], "Microsoft", "Windows", "Start Menu", "Programs")
    dir_start_menu = os.path.join(menu_inicio, "Convertidor PDF")
    os.makedirs(dir_start_menu, exist_ok=True)
    ruta_start_menu = os.path.join(dir_start_menu, "Convertidor PDF.lnk")
    crear_acceso_directo_powershell(ruta_start_menu, RUTA_EXE_DESTINO, descripcion="Convertidor de imágenes y Word a PDF")

    # 3. Menú Enviar a (SendTo) - CLAVE PARA MÚLTIPLES ARCHIVOS
    sendto_dir = os.path.join(os.environ["APPDATA"], "Microsoft", "Windows", "SendTo")
    ruta_sendto = os.path.join(sendto_dir, "Convertidor PDF.lnk")
    crear_acceso_directo_powershell(ruta_sendto, RUTA_EXE_DESTINO, descripcion="Convertidor de imágenes y Word a PDF")


def generar_desinstalador():
    """Genera el script uninstall.py dentro del directorio de instalación."""
    script_content = f"""# Script de Desinstalación de Convertidor PDF
import os
import winreg

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
        except Exception:
            pass

dir_start_menu = os.path.join(os.environ["APPDATA"], "Microsoft", "Windows", "Start Menu", "Programs", "Convertidor PDF")
if os.path.exists(dir_start_menu):
    try:
        os.rmdir(dir_start_menu)
    except Exception:
        pass

# 2. Remover del Registro de Windows
try:
    winreg.DeleteKey(winreg.HKEY_CURRENT_USER, r"Software\\Classes\\*\\shell\\ConvertidorPDF\\command")
    winreg.DeleteKey(winreg.HKEY_CURRENT_USER, r"Software\\Classes\\*\\shell\\ConvertidorPDF")
except Exception:
    pass

print("Desinstalación completada con éxito.")
"""
    with open(RUTA_UNINSTALL_DESTINO, "w", encoding="utf-8") as f:
        f.write(script_content)


class InstallerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Instalador - Convertidor PDF")
        self.root.configure(bg=COLOR_BG)
        self.root.geometry("460x320")
        self.root.resizable(False, False)

        # Centrar ventana
        pantalla_ancho = self.root.winfo_screenwidth()
        pantalla_alto = self.root.winfo_screenheight()
        x = (pantalla_ancho - 460) // 2
        y = (pantalla_alto - 320) // 2
        self.root.geometry(f"460x320+{x}+{y}")

        # Intentar cargar icono
        try:
            self.root.iconbitmap(obtener_ruta_recurso("logo.ico"))
        except Exception:
            pass

        self.crear_interfaz()

    def crear_interfaz(self):
        # Header
        frame_header = tk.Frame(self.root, bg=COLOR_HEADER, height=55)
        frame_header.pack(fill="x")
        frame_header.pack_propagate(False)

        tk.Label(
            frame_header, text="📄 INSTALACIÓN DE CONVERTIDOR PDF",
            font=("Segoe UI", 12, "bold"), bg=COLOR_HEADER, fg=COLOR_TEXT_PRIMARY,
        ).pack(pady=14)

        # Cuerpo
        self.frame_cuerpo = tk.Frame(self.root, bg=COLOR_BG)
        self.frame_cuerpo.pack(fill="both", expand=True, padx=25, pady=20)

        self.lbl_info = tk.Label(
            self.frame_cuerpo,
            text="Este asistente instalará el Convertidor PDF en su equipo.\n\n"
                 "Se configurará el menú contextual para que aparezca la opción "
                 "al hacer clic derecho sobre sus imágenes o documentos Word.",
            font=("Segoe UI", 9), bg=COLOR_BG, fg=COLOR_TEXT_PRIMARY,
            justify="left", wraplength=400,
        )
        self.lbl_info.pack(anchor="w", pady=(10, 15))

        self.lbl_ruta = tk.Label(
            self.frame_cuerpo,
            text=f"Directorio de instalación:\n{DIR_INSTALACION}",
            font=("Segoe UI", 8, "italic"), bg=COLOR_BG, fg=COLOR_TEXT_MUTED,
            justify="left", wraplength=400,
        )
        self.lbl_ruta.pack(anchor="w", pady=(0, 20))

        # Botonera
        self.frame_botones = tk.Frame(self.frame_cuerpo, bg=COLOR_BG)
        self.frame_botones.pack(fill="x")

        self.btn_instalar = tk.Button(
            self.frame_botones, text="Instalar", font=("Segoe UI", 9, "bold"),
            bg=COLOR_ACCENT, fg=COLOR_TEXT_PRIMARY,
            activebackground=COLOR_ACCENT_HOVER, activeforeground=COLOR_TEXT_PRIMARY,
            bd=0, width=12, pady=6, cursor="hand2",
            command=self.ejecutar_instalacion,
        )
        self.btn_instalar.pack(side="right", padx=5)

        self.btn_cancelar = tk.Button(
            self.frame_botones, text="Cancelar", font=("Segoe UI", 9, "bold"),
            bg=COLOR_HEADER, fg=COLOR_TEXT_PRIMARY,
            activebackground=COLOR_CARD_BORDER, activeforeground=COLOR_TEXT_PRIMARY,
            bd=0, width=12, pady=6, cursor="hand2",
            command=self.root.destroy,
        )
        self.btn_cancelar.pack(side="right", padx=5)

        # Estado (Inicialmente oculto)
        self.lbl_estado = tk.Label(
            self.frame_cuerpo, text="", font=("Segoe UI", 9, "bold"),
            bg=COLOR_BG, fg=COLOR_ACCENT,
        )

    def ejecutar_instalacion(self):
        """Ejecuta la copia de archivos y registros."""
        self.btn_instalar.pack_forget()
        self.btn_cancelar.pack_forget()

        self.lbl_estado.pack(pady=10)

        try:
            # 1. Rutas de origen
            exe_origen = obtener_ruta_recurso("ConvertidorPDF.exe")
            logo_origen = obtener_ruta_recurso("logo.ico")

            if not os.path.exists(exe_origen):
                raise FileNotFoundError(
                    "No se encontró el ejecutable interno ConvertidorPDF.exe. "
                    "Por favor compile la app antes de generar el instalador."
                )

            # 2. Crear carpeta e instalar
            self.lbl_estado.config(text="Creando carpetas del sistema...")
            self.root.update_idletasks()
            os.makedirs(DIR_INSTALACION, exist_ok=True)

            self.lbl_estado.config(text="Copiando archivos de la aplicación...")
            self.root.update_idletasks()
            shutil.copy2(exe_origen, RUTA_EXE_DESTINO)

            if os.path.exists(logo_origen):
                shutil.copy2(logo_origen, RUTA_LOGO_DESTINO)

            # 3. Desinstalador
            generar_desinstalador()

            # 4. Accesos directos
            self.lbl_estado.config(text="Creando accesos directos en Windows...")
            self.root.update_idletasks()
            crear_accesos_directos()

            # 5. Registro contextual
            self.lbl_estado.config(text="Registrando menú contextual (anticlick)...")
            self.root.update_idletasks()
            registrar_menu_contextual()

            self.lbl_estado.pack_forget()

            # Pantalla de éxito
            self.lbl_info.config(
                text="¡Instalación completada exitosamente!\n\n"
                     "El programa ya está configurado y listo para usarse.\n"
                     "• En Escritorio y Menú Inicio.\n"
                     "• Con clic derecho directo sobre un archivo.\n"
                     "• Con clic derecho -> Enviar a -> Convertidor PDF (para múltiples archivos).",
                fg=COLOR_SUCCESS,
            )

            btn_finalizar = tk.Button(
                self.frame_botones, text="Finalizar", font=("Segoe UI", 9, "bold"),
                bg=COLOR_ACCENT, fg=COLOR_TEXT_PRIMARY,
                activebackground=COLOR_ACCENT_HOVER, activeforeground=COLOR_TEXT_PRIMARY,
                bd=0, width=15, pady=8, cursor="hand2",
                command=self.root.destroy,
            )
            btn_finalizar.pack(side="right")

        except Exception as e:
            self.lbl_estado.pack_forget()
            messagebox.showerror("Error de instalación", f"Ocurrió un error inesperado:\n\n{e}")
            self.root.destroy()


def main():
    root = tk.Tk()
    _app = InstallerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
