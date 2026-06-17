"""
Interfaz gráfica de usuario para el Convertidor a PDF.

Incluye:
- Lista visual scrollable de archivos con iconos por tipo
- Botones para reordenar y eliminar archivos
- Selector de carpeta de salida y nombre personalizado
- Tooltips informativos en opciones de calidad
- Barra de progreso con animación shimmer
- Post-conversión: no cierra la app, ofrece abrir la carpeta de salida
"""
import os
import sys
import subprocess
import threading
import tkinter as tk
from tkinter import messagebox, filedialog
from src.config import (
    CALIDADES, EXTENSIONES_IMAGEN, EXTENSIONES_WORD,
    EXTENSIONES_SOPORTADAS, cargar_configuracion, clasificar_archivo,
)
from src.converter import ejecutar_conversion

# ===== PALETA DE COLORES - TONALIDADES AZULES PREMIUM =====
COLOR_BG = "#001333"
COLOR_HEADER = "#002060"
COLOR_CARD = "#001a40"
COLOR_CARD_BORDER = "#003399"
COLOR_TEXT_PRIMARY = "#ffffff"
COLOR_TEXT_MUTED = "#8cadd3"
COLOR_ACCENT = "#007acc"
COLOR_ACCENT_HOVER = "#0099ff"
COLOR_RADIO_SELECT = "#002b66"
COLOR_DANGER = "#ff6666"
COLOR_SUCCESS = "#4ec97a"
COLOR_LIST_BG = "#000d26"
COLOR_LIST_SELECT = "#003070"
COLOR_ENTRY_BG = "#001029"
COLOR_ENTRY_BORDER = "#003399"


# ===== TOOLTIP =====
class ToolTip:
    """Tooltip personalizado que aparece al pasar el mouse sobre un widget."""

    def __init__(self, widget, texto):
        self.widget = widget
        self.texto = texto
        self.tip_window = None
        self.widget.bind("<Enter>", self.mostrar)
        self.widget.bind("<Leave>", self.ocultar)

    def mostrar(self, _event=None):
        if self.tip_window or not self.texto:
            return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        lbl = tk.Label(
            tw, text=self.texto,
            justify="left", relief="solid", borderwidth=1,
            font=("Segoe UI", 8), bg="#1a1a2e", fg="#e0e0e0",
            padx=8, pady=4,
        )
        lbl.pack()

    def ocultar(self, _event=None):
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None


# ===== BARRA DE PROGRESO CON SHIMMER =====
class CustomProgressBar(tk.Canvas):
    """Barra de progreso moderna con efecto shimmer animado."""

    def __init__(self, parent, width=340, height=12, bg_color="#000d26",
                 fill_color="#0099ff", shimmer_color="#66ccff", border_color="#003399"):
        super().__init__(
            parent, width=width, height=height, bg=bg_color,
            highlightthickness=1, highlightbackground=border_color, bd=0,
        )
        self.bar_width = width
        self.bar_height = height
        self.fill_color = fill_color
        self.shimmer_color = shimmer_color
        self._porcentaje = 0.0
        self._shimmer_pos = -40
        self._shimmer_activo = False

        # Rectángulo de fondo de la barra
        self.rect = self.create_rectangle(0, 0, 0, height, fill=fill_color, width=0)
        # Rectángulo de shimmer (brillo que recorre la barra)
        self.shimmer_rect = self.create_rectangle(0, 0, 0, 0, fill=shimmer_color, width=0, stipple="gray25")

    def actualizar_progreso(self, porcentaje):
        """Ajusta el ancho del rectángulo de progreso."""
        self._porcentaje = max(0.0, min(1.0, porcentaje))
        w = int(self.bar_width * self._porcentaje)
        self.coords(self.rect, 0, 0, w, self.bar_height)
        self.update_idletasks()

    def iniciar_shimmer(self):
        """Inicia la animación de brillo que recorre la barra."""
        self._shimmer_activo = True
        self._animar_shimmer()

    def detener_shimmer(self):
        """Detiene la animación shimmer."""
        self._shimmer_activo = False
        self.coords(self.shimmer_rect, 0, 0, 0, 0)

    def _animar_shimmer(self):
        if not self._shimmer_activo:
            return
        w_barra = int(self.bar_width * self._porcentaje)
        ancho_shimmer = 40
        self._shimmer_pos += 4

        if self._shimmer_pos > w_barra:
            self._shimmer_pos = -ancho_shimmer

        x1 = max(0, self._shimmer_pos)
        x2 = min(w_barra, self._shimmer_pos + ancho_shimmer)
        if x2 > x1:
            self.coords(self.shimmer_rect, x1, 0, x2, self.bar_height)
        else:
            self.coords(self.shimmer_rect, 0, 0, 0, 0)

        self.after(50, self._animar_shimmer)


