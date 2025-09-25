#!/usr/bin/env python3
"""
Script para ejecutar la aplicación Homologador de forma visible y persistente.
"""

import sys
import os
import subprocess
import time

def main():
    """Ejecuta la aplicación y espera."""
    project_root = "C:\\Users\\Antware\\OneDrive\\Desktop\\PROYECTOS DEV\\APP HOMOLOGACIONES"
    python_exe = f"{project_root}\\.venv\\Scripts\\python.exe"
    script_path = f"{project_root}\\ejecutar_homologador.py"
    
    print("🚀 Iniciando aplicación Homologador...")
    print("📝 Con el nuevo tema negro-azul moderno")
    print("⏳ Esperando que aparezca la ventana de login...")
    print()
    print("💡 Credenciales para probar:")
    print("   Usuario: admin")
    print("   Contraseña: admin123")
    print()
    
    # Ejecutar la aplicación
    try:
        result = subprocess.run([python_exe, script_path], 
                              cwd=project_root,
                              capture_output=False)
        
        if result.returncode == 0:
            print("✅ Aplicación cerrada correctamente")
        else:
            print(f"⚠️ Aplicación cerrada con código: {result.returncode}")
            
    except Exception as e:
        print(f"❌ Error ejecutando aplicación: {e}")
    
    print()
    print("🔄 La aplicación se ha cerrado.")
    input("Presiona Enter para salir...")

if __name__ == "__main__":
    main()