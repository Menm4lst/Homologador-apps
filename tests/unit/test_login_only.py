#!/usr/bin/env python3
"""
Script para detectar y solucionar el problema de la aplicación.
"""

import sys
import os

# Agregar el directorio principal al path
project_root = os.path.dirname(os.path.abspath(__file__))
homologador_path = os.path.join(project_root, 'homologador')
sys.path.insert(0, project_root)
sys.path.insert(0, homologador_path)

def test_login_window():
    """Prueba solo la ventana de login."""
    try:
        from PyQt6.QtWidgets import QApplication
        from homologador.ui.final_login import FinalLoginWindow
        from homologador.ui.theme import apply_dark_theme
        
        print("🧪 Creando aplicación de prueba...")
        app = QApplication(sys.argv)
        
        print("🎨 Aplicando tema negro-azul...")
        apply_dark_theme(app)
        
        print("🔐 Creando ventana de login...")
        login_window = FinalLoginWindow()
        
        print("👁️ Mostrando ventana de login...")
        login_window.show()
        login_window.raise_()
        login_window.activateWindow()
        
        print("✅ Ventana de login creada exitosamente!")
        print("💡 Usa: admin / admin123")
        
        # Ejecutar aplicación
        return app.exec()
        
    except Exception as e:
        print(f"❌ Error en ventana de login: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(test_login_window())