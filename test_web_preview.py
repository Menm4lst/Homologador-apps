#!/usr/bin/env python
"""
Script de prueba para la funcionalidad de previsualización web
"""

import sys
import os

# Agregar el directorio padre al path para poder importar los módulos
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QMessageBox
from homologador.ui.web_preview import show_web_preview

class TestMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Prueba de Previsualización Web")
        self.setGeometry(100, 100, 400, 200)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Botón de prueba
        test_btn = QPushButton("🌐 Probar Previsualización Web")
        test_btn.clicked.connect(self.test_web_preview)
        layout.addWidget(test_btn)
    
    def test_web_preview(self):
        """Prueba la funcionalidad de previsualización web"""
        test_url = "https://www.google.com"
        
        try:
            show_web_preview(test_url, parent=self)
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Error al abrir previsualización: {str(e)}"
            )

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestMainWindow()
    window.show()
    sys.exit(app.exec())