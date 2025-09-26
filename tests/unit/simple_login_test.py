#!/usr/bin/env python3
"""
Script simple para ejecutar la ventana de login de forma persistente.
"""

import sys
import os

# Agregar paths
project_root = os.path.dirname(os.path.abspath(__file__))
homologador_path = os.path.join(project_root, 'homologador')
sys.path.insert(0, project_root)
sys.path.insert(0, homologador_path)

def run_login_simple():
    """Ejecuta solo la ventana de login de forma simple."""
    try:
        print("🚀 Iniciando ventana de login...")
        
        # Importar PyQt6
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import Qt
        
        # Crear aplicación
        app = QApplication(sys.argv)
        app.setQuitOnLastWindowClosed(True)
        
        print("🎨 Aplicando tema negro-azul...")
        
        # Importar y aplicar tema
        from homologador.ui.theme import apply_dark_theme
        apply_dark_theme(app)
        
        print("🔐 Creando ventana de login...")
        
        # Importar ventana de login
        from homologador.ui.final_login import FinalLoginWindow
        
        # Crear ventana de login
        login_window = FinalLoginWindow()
        
        # Configurar ventana para que se mantenga visible
        login_window.setWindowFlags(
            Qt.WindowType.Window | 
            Qt.WindowType.WindowTitleHint | 
            Qt.WindowType.WindowCloseButtonHint |
            Qt.WindowType.WindowMinimizeButtonHint
        )
        
        # Mostrar ventana
        login_window.show()
        login_window.raise_()
        login_window.activateWindow()
        
        print("✅ Ventana de login mostrada")
        print("🎯 Credenciales: admin / admin123")
        print("⚠️ Si no ves la ventana, verifica el administrador de ventanas")
        
        # Ejecutar aplicación
        return app.exec()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    print("🔐 VENTANA DE LOGIN - TEMA NEGRO-AZUL")
    print("=" * 40)
    
    result = run_login_simple()
    
    print(f"\n🏁 Aplicación cerrada con código: {result}")
    
    if result == 0:
        print("✅ Ejecución exitosa")
    else:
        print("⚠️ Hubo algún problema")
        
    input("Presiona Enter para continuar...")