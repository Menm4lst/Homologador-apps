#!/usr/bin/env python3
"""
Script de prueba rápida para validar la funcionalidad de cambio de contraseñas.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel
from PyQt6.QtCore import Qt

from ui.change_password_dialog import ChangeMyPasswordDialog
from ui.theme import apply_dark_theme


class TestPasswordWindow(QMainWindow):
    """Ventana de prueba para el cambio de contraseñas."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🔑 Prueba de Cambio de Contraseñas")
        self.resize(400, 300)
        
        # Datos de usuario simulado
        self.user_info = {
            'user_id': 1,
            'username': 'admin',
            'role': 'admin'
        }
        
        self.setup_ui()
    
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Etiqueta de información
        info_label = QLabel("🧪 Prueba de Funcionalidad de Cambio de Contraseñas")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info_label)
        
        user_label = QLabel(f"Usuario de prueba: {self.user_info['username']}")
        user_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(user_label)
        
        # Botón para abrir diálogo
        test_button = QPushButton("🔑 Probar Cambio de Contraseña")
        test_button.clicked.connect(self.test_change_password)
        layout.addWidget(test_button)
        
        # Información adicional
        info_text = QLabel("""
        ℹ️ Esta prueba abrirá el diálogo de cambio de contraseñas.
        
        💡 Tips:
        • La contraseña actual es: admin123
        • Puedes usar el botón "Generar" para crear una nueva
        • El sistema validará la fortaleza de la contraseña
        • Los cambios se aplicarán inmediatamente
        """)
        info_text.setWordWrap(True)
        layout.addWidget(info_text)
    
    def test_change_password(self):
        """Abre el diálogo de cambio de contraseñas para prueba."""
        try:
            dialog = ChangeMyPasswordDialog(self.user_info, self)
            dialog.password_changed.connect(self.on_password_changed)
            dialog.exec()
        except Exception as e:
            print(f"Error al abrir diálogo: {e}")
            import traceback
            traceback.print_exc()
    
    def on_password_changed(self):
        """Maneja el evento de cambio de contraseña."""
        print("✅ Contraseña cambiada exitosamente en la prueba!")


def main():
    """Función principal para ejecutar la prueba."""
    app = QApplication(sys.argv)
    
    # Aplicar tema
    apply_dark_theme(app)
    
    # Crear ventana de prueba
    window = TestPasswordWindow()
    window.show()
    
    print("🔑 Iniciando prueba de cambio de contraseñas...")
    print("📝 Usa las credenciales: admin / admin123")
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()