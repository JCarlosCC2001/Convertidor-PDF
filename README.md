<div align="center">
  <h1>📄 Convertidor PDF</h1>
  <p><i>Automatización de imágenes a PDF (A4) directo desde el menú contextual o de forma independiente.</i></p>
  
  ![Python](https://img.shields.io/badge/Python-Script-blue?style=for-the-badge&logo=python&logoColor=white)
  ![Pillow](https://img.shields.io/badge/Pillow-Library-green?style=for-the-badge)
  ![Tkinter](https://img.shields.io/badge/Tkinter-GUI-orange?style=for-the-badge)
</div>

---

> **Descripción**
> Utilidad moderna con interfaz gráfica desarrollada en Python para automatizar la conversión de imágenes a formato PDF. Diseñada específicamente para optimizar el flujo de trabajo diario y organizar rápidamente los documentos probatorios del proyecto de **Mantenimiento Amazonas**.

## ✨ Características Principales y Mejoras

* 🖥️ **Interfaz Gráfica Premium**: Rediseñada por completo con una tonalidad azul `#002060`, organización visual mejorada y micro-animaciones en los botones.
* ⚡ **Procesamiento Asíncrono**: Ejecución de conversiones en segundo plano para evitar que la ventana se congele ("No responde") al procesar imágenes pesadas o numerosos archivos.
* 📊 **Indicador de Progreso en Tiempo Real**: Incorpora una barra de progreso personalizada y texto descriptivo que indica dinámicamente qué imagen se está procesando.
* 📂 **Selector de Archivos Integrado**: Si abres el programa directamente (sin arrastrar imágenes), ahora permite elegir imágenes de forma interactiva desde la GUI.
* 📐 **Ajuste Perfecto a A4 Vertical**: Recorta y escala las imágenes de manera inteligente al tamaño A4 exacto sin distorsionarlas y eliminando márgenes blancos.
* 🎛️ **Opciones Flexibles**:
  * Unificar múltiples imágenes en un único PDF o generar un PDF independiente para cada una.
  * Opciones de color: a todo color o escala de grises optimizada (Blanco y Negro).
  * 3 calidades de resolución configurables (Baja, Media, Alta a 300 DPI).
* 💾 **Memoria de Preferencias**: Guarda automáticamente tu última configuración elegida para agilizar futuras conversiones.
* 🚀 **Optimización de Memoria**: Carga perezosa (lazy evaluation) y liberación de recursos inmediata, previniendo picos de uso de memoria RAM al procesar grandes lotes de imágenes.

## 📂 Estructura del Proyecto

El proyecto está organizado siguiendo buenas prácticas de modularidad:
```
Convertidor-PDF/
├── src/
│   ├── __init__.py      # Inicializador de paquete
│   ├── config.py        # Gestión de configuraciones del usuario
│   ├── converter.py     # Motor de conversión y procesamiento de imágenes
│   └── gui.py           # Interfaz gráfica moderna (Tema Azul #002060)
├── main.py              # Punto de entrada de la aplicación
├── requirements.txt     # Dependencias del proyecto (Pillow)
└── README.md            # Documentación
```

## 🚀 Requisitos e Instalación

Para configurar el entorno de desarrollo y utilizar el script correctamente:

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

## 📎 Configuración del Menú Contextual (Anticlick)

Para utilizar esta herramienta directamente desde el explorador de archivos (menú contextual):

1. Presiona `Windows + R`.
2. Escribe `shell:sendto` y presiona `Enter`.
3. Haz clic derecho en el espacio en blanco y selecciona **Nuevo > Acceso directo**.
4. En el campo de ubicación, agrega la ruta completa del ejecutable de Python del entorno virtual seguida de la ruta del script principal. Ejemplo:
   ```bash
   "D:\Desarrollo Software\Convertidor-PDF\.venv\Scripts\python.exe" "D:\Desarrollo Software\Convertidor-PDF\main.py"
   ```
5. Asigna un nombre descriptivo al acceso directo (ej. `Convertidor PDF`).
6. **Opcional**: Cambia el icono del acceso directo por uno personalizado (.ico) desde sus propiedades.

## 🔍 Solución de Problemas (Troubleshooting)

Si tienes problemas para activar el entorno virtual debido a restricciones de permisos en PowerShell:

1. Abre una terminal en la carpeta del proyecto.
2. Ejecuta el siguiente comando para otorgar permisos temporales:
   ```bash
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
   ```
3. Intenta activar el entorno nuevamente con:
   ```bash
   .\.venv\Scripts\Activate.ps1
   ```

---

<div align="center">
  <p><i>Desarrollado con ❤️ por JCarlosCC2001</i></p>
</div>