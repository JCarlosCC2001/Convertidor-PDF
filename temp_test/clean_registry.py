import winreg
import os
import sys

def remover_accion(ext, accion_id):
    try:
        winreg.DeleteKey(winreg.HKEY_CURRENT_USER, fr"Software\Classes\SystemFileAssociations\{ext}\shell\{accion_id}\command")
        print(f"Borrando comando de {ext} - {accion_id}")
    except Exception as e:
        pass
    try:
        winreg.DeleteKey(winreg.HKEY_CURRENT_USER, fr"Software\Classes\SystemFileAssociations\{ext}\shell\{accion_id}")
        print(f"Borrando llave de {ext} - {accion_id}")
    except Exception as e:
        pass

def clean():
    extensiones_todas = [".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tiff", ".tif", ".docx", ".pdf"]
    extensiones_transformar = [".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tiff", ".docx"]

    for ext in extensiones_todas:
        remover_accion(ext, "ConvertidorPDF_Abrir")
    
    for ext in extensiones_transformar:
        remover_accion(ext, "ConvertidorPDF_Transformar")
    
    remover_accion(".pdf", "ConvertidorPDF_Unir")
    remover_accion(".pdf", "ConvertidorPDF_Dividir")
    remover_accion(".pdf", "ConvertidorPDF_BN")
    
    # Intentar también borrar registros antiguos si existen
    try: winreg.DeleteKey(winreg.HKEY_CURRENT_USER, r"Software\Classes\*\shell\ConvertidorPDF\command")
    except: pass
    try: winreg.DeleteKey(winreg.HKEY_CURRENT_USER, r"Software\Classes\*\shell\ConvertidorPDF")
    except: pass
    
    print("Limpieza de registro completada.")

if __name__ == '__main__':
    clean()
