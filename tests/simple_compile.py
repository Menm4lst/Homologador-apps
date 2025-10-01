#!/usr/bin/env python3
"""
Script simplificado de compilación para el Homologador.
"""


from pathlib import Path
import os
import shutil
import sys

import subprocess
def simple_compile():
    """Compilación simple con PyInstaller."""
    
    print("🔧 Compilando Homologador de Aplicaciones...")
    
    # Crear carpeta de destino
    output_dir = Path("../HOMOLOGADOR_COMPILADO")
    output_dir.mkdir(exist_ok=True)
    
    # Comando básico de PyInstaller
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--name=HomologadorApp", 
        "--windowed",
        f"--distpath={output_dir.absolute()}",
        "--clean",
        "homologador/app.py"
    ]
    
    print(f"Ejecutando: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, cwd=os.getcwd())
        print("✅ Compilación básica exitosa!")
        
        # Copiar archivos importantes
        files_to_copy = [
            "requirements.txt",
            "README.md"
        ]
        
        for file in files_to_copy:
            if Path(file).exists():
                shutil.copy2(file, output_dir / file)
                print(f"  ✓ Copiado: {file}")
        
        # Crear script de lanzamiento
        bat_content = '''@echo off
title Homologador de Aplicaciones
echo Iniciando Homologador...
HomologadorApp.exe
'''
        
        with open(output_dir / "Ejecutar.bat", "w") as f:
            f.write(bat_content)
        
        print(f"\n🎉 Compilación completada en: {output_dir.absolute()}")
        print("📁 Archivos generados:")
        for item in output_dir.iterdir():
            print(f"  - {item.name}")
            
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    simple_compile()