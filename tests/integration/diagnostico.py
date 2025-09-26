#!/usr/bin/env python3
"""
Script de diagnóstico para identificar problemas en la ejecución del Homologador.
"""

import sys
import os
import traceback
from pathlib import Path

def print_separator(title):
    """Imprimir separador con título."""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def diagnose_environment():
    """Diagnosticar el entorno de ejecución."""
    print_separator("DIAGNOSTICO DEL ENTORNO")
    
    # Información básica
    print(f"Python version: {sys.version}")
    print(f"Platform: {sys.platform}")
    print(f"Current working directory: {os.getcwd()}")
    
    # Verificar PyQt6
    try:
        import PyQt6
        from PyQt6 import QtCore
        print(f"PyQt6 version: {QtCore.PYQT_VERSION_STR}")
        print("PyQt6: OK")
    except ImportError as e:
        print(f"PyQt6: ERROR - {e}")
        return False
    
    return True

def check_project_structure():
    """Verificar la estructura del proyecto."""
    print_separator("ESTRUCTURA DEL PROYECTO")
    
    project_root = Path("c:/Users/Antware/OneDrive/Desktop/PROYECTOS DEV/APP HOMOLOGACIONES")
    homologador_path = project_root / "homologador"
    
    print(f"Project root: {project_root}")
    print(f"Project root exists: {project_root.exists()}")
    print(f"Homologador path: {homologador_path}")
    print(f"Homologador path exists: {homologador_path.exists()}")
    
    # Verificar archivos clave
    key_files = [
        homologador_path / "app.py",
        homologador_path / "ui" / "main_window.py",
        homologador_path / "ui" / "metrics_panel.py",
        homologador_path / "ui" / "advanced_filters.py",
        homologador_path / "ui" / "export_dialog.py",
        homologador_path / "ui" / "tooltips.py",
        homologador_path / "ui" / "user_guide.py"
    ]
    
    print("\nArchivos clave:")
    all_exist = True
    for file_path in key_files:
        exists = file_path.exists()
        size = file_path.stat().st_size if exists else 0
        print(f"  {file_path.name}: {'OK' if exists else 'MISSING'} ({size} bytes)")
        if not exists:
            all_exist = False
    
    return all_exist

def test_imports():
    """Probar las importaciones críticas."""
    print_separator("PRUEBA DE IMPORTACIONES")
    
    # Cambiar al directorio correcto
    homologador_path = Path("c:/Users/Antware/OneDrive/Desktop/PROYECTOS DEV/APP HOMOLOGACIONES/homologador")
    os.chdir(str(homologador_path))
    sys.path.insert(0, str(homologador_path))
    sys.path.insert(0, str(homologador_path.parent))
    
    imports_to_test = [
        ("PyQt6.QtWidgets", "QApplication"),
        ("PyQt6.QtCore", "Qt"),
        ("ui.main_window", "MainWindow"),
        ("ui.metrics_panel", "MetricsPanel"),
        ("ui.advanced_filters", "AdvancedFilterWidget"),
        ("ui.export_dialog", "ExportDialog"),
        ("ui.tooltips", "TooltipManager"),
        ("ui.user_guide", "UserGuideManager")
    ]
    
    success_count = 0
    for module_name, class_name in imports_to_test:
        try:
            module = __import__(module_name, fromlist=[class_name])
            getattr(module, class_name)
            print(f"  {module_name}.{class_name}: OK")
            success_count += 1
        except Exception as e:
            print(f"  {module_name}.{class_name}: ERROR - {e}")
    
    print(f"\nResultado: {success_count}/{len(imports_to_test)} importaciones exitosas")
    return success_count == len(imports_to_test)

def test_minimal_app():
    """Probar una aplicación mínima."""
    print_separator("PRUEBA DE APLICACION MINIMA")
    
    try:
        from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel
        from PyQt6.QtCore import Qt
        
        # Crear aplicación mínima
        app = QApplication(sys.argv)
        
        window = QMainWindow()
        window.setWindowTitle("Homologador - Test")
        window.setGeometry(100, 100, 400, 200)
        
        label = QLabel("Aplicacion de prueba funcionando!")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        window.setCentralWidget(label)
        
        print("Aplicacion minima creada exitosamente")
        print("NOTA: La ventana no se mostrara en este contexto, pero el codigo funciona")
        
        return True
        
    except Exception as e:
        print(f"ERROR en aplicacion minima: {e}")
        traceback.print_exc()
        return False

def create_simple_launcher():
    """Crear un launcher simple que funcione."""
    print_separator("CREANDO LAUNCHER SIMPLE")
    
    launcher_content = '''#!/usr/bin/env python3
"""
Launcher simple para el Homologador.
"""

import sys
import os
from pathlib import Path

def main():
    print("Iniciando Homologador...")
    
    # Configurar paths
    project_root = Path(__file__).parent
    homologador_path = project_root / "homologador"
    
    os.chdir(str(homologador_path))
    sys.path.insert(0, str(project_root))
    sys.path.insert(0, str(homologador_path))
    
    try:
        # Importar y ejecutar
        import app
        print("Modulo app importado")
        
        if hasattr(app, 'main'):
            print("Ejecutando aplicacion...")
            return app.main()
        else:
            print("Funcion main no encontrada")
            return 1
            
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
'''
    
    launcher_path = Path("c:/Users/Antware/OneDrive/Desktop/PROYECTOS DEV/APP HOMOLOGACIONES/start_homologador.py")
    
    try:
        with open(launcher_path, 'w', encoding='utf-8') as f:
            f.write(launcher_content)
        print(f"Launcher creado en: {launcher_path}")
        return True
    except Exception as e:
        print(f"ERROR creando launcher: {e}")
        return False

def main():
    """Función principal de diagnóstico."""
    print("DIAGNOSTICO DEL HOMOLOGADOR")
    print("Fecha:", "2025-09-22")
    
    # Ejecutar diagnósticos
    env_ok = diagnose_environment()
    structure_ok = check_project_structure()
    imports_ok = test_imports()
    app_ok = test_minimal_app()
    launcher_ok = create_simple_launcher()
    
    # Resumen
    print_separator("RESUMEN DEL DIAGNOSTICO")
    print(f"Entorno PyQt6: {'OK' if env_ok else 'ERROR'}")
    print(f"Estructura del proyecto: {'OK' if structure_ok else 'ERROR'}")
    print(f"Importaciones: {'OK' if imports_ok else 'ERROR'}")
    print(f"Aplicacion minima: {'OK' if app_ok else 'ERROR'}")
    print(f"Launcher creado: {'OK' if launcher_ok else 'ERROR'}")
    
    if all([env_ok, structure_ok, imports_ok, app_ok]):
        print("\nCONCLUSION: El proyecto deberia funcionar correctamente")
        print("COMANDO RECOMENDADO:")
        print("cd 'c:/Users/Antware/OneDrive/Desktop/PROYECTOS DEV/APP HOMOLOGACIONES'")
        print("python start_homologador.py")
    else:
        print("\nCONCLUSION: Hay problemas que necesitan solucionarse")
    
    print_separator("FIN DEL DIAGNOSTICO")

if __name__ == "__main__":
    main()