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
COLOR_SUCCESS = "#4ec97a"
COLOR_DANGER = "#ff6666"
COLOR_DANGER_HOVER = "#ff9999"


DIR_PROYECTO = os.path.dirname(os.path.abspath(__file__))

# Directorio destino de instalación (local del usuario para evitar requerir permisos de admin)
DIR_INSTALACION = os.path.join(os.environ["LOCALAPPDATA"], "Programs", "ConvertidorPDF")
RUTA_EXE_DESTINO = os.path.join(DIR_INSTALACION, "ConvertidorPDF.exe")
RUTA_LOGO_DESTINO = os.path.join(DIR_INSTALACION, "logo.ico")


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


def es_modo_desinstalacion():
    """Determina si el script/ejecutable debe ejecutarse en modo desinstalación."""
    if "--uninstall" in sys.argv:
        return True
    
    nombre_exe = os.path.basename(sys.executable).lower()
    if "uninstall" in nombre_exe:
        return True
        
    if hasattr(sys, "argv") and len(sys.argv) > 0:
        nombre_script = os.path.basename(sys.argv[0]).lower()
        if "uninstall" in nombre_script:
            return True
            
    return False


def registrar_desinstalador_windows():
    """Registra la aplicación en 'Agregar o quitar programas' de Windows para el usuario actual."""
    try:
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Uninstall\ConvertidorPDF"
        with winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, "DisplayName", 0, winreg.REG_SZ, "Convertidor PDF")
            
            if hasattr(sys, "_MEIPASS"):
                # Si está compilado por PyInstaller, el desinstalador copiado será uninstall.exe
                ruta_uninstall = os.path.join(DIR_INSTALACION, "uninstall.exe")
                winreg.SetValueEx(key, "UninstallString", 0, winreg.REG_SZ, f'"{ruta_uninstall}"')
            else:
                # Si está en modo script de desarrollo, llamamos a python con uninstall.py --uninstall
                ruta_script = os.path.join(DIR_INSTALACION, "uninstall.py")
                winreg.SetValueEx(key, "UninstallString", 0, winreg.REG_SZ, f'"{sys.executable}" "{ruta_script}" --uninstall')
                
            winreg.SetValueEx(key, "DisplayIcon", 0, winreg.REG_SZ, RUTA_LOGO_DESTINO)
            winreg.SetValueEx(key, "Publisher", 0, winreg.REG_SZ, "JCarlosCC2001")
            winreg.SetValueEx(key, "DisplayVersion", 0, winreg.REG_SZ, "1.0.0")
            winreg.SetValueEx(key, "NoModify", 0, winreg.REG_DWORD, 1)
            winreg.SetValueEx(key, "NoRepair", 0, winreg.REG_DWORD, 1)
    except Exception as e:
        raise Exception(f"No se pudo registrar en Agregar o quitar programas: {e}")


class UninstallerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Desinstalador - Convertidor PDF")
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
            frame_header, text="🗑 DESINSTALACIÓN DE CONVERTIDOR PDF",
            font=("Segoe UI", 12, "bold"), bg=COLOR_HEADER, fg=COLOR_TEXT_PRIMARY,
        ).pack(pady=14)

        # Cuerpo
        self.frame_cuerpo = tk.Frame(self.root, bg=COLOR_BG)
        self.frame_cuerpo.pack(fill="both", expand=True, padx=25, pady=20)

        self.lbl_info = tk.Label(
            self.frame_cuerpo,
            text="Este asistente eliminará el Convertidor PDF y todas sus integraciones de su equipo.\n\n"
                 "Se removerán los accesos directos, el menú contextual de clic derecho y la configuración local.",
            font=("Segoe UI", 9), bg=COLOR_BG, fg=COLOR_TEXT_PRIMARY,
            justify="left", wraplength=400,
        )
        self.lbl_info.pack(anchor="w", pady=(10, 15))

        self.lbl_ruta = tk.Label(
            self.frame_cuerpo,
            text=f"Directorio a eliminar:\n{DIR_INSTALACION}",
            font=("Segoe UI", 8, "italic"), bg=COLOR_BG, fg=COLOR_TEXT_MUTED,
            justify="left", wraplength=400,
        )
        self.lbl_ruta.pack(anchor="w", pady=(0, 20))

        # Botonera
        self.frame_botones = tk.Frame(self.frame_cuerpo, bg=COLOR_BG)
        self.frame_botones.pack(fill="x")

        self.btn_desinstalar = tk.Button(
            self.frame_botones, text="Desinstalar", font=("Segoe UI", 9, "bold"),
            bg=COLOR_DANGER, fg=COLOR_TEXT_PRIMARY,
            activebackground=COLOR_DANGER_HOVER, activeforeground=COLOR_TEXT_PRIMARY,
            bd=0, width=12, pady=6, cursor="hand2",
            command=self.ejecutar_desinstalacion,
        )
        self.btn_desinstalar.pack(side="right", padx=5)

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

    def ejecutar_desinstalacion(self):
        """Ejecuta la remoción de archivos, registros y accesos directos."""
        self.btn_desinstalar.pack_forget()
        self.btn_cancelar.pack_forget()

        self.lbl_estado.pack(pady=10)

        try:
            # 1. Eliminar accesos directos
            self.lbl_estado.config(text="Eliminando accesos directos...")
            self.root.update_idletasks()
            
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

            # 2. Remover del Registro de Windows (Menú Contextual)
            self.lbl_estado.config(text="Removiendo menú contextual...")
            self.root.update_idletasks()
            
            try:
                winreg.DeleteKey(winreg.HKEY_CURRENT_USER, r"Software\Classes\*\shell\ConvertidorPDF\command")
            except Exception:
                pass
            try:
                winreg.DeleteKey(winreg.HKEY_CURRENT_USER, r"Software\Classes\*\shell\ConvertidorPDF")
            except Exception:
                pass

            # 3. Remover del Registro de Windows (Agregar o quitar programas)
            self.lbl_estado.config(text="Removiendo registro de aplicaciones...")
            self.root.update_idletasks()
            try:
                winreg.DeleteKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Uninstall\ConvertidorPDF")
            except Exception:
                pass

            # 4. Eliminar otros archivos del directorio de instalación
            self.lbl_estado.config(text="Borrando archivos de la aplicación...")
            self.root.update_idletasks()
            
            archivos_a_borrar = ["ConvertidorPDF.exe", "logo.ico", "configuracion_pdf.json", "uninstall.py"]
            for a in archivos_a_borrar:
                path_a = os.path.join(DIR_INSTALACION, a)
                if os.path.exists(path_a):
                    try:
                        os.remove(path_a)
                    except Exception:
                        pass

            # 5. Programar autodestrucción del directorio
            self.lbl_estado.config(text="Completando desinstalación...")
            self.root.update_idletasks()
            
            creationflags = 0
            if sys.platform == "win32":
                creationflags = 0x08000000  # CREATE_NO_WINDOW
                
            cmd_destruccion = f'timeout /t 2 /nobreak > NUL && rd /s /q "{DIR_INSTALACION}"'
            subprocess.Popen(cmd_destruccion, shell=True, creationflags=creationflags)

            self.lbl_estado.pack_forget()

            # Pantalla de éxito
            self.lbl_info.config(
                text="¡Convertidor PDF ha sido desinstalado correctamente de su equipo!\n\n"
                     "La carpeta y los accesos directos se han removido.",
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
            messagebox.showerror("Error al desinstalar", f"Ocurrió un error inesperado:\n\n{e}")
            self.root.destroy()


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
            # 0. Verificar si la aplicación está ejecutándose
            if os.path.exists(RUTA_EXE_DESTINO):
                try:
                    with open(RUTA_EXE_DESTINO, "ab"):
                        pass
                except OSError:
                    raise PermissionError(
                        "El Convertidor PDF está actualmente abierto.\n\n"
                        "Por favor, cierre la aplicación antes de instalar o actualizar."
                    )

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

            # 3. Desinstalador (Copia del propio instalador)
            self.lbl_estado.config(text="Configurando desinstalador...")
            self.root.update_idletasks()
            if hasattr(sys, "_MEIPASS"):
                # Si está compilado, copiamos el propio exe ejecutable
                ruta_uninstall_exe = os.path.join(DIR_INSTALACION, "uninstall.exe")
                shutil.copy2(sys.executable, ruta_uninstall_exe)
            else:
                # Si se ejecuta como script, copiamos este script como uninstall.py
                ruta_uninstall_py = os.path.join(DIR_INSTALACION, "uninstall.py")
                shutil.copy2(__file__, ruta_uninstall_py)

            # 4. Accesos directos
            self.lbl_estado.config(text="Creando accesos directos en Windows...")
            self.root.update_idletasks()
            crear_accesos_directos()

            # 5. Registro contextual
            self.lbl_estado.config(text="Registrando menú contextual (anticlick)...")
            self.root.update_idletasks()
            registrar_menu_contextual()

            # 6. Registrar en Agregar o quitar programas
            self.lbl_estado.config(text="Registrando en Agregar o quitar programas...")
            self.root.update_idletasks()
            registrar_desinstalador_windows()

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
    if es_modo_desinstalacion():
        root = tk.Tk()
        _app = UninstallerGUI(root)
        root.mainloop()
    else:
        root = tk.Tk()
        _app = InstallerGUI(root)
        root.mainloop()


if __name__ == "__main__":
    main()
