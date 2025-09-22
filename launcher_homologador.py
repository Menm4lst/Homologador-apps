#!/usr/bin/env python3
"""
Launcher mejorado para el Homologador con feedback visual.
"""

import sys
import os
import time
from pathlib import Path

def print_header():
    """Mostrar cabecera del launcher."""
    print("*" * 60)
    print("*" + " " * 58 + "*")
    print("*" + " HOMOLOGADOR DE APLICACIONES - LAUNCHER ".center(58) + "*")
    print("*" + " CON NUEVAS FUNCIONALIDADES ".center(58) + "*")
    print("*" + " " * 58 + "*")
    print("*" * 60)
    print()

def print_progress(message, success=True):
    """Mostrar progreso con indicador visual."""
    status = "[OK]" if success else "[ERROR]"
    print(f"{status} {message}")
    time.sleep(0.1)  # Pequeña pausa para visualizar el progreso

def setup_environment():
    """Configurar el entorno de ejecución."""
    print_progress("Configurando entorno...")
    
    project_root = Path(__file__).parent.absolute()
    homologador_path = project_root / "homologador"
    
    # Verificar rutas
    if not project_root.exists():
        print_progress(f"Directorio del proyecto no encontrado: {project_root}", False)
        return None, None
    
    if not homologador_path.exists():
        print_progress(f"Directorio homologador no encontrado: {homologador_path}", False)
        return None, None
    
    print_progress(f"Directorio del proyecto: {project_root}")
    print_progress(f"Directorio homologador: {homologador_path}")
    
    # Configurar Python path
    sys.path.insert(0, str(project_root))
    sys.path.insert(0, str(homologador_path))
    
    # Cambiar al directorio homologador
    os.chdir(str(homologador_path))
    print_progress(f"Directorio actual: {os.getcwd()}")
    
    return project_root, homologador_path

def verify_dependencies():
    """Verificar dependencias."""
    print_progress("Verificando dependencias...")
    
    try:
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import Qt
        print_progress("PyQt6 disponible")
        return True
    except ImportError as e:
        print_progress(f"PyQt6 no disponible: {e}", False)
        return False

def verify_files():
    """Verificar archivos del proyecto."""
    print_progress("Verificando archivos del proyecto...")
    
    required_files = [
        "app.py",
        "ui/main_window.py",
        "ui/metrics_panel.py",
        "ui/advanced_filters.py",
        "ui/export_dialog.py",
        "ui/tooltips.py",
        "ui/user_guide.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print_progress(f"  {file_path} ({size:,} bytes)")
        else:
            print_progress(f"  {file_path} - FALTANTE", False)
            missing_files.append(file_path)
    
    if missing_files:
        print_progress(f"Archivos faltantes: {len(missing_files)}", False)
        return False
    
    print_progress("Todos los archivos requeridos están presentes")
    return True

def test_imports():
    """Probar importaciones críticas."""
    print_progress("Probando importaciones críticas...")
    
    try:
        import app
        print_progress("  app.py importado")
        
        if hasattr(app, 'main'):
            print_progress("  función main() encontrada")
        else:
            print_progress("  función main() no encontrada", False)
            return False
            
        if hasattr(app, 'HomologatorApp'):
            print_progress("  clase HomologatorApp encontrada")
        else:
            print_progress("  clase HomologatorApp no encontrada", False)
        
        return True
        
    except Exception as e:
        print_progress(f"Error en importaciones: {e}", False)
        return False

def run_application():
    """Ejecutar la aplicación."""
    print_progress("Iniciando aplicación...")
    print()
    print("=" * 60)
    print("APLICACION INICIANDOSE...")
    print("Si no aparece una ventana, verifique:")
    print("1. Que no esté minimizada en la barra de tareas")
    print("2. Que no haya errores en la consola")
    print("3. Que PyQt6 esté correctamente instalado")
    print("=" * 60)
    print()
    
    try:
        import app
        
        # Ejecutar la aplicación
        exit_code = app.main()
        
        print()
        print("=" * 60)
        print(f"APLICACION TERMINADA CON CODIGO: {exit_code}")
        print("=" * 60)
        
        return exit_code
        
    except KeyboardInterrupt:
        print()
        print("=" * 60)
        print("APLICACION INTERRUMPIDA POR EL USUARIO")
        print("=" * 60)
        return 0
        
    except Exception as e:
        print()
        print("=" * 60)
        print(f"ERROR EJECUTANDO APLICACION: {e}")
        print("=" * 60)
        import traceback
        traceback.print_exc()
        return 1

def main():
    """Función principal del launcher."""
    print_header()
    
    # Configuración del entorno
    project_root, homologador_path = setup_environment()
    if not project_root:
        print("\nERROR: No se pudo configurar el entorno")
        input("Presiona Enter para cerrar...")
        return 1
    
    print()
    
    # Verificaciones
    if not verify_dependencies():
        print("\nERROR: Dependencias no disponibles")
        input("Presiona Enter para cerrar...")
        return 1
    
    print()
    
    if not verify_files():
        print("\nERROR: Archivos del proyecto faltantes")
        input("Presiona Enter para cerrar...")
        return 1
    
    print()
    
    if not test_imports():
        print("\nERROR: Problemas con las importaciones")
        input("Presiona Enter para cerrar...")
        return 1
    
    print()
    print_progress("TODAS LAS VERIFICACIONES PASARON EXITOSAMENTE")
    print()
    
    # Mostrar funcionalidades disponibles
    print("FUNCIONALIDADES DISPONIBLES EN LA APLICACION:")
    print("  • Panel de métricas y estadísticas")
    print("  • Filtros avanzados")
    print("  • Sistema de exportación")
    print("  • Tooltips contextuales")
    print("  • Tour guiado interactivo")
    print()
    
    # Ejecutar aplicación
    exit_code = run_application()
    
    print()
    input("Presiona Enter para cerrar...")
    return exit_code

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        print(f"\nERROR CRITICO: {e}")
        import traceback
        traceback.print_exc()
        input("Presiona Enter para cerrar...")
        sys.exit(1)