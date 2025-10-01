#!/usr/bin/env python3
"""
Test básico para validar que la aplicación se importa correctamente
"""


# Agregar el directorio padre al path

from pathlib import Path
import sys

import pytest
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_imports():
    """Test que las importaciones básicas funcionen"""
    try:
        # Test de importaciones críticas
        
        # Verificar que los singletons funcionen

        from homologador.core.settings import get_settings
        from homologador.core.storage import get_database_manager  
        from homologador.data.seed import get_auth_service
        settings = get_settings()
        assert settings is not None
        
        db_manager = get_database_manager()
        assert db_manager is not None
        
        auth_service = get_auth_service()
        assert auth_service is not None
        
        print("✅ Todas las importaciones críticas exitosas")
        
    except ImportError as e:
        pytest.fail(f"Error de importación: {e}")
    except Exception as e:
        pytest.fail(f"Error inesperado: {e}")

def test_pyqt6_available():
    """Test que PyQt6 esté disponible"""
    try:
        
        # Crear aplicación temporal (sin mostrar)

        import sys

        from PyQt6.QtCore import Qt
        from PyQt6.QtWidgets import QApplication
        if not QApplication.instance():
            app = QApplication([])
            app.setQuitOnLastWindowClosed(False)
        
        print("✅ PyQt6 disponible y funcional")
        
    except ImportError as e:
        pytest.fail(f"PyQt6 no disponible: {e}")

if __name__ == "__main__":
    test_imports()
    test_pyqt6_available()
    print("🎉 Todos los tests básicos pasaron")