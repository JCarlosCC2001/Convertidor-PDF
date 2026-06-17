<div align="center">
  <h1>📄 Convertidor PDF</h1>
  <p><i>Automatización de imágenes a PDF (A4) directo desde el menú contextual.</i></p>
  
  ![Python](https://img.shields.io/badge/Python-Script-blue?style=for-the-badge&logo=python&logoColor=white)
  ![Pillow](https://img.shields.io/badge/Pillow-Library-green?style=for-the-badge)
  ![Tkinter](https://img.shields.io/badge/Tkinter-GUI-orange?style=for-the-badge)
</div>

---

> **Descripción**
> Pequeña utilidad con interfaz gráfica desarrollada en Python para automatizar la conversión de imágenes a formato PDF. Diseñada específicamente para optimizar el flujo de trabajo diario y organizar rápidamente los documentos probatorios del proyecto de **Mantenimiento Amazonas**.

## ✨ Características Principales

* 🖥️ **Interfaz gráfica intuitiva** para agilizar la selección de parámetros.
* 📐 **Ajuste perfecto a A4 Vertical** sin dejar márgenes blancos indeseados.
* 🎛️ **Múltiples calidades de salida**, incluyendo una opción de alta resolución a 300 DPI.
* 📑 **Flexibilidad de exportación**, permitiendo unificar múltiples imágenes en un solo PDF o procesarlas por separado.
* 💾 **Memoria de preferencias**, guardando tus últimas elecciones para ahorrar tiempo en futuras conversiones.

## 🚀 Requisitos e Instalación

Para configurar el entorno de desarrollo y utilizar el script correctamente:

1. Abre una terminal en la carpeta raíz del proyecto.
2. Crea un entorno virtual aislado:
   ```bash
   python -m venv .venv
3. Activa el entorno virtual:
   ```bash
   .venv\Scripts\Activate.ps1
   ```
4. Instala las dependencias necesarias:
   ```bash
   pip install Pillow
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