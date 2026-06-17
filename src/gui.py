import os
import sys
import threading
import tkinter as tk
from tkinter import messagebox, filedialog
from src.config import CALIDADES, cargar_configuracion
from src.converter import ejecutar_conversion

# Paleta de Colores - Tonalidades Azules Premium
COLOR_BG = "#001333"            # Azul muy oscuro para el fondo general de la ventana
COLOR_HEADER = "#002060"        # Azul #002060 solicitado (Tema del encabezado)
COLOR_CARD = "#001a40"          # Azul intermedio para las tarjetas de opciones
COLOR_CARD_BORDER = "#003399"   # Azul claro para los bordes de las tarjetas
COLOR_TEXT_PRIMARY = "#ffffff"  # Blanco para textos importantes
COLOR_TEXT_MUTED = "#8cadd3"    # Azul grisáceo para textos secundarios y etiquetas
COLOR_ACCENT = "#007acc"        # Azul brillante para el botón de conversión y acentos
COLOR_ACCENT_HOVER = "#0099ff"  # Azul más claro para el hover del botón
COLOR_RADIO_SELECT = "#002b66"  # Color de fondo de los círculos de opción cuando están seleccionados

class CustomProgressBar(tk.Canvas):
    """Barra de progreso moderna basada en Canvas para personalización total de colores."""
    def __init__(self, parent, width=340, height=10, bg="#000d26", fill_color="#0099ff", border_color="#003399"):
        super().__init__(parent, width=width, height=height, bg=bg, highlightthickness=1, highlightbackground=border_color, bd=0)
        self.width = width
        self.height = height
        self.rect = self.create_rectangle(0, 0, 0, height, fill=fill_color, width=0)
        
    def actualizar_progreso(self, porcentaje):
        """Ajusta el ancho del rectángulo de progreso según el porcentaje (0.0 a 1.0)."""
        w = int(self.width * porcentaje)
        self.coords(self.rect, 0, 0, w, self.height)
        self.update_idletasks()

