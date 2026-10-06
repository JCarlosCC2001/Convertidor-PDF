import os
import sys
import shutil
import winreg
import subprocess
import tkinter as tk
from tkinter import messagebox

# Paleta de colores consistente (Tema Claro)
COLOR_BG = "#f3f4f6"
COLOR_HEADER = "#ffffff"
COLOR_TEXT_PRIMARY = "#1f2937"
COLOR_TEXT_MUTED = "#6b7280"
COLOR_ACCENT = "#2563eb"
COLOR_ACCENT_HOVER = "#1d4ed8"
COLOR_CARD = "#ffffff"
COLOR_CARD_BORDER = "#d1d5db"
COLOR_SUCCESS = "#10b981"
COLOR_DANGER = "#ef4444"
COLOR_DANGER_HOVER = "#dc2626"


DIR_PROYECTO = os.path.dirname(os.path.abspath(__file__))

# Directorio destino de instalación (local del usuario para evitar requerir permisos de admin)
DIR_INSTALACION = os.path.join(os.environ["LOCALAPPDATA"], "Programs", "ConvertidorPDF")
RUTA_EXE_DESTINO = os.path.join(DIR_INSTALACION, "ConvertidorPDF.exe")
RUTA_LOGO_DESTINO = os.path.join(DIR_INSTALACION, "logo.ico")

# Clave de registro para detección de versión anterior
REGISTRY_UNINSTALL_KEY = r"Software\Microsoft\Windows\CurrentVersion\Uninstall\ConvertidorPDF"


def obtener_version_actual():
    """Obtiene la versión actual del programa desde config.py."""
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("config", os.path.join(DIR_PROYECTO, "src", "config.py"))
        config_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(config_module)
        return getattr(config_module, "VERSION", "1.0.0")
    except Exception:
        return "1.0.0"


def detectar_version_anterior():
    """Detecta si existe una versión anterior instalada.
    
    Returns:
        tuple: (instalada: bool, version: str o None, ruta: str o None)
    """
    # 1. Verificar en el registro de Windows
    try:
        with winreg.OpenKeyEx(winreg.HKEY_CURRENT_USER, REGISTRY_UNINSTALL_KEY, 0, winreg.KEY_READ) as key:
            version_reg = winreg.QueryValueEx(key, "DisplayVersion")[0]
            return True, version_reg, DIR_INSTALACION
    except FileNotFoundError:
        pass
    except Exception:
        pass

    # 2. Si no hay registro pero existe el exe, es una instalación sin registro (legacy)
    if os.path.exists(RUTA_EXE_DESTINO):
        return True, "desconocida", DIR_INSTALACION

    return False, None, None


