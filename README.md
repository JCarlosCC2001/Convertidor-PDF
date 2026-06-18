<div align="center">
  <h1>📄 Convertidor PDF Multipropósito</h1>
  <p><i>Automatización de imágenes, documentos Word (.docx) y combinación de archivos PDF a PDF (A4) con interfaz gráfica premium e independiente.</i></p>
  
  ![Python](https://img.shields.io/badge/Python-Script-blue?style=for-the-badge&logo=python&logoColor=white)
  ![Pillow](https://img.shields.io/badge/Pillow-Library-green?style=for-the-badge)
  ![python-docx](https://img.shields.io/badge/python--docx-Word-blue?style=for-the-badge)
  ![reportlab](https://img.shields.io/badge/reportlab-PDF--Gen-red?style=for-the-badge)
  ![Tkinter](https://img.shields.io/badge/Tkinter-GUI-orange?style=for-the-badge)
</div>

---

> **Descripción**
> Utilidad moderna con interfaz gráfica desarrollada en Python para automatizar la conversión de imágenes, documentos de Microsoft Word y la unión de archivos PDF a formato PDF. Diseñada específicamente para optimizar el flujo de trabajo diario y organizar rápidamente documentos probatorios.

---

## ✨ Características Principales y Mejoras

* 🖥️ **Interfaz Gráfica Premium**: Tema azul oscuro con base en `#002060`, organización visual en tarjetas de configuración y controles modernos.
* 📄 **Soporte Nativo de Word (.docx)**: Conversión directa de archivos Word a PDF manteniendo formato básico (negritas, cursivas, subrayados, listas de viñetas, tablas alineadas y encabezados) de forma local, **sin requerir Microsoft Office instalado**.
* 📕 **Fusión de PDFs existentes**: Soporte nativo para importar, ordenar y fusionar múltiples documentos PDF en uno solo.
* 📋 **Lista Visual Scrollable**: Muestra de manera clara la cola de archivos cargados con iconos indicativos para cada formato (📷 para imágenes, 📄 para documentos Word, 📕 para archivos PDF).
* 🎛️ **Gestión de Cola**: Botones integrados para ordenar (**▲ Subir** / **▼ Bajar**) y eliminar (**🗑 Quitar**) archivos individuales antes de la conversión.
* 📐 **Orientación Automática Inteligente**: Detección dinámica de imágenes horizontales para ajustar la página A4 en modo apaisado automáticamente, evitando distorsiones y manteniendo el flujo de página natural.
* 📁 **Control de Salida Flexible**: Permite elegir una carpeta de destino personalizada para los PDFs resultantes y definir un nombre personalizado para la salida en modo unido.
* 💡 **Tooltips Interactivos**: Ayudas visuales al pasar el mouse por encima de los controles para una mejor comprensión de los niveles de calidad y DPI.
* ⚡ **Procesamiento Asíncrono con Shimmer**: Barra de progreso animada con efecto shimmer (brillo en movimiento) e indicador de estado detallado en tiempo real que corre en un hilo secundario para evitar bloqueos de la GUI.
* 💾 **Persistencia de Opciones**: Guarda y recupera las últimas preferencias del usuario (carpeta de destino, calidad, modo de color, etc.) para futuras sesiones.
* 🔄 **Flujo de Trabajo Continuo**: La aplicación permanece abierta tras completar con éxito una conversión, permitiendo nuevos trabajos al instante y ofreciendo acceso rápido con el botón **📂 Abrir carpeta de salida**.

---

## 📂 Estructura del Proyecto

El proyecto está organizado siguiendo buenas prácticas de modularidad:
```
Convertidor-PDF/
├── src/
│   ├── __init__.py        # Inicializador de paquete
│   ├── config.py          # Constantes, clasificación y persistencia de configuración
│   ├── converter.py       # Motor principal y enrutador de conversiones
│   ├── word_converter.py  # Conversión y renderizado de Word a PDF (.docx -> .pdf)
│   └── gui.py             # Interfaz gráfica (Tkinter con Tooltips y Barra Shimmer)
├── main.py                # Punto de entrada de la aplicación y gestión de logs
├── requirements.txt       # Dependencias actualizadas del proyecto
├── configuracion_pdf.json # Archivo local de preferencias del usuario
└── README.md              # Documentación principal
```

---

## 🚀 Requisitos e Instalación

Para configurar el entorno de desarrollo y utilizar la herramienta correctamente:

1. Abre una terminal en la carpeta raíz del proyecto.
2. Crea un entorno virtual aislado:
   ```bash
   python -m venv .venv
   ```
3. Activa el entorno virtual:
   - **En Windows (PowerShell)**:
     ```bash
     .venv\Scripts\Activate.ps1
     ```
   - **En Windows (CMD)**:
     ```cmd
     .venv\Scripts\activate.bat
     ```
4. Instala las dependencias necesarias:
   ```bash
   pip install -r requirements.txt
   ```

## 🚀 Instalación y Compilación Automática (Windows)

Esta aplicación incluye scripts para compilarse en un ejecutable independiente de Windows que corre de manera silenciosa (sin ventana de consola) y se instala con un solo comando.

### 1. Compilación del Ejecutable Silencioso
El script `build_exe.py` empaqueta la aplicación en un archivo único (`ConvertidorPDF.exe`) sin ventana de terminal CMD:
```bash
python build_exe.py
```
*Este comando generará el ejecutable y su respectivo icono premium en la carpeta `dist/`.*

### 2. Instalador Automático
El script `setup_installer.py` realiza la instalación local de la aplicación en el equipo:
```bash
python setup_installer.py
```

**¿Qué hace el instalador automáticamente?**
- Copia los ejecutables y logos al directorio local `%LOCALAPPDATA%\Programs\ConvertidorPDF` (no requiere permisos de administrador).
- **Acceso directo en el Escritorio y Menú Inicio**.
- **Menú Enviar a (SendTo)**: Registra la app en `Enviar a -> Convertidor PDF`, permitiendo seleccionar **múltiples archivos juntos** en el explorador de archivos y abrirlos en una sola ventana de la cola de conversión.
- **Menú Contextual directo (Anticlick)**: Registra la opción `Convertidor PDF` con su respectivo icono en el menú de clic derecho principal de archivos de Windows.

### 3. Desinstalación
Si deseas eliminar la aplicación y todas sus integraciones (accesos directos y registro), simplemente ve al directorio del programa o ejecuta:
```bash
python %LOCALAPPDATA%\Programs\ConvertidorPDF\uninstall.py
```

---

<div align="center">
  <p><i>Desarrollado con ❤️ por JCarlosCC2001</i></p>
</div>