class ConvertidorGUI:
    def __init__(self, root, rutas_iniciales=None):
        self.root = root
        self.rutas_imagenes = rutas_iniciales if rutas_iniciales else []
        self.is_converting = False
        
        # Cargar las opciones previas del usuario
        self.config_guardada = cargar_configuracion()
        
        # Configuración de la ventana principal
        self.root.title("Convertidor PDF")
        self.root.configure(bg=COLOR_BG)
        self.root.resizable(False, False)
        
        # Centrar la ventana
        self.centrar_ventana(400, 520)
        
        # Intentar cargar icono
        try:
            self.root.iconbitmap("logo.ico")
        except Exception:
            pass
            
        # Variables de Tkinter vinculadas a las opciones
        self.var_union = tk.StringVar(value=self.config_guardada.get("union", "Unido"))
        self.var_color = tk.StringVar(value=self.config_guardada.get("color", "A Colores"))
        self.var_calidad = tk.StringVar(value=self.config_guardada.get("calidad", "Alta"))
        
        # Construir la interfaz gráfica
        self.crear_interfaz()
        
    def centrar_ventana(self, ancho, alto):
        """Centra la ventana principal en la pantalla del usuario."""
        pantalla_ancho = self.root.winfo_screenwidth()
        pantalla_alto = self.root.winfo_screenheight()
        x = (pantalla_ancho - ancho) // 2
        y = (pantalla_alto - alto) // 2
        self.root.geometry(f"{ancho}x{alto}+{x}+{y}")

    def crear_interfaz(self):
        # --- ENCABEZADO ---
        self.frame_header = tk.Frame(self.root, bg=COLOR_HEADER, height=70)
        self.frame_header.pack(fill="x")
        self.frame_header.pack_propagate(False)
        
        lbl_titulo = tk.Label(
            self.frame_header, 
            text="📄 CONVERTIDOR DE IMÁGENES A PDF", 
            font=("Segoe UI", 11, "bold"), 
            bg=COLOR_HEADER, 
            fg=COLOR_TEXT_PRIMARY
        )
        lbl_titulo.pack(pady=12)
        
        # --- ÁREA DE INFORMACIÓN DE ARCHIVOS ---
        self.frame_archivos = tk.Frame(self.root, bg=COLOR_BG)
        self.frame_archivos.pack(fill="x", padx=20, pady=10)
        
        self.lbl_archivos = tk.Label(
            self.frame_archivos, 
            text="", 
            font=("Segoe UI", 9, "bold"), 
            bg=COLOR_BG, 
            fg=COLOR_TEXT_PRIMARY
        )
        self.lbl_archivos.pack(side="left")
        
        self.btn_cambiar_archivos = tk.Button(
            self.frame_archivos, 
            text="Seleccionar imágenes", 
            font=("Segoe UI", 8, "bold"), 
            bg=COLOR_HEADER, 
            fg=COLOR_TEXT_PRIMARY, 
            activebackground=COLOR_CARD_BORDER, 
            activeforeground=COLOR_TEXT_PRIMARY,
            bd=0, 
            padx=10, 
            pady=3,
            cursor="hand2",
            command=self.seleccionar_archivos
        )
        self.btn_cambiar_archivos.pack(side="right")
        
        self.actualizar_vista_archivos()

        # --- SECCIONES DE CONFIGURACIÓN ---
        # Card 1: Formato de Salida
        self.card_union = self.crear_tarjeta("Formato de salida")
        self.crear_radio(self.card_union, "Unido (Un solo PDF conteniendo todas las imágenes)", self.var_union, "Unido").pack(anchor="w", pady=2)
        self.crear_radio(self.card_union, "Dividido (Un archivo PDF independiente por imagen)", self.var_union, "Dividido").pack(anchor="w", pady=2)
        
        # Card 2: Modo de Color
        self.card_color = self.crear_tarjeta("Configuración de color")
        self.crear_radio(self.card_color, "A Colores (Conserva la gama de colores original)", self.var_color, "A Colores").pack(anchor="w", pady=2)
        self.crear_radio(self.card_color, "Blanco y Negro (Escala de grises optimizada)", self.var_color, "Blanco y Negro").pack(anchor="w", pady=2)

        # Card 3: Calidad / Resolución (A4 Vertical)
        self.card_calidad = self.crear_tarjeta("Calidad de salida (Formato A4)")
        frame_radios_calidad = tk.Frame(self.card_calidad, bg=COLOR_CARD)
        frame_radios_calidad.pack(fill="x", pady=2)
        
        for cal, info in CALIDADES.items():
            self.crear_radio(frame_radios_calidad, info["label"], self.var_calidad, cal).pack(side="left", expand=True, anchor="w")

        # --- SECCIÓN DE ACCIÓN Y PROGRESO ---
        self.frame_accion = tk.Frame(self.root, bg=COLOR_BG)
        self.frame_accion.pack(fill="x", padx=20, pady=15)
        
        # Botón de Conversión
        self.btn_convertir = tk.Button(
            self.frame_accion, 
            text="Transformar a PDF", 
            font=("Segoe UI", 11, "bold"), 
            bg=COLOR_ACCENT, 
            fg=COLOR_TEXT_PRIMARY,
            activebackground=COLOR_ACCENT_HOVER,
            activeforeground=COLOR_TEXT_PRIMARY,
            bd=0, 
            height=2,
            cursor="hand2",
            command=self.iniciar_conversion
        )
        self.btn_convertir.pack(fill="x", pady=5)
        
        # Micro-animaciones (Hover) en el botón convertir
        self.btn_convertir.bind("<Enter>", lambda e: self.btn_convertir.config(bg=COLOR_ACCENT_HOVER))
        self.btn_convertir.bind("<Leave>", lambda e: self.btn_convertir.config(bg=COLOR_ACCENT))

        # Indicador de estado y progreso (Ocultos al inicio)
        self.lbl_estado = tk.Label(
            self.frame_accion, 
            text="", 
            font=("Segoe UI", 9, "italic"), 
            bg=COLOR_BG, 
            fg=COLOR_TEXT_MUTED
        )
        self.lbl_estado.pack(fill="x", pady=2)
        
        self.progreso = CustomProgressBar(self.frame_accion)
        self.progreso.pack(pady=5)
        self.progreso.pack_forget() # Ocultar inicialmente
        
    def crear_tarjeta(self, titulo):
        """Crea un contenedor estilizado tipo tarjeta con bordes y fondo oscuro."""
        card = tk.Frame(
            self.root, 
            bg=COLOR_CARD, 
            bd=1, 
            relief="solid", 
            highlightthickness=1, 
            highlightbackground=COLOR_CARD_BORDER,
            highlightcolor=COLOR_CARD_BORDER
        )
        card.pack(fill="x", padx=20, pady=6, ipady=4)
        
        lbl_titulo = tk.Label(
            card, 
            text=titulo.upper(), 
            font=("Segoe UI", 8, "bold"), 
            bg=COLOR_CARD, 
            fg=COLOR_TEXT_MUTED,
            padx=10,
            pady=4
        )
        lbl_titulo.pack(anchor="w")
        
        # Contenedor interno con margen
        interno = tk.Frame(card, bg=COLOR_CARD, padx=10)
        interno.pack(fill="x")
        return interno

    def crear_radio(self, parent, text, variable, value):
        """Crea un Radiobutton estilizado para armonizar con el fondo oscuro."""
        return tk.Radiobutton(
            parent, 
            text=text, 
            variable=variable, 
            value=value, 
            bg=COLOR_CARD, 
            fg=COLOR_TEXT_PRIMARY,
            activebackground=COLOR_CARD, 
            activeforeground=COLOR_TEXT_PRIMARY,
            selectcolor=COLOR_RADIO_SELECT,
            font=("Segoe UI", 9),
            cursor="hand2",
            bd=0
        )

    def seleccionar_archivos(self):
        """Abre un diálogo para seleccionar imágenes interactivamente."""
        tipos = [("Imágenes", "*.jpg *.jpeg *.png *.bmp *.webp")]
        archivos = filedialog.askopenfilenames(
            title="Seleccionar imágenes para convertir",
            filetypes=tipos
        )
        if archivos:
            self.rutas_imagenes = list(archivos)
            self.actualizar_vista_archivos()

    def actualizar_vista_archivos(self):
        """Actualiza la etiqueta con la cantidad de imágenes cargadas y habilita/deshabilita el botón."""
        total = len(self.rutas_imagenes)
        if total == 0:
            self.lbl_archivos.config(text="Ninguna imagen cargada", fg="#ff6666")
            if hasattr(self, "btn_convertir"):
                self.btn_convertir.config(state="disabled", bg="#4f5d75")
        else:
            self.lbl_archivos.config(text=f"Imágenes cargadas: {total}", fg=COLOR_TEXT_PRIMARY)
            if hasattr(self, "btn_convertir"):
                self.btn_convertir.config(state="normal", bg=COLOR_ACCENT)

    def cambiar_estado_widgets(self, estado):
        """Activa o desactiva la interacción con los controles de la GUI."""
        self.btn_cambiar_archivos.config(state=estado)
        self.btn_convertir.config(state=estado)
        
        # Modificar el estado de todos los radiobuttons recorriendo los contenedores
        for card in [self.card_union, self.card_color, self.card_calidad]:
            for child in card.winfo_children():
                if isinstance(child, tk.Radiobutton):
                    child.config(state=estado)
                elif isinstance(child, tk.Frame):
                    # Para la calidad que tiene un frame secundario interno
                    for subchild in child.winfo_children():
                        if isinstance(subchild, tk.Radiobutton):
                            subchild.config(state=estado)

    def iniciar_conversion(self):
        """Valida e inicia el hilo de conversión para mantener la GUI responsiva."""
        if not self.rutas_imagenes:
            messagebox.showwarning("Advertencia", "Por favor, selecciona al menos una imagen.")
            return
            
        self.is_converting = True
        self.cambiar_estado_widgets("disabled")
        
        # Mostrar barra de progreso y estado
        self.lbl_estado.config(text="Preparando conversión...")
        self.progreso.actualizar_progreso(0.0)
        self.progreso.pack(pady=5)
        
        # Lanzar la conversión en un hilo separado
        hilo = threading.Thread(target=self.hilo_conversion, daemon=True)
        hilo.start()

    def hilo_conversion(self):
        """Método ejecutado en segundo plano."""
        try:
            ejecutar_conversion(
                self.rutas_imagenes,
                self.var_union.get(),
                self.var_color.get(),
                self.var_calidad.get(),
                callback_progreso=self.callback_progreso_seguro
            )
            # Notificación de éxito en el hilo principal
            self.root.after(0, self.conversion_exitosa)
        except Exception as e:
            # Notificación de error en el hilo principal
            self.root.after(0, self.conversion_fallida, str(e))

    def callback_progreso_seguro(self, actual, total, mensaje):
        """Envía de forma segura el progreso desde el hilo secundario al hilo de la GUI."""
        porcentaje = actual / total if total > 0 else 0.0
        self.root.after(0, self.actualizar_progreso_gui, porcentaje, mensaje)

    def actualizar_progreso_gui(self, porcentaje, mensaje):
        """Actualiza la barra y el texto en el hilo principal."""
        self.lbl_estado.config(text=mensaje)
        self.progreso.actualizar_progreso(porcentaje)

    def conversion_exitosa(self):
        """Maneja las operaciones tras una conversión exitosa."""
        self.is_converting = False
        self.progreso.actualizar_progreso(1.0)
        self.lbl_estado.config(text="¡Completado!")
        
        calidad = self.var_calidad.get()
        messagebox.showinfo("Éxito", f"¡Conversión completada con éxito!\nCalidad utilizada: {calidad}")
        
        # Cerrar el programa tras la conversión
        self.root.destroy()
        sys.exit(0)

    def conversion_fallida(self, error_msg):
        """Maneja las operaciones tras un error en la conversión."""
        self.is_converting = False
        self.lbl_estado.config(text="Error en la conversión")
        self.progreso.pack_forget()
        self.cambiar_estado_widgets("normal")
        
        messagebox.showerror("Error", f"Ocurrió un error al procesar las imágenes:\n\n{error_msg}")
