#!/usr/bin/env python3
"""
Script de compilación para el Homologador de Aplicaciones.
Crea un ejecutable independiente con todas las dependencias.
"""


from pathlib import Path
import os
import shutil
import sys

import subprocess
def compile_application():
    """Compila la aplicación usando PyInstaller."""
    
    print("🔧 Iniciando compilación del Homologador de Aplicaciones...")
    
    # Directorio base
    base_dir = Path(__file__).parent
    
    # Directorio de destino
    output_dir = Path(r"c:\temp\HOMOLOGADOR_COMPILADO")
    
    # Limpiar directorio de destino si existe
    if output_dir.exists():
        print(f"🧹 Limpiando directorio: {output_dir}")
        shutil.rmtree(output_dir)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Configuración de PyInstaller
    pyinstaller_args = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",  # Un solo archivo ejecutable
        "--windowed",  # Sin consola (aplicación GUI)
        "--name=HomologadorApp",
        "--icon=homologador/ui/icons/app_icon.ico" if Path("homologador/ui/icons/app_icon.ico").exists() else "",
        f"--distpath={output_dir}",
        f"--workpath={output_dir}/build",
        f"--specpath={output_dir}",
        "--add-data=homologador/data;homologador/data",
        "--add-data=homologador/ui;homologador/ui",
        "--add-data=homologador/core;homologador/core",
        "--hidden-import=PyQt6.QtCore",
        "--hidden-import=PyQt6.QtWidgets", 
        "--hidden-import=PyQt6.QtGui",
        "--hidden-import=sqlite3",
        "--hidden-import=argon2",
        "--hidden-import=portalocker",
        "--hidden-import=pandas",
        "--clean",
        "homologador/app.py"
    ]
    
    # Filtrar argumentos vacíos
    pyinstaller_args = [arg for arg in pyinstaller_args if arg]
    
    print("📦 Ejecutando PyInstaller...")
    print(f"Comando: {' '.join(pyinstaller_args)}")
    
    try:
        # Ejecutar PyInstaller
        result = subprocess.run(pyinstaller_args, check=True, capture_output=True, text=True)
        print("✅ Compilación exitosa!")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error en la compilación:")
        print(f"Código de salida: {e.returncode}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        return False
    
    # Copiar archivos adicionales necesarios
    print("📋 Copiando archivos adicionales...")
    
    # Crear estructura de carpetas en el directorio compilado
    compiled_data_dir = output_dir / "data"
    compiled_data_dir.mkdir(exist_ok=True)
    
    # Copiar archivos de datos
    files_to_copy = [
        ("homologador/data/schema.sql", "data/schema.sql"),
        ("requirements.txt", "requirements.txt"),
        ("README.md", "README.md"),
        ("MANUAL_USUARIO.md", "MANUAL_USUARIO.md") if Path("MANUAL_USUARIO.md").exists() else None
    ]
    
    for source, dest in files_to_copy:
        if source and Path(source).exists():
            source_path = Path(source)
            dest_path = output_dir / dest
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_path, dest_path)
            print(f"  ✓ Copiado: {source} → {dest}")
    
    # Crear script de ejecución
    create_launcher_script(output_dir)
    
    # Crear documentación de instalación
    create_installation_guide(output_dir)
    
    print(f"\n🎉 ¡Compilación completada!")
    print(f"📁 Archivos generados en: {output_dir}")
    print(f"🚀 Ejecutable principal: {output_dir}/HomologadorApp.exe")
    
    return True

def create_launcher_script(output_dir):
    """Crea un script de lanzamiento adicional."""
    launcher_content = '''@echo off
title Homologador de Aplicaciones
echo ===============================================
echo    Homologador de Aplicaciones v1.0.0
echo    Iniciando sistema...
echo ===============================================
echo.

REM Verificar si el ejecutable existe
if not exist "HomologadorApp.exe" (
    echo ❌ Error: No se encontro HomologadorApp.exe
    echo.
    echo Asegurese de que este archivo se encuentre en la misma carpeta que HomologadorApp.exe
    pause
    exit /b 1
)

REM Ejecutar la aplicacion
echo ✅ Ejecutando Homologador...
start "" "HomologadorApp.exe"

REM Opcional: mantener la ventana abierta para ver mensajes de debug
REM timeout /t 3 /nobreak >nul
exit
'''
    
    launcher_path = output_dir / "Ejecutar_Homologador.bat"
    with open(launcher_path, 'w', encoding='utf-8') as f:
        f.write(launcher_content)
    print(f"  ✓ Script de lanzamiento creado: {launcher_path}")

def create_installation_guide(output_dir):
    """Crea una guía de instalación y uso."""
    guide_content = '''# 📋 GUÍA DE INSTALACIÓN - HOMOLOGADOR DE APLICACIONES

## 🎯 ARCHIVOS INCLUIDOS:
- `HomologadorApp.exe` - Ejecutable principal de la aplicación
- `Ejecutar_Homologador.bat` - Script de lanzamiento rápido
- `data/` - Carpeta con archivos de datos del sistema
- `INSTRUCCIONES_INSTALACION.md` - Este archivo

## 🚀 CÓMO EJECUTAR:

### Opción 1: Ejecutable directo
1. Hacer doble clic en `HomologadorApp.exe`
2. La aplicación se iniciará automáticamente

### Opción 2: Script de lanzamiento
1. Hacer doble clic en `Ejecutar_Homologador.bat`
2. Se abrirá una ventana de comandos y luego la aplicación

## 🔐 CREDENCIALES DE ACCESO:
- **Usuario:** admin
- **Contraseña:** admin123

## 📁 REQUISITOS DEL SISTEMA:
- Windows 10/11 (64-bit recomendado)
- 4 GB de RAM mínimo
- 100 MB de espacio en disco
- **NO requiere Python instalado** (incluido en el ejecutable)

## 🗃️ UBICACIÓN DE DATOS:
- La base de datos se crea automáticamente en: `%USERPROFILE%\OneDrive\homologador.db`
- Los respaldos se guardan en: `%USERPROFILE%\OneDrive\backups\`

## ⚡ CARACTERÍSTICAS PRINCIPALES:
✅ Gestión completa de homologaciones
✅ Sistema de usuarios con roles
✅ Respaldos automáticos
✅ Exportación de datos
✅ Interfaz moderna y intuitiva
✅ Sistema de auditoría

## 🛠️ SOLUCIÓN DE PROBLEMAS:

### Problema: "El programa no se puede ejecutar"
**Solución:** Instalar Microsoft Visual C++ Redistributable más reciente

### Problema: "Error al inicializar base de datos"
**Solución:** Verificar permisos de escritura en la carpeta OneDrive

### Problema: "Pantalla en blanco al iniciar"
**Solución:** Ejecutar como administrador

## 📞 SOPORTE:
- Versión del software: v1.0.0
- Fecha de compilación: Septiembre 2025
- Sistema: Homologador Corporativo

---
**¡Listo para usar!** 🎉
'''
    
    guide_path = output_dir / "INSTRUCCIONES_INSTALACION.md"
    with open(guide_path, 'w', encoding='utf-8') as f:
        f.write(guide_content)
    print(f"  ✓ Guía de instalación creada: {guide_path}")

if __name__ == "__main__":
    try:
        success = compile_application()
        if success:
            print("\n🎊 ¡COMPILACIÓN EXITOSA!")
            print("📦 El software está listo para distribuir")
        else:
            print("\n❌ Error en la compilación")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⏹️ Compilación cancelada por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Error inesperado: {e}")
        sys.exit(1)