def limpiar_instalacion_anterior(callback_estado=None):
    """Limpia silenciosamente la instalación anterior antes de actualizar.
    
    Args:
        callback_estado: función opcional que recibe un str con el estado actual.
    """
    def estado(msg):
        if callback_estado:
            callback_estado(msg)

    # 1. Eliminar accesos directos existentes
    estado("Eliminando accesos directos anteriores...")
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

    # 2. Limpiar registros del menú contextual
    estado("Limpiando registros anteriores del menú contextual...")
    try:
        winreg.DeleteKey(winreg.HKEY_CURRENT_USER, r"Software\Classes\*\shell\ConvertidorPDF\command")
    except Exception:
        pass
    try:
        winreg.DeleteKey(winreg.HKEY_CURRENT_USER, r"Software\Classes\*\shell\ConvertidorPDF")
    except Exception:
        pass

    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("config", os.path.join(DIR_PROYECTO, "src", "config.py"))
        config_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(config_module)
        extensiones_todas = list(config_module.EXTENSIONES_SOPORTADAS)
        extensiones_transformar = list(config_module.EXTENSIONES_IMAGEN) + list(config_module.EXTENSIONES_WORD)
    except Exception:
        extensiones_todas = [".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tiff", ".tif", ".docx", ".pdf"]
        extensiones_transformar = [".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tiff", ".docx"]

    def remover_accion(ext, accion_id):
        try:
            winreg.DeleteKey(winreg.HKEY_CURRENT_USER, fr"Software\Classes\SystemFileAssociations\{ext}\shell\{accion_id}\command")
        except Exception:
            pass
        try:
            winreg.DeleteKey(winreg.HKEY_CURRENT_USER, fr"Software\Classes\SystemFileAssociations\{ext}\shell\{accion_id}")
        except Exception:
            pass

    for ext in extensiones_todas:
        remover_accion(ext, "ConvertidorPDF_Abrir")
    for ext in extensiones_transformar:
        remover_accion(ext, "ConvertidorPDF_Transformar")
    remover_accion(".pdf", "ConvertidorPDF_Unir")
    remover_accion(".pdf", "ConvertidorPDF_Dividir")
    remover_accion(".pdf", "ConvertidorPDF_BN")

    # 3. Remover registro de "Agregar o quitar programas"
    estado("Limpiando registro de aplicaciones anterior...")
    try:
        winreg.DeleteKey(winreg.HKEY_CURRENT_USER, REGISTRY_UNINSTALL_KEY)
    except Exception:
        pass

    # 4. Eliminar archivos de la instalación anterior (excepto configuración del usuario)
    estado("Eliminando archivos de la versión anterior...")
    archivos_a_borrar = ["ConvertidorPDF.exe", "logo.ico", "uninstall.py", "uninstall.exe"]
    for a in archivos_a_borrar:
        path_a = os.path.join(DIR_INSTALACION, a)
        if os.path.exists(path_a):
            try:
                os.remove(path_a)
            except Exception:
                pass


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
    """Registra la aplicación en el menú contextual de Windows dependiendo de la extensión."""
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("config", os.path.join(DIR_PROYECTO, "src", "config.py"))
        config_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(config_module)

        extensiones_transformar = list(config_module.EXTENSIONES_IMAGEN) + list(config_module.EXTENSIONES_WORD)
        
        def registrar_accion(ext, accion_id, nombre_mostrar, comando):
            key_path = fr"Software\Classes\SystemFileAssociations\{ext}\shell\{accion_id}"
            with winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE) as key:
                winreg.SetValueEx(key, "", 0, winreg.REG_SZ, nombre_mostrar)
                winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, RUTA_LOGO_DESTINO)
            
            cmd_path = key_path + r"\command"
            with winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, cmd_path, 0, winreg.KEY_SET_VALUE) as cmd_key:
                winreg.SetValueEx(cmd_key, "", 0, winreg.REG_SZ, comando)

        # Registro unificado: Un solo botón en el menú contextual para todas las extensiones
        extensiones_todas = list(config_module.EXTENSIONES_SOPORTADAS)
        
        for ext in extensiones_todas:
            registrar_accion(
                ext, "ConvertidorPDF_Abrir", 
                "Abrir en Convertidor PDF", 
                f'"{RUTA_EXE_DESTINO}" "%1"'
            )

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
    version_actual = obtener_version_actual()
    try:
        with winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, REGISTRY_UNINSTALL_KEY, 0, winreg.KEY_SET_VALUE) as key:
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
            winreg.SetValueEx(key, "DisplayVersion", 0, winreg.REG_SZ, version_actual)
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
            
            # Limpiar el registro general viejo (compatibilidad hacia atrás)
            try: winreg.DeleteKey(winreg.HKEY_CURRENT_USER, r"Software\Classes\*\shell\ConvertidorPDF\command")
            except Exception: pass
            try: winreg.DeleteKey(winreg.HKEY_CURRENT_USER, r"Software\Classes\*\shell\ConvertidorPDF")
            except Exception: pass

            # Limpiar nuevos registros por extensión (incluyendo las claves antiguas por si existen)
            try:
                import importlib.util
                spec = importlib.util.spec_from_file_location("config", os.path.join(DIR_PROYECTO, "src", "config.py"))
                config_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(config_module)
                extensiones_todas = list(config_module.EXTENSIONES_SOPORTADAS)
                extensiones_transformar = list(config_module.EXTENSIONES_IMAGEN) + list(config_module.EXTENSIONES_WORD)
            except Exception:
                extensiones_todas = [".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tiff", ".tif", ".docx", ".pdf"]
                extensiones_transformar = [".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tiff", ".docx"]

            def remover_accion(ext, accion_id):
                try: winreg.DeleteKey(winreg.HKEY_CURRENT_USER, fr"Software\Classes\SystemFileAssociations\{ext}\shell\{accion_id}\command")
                except Exception: pass
                try: winreg.DeleteKey(winreg.HKEY_CURRENT_USER, fr"Software\Classes\SystemFileAssociations\{ext}\shell\{accion_id}")
                except Exception: pass

            # Remover claves nuevas y antiguas para limpieza total
            for ext in extensiones_todas:
                remover_accion(ext, "ConvertidorPDF_Abrir")
            
            for ext in extensiones_transformar:
                remover_accion(ext, "ConvertidorPDF_Transformar")
            
            remover_accion(".pdf", "ConvertidorPDF_Unir")
            remover_accion(".pdf", "ConvertidorPDF_Dividir")
            remover_accion(".pdf", "ConvertidorPDF_BN")

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
        self.root.configure(bg=COLOR_BG)
        self.root.geometry("460x360")
        self.root.resizable(False, False)

        # Detectar versión anterior
        self.hay_version_anterior, self.version_anterior, self.ruta_anterior = detectar_version_anterior()
        self.version_nueva = obtener_version_actual()
        self.es_actualizacion = self.hay_version_anterior

        # Título dinámico según el modo
        if self.es_actualizacion:
            self.root.title("Actualizador - Convertidor PDF")
        else:
            self.root.title("Instalador - Convertidor PDF")

        # Centrar ventana
        pantalla_ancho = self.root.winfo_screenwidth()
        pantalla_alto = self.root.winfo_screenheight()
        x = (pantalla_ancho - 460) // 2
        y = (pantalla_alto - 360) // 2
        self.root.geometry(f"460x360+{x}+{y}")

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

        if self.es_actualizacion:
            titulo_header = "🔄 ACTUALIZACIÓN DE CONVERTIDOR PDF"
        else:
            titulo_header = "📄 INSTALACIÓN DE CONVERTIDOR PDF"

        tk.Label(
            frame_header, text=titulo_header,
            font=("Segoe UI", 12, "bold"), bg=COLOR_HEADER, fg=COLOR_TEXT_PRIMARY,
        ).pack(pady=14)

        # Cuerpo
        self.frame_cuerpo = tk.Frame(self.root, bg=COLOR_BG)
        self.frame_cuerpo.pack(fill="both", expand=True, padx=25, pady=20)

        # Mensaje dinámico según el modo (instalación nueva vs actualización)
        if self.es_actualizacion:
            texto_info = (
                f"Se ha detectado una versión anterior instalada (v{self.version_anterior}).\n\n"
                f"Este asistente actualizará a la versión {self.version_nueva}.\n"
                "La versión anterior será reemplazada automáticamente.\n"
                "Su configuración personal se conservará."
            )
        else:
            texto_info = (
                "Este asistente instalará el Convertidor PDF en su equipo.\n\n"
                "Se configurará el menú contextual para que aparezca la opción "
                "al hacer clic derecho sobre sus imágenes o documentos Word."
            )

        self.lbl_info = tk.Label(
            self.frame_cuerpo,
            text=texto_info,
            font=("Segoe UI", 9), bg=COLOR_BG, fg=COLOR_TEXT_PRIMARY,
            justify="left", wraplength=400,
        )
        self.lbl_info.pack(anchor="w", pady=(10, 8))

        # Badge de versión (solo en modo actualización)
        if self.es_actualizacion:
            frame_version = tk.Frame(self.frame_cuerpo, bg=COLOR_BG)
            frame_version.pack(anchor="w", pady=(0, 8))

            tk.Label(
                frame_version,
                text=f"  v{self.version_anterior}  ",
                font=("Segoe UI", 8, "bold"), bg=COLOR_DANGER, fg="#ffffff",
                padx=4, pady=1,
            ).pack(side="left")

            tk.Label(
                frame_version,
                text="  →  ",
                font=("Segoe UI", 9, "bold"), bg=COLOR_BG, fg=COLOR_TEXT_MUTED,
            ).pack(side="left")

            tk.Label(
                frame_version,
                text=f"  v{self.version_nueva}  ",
                font=("Segoe UI", 8, "bold"), bg=COLOR_SUCCESS, fg="#ffffff",
                padx=4, pady=1,
            ).pack(side="left")

        self.lbl_ruta = tk.Label(
            self.frame_cuerpo,
            text=f"Directorio de instalación:\n{DIR_INSTALACION}",
            font=("Segoe UI", 8, "italic"), bg=COLOR_BG, fg=COLOR_TEXT_MUTED,
            justify="left", wraplength=400,
        )
        self.lbl_ruta.pack(anchor="w", pady=(0, 15))

        # Botonera
        self.frame_botones = tk.Frame(self.frame_cuerpo, bg=COLOR_BG)
        self.frame_botones.pack(fill="x")

        texto_boton = "Actualizar" if self.es_actualizacion else "Instalar"

        self.btn_instalar = tk.Button(
            self.frame_botones, text=texto_boton, font=("Segoe UI", 9, "bold"),
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

    def _actualizar_estado(self, texto):
        """Actualiza el label de estado y refresca la UI."""
        self.lbl_estado.config(text=texto)
        self.root.update_idletasks()

    def ejecutar_instalacion(self):
        """Ejecuta la copia de archivos y registros, con limpieza previa si es actualización."""
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

            # 0.5. Si es actualización, limpiar la versión anterior primero
            if self.es_actualizacion:
                self._actualizar_estado("Removiendo versión anterior...")
                limpiar_instalacion_anterior(callback_estado=self._actualizar_estado)

            # 1. Rutas de origen
            exe_origen = obtener_ruta_recurso("ConvertidorPDF.exe")
            logo_origen = obtener_ruta_recurso("logo.ico")

            if not os.path.exists(exe_origen):
                raise FileNotFoundError(
                    "No se encontró el ejecutable interno ConvertidorPDF.exe. "
                    "Por favor compile la app antes de generar el instalador."
                )

            # 2. Crear carpeta e instalar
            self._actualizar_estado("Creando carpetas del sistema...")
            os.makedirs(DIR_INSTALACION, exist_ok=True)

            self._actualizar_estado("Copiando archivos de la aplicación...")
            shutil.copy2(exe_origen, RUTA_EXE_DESTINO)

            if os.path.exists(logo_origen):
                shutil.copy2(logo_origen, RUTA_LOGO_DESTINO)

            # 3. Desinstalador (Copia del propio instalador)
            self._actualizar_estado("Configurando desinstalador...")
            if hasattr(sys, "_MEIPASS"):
                # Si está compilado, copiamos el propio exe ejecutable
                ruta_uninstall_exe = os.path.join(DIR_INSTALACION, "uninstall.exe")
                shutil.copy2(sys.executable, ruta_uninstall_exe)
            else:
                # Si se ejecuta como script, copiamos este script como uninstall.py
                ruta_uninstall_py = os.path.join(DIR_INSTALACION, "uninstall.py")
                shutil.copy2(__file__, ruta_uninstall_py)

            # 4. Accesos directos
            self._actualizar_estado("Creando accesos directos en Windows...")
            crear_accesos_directos()

            # 5. Registro contextual
            self._actualizar_estado("Registrando menú contextual (anticlick)...")
            registrar_menu_contextual()

            # 6. Registrar en Agregar o quitar programas
            self._actualizar_estado("Registrando en Agregar o quitar programas...")
            registrar_desinstalador_windows()

            self.lbl_estado.pack_forget()

            # Pantalla de éxito (mensaje dinámico según modo)
            if self.es_actualizacion:
                texto_exito = (
                    f"¡Actualización completada exitosamente!\n\n"
                    f"Se actualizó de v{self.version_anterior} a v{self.version_nueva}.\n"
                    "El programa ya está configurado y listo para usarse.\n"
                    "Su configuración personal fue conservada."
                )
            else:
                texto_exito = (
                    "¡Instalación completada exitosamente!\n\n"
                    "El programa ya está configurado y listo para usarse.\n"
                    "• En Escritorio y Menú Inicio.\n"
                    "• Con clic derecho directo sobre un archivo.\n"
                    "• Con clic derecho -> Enviar a -> Convertidor PDF (para múltiples archivos)."
                )

            self.lbl_info.config(text=texto_exito, fg=COLOR_SUCCESS)
            self.lbl_ruta.pack_forget()

            # Ocultar badge de versión si existe
            for widget in self.frame_cuerpo.winfo_children():
                if isinstance(widget, tk.Frame) and widget != self.frame_botones:
                    widget.pack_forget()

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
            titulo_error = "Error de actualización" if self.es_actualizacion else "Error de instalación"
            messagebox.showerror(titulo_error, f"Ocurrió un error inesperado:\n\n{e}")
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
