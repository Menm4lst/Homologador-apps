#!/usr/bin/env python
"""
Prueba completa de la funcionalidad de previsualización web integrada
Este script simula el uso de la función desde el menú contextual
"""

import sys
import os

# Agregar el directorio padre al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, 
    QMessageBox, QLabel, QHBoxLayout
)
from PyQt6.QtCore import Qt

from homologador.core.storage import get_homologation_repository
from homologador.ui.web_preview import show_web_preview

class TestWebPreviewWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🌐 Prueba de Previsualización Web - Homologador")
        self.setGeometry(100, 100, 500, 300)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Título
        title = QLabel("Prueba de Funcionalidad de Previsualización Web")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)
        
        # Cargar homologaciones con URLs
        self.load_homologations()
        
        # Crear botones para cada homologación con URL
        if hasattr(self, 'homologations_with_urls') and self.homologations_with_urls:
            info_label = QLabel(f"Homologaciones encontradas con URLs: {len(self.homologations_with_urls)}")
            info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(info_label)
            
            for homol in self.homologations_with_urls:
                self.create_test_button(layout, homol)
        else:
            error_label = QLabel("❌ No se encontraron homologaciones con URLs válidas")
            error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            error_label.setStyleSheet("color: red; font-weight: bold;")
            layout.addWidget(error_label)
        
        # Botón de prueba con URL manual
        layout.addWidget(QLabel(""))  # Espaciador
        manual_label = QLabel("Prueba manual con URL conocida:")
        manual_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(manual_label)
        
        manual_btn = QPushButton("🌐 Probar con Google.com")
        manual_btn.clicked.connect(self.test_manual_url)
        layout.addWidget(manual_btn)
    
    def load_homologations(self):
        """Carga las homologaciones que tienen URLs"""
        try:
            repo = get_homologation_repository()
            homologations = repo.get_all()
            
            self.homologations_with_urls = []
            for h in homologations:
                h_dict = dict(h)
                if h_dict.get('kb_url', '').strip():
                    self.homologations_with_urls.append(h_dict)
                    
        except Exception as e:
            print(f"Error cargando homologaciones: {e}")
            self.homologations_with_urls = []
    
    def create_test_button(self, layout, homol_dict):
        """Crea un botón de prueba para una homologación"""
        container = QWidget()
        h_layout = QHBoxLayout(container)
        
        # Información de la homologación
        info = QLabel(f"{homol_dict.get('app_name', 'Sin nombre')}")
        info.setMinimumWidth(200)
        h_layout.addWidget(info)
        
        # URL
        url_label = QLabel(f"{homol_dict.get('kb_url', 'Sin URL')}")
        url_label.setStyleSheet("color: blue; font-family: monospace;")
        h_layout.addWidget(url_label)
        
        # Botón de previsualización
        preview_btn = QPushButton("🌐 Previsualizar")
        preview_btn.clicked.connect(lambda: self.preview_homologation(homol_dict))
        h_layout.addWidget(preview_btn)
        
        layout.addWidget(container)
    
    def preview_homologation(self, homol_dict):
        """Previsualiza la URL de una homologación (simula el comportamiento real)"""
        kb_url = homol_dict.get('kb_url', '').strip()
        
        if not kb_url:
            QMessageBox.warning(
                self,
                "Sin URL",
                "Esta homologación no tiene una URL de KB asociada."
            )
            return
        
        try:
            print(f"Abriendo previsualización para: {homol_dict.get('app_name', 'Sin nombre')}")
            print(f"URL: {kb_url}")
            show_web_preview(kb_url, parent=self)
            
        except Exception as e:
            print(f"Error: {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"No se pudo abrir la previsualización web:\n{str(e)}"
            )
    
    def test_manual_url(self):
        """Prueba con una URL conocida que funciona"""
        test_url = "https://www.google.com"
        
        try:
            print(f"Probando previsualización manual con: {test_url}")
            show_web_preview(test_url, parent=self)
            
        except Exception as e:
            print(f"Error en prueba manual: {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"No se pudo abrir la previsualización web:\n{str(e)}"
            )

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    print("🚀 Iniciando prueba de previsualización web...")
    print("📝 Funcionalidad disponible:")
    
    try:
        from PyQt6.QtWebEngineWidgets import QWebEngineView
        print("   ✅ PyQt6-WebEngine disponible - Vista integrada")
    except ImportError:
        print("   📱 PyQt6-WebEngine no disponible - Navegador externo")
    
    print()
    
    window = TestWebPreviewWindow()
    window.show()
    
    print("💡 Instrucciones:")
    print("   - Haz clic en cualquier botón '🌐 Previsualizar'")
    print("   - Se abrirá la ventana de previsualización web")
    print("   - Si PyQt6-WebEngine no está disponible, se abrirá el navegador por defecto")
    print()
    
    sys.exit(app.exec())