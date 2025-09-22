#!/usr/bin/env python3
"""
Script simple para ejecutar el Homologador.
"""

import sys
import os
from pathlib import Path

# Configurar el path
project_root = Path(__file__).parent
homologador_path = project_root / "homologador"
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(homologador_path))

# Cambiar al directorio homologador para imports relativos
os.chdir(str(homologador_path))

def main():
    """Ejecutar la aplicación."""
    print("🚀 Iniciando Homologador de Aplicaciones...")
    print("📁 Directorio del proyecto:", project_root)
    
    try:
        # Cambiar al directorio del proyecto
        os.chdir(str(project_root))
        
        # Importar PyQt6
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import Qt
        
        print("✓ PyQt6 importado correctamente")
        
        # Crear aplicación
        app = QApplication(sys.argv)
        app.setApplicationName("Homologador")
        app.setApplicationVersion("1.0.0")
        
        # Configurar para que no se cierre al cerrar la última ventana
        app.setQuitOnLastWindowClosed(True)
        
        print("✓ QApplication creada")
        
        # Intentar importar la aplicación principal
        try:
            from app import HomologadorApplication, main as app_main
            print("✓ Módulo principal importado")
            
            # Ejecutar la función main de la aplicación
            return app_main()
            
        except ImportError as e:
            print(f"❌ Error importando aplicación: {e}")
            print("❌ Verifique que los archivos estén en su lugar correcto")
            return 1
            
            return app_main()
            
    except Exception as e:
        print(f"❌ Error ejecutando aplicación: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = main()
    print(f"📝 Aplicación terminada con código: {exit_code}")
    sys.exit(exit_code)