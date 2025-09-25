#!/usr/bin/env python
"""
Script de prueba para el dashboard optimizado
Verifica que todas las métricas se calculen correctamente
"""

import sys
import os
sys.path.insert(0, os.getcwd())

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel
from PyQt6.QtCore import Qt

def test_optimized_dashboard():
    """Prueba el dashboard optimizado."""
    
    print("🧪 PRUEBA DEL DASHBOARD OPTIMIZADO")
    print("=" * 50)
    
    app = QApplication(sys.argv)
    
    # Crear ventana de prueba
    class TestWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("🧪 Prueba Dashboard Optimizado")
            self.setGeometry(100, 100, 1200, 800)
            
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            layout = QVBoxLayout(central_widget)
            
            # Título
            title = QLabel("Prueba del Dashboard de Métricas Optimizado")
            title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 20px;")
            title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(title)
            
            # Botón para abrir dashboard
            btn_open_dashboard = QPushButton("📊 Abrir Dashboard Optimizado")
            btn_open_dashboard.setStyleSheet("""
                QPushButton {
                    background-color: #0078d4;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 15px 30px;
                    font-size: 16px;
                    font-weight: bold;
                    margin: 20px;
                }
                QPushButton:hover {
                    background-color: #106ebe;
                }
            """)
            btn_open_dashboard.clicked.connect(self.open_dashboard)
            layout.addWidget(btn_open_dashboard)
            
            # Información
            info = QLabel("""
            ✅ Dashboard completamente optimizado con:
            
            🔹 Consultas SQL directas para mejor rendimiento
            🔹 Campos de base de datos correctos (repository_location, homologation_date, etc.)
            🔹 Métricas precisas basadas en datos reales
            🔹 Estadísticas de finalización mejoradas
            🔹 Top repositorios con nombres limpios
            🔹 Manejo robusto de errores
            🔹 Cache interno para evitar recálculos
            🔹 UI moderna con temas
            
            Haz clic en el botón para abrir el dashboard y ver las mejoras!
            """)
            info.setStyleSheet("margin: 20px; padding: 20px; background-color: #f0f8ff; border-radius: 8px; line-height: 1.6;")
            layout.addWidget(info)
            
            self.dashboard_window = None
        
        def open_dashboard(self):
            """Abre el dashboard optimizado."""
            try:
                from homologador.ui.metrics_panel import MetricsPanel
                
                if self.dashboard_window:
                    self.dashboard_window.close()
                
                # Crear ventana del dashboard
                self.dashboard_window = QWidget()
                self.dashboard_window.setWindowTitle("📊 Dashboard de Métricas Optimizado")
                self.dashboard_window.setGeometry(150, 150, 1200, 800)
                
                layout = QVBoxLayout(self.dashboard_window)
                layout.setContentsMargins(0, 0, 0, 0)
                
                # Crear panel de métricas optimizado
                metrics_panel = MetricsPanel()
                layout.addWidget(metrics_panel)
                
                self.dashboard_window.show()
                
                print("✅ Dashboard optimizado abierto exitosamente!")
                
            except Exception as e:
                print(f"❌ Error abriendo dashboard: {e}")
                import traceback
                traceback.print_exc()
    
    # Mostrar ventana de prueba
    window = TestWindow()
    window.show()
    
    print("🚀 Aplicación de prueba iniciada")
    print("📝 Instrucciones:")
    print("   1. Haz clic en 'Abrir Dashboard Optimizado'")
    print("   2. Verifica que las métricas se calculen correctamente")
    print("   3. Prueba diferentes períodos de tiempo")
    print("   4. Verifica que no hay errores de 'status' o 'repository_url'")
    print()
    
    return app.exec()

if __name__ == "__main__":
    sys.exit(test_optimized_dashboard())