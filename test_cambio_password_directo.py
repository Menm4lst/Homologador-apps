#!/usr/bin/env python3
"""
Prueba específica del sistema de cambio de contraseñas.
Este script abre directamente el diálogo de cambio sin necesidad de la app completa.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt

from homologador.ui.change_password_dialog import ChangeMyPasswordDialog
from homologador.ui.theme import apply_dark_theme
from homologador.data.seed import create_seed_data


def test_password_change():
    """Prueba directa del cambio de contraseñas."""
    
    print("🔑 Iniciando prueba del sistema de cambio de contraseñas...")
    
    # Crear aplicación Qt
    app = QApplication(sys.argv)
    
    # Aplicar tema
    apply_dark_theme(app)
    
    # Asegurar que existen los datos
    create_seed_data()
    
    # Datos de usuario de prueba
    user_info = {
        'user_id': 1,
        'username': 'admin', 
        'role': 'admin'
    }
    
    print(f"👤 Usuario de prueba: {user_info['username']}")
    print("🔐 Contraseña actual para prueba: admin123")
    print("✨ Abriendo diálogo de cambio de contraseñas...")
    
    try:
        # Crear y mostrar diálogo
        dialog = ChangeMyPasswordDialog(user_info)
        
        # Conectar señal de éxito
        def on_success():
            QMessageBox.information(
                None,
                "✅ Prueba Exitosa",
                "¡El cambio de contraseña funcionó correctamente!"
            )
        
        dialog.password_changed.connect(on_success)
        
        # Mostrar diálogo
        result = dialog.exec()
        
        if result:
            print("✅ Diálogo cerrado correctamente")
        else:
            print("ℹ️ Usuario canceló el diálogo")
    
    except Exception as e:
        print(f"❌ Error en la prueba: {e}")
        import traceback
        traceback.print_exc()
        
        QMessageBox.critical(
            None,
            "❌ Error de Prueba",
            f"Error durante la prueba:\n{str(e)}"
        )


if __name__ == "__main__":
    test_password_change()