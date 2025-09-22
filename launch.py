#!/usr/bin/env python3
"""
Launcher final para el Homologador de Aplicaciones.
Ejecuta la aplicación con todas las nuevas funcionalidades.
"""

import sys
import os
from pathlib import Path

def setup_environment():
    """Configurar el entorno de ejecución."""
    # Obtener la ruta del proyecto
    project_root = Path(__file__).parent.absolute()
    homologador_path = project_root / "homologador"
    
    # Configurar paths
    sys.path.insert(0, str(project_root))
    sys.path.insert(0, str(homologador_path))
    
    # Cambiar al directorio del proyecto
    os.chdir(str(homologador_path))
    
    return project_root, homologador_path

def main():
    """Función principal."""
    print("=" * 50)
    print("HOMOLOGADOR DE APLICACIONES")
    print("=" * 50)
    print("Iniciando aplicacion con nuevas funcionalidades...")
    
    try:
        # Configurar entorno
        project_root, homologador_path = setup_environment()
        print(f"Directorio del proyecto: {project_root}")
        print(f"Directorio homologador: {homologador_path}")
        
        # Verificar que PyQt6 esté disponible
        try:
            from PyQt6.QtWidgets import QApplication
            print("PyQt6 importado correctamente")
        except ImportError:
            print("ERROR: PyQt6 no esta instalado")
            print("Instale con: pip install PyQt6")
            return 1
        
        # Importar y ejecutar la aplicación
        try:
            import app
            print("Modulo principal importado")
            
            # Ejecutar la aplicación
            if hasattr(app, 'main'):
                print("Ejecutando aplicacion...")
                return app.main()
            else:
                print("Funcion main no encontrada")
                return 1
                
        except Exception as e:
            print(f"ERROR al ejecutar: {e}")
            print("\nDetalles del error:")
            import traceback
            traceback.print_exc()
            return 1
            
    except Exception as e:
        print(f"ERROR en configuracion: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    print("Launcher iniciado...")
    exit_code = main()
    print(f"Aplicacion terminada con codigo: {exit_code}")
    input("Presiona Enter para cerrar...")
    sys.exit(exit_code)