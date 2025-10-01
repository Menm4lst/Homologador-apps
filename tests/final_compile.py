#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de compilación final para Homologador
Usa esquema embebido para evitar dependencias externas
"""


from pathlib import Path
import os
import shutil
import sys

import subprocess
def clean_build_dirs():
    """Limpia directorios de compilación anteriores"""
    dirs_to_clean = ['build', 'dist', '__pycache__']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"Eliminando {dir_name}...")
            try:
                shutil.rmtree(dir_name)
            except PermissionError:
                print(f"  ⚠️ No se pudo eliminar {dir_name} (archivos en uso)")
                print(f"  Continuando sin eliminar...")
            except Exception as e:
                print(f"  ⚠️ Error eliminando {dir_name}: {e}")
                print(f"  Continuando...")
    
    # Limpiar archivos spec
    for spec_file in Path('.').glob('*.spec'):
        print(f"Eliminando {spec_file}...")
        spec_file.unlink()

def create_spec_file():
    """Crea archivo .spec para PyInstaller"""
    spec_content = """# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['homologador/app.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'PyQt6.QtCore',
        'PyQt6.QtGui', 
        'PyQt6.QtWidgets',
        'homologador.data.embedded_schema',
        'homologador.core',
        'homologador.ui',
        'homologador.utils',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Homologador',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
"""
    
    with open('homologador_final.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("Archivo .spec creado: homologador_final.spec")

def compile_app():
    """Compila la aplicación"""
    print("Iniciando compilación final...")
    
    # Verificar que PyInstaller esté instalado
    try:
        import PyInstaller
        print(f"PyInstaller versión: {PyInstaller.__version__}")
    except ImportError:
        print("PyInstaller no está instalado. Instalando...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # Comando de compilación
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--clean",
        "--noconfirm", 
        "homologador_final.spec"
    ]
    
    print(f"Ejecutando: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Compilación exitosa!")
        return True
    else:
        print("❌ Error en compilación:")
        print(result.stdout)
        print(result.stderr)
        return False

def create_deployment_folder():
    """Crea carpeta de deployment con todos los archivos necesarios"""
    deployment_path = Path("Homologador_Deployment")
    
    if deployment_path.exists():
        print("Eliminando deployment anterior...")
        shutil.rmtree(deployment_path)
    
    deployment_path.mkdir()
    print(f"Creando carpeta de deployment: {deployment_path}")
    
    # Copiar ejecutable
    exe_source = Path("dist/Homologador.exe")
    if exe_source.exists():
        shutil.copy2(exe_source, deployment_path / "Homologador.exe")
        print("✅ Ejecutable copiado")
    else:
        print("❌ No se encontró el ejecutable compilado")
        return False
    
    # Crear README
    readme_content = """# Homologador de Aplicaciones

## Instalación y Uso

1. Ejecute `Homologador.exe` 
2. La aplicación creará automáticamente la base de datos y archivos necesarios
3. Use las credenciales por defecto:
   - Usuario: admin
   - Contraseña: admin123

## Características

- Gestión de homologaciones de aplicaciones
- Sistema de backup automático 
- Gestión de usuarios con roles
- Interfaz moderna con tema oscuro
- Base de datos SQLite integrada

## Soporte Técnico

Para reportar problemas o solicitar nuevas características, contacte al equipo de desarrollo.

Versión: 1.0.0
Fecha de compilación: 2024
"""
    
    with open(deployment_path / "README.md", 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print("✅ Carpeta de deployment creada exitosamente")
    return True

def main():
    """Función principal de compilación"""
    print("=== COMPILACIÓN FINAL HOMOLOGADOR ===")
    print()
    
    # Verificar que estemos en el directorio correcto
    if not Path("homologador").exists():
        print("❌ Error: No se encuentra el directorio 'homologador'")
        print("Ejecute este script desde el directorio raíz del proyecto")
        return False
    
    try:
        # 1. Limpiar compilaciones anteriores
        clean_build_dirs()
        
        # 2. Crear archivo .spec
        create_spec_file()
        
        # 3. Compilar aplicación
        if not compile_app():
            return False
        
        # 4. Crear carpeta de deployment
        if not create_deployment_folder():
            return False
        
        print()
        print("🎉 ¡COMPILACIÓN COMPLETADA EXITOSAMENTE!")
        print(f"📁 Encuentra tu aplicación en: Homologador_Deployment/")
        print(f"🚀 Ejecutable: Homologador_Deployment/Homologador.exe")
        
        return True
        
    except Exception as e:
        print(f"❌ Error durante la compilación: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
    
    input("\nPresiona Enter para continuar...")