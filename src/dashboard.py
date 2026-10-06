import os
import tkinter as tk
from tkinter import filedialog, messagebox
from src.config import clasificar_archivo, EXTENSIONES_IMAGEN, EXTENSIONES_WORD, EXTENSIONES_PDF
from src.gui import ConvertidorGUI

# Paleta de colores (Tema Claro/Blanco)
COLOR_BG = "#f3f4f6"
COLOR_HEADER = "#ffffff"
COLOR_CARD = "#ffffff"
COLOR_CARD_BORDER = "#d1d5db"
COLOR_TEXT_PRIMARY = "#1f2937"
COLOR_TEXT_MUTED = "#6b7280"
COLOR_ACCENT = "#2563eb"
COLOR_ACCENT_HOVER = "#1d4ed8"
COLOR_DISABLED = "#f9fafb"
COLOR_TEXT_DISABLED = "#9ca3af"
COLOR_SUCCESS = "#10b981"

class DashboardGUI:
    def __init__(self, root, rutas_iniciales=None, accion_inicial=None):
        self.root = root
        self.rutas_archivos = list(rutas_iniciales) if rutas_iniciales else []
        self.accion_inicial = accion_inicial
        
        self.root.title("Convertidor PDF - Centro de Herramientas")
        self.root.configure(bg=COLOR_BG)
        self.root.resizable(False, False)
        
        # Tamaño de la ventana del dashboard (más ancho, menos alto para 4 columnas)
        self.centrar_ventana(850, 560)
        
        try:
            self.root.iconbitmap("logo.ico")
        except Exception:
            pass
            
        self.crear_interfaz()
        self.actualizar_estado_botones()
        
    def centrar_ventana(self, ancho, alto):
        pantalla_ancho = self.root.winfo_screenwidth()
        pantalla_alto = self.root.winfo_screenheight()
        x = (pantalla_ancho - ancho) // 2
        y = (pantalla_alto - alto) // 2
        self.root.geometry(f"{ancho}x{alto}+{x}+{y}")
        
    def crear_interfaz(self):
        # Header
        self.frame_header = tk.Frame(self.root, bg=COLOR_HEADER, height=60)
        self.frame_header.pack(fill="x")
        self.frame_header.pack_propagate(False)
        
        self.lbl_titulo = tk.Label(
            self.frame_header, text="🧰 CENTRO DE HERRAMIENTAS PDF",
            font=("Segoe UI", 14, "bold"), bg=COLOR_HEADER, fg=COLOR_TEXT_PRIMARY
        )
        self.lbl_titulo.pack(pady=15)
        
        # Barra de estado de archivos
        self.frame_estado = tk.Frame(self.root, bg=COLOR_BG)
        self.frame_estado.pack(fill="x", padx=20, pady=(15, 5))
        
        self.lbl_archivos = tk.Label(
            self.frame_estado, text="No hay archivos seleccionados",
            font=("Segoe UI", 11, "bold"), bg=COLOR_BG, fg=COLOR_TEXT_MUTED
        )
        self.lbl_archivos.pack(side="left")
        
        btn_agregar = tk.Button(
            self.frame_estado, text="＋ Agregar Archivos", font=("Segoe UI", 9, "bold"),
            bg=COLOR_ACCENT, fg=COLOR_TEXT_PRIMARY, bd=0, padx=15, pady=5, cursor="hand2",
            activebackground=COLOR_ACCENT_HOVER, activeforeground=COLOR_TEXT_PRIMARY,
            command=self.agregar_archivos
        )
        btn_agregar.pack(side="right")
        
        btn_limpiar = tk.Button(
            self.frame_estado, text="✕ Limpiar", font=("Segoe UI", 9, "bold"),
            bg=COLOR_HEADER, fg=COLOR_TEXT_PRIMARY, bd=0, padx=10, pady=5, cursor="hand2",
            activebackground=COLOR_CARD_BORDER, activeforeground=COLOR_TEXT_PRIMARY,
            command=self.limpiar_archivos
        )
        btn_limpiar.pack(side="right", padx=10)
        
        # Cuadrícula de herramientas (Grid)
        self.frame_grid = tk.Frame(self.root, bg=COLOR_BG)
        self.frame_grid.pack(fill="both", expand=True, padx=20, pady=15)
        
        # Configurar 4 columnas y 3 filas
        for i in range(4):
            self.frame_grid.columnconfigure(i, weight=1, uniform="col")
        for i in range(3):
            self.frame_grid.rowconfigure(i, weight=1, uniform="row")
            
        # Definición de las 10 herramientas (4 columnas x 3 filas)
        self.herramientas = [
            {"id": "unir", "nombre": "Unir PDF", "icono": "🔗", "row": 0, "col": 0},
            {"id": "dividir", "nombre": "Dividir PDF", "icono": "✂️", "row": 0, "col": 1},
            {"id": "comprimir", "nombre": "Comprimir PDF", "icono": "🗜️", "row": 0, "col": 2},
            {"id": "pdf2word", "nombre": "De PDF a Word", "icono": "📝", "row": 0, "col": 3},
            {"id": "word2pdf", "nombre": "De Word a PDF", "icono": "📄", "row": 1, "col": 0},
            {"id": "pdf2img", "nombre": "De PDF a Imagen", "icono": "🖼️", "row": 1, "col": 1},
            {"id": "img2pdf", "nombre": "De Imagen a PDF", "icono": "📸", "row": 1, "col": 2},
            {"id": "editar", "nombre": "Editar PDF", "icono": "🛠️", "row": 1, "col": 3},
            {"id": "bloquear", "nombre": "Bloqueo de PDF", "icono": "🔒", "row": 2, "col": 1}, # Centrado en col 1
            {"id": "reparar", "nombre": "Reparar PDF", "icono": "🔧", "row": 2, "col": 2},   # Centrado en col 2
        ]
        
        self.botones = {}
        for h in self.herramientas:
            btn = self.crear_boton_herramienta(self.frame_grid, h)
            btn.grid(row=h["row"], column=h["col"], sticky="nsew", padx=6, pady=6)
            self.botones[h["id"]] = btn
            
    def crear_boton_herramienta(self, parent, config):
        frame = tk.Frame(
            parent, bg=COLOR_CARD, bd=1, relief="solid",
            highlightthickness=1, highlightbackground=COLOR_CARD_BORDER
        )
        
        lbl_icono = tk.Label(frame, text=config["icono"], font=("Segoe UI", 28), bg=COLOR_CARD, fg=COLOR_TEXT_PRIMARY)
        lbl_icono.pack(expand=True, pady=(10, 0))
        
        lbl_texto = tk.Label(frame, text=config["nombre"], font=("Segoe UI", 9, "bold"), bg=COLOR_CARD, fg=COLOR_TEXT_PRIMARY)
        lbl_texto.pack(expand=True, pady=(0, 10))
        
        # Hacer que los clics en cualquier parte del frame disparen la acción
        for widget in (frame, lbl_icono, lbl_texto):
            widget.bind("<Button-1>", lambda e, id_h=config["id"]: self.ejecutar_herramienta(id_h))
            widget.bind("<Enter>", lambda e, f=frame: self.hover_enter(f))
            widget.bind("<Leave>", lambda e, f=frame: self.hover_leave(f))
            
        frame.lbl_icono = lbl_icono
        frame.lbl_texto = lbl_texto
        frame.config_id = config["id"]
        frame.estado = "normal"
        
        return frame
        
    def hover_enter(self, frame):
        if frame.estado == "normal":
            frame.config(bg=COLOR_CARD_BORDER, cursor="hand2")
            frame.lbl_icono.config(bg=COLOR_CARD_BORDER, cursor="hand2")
            frame.lbl_texto.config(bg=COLOR_CARD_BORDER, cursor="hand2")
            
    def hover_leave(self, frame):
        if frame.estado == "normal":
            frame.config(bg=COLOR_CARD, cursor="arrow")
            frame.lbl_icono.config(bg=COLOR_CARD, cursor="arrow")
            frame.lbl_texto.config(bg=COLOR_CARD, cursor="arrow")
            
    def agregar_archivos(self):
        extensiones_img = " ".join(f"*{ext}" for ext in sorted(EXTENSIONES_IMAGEN))
        extensiones_word = " ".join(f"*{ext}" for ext in sorted(EXTENSIONES_WORD))
        extensiones_pdf = " ".join(f"*{ext}" for ext in sorted(EXTENSIONES_PDF))
        
        tipos = [
            ("Todos los soportados", f"{extensiones_img} {extensiones_word} {extensiones_pdf}"),
            ("Imágenes", extensiones_img),
            ("Documentos Word", extensiones_word),
            ("Archivos PDF", extensiones_pdf),
        ]
        
        archivos = filedialog.askopenfilenames(title="Seleccionar archivos", filetypes=tipos)
        if archivos:
            self.rutas_archivos.extend(a for a in archivos if a not in self.rutas_archivos)
            self.actualizar_estado_botones()
            
    def limpiar_archivos(self):
        self.rutas_archivos.clear()
        self.actualizar_estado_botones()
        
    def agregar_archivos_externos(self, archivos, accion=None):
        if archivos:
            self.rutas_archivos.extend(a for a in archivos if a not in self.rutas_archivos)
            self.root.after(0, self.actualizar_estado_botones)
            
            # Traer al frente
            if self.root.state() == 'iconic':
                self.root.deiconify()
            self.root.lift()
            self.root.attributes('-topmost', True)
            self.root.attributes('-topmost', False)
            
    def actualizar_estado_botones(self):
        # Contar tipos de archivos
        num_pdf = sum(1 for r in self.rutas_archivos if clasificar_archivo(r) == "pdf")
        num_word = sum(1 for r in self.rutas_archivos if clasificar_archivo(r) == "word")
        num_img = sum(1 for r in self.rutas_archivos if clasificar_archivo(r) == "imagen")
        total = len(self.rutas_archivos)
        
        # Actualizar texto superior
        if total == 0:
            self.lbl_archivos.config(text="No hay archivos seleccionados. Agrega archivos para habilitar opciones.", fg=COLOR_TEXT_MUTED)
        else:
            textos = []
            if num_pdf: textos.append(f"{num_pdf} PDF{'s' if num_pdf>1 else ''}")
            if num_word: textos.append(f"{num_word} Word")
            if num_img: textos.append(f"{num_img} Imagen{'es' if num_img>1 else ''}")
            self.lbl_archivos.config(text="Selección actual: " + " + ".join(textos), fg=COLOR_SUCCESS)
            
        # Lógica de habilitación
        def set_estado(btn_id, habilitado):
            btn = self.botones[btn_id]
            if habilitado:
                btn.estado = "normal"
                btn.config(bg=COLOR_CARD, highlightbackground=COLOR_CARD_BORDER)
                btn.lbl_icono.config(bg=COLOR_CARD, fg=COLOR_TEXT_PRIMARY)
                btn.lbl_texto.config(bg=COLOR_CARD, fg=COLOR_TEXT_PRIMARY)
            else:
                btn.estado = "disabled"
                btn.config(bg=COLOR_DISABLED, highlightbackground=COLOR_CARD_BORDER)
                btn.lbl_icono.config(bg=COLOR_DISABLED, fg=COLOR_TEXT_DISABLED)
                btn.lbl_texto.config(bg=COLOR_DISABLED, fg=COLOR_TEXT_DISABLED)

        # Si no hay archivos, bloqueamos todo
        if total == 0:
            for b in self.botones:
                set_estado(b, False)
            return

        # Habilitar según reglas precisas solicitadas
        set_estado("unir", num_pdf >= 2 and total == num_pdf)
        set_estado("dividir", num_pdf == 1 and total == 1)
        set_estado("comprimir", num_pdf > 0 and total == num_pdf)
        set_estado("pdf2word", num_pdf > 0 and total == num_pdf)
        
        # Opciones mixtas o singulares
        set_estado("word2pdf", num_word > 0 and total == num_word)
        set_estado("pdf2img", num_pdf > 0 and total == num_pdf)
        set_estado("img2pdf", num_img > 0 and total == num_img)
        
        set_estado("editar", num_pdf == 1 and total == 1)
        set_estado("bloquear", num_pdf > 0 and total == num_pdf)
        set_estado("reparar", num_pdf > 0 and total == num_pdf)
            
    def ejecutar_herramienta(self, btn_id):
        btn = self.botones[btn_id]
        if btn.estado == "disabled":
            # Opcional: mostrar tooltip de por qué está deshabilitado
            messagebox.showinfo("Opción no disponible", "Los archivos seleccionados no son compatibles con esta función.")
            return
            
        if btn_id in ["unir", "dividir", "word2pdf", "img2pdf", "pdf2word", "pdf2img"]:
            self.abrir_vista_clasica(btn_id)
        else:
            # Funciones por construir en la próxima iteración
            messagebox.showinfo(
                "En desarrollo", 
                f"La herramienta '{btn.lbl_texto.cget('text')}' está en desarrollo en esta versión del plan.\n\n"
                "Pronto podrás usar esta nueva función."
            )

    def abrir_vista_clasica(self, accion):
        # Mapear accion del dashboard a la accion clásica
        accion_map = {
            "unir": "unir",
            "dividir": "dividir",
            "word2pdf": "transformar",
            "img2pdf": "transformar",
            "pdf2word": "pdf2word",
            "pdf2img": "pdf2img"
        }
        accion_str = accion_map.get(accion, "transformar")
        
        # Ocultar dashboard
        self.root.withdraw()
        
        top = tk.Toplevel(self.root)
        
        def on_close():
            top.destroy()
            self.root.deiconify()
            
        top.protocol("WM_DELETE_WINDOW", on_close)
        
        # Iniciar la interfaz clásica en el Toplevel
        app = ConvertidorGUI(top, self.rutas_archivos, accion_str)