# ===== INTERFAZ PRINCIPAL =====
class ConvertidorGUI:
    def __init__(self, root, rutas_iniciales=None):
        self.root = root
        self.rutas_archivos = list(rutas_iniciales) if rutas_iniciales else []
        self.is_converting = False

        # Cargar las opciones previas del usuario
        self.config_guardada = cargar_configuracion()

        # Configuración de la ventana principal
        self.root.title("Convertidor a PDF")
        self.root.configure(bg=COLOR_BG)
        self.root.resizable(False, True)
        self.root.minsize(440, 600)

        # Centrar la ventana
        self.centrar_ventana(440, 680)

        # Intentar cargar icono
        try:
            self.root.iconbitmap("logo.ico")
        except Exception:
            pass

        # Variables de Tkinter vinculadas a las opciones
        self.var_union = tk.StringVar(value=self.config_guardada.get("union", "Unido"))
        self.var_color = tk.StringVar(value=self.config_guardada.get("color", "A Colores"))
        self.var_calidad = tk.StringVar(value=self.config_guardada.get("calidad", "Alta"))
        self.var_orientacion = tk.BooleanVar(value=self.config_guardada.get("orientacion_auto", True))
        self.var_carpeta_salida = tk.StringVar(value=self.config_guardada.get("carpeta_salida", ""))
        self.var_nombre_pdf = tk.StringVar(value=self.config_guardada.get("nombre_archivo", ""))

        # Construir la interfaz gráfica
        self.crear_interfaz()

    def centrar_ventana(self, ancho, alto):
        """Centra la ventana principal en la pantalla del usuario."""
        pantalla_ancho = self.root.winfo_screenwidth()
        pantalla_alto = self.root.winfo_screenheight()
        x = (pantalla_ancho - ancho) // 2
        y = (pantalla_alto - alto) // 2
        self.root.geometry(f"{ancho}x{alto}+{x}+{y}")

    # ---------- CONSTRUCCIÓN DE LA INTERFAZ ----------

    def crear_interfaz(self):
        # --- ENCABEZADO ---
        self.frame_header = tk.Frame(self.root, bg=COLOR_HEADER, height=60)
        self.frame_header.pack(fill="x")
        self.frame_header.pack_propagate(False)

        lbl_titulo = tk.Label(
            self.frame_header,
            text="📄 CONVERTIDOR A PDF",
            font=("Segoe UI", 12, "bold"),
            bg=COLOR_HEADER, fg=COLOR_TEXT_PRIMARY,
        )
        lbl_titulo.pack(pady=14)

        # --- CONTENEDOR PRINCIPAL SCROLLABLE ---
        self.frame_main = tk.Frame(self.root, bg=COLOR_BG)
        self.frame_main.pack(fill="both", expand=True, padx=0, pady=0)

        # --- SECCIÓN DE ARCHIVOS ---
        self._crear_seccion_archivos()

        # --- SECCIONES DE CONFIGURACIÓN ---
        self._crear_seccion_formato()
        self._crear_seccion_color()
        self._crear_seccion_calidad()
        self._crear_seccion_salida()

        # --- SECCIÓN DE ACCIÓN Y PROGRESO ---
        self._crear_seccion_accion()

    def _crear_seccion_archivos(self):
        """Crea la sección de archivos con lista, conteo y botones de gestión."""
        # Barra superior: conteo + botones
        frame_top = tk.Frame(self.frame_main, bg=COLOR_BG)
        frame_top.pack(fill="x", padx=20, pady=(10, 2))

        self.lbl_conteo = tk.Label(
            frame_top, text="", font=("Segoe UI", 9, "bold"),
            bg=COLOR_BG, fg=COLOR_TEXT_PRIMARY,
        )
        self.lbl_conteo.pack(side="left")

        # Botones de acción sobre archivos
        frame_botones = tk.Frame(frame_top, bg=COLOR_BG)
        frame_botones.pack(side="right")

        self.btn_agregar = self._crear_btn_mini(frame_botones, "＋ Agregar", self.seleccionar_archivos)
        self.btn_agregar.pack(side="left", padx=2)

        self.btn_limpiar = self._crear_btn_mini(frame_botones, "✕ Limpiar", self.limpiar_archivos)
        self.btn_limpiar.pack(side="left", padx=2)

        # Lista de archivos
        frame_lista = tk.Frame(
            self.frame_main, bg=COLOR_LIST_BG, bd=1, relief="solid",
            highlightthickness=1, highlightbackground=COLOR_CARD_BORDER,
            highlightcolor=COLOR_CARD_BORDER,
        )
        frame_lista.pack(fill="x", padx=20, pady=(2, 4))

        self.listbox = tk.Listbox(
            frame_lista,
            height=5, font=("Segoe UI", 9),
            bg=COLOR_LIST_BG, fg=COLOR_TEXT_PRIMARY,
            selectbackground=COLOR_LIST_SELECT, selectforeground=COLOR_TEXT_PRIMARY,
            activestyle="none", bd=0, highlightthickness=0,
            selectmode="single",
        )
        scrollbar = tk.Scrollbar(frame_lista, orient="vertical", command=self.listbox.yview)
        self.listbox.config(yscrollcommand=scrollbar.set)

        self.listbox.pack(side="left", fill="both", expand=True, padx=(4, 0), pady=4)
        scrollbar.pack(side="right", fill="y", pady=4)

        # Botones de reordenar y eliminar bajo la lista
        frame_acciones_lista = tk.Frame(self.frame_main, bg=COLOR_BG)
        frame_acciones_lista.pack(fill="x", padx=20, pady=(0, 6))

        self.btn_subir = self._crear_btn_mini(frame_acciones_lista, "▲ Subir", self.mover_arriba)
        self.btn_subir.pack(side="left", padx=2)

        self.btn_bajar = self._crear_btn_mini(frame_acciones_lista, "▼ Bajar", self.mover_abajo)
        self.btn_bajar.pack(side="left", padx=2)

        self.btn_eliminar = self._crear_btn_mini(frame_acciones_lista, "🗑 Quitar", self.eliminar_seleccionado)
        self.btn_eliminar.pack(side="left", padx=2)

        # Actualizar la vista
        self._actualizar_lista_archivos()

    def _crear_seccion_formato(self):
        """Card de formato de salida (unido / dividido)."""
        card = self._crear_tarjeta("Formato de salida")
        self._crear_radio(card, "Unido (Un solo PDF con todos los archivos)", self.var_union, "Unido").pack(anchor="w", pady=2)
        self._crear_radio(card, "Dividido (Un PDF independiente por archivo)", self.var_union, "Dividido").pack(anchor="w", pady=2)

    def _crear_seccion_color(self):
        """Card de modo de color."""
        card = self._crear_tarjeta("Configuración de color (imágenes)")
        self._crear_radio(card, "A Colores (Conserva los colores originales)", self.var_color, "A Colores").pack(anchor="w", pady=2)
        self._crear_radio(card, "Blanco y Negro (Escala de grises)", self.var_color, "Blanco y Negro").pack(anchor="w", pady=2)

    def _crear_seccion_calidad(self):
        """Card de calidad con tooltips."""
        card = self._crear_tarjeta("Calidad de salida (imágenes – Formato A4)")
        frame_radios = tk.Frame(card, bg=COLOR_CARD)
        frame_radios.pack(fill="x", pady=2)

        for cal, info in CALIDADES.items():
            radio = self._crear_radio(frame_radios, info["label"], self.var_calidad, cal)
            radio.pack(side="left", expand=True, anchor="w")
            ToolTip(radio, info.get("descripcion", ""))

        # Checkbox de orientación automática
        chk_orientacion = tk.Checkbutton(
            card, text="Orientación automática (horizontal/vertical)",
            variable=self.var_orientacion,
            font=("Segoe UI", 8), bg=COLOR_CARD, fg=COLOR_TEXT_MUTED,
            activebackground=COLOR_CARD, activeforeground=COLOR_TEXT_PRIMARY,
            selectcolor=COLOR_RADIO_SELECT, bd=0, cursor="hand2",
        )
        chk_orientacion.pack(anchor="w", pady=(4, 0))
        ToolTip(chk_orientacion, "Detecta si la imagen es horizontal y rota la página automáticamente")

    def _crear_seccion_salida(self):
        """Card de opciones de salida (carpeta destino + nombre personalizado)."""
        card = self._crear_tarjeta("Opciones de salida")

        # Carpeta de destino
        frame_carpeta = tk.Frame(card, bg=COLOR_CARD)
        frame_carpeta.pack(fill="x", pady=2)

        tk.Label(
            frame_carpeta, text="Carpeta:", font=("Segoe UI", 8, "bold"),
            bg=COLOR_CARD, fg=COLOR_TEXT_MUTED,
        ).pack(side="left")

        self.entry_carpeta = tk.Entry(
            frame_carpeta, textvariable=self.var_carpeta_salida,
            font=("Segoe UI", 8), bg=COLOR_ENTRY_BG, fg=COLOR_TEXT_PRIMARY,
            insertbackground=COLOR_TEXT_PRIMARY, bd=1, relief="solid",
            highlightthickness=1, highlightbackground=COLOR_ENTRY_BORDER,
            highlightcolor=COLOR_ACCENT,
        )
        self.entry_carpeta.pack(side="left", fill="x", expand=True, padx=4)
        ToolTip(self.entry_carpeta, "Dejar vacío para guardar junto al archivo original")

        btn_carpeta = self._crear_btn_mini(frame_carpeta, "📁", self.seleccionar_carpeta_salida)
        btn_carpeta.pack(side="right")

        # Nombre personalizado del PDF
        frame_nombre = tk.Frame(card, bg=COLOR_CARD)
        frame_nombre.pack(fill="x", pady=2)

        tk.Label(
            frame_nombre, text="Nombre:", font=("Segoe UI", 8, "bold"),
            bg=COLOR_CARD, fg=COLOR_TEXT_MUTED,
        ).pack(side="left")

        self.entry_nombre = tk.Entry(
            frame_nombre, textvariable=self.var_nombre_pdf,
            font=("Segoe UI", 8), bg=COLOR_ENTRY_BG, fg=COLOR_TEXT_PRIMARY,
            insertbackground=COLOR_TEXT_PRIMARY, bd=1, relief="solid",
            highlightthickness=1, highlightbackground=COLOR_ENTRY_BORDER,
            highlightcolor=COLOR_ACCENT,
        )
        self.entry_nombre.pack(side="left", fill="x", expand=True, padx=4)
        ToolTip(self.entry_nombre, "Nombre del PDF unido (sin extensión). Dejar vacío para nombre automático")

    def _crear_seccion_accion(self):
        """Sección del botón de conversión, progreso y post-conversión."""
        self.frame_accion = tk.Frame(self.frame_main, bg=COLOR_BG)
        self.frame_accion.pack(fill="x", padx=20, pady=(6, 15))

        # Botón de conversión
        self.btn_convertir = tk.Button(
            self.frame_accion,
            text="⚡ Transformar a PDF",
            font=("Segoe UI", 11, "bold"),
            bg=COLOR_ACCENT, fg=COLOR_TEXT_PRIMARY,
            activebackground=COLOR_ACCENT_HOVER, activeforeground=COLOR_TEXT_PRIMARY,
            bd=0, height=2, cursor="hand2",
            command=self.iniciar_conversion,
        )
        self.btn_convertir.pack(fill="x", pady=5)

        # Hover del botón
        self.btn_convertir.bind("<Enter>", lambda e: self.btn_convertir.config(bg=COLOR_ACCENT_HOVER) if not self.is_converting else None)
        self.btn_convertir.bind("<Leave>", lambda e: self.btn_convertir.config(bg=COLOR_ACCENT) if not self.is_converting else None)

        # Estado y progreso
        self.lbl_estado = tk.Label(
            self.frame_accion, text="", font=("Segoe UI", 9, "italic"),
            bg=COLOR_BG, fg=COLOR_TEXT_MUTED,
        )
        self.lbl_estado.pack(fill="x", pady=2)

        self.progreso = CustomProgressBar(self.frame_accion)
        self.progreso.pack(pady=5)
        self.progreso.pack_forget()

        # Botón "Abrir carpeta" (oculto hasta completar la conversión)
        self.btn_abrir_carpeta = tk.Button(
            self.frame_accion,
            text="📂 Abrir carpeta de salida",
            font=("Segoe UI", 9, "bold"),
            bg=COLOR_HEADER, fg=COLOR_TEXT_PRIMARY,
            activebackground=COLOR_CARD_BORDER, activeforeground=COLOR_TEXT_PRIMARY,
            bd=0, pady=4, cursor="hand2",
            command=self.abrir_carpeta_salida,
        )
        # No lo empaquetamos todavía

        self._actualizar_estado_boton()

    # ---------- WIDGETS AUXILIARES ----------

    def _crear_tarjeta(self, titulo):
        """Crea un contenedor estilizado tipo tarjeta."""
        card = tk.Frame(
            self.frame_main, bg=COLOR_CARD, bd=1, relief="solid",
            highlightthickness=1, highlightbackground=COLOR_CARD_BORDER,
            highlightcolor=COLOR_CARD_BORDER,
        )
        card.pack(fill="x", padx=20, pady=4, ipady=3)

        tk.Label(
            card, text=titulo.upper(),
            font=("Segoe UI", 8, "bold"),
            bg=COLOR_CARD, fg=COLOR_TEXT_MUTED, padx=10, pady=3,
        ).pack(anchor="w")

        interno = tk.Frame(card, bg=COLOR_CARD, padx=10)
        interno.pack(fill="x")
        return interno

    def _crear_radio(self, parent, text, variable, value):
        """Crea un Radiobutton estilizado."""
        return tk.Radiobutton(
            parent, text=text, variable=variable, value=value,
            bg=COLOR_CARD, fg=COLOR_TEXT_PRIMARY,
            activebackground=COLOR_CARD, activeforeground=COLOR_TEXT_PRIMARY,
            selectcolor=COLOR_RADIO_SELECT, font=("Segoe UI", 9),
            cursor="hand2", bd=0,
        )

    def _crear_btn_mini(self, parent, text, command):
        """Crea un botón pequeño estilizado."""
        btn = tk.Button(
            parent, text=text, font=("Segoe UI", 8, "bold"),
            bg=COLOR_HEADER, fg=COLOR_TEXT_PRIMARY,
            activebackground=COLOR_CARD_BORDER, activeforeground=COLOR_TEXT_PRIMARY,
            bd=0, padx=8, pady=2, cursor="hand2",
            command=command,
        )
        btn.bind("<Enter>", lambda e: btn.config(bg=COLOR_CARD_BORDER))
        btn.bind("<Leave>", lambda e: btn.config(bg=COLOR_HEADER))
        return btn

    # ---------- GESTIÓN DE ARCHIVOS ----------

    def seleccionar_archivos(self):
        """Abre un diálogo para seleccionar imágenes y/o documentos Word."""
        extensiones_img = " ".join(f"*{ext}" for ext in sorted(EXTENSIONES_IMAGEN))
        extensiones_word = " ".join(f"*{ext}" for ext in sorted(EXTENSIONES_WORD))
        extensiones_todas = f"{extensiones_img} {extensiones_word}"

        tipos = [
            ("Todos los soportados", extensiones_todas),
            ("Imágenes", extensiones_img),
            ("Documentos Word", extensiones_word),
        ]
        archivos = filedialog.askopenfilenames(
            title="Seleccionar archivos para convertir",
            filetypes=tipos,
        )
        if archivos:
            # Agregar sin duplicar
            existentes = set(self.rutas_archivos)
            for a in archivos:
                if a not in existentes:
                    self.rutas_archivos.append(a)
                    existentes.add(a)
            self._actualizar_lista_archivos()

    def limpiar_archivos(self):
        """Elimina todos los archivos de la lista."""
        self.rutas_archivos.clear()
        self._actualizar_lista_archivos()

    def eliminar_seleccionado(self):
        """Elimina el archivo actualmente seleccionado en la lista."""
        seleccion = self.listbox.curselection()
        if seleccion:
            idx = seleccion[0]
            self.rutas_archivos.pop(idx)
            self._actualizar_lista_archivos()
            # Re-seleccionar el elemento más cercano
            if self.rutas_archivos:
                nuevo_idx = min(idx, len(self.rutas_archivos) - 1)
                self.listbox.selection_set(nuevo_idx)

    def mover_arriba(self):
        """Mueve el archivo seleccionado una posición hacia arriba."""
        seleccion = self.listbox.curselection()
        if seleccion and seleccion[0] > 0:
            idx = seleccion[0]
            self.rutas_archivos[idx], self.rutas_archivos[idx - 1] = \
                self.rutas_archivos[idx - 1], self.rutas_archivos[idx]
            self._actualizar_lista_archivos()
            self.listbox.selection_set(idx - 1)

    def mover_abajo(self):
        """Mueve el archivo seleccionado una posición hacia abajo."""
        seleccion = self.listbox.curselection()
        if seleccion and seleccion[0] < len(self.rutas_archivos) - 1:
            idx = seleccion[0]
            self.rutas_archivos[idx], self.rutas_archivos[idx + 1] = \
                self.rutas_archivos[idx + 1], self.rutas_archivos[idx]
            self._actualizar_lista_archivos()
            self.listbox.selection_set(idx + 1)

    def seleccionar_carpeta_salida(self):
        """Abre un diálogo para elegir la carpeta de destino."""
        carpeta = filedialog.askdirectory(title="Seleccionar carpeta de salida")
        if carpeta:
            self.var_carpeta_salida.set(carpeta)

    def _actualizar_lista_archivos(self):
        """Actualiza la Listbox y el conteo de archivos."""
        self.listbox.delete(0, tk.END)

        num_imagenes = 0
        num_word = 0

        for ruta in self.rutas_archivos:
            nombre = os.path.basename(ruta)
            tipo = clasificar_archivo(ruta)
            if tipo == "imagen":
                icono = "📷"
                num_imagenes += 1
            elif tipo == "word":
                icono = "📄"
                num_word += 1
            else:
                icono = "❓"
            self.listbox.insert(tk.END, f"  {icono}  {nombre}")

        # Actualizar conteo
        partes = []
        if num_imagenes:
            partes.append(f"{num_imagenes} imagen{'es' if num_imagenes != 1 else ''}")
        if num_word:
            partes.append(f"{num_word} documento{'s' if num_word != 1 else ''} Word")

        if partes:
            self.lbl_conteo.config(text=" · ".join(partes), fg=COLOR_TEXT_PRIMARY)
        else:
            self.lbl_conteo.config(text="Ningún archivo cargado", fg=COLOR_DANGER)

        self._actualizar_estado_boton()

    def _actualizar_estado_boton(self):
        """Habilita o deshabilita el botón de conversión según los archivos cargados."""
        if hasattr(self, "btn_convertir"):
            if self.rutas_archivos and not self.is_converting:
                self.btn_convertir.config(state="normal", bg=COLOR_ACCENT)
            else:
                self.btn_convertir.config(state="disabled", bg="#4f5d75")

    # ---------- CONVERSIÓN ----------

    def _cambiar_estado_widgets(self, estado):
        """Activa o desactiva todos los controles interactivos."""
        widgets_directos = [
            self.btn_agregar, self.btn_limpiar,
            self.btn_subir, self.btn_bajar, self.btn_eliminar,
            self.btn_convertir,
        ]
        for w in widgets_directos:
            try:
                w.config(state=estado)
            except tk.TclError:
                pass

        # Radiobuttons dentro de las tarjetas
        for widget in self.frame_main.winfo_children():
            if isinstance(widget, tk.Frame):
                self._deshabilitar_radios_recursivo(widget, estado)

    def _deshabilitar_radios_recursivo(self, parent, estado):
        """Recorre recursivamente los widgets hijos para cambiar estado de Radiobuttons y Checkbuttons."""
        for child in parent.winfo_children():
            if isinstance(child, (tk.Radiobutton, tk.Checkbutton)):
                child.config(state=estado)
            elif isinstance(child, tk.Frame):
                self._deshabilitar_radios_recursivo(child, estado)

    def iniciar_conversion(self):
        """Valida e inicia el hilo de conversión."""
        if not self.rutas_archivos:
            messagebox.showwarning("Advertencia", "Por favor, selecciona al menos un archivo.")
            return

        self.is_converting = True
        self._cambiar_estado_widgets("disabled")
        self.btn_abrir_carpeta.pack_forget()

        # Mostrar barra de progreso
        self.lbl_estado.config(text="Preparando conversión...", fg=COLOR_TEXT_MUTED)
        self.progreso.actualizar_progreso(0.0)
        self.progreso.pack(pady=5)
        self.progreso.iniciar_shimmer()

        # Lanzar la conversión en un hilo separado
        hilo = threading.Thread(target=self._hilo_conversion, daemon=True)
        hilo.start()

    def _hilo_conversion(self):
        """Ejecuta la conversión en segundo plano."""
        try:
            self._pdfs_generados = ejecutar_conversion(
                self.rutas_archivos,
                self.var_union.get(),
                self.var_color.get(),
                self.var_calidad.get(),
                directorio_salida=self.var_carpeta_salida.get(),
                nombre_personalizado=self.var_nombre_pdf.get(),
                orientacion_auto=self.var_orientacion.get(),
                callback_progreso=self._callback_progreso_seguro,
            )
            self.root.after(0, self._conversion_exitosa)
        except Exception as e:
            self.root.after(0, self._conversion_fallida, str(e))

    def _callback_progreso_seguro(self, actual, total, mensaje):
        """Envía el progreso al hilo de la GUI de forma segura."""
        porcentaje = actual / total if total > 0 else 0.0
        self.root.after(0, self._actualizar_progreso_gui, porcentaje, mensaje)

    def _actualizar_progreso_gui(self, porcentaje, mensaje):
        """Actualiza la barra y el texto en el hilo principal."""
        self.lbl_estado.config(text=mensaje)
        self.progreso.actualizar_progreso(porcentaje)

    def _conversion_exitosa(self):
        """Post-conversión exitosa: mantiene la app abierta y ofrece abrir carpeta."""
        self.is_converting = False
        self.progreso.actualizar_progreso(1.0)
        self.progreso.detener_shimmer()
        self.lbl_estado.config(text="✅ ¡Conversión completada con éxito!", fg=COLOR_SUCCESS)

        # Determinar la carpeta de salida
        if self.var_carpeta_salida.get():
            self._ultima_carpeta_salida = self.var_carpeta_salida.get()
        elif self.rutas_archivos:
            self._ultima_carpeta_salida = os.path.dirname(self.rutas_archivos[0])
        else:
            self._ultima_carpeta_salida = ""

        # Mostrar botón "Abrir carpeta" y conteo de PDFs
        num_pdfs = len(self._pdfs_generados) if hasattr(self, "_pdfs_generados") else 0
        calidad = self.var_calidad.get()
        messagebox.showinfo(
            "Éxito",
            f"¡Conversión completada!\n\n"
            f"PDFs generados: {num_pdfs}\n"
            f"Calidad: {calidad}\n"
            f"Ubicación: {self._ultima_carpeta_salida}"
        )

        self.btn_abrir_carpeta.pack(fill="x", pady=5)
        self._cambiar_estado_widgets("normal")
        self._actualizar_estado_boton()

    def _conversion_fallida(self, error_msg):
        """Maneja errores de conversión."""
        self.is_converting = False
        self.progreso.detener_shimmer()
        self.lbl_estado.config(text="❌ Error en la conversión", fg=COLOR_DANGER)
        self.progreso.pack_forget()
        self._cambiar_estado_widgets("normal")
        self._actualizar_estado_boton()

        messagebox.showerror("Error", f"Ocurrió un error durante la conversión:\n\n{error_msg}")

    def abrir_carpeta_salida(self):
        """Abre la carpeta donde se guardaron los PDFs en el explorador de archivos."""
        carpeta = getattr(self, "_ultima_carpeta_salida", "")
        if carpeta and os.path.isdir(carpeta):
            if sys.platform == "win32":
                os.startfile(carpeta)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", carpeta])
            else:
                subprocess.Popen(["xdg-open", carpeta])
