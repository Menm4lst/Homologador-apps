#!/usr/bin/env python
"""
Script de prueba para las nuevas funcionalidades implementadas.
Permite probar cada módulo independientemente.
"""

import sys
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel
from PyQt6.QtCore import Qt

# Añadir el directorio principal al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class TestWindow(QMainWindow):
    """Ventana de prueba para las nuevas funcionalidades."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Prueba de Nuevas Funcionalidades")
        self.setGeometry(100, 100, 600, 400)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Título
        title = QLabel("🎉 Pruebas de Nuevas Funcionalidades")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 20px;")
        layout.addWidget(title)
        
        # Botones de prueba
        self.create_test_buttons(layout)
    
    def create_test_buttons(self, layout):
        """Crear botones para probar cada funcionalidad."""
        
        # Prueba de Panel de Métricas
        btn_metrics = QPushButton("🔍 Probar Panel de Métricas")
        btn_metrics.clicked.connect(self.test_metrics_panel)
        layout.addWidget(btn_metrics)
        
        # Prueba de Filtros Avanzados
        btn_filters = QPushButton("🔧 Probar Filtros Avanzados")
        btn_filters.clicked.connect(self.test_advanced_filters)
        layout.addWidget(btn_filters)
        
        # Prueba de Exportación
        btn_export = QPushButton("📤 Probar Sistema de Exportación")
        btn_export.clicked.connect(self.test_export_system)
        layout.addWidget(btn_export)
        
        # Prueba de Tooltips
        btn_tooltips = QPushButton("💬 Probar Sistema de Tooltips")
        btn_tooltips.clicked.connect(self.test_tooltips)
        layout.addWidget(btn_tooltips)
        
        # Prueba de Tour Guiado
        btn_tour = QPushButton("🎯 Probar Tour Guiado")
        btn_tour.clicked.connect(self.test_user_guide)
        layout.addWidget(btn_tour)
        
        # Estado
        self.status_label = QLabel("✅ Todas las funcionalidades están listas para probar")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: green; margin: 20px;")
        layout.addWidget(self.status_label)
    
    def test_metrics_panel(self):
        """Probar el panel de métricas."""
        try:
            from homologador.ui.metrics_panel import MetricsPanel
            
            # Crear datos de prueba
            test_data = {
                'total_homologations': 125,
                'completed': 87,
                'in_progress': 23,
                'pending': 15,
                'avg_completion_days': 5.3,
                'repositories': [
                    {'name': 'repo-test-1', 'count': 45},
                    {'name': 'repo-test-2', 'count': 32},
                    {'name': 'repo-test-3', 'count': 28}
                ]
            }
            
            # Crear el panel
            metrics_panel = MetricsPanel(self)
            metrics_panel.show()
            
            self.status_label.setText("✅ Panel de métricas creado exitosamente!")
            self.status_label.setStyleSheet("color: green; margin: 20px;")
            
        except Exception as e:
            self.status_label.setText(f"❌ Error en panel de métricas: {str(e)}")
            self.status_label.setStyleSheet("color: red; margin: 20px;")
    
    def test_advanced_filters(self):
        """Probar filtros avanzados."""
        try:
            from homologador.ui.advanced_filters import AdvancedFilterWidget
            
            # Crear el widget de filtros
            filter_widget = AdvancedFilterWidget(self)
            filter_widget.show()
            
            self.status_label.setText("✅ Filtros avanzados creados exitosamente!")
            self.status_label.setStyleSheet("color: green; margin: 20px;")
            
        except Exception as e:
            self.status_label.setText(f"❌ Error en filtros avanzados: {str(e)}")
            self.status_label.setStyleSheet("color: red; margin: 20px;")
    
    def test_export_system(self):
        """Probar sistema de exportación."""
        try:
            from homologador.ui.export_dialog import ExportDialog
            
            # Datos de prueba para exportar
            test_data = [
                {'id': 1, 'repository': 'test-repo', 'status': 'completed'},
                {'id': 2, 'repository': 'other-repo', 'status': 'in_progress'}
            ]
            
            # Crear el diálogo de exportación
            export_dialog = ExportDialog(test_data, self)
            export_dialog.show()
            
            self.status_label.setText("✅ Sistema de exportación creado exitosamente!")
            self.status_label.setStyleSheet("color: green; margin: 20px;")
            
        except Exception as e:
            self.status_label.setText(f"❌ Error en sistema de exportación: {str(e)}")
            self.status_label.setStyleSheet("color: red; margin: 20px;")
    
    def test_tooltips(self):
        """Probar sistema de tooltips."""
        try:
            from homologador.ui.tooltips import setup_widget_tooltips, TooltipManager
            
            # Aplicar tooltips a los botones
            buttons = self.findChildren(QPushButton)
            for i, button in enumerate(buttons):
                setup_widget_tooltips(button, f'test_button_{i}')
            
            self.status_label.setText("✅ Sistema de tooltips aplicado exitosamente!")
            self.status_label.setStyleSheet("color: green; margin: 20px;")
            
        except Exception as e:
            self.status_label.setText(f"❌ Error en sistema de tooltips: {str(e)}")
            self.status_label.setStyleSheet("color: red; margin: 20px;")
    
    def test_user_guide(self):
        """Probar tour guiado."""
        try:
            from homologador.ui.user_guide import TourGuide, TourStep
            
            # Crear pasos del tour
            steps = [
                TourStep(
                    "welcome",
                    "¡Bienvenido!",
                    "Esta es una prueba del sistema de tour guiado.",
                    self
                ),
                TourStep(
                    "buttons",
                    "Botones de Prueba",
                    "Estos botones te permiten probar cada funcionalidad.",
                    self.findChild(QPushButton)
                )
            ]
            
            # Crear y mostrar el tour
            tour = TourGuide(steps, self)
            tour.show()
            
            self.status_label.setText("✅ Tour guiado iniciado exitosamente!")
            self.status_label.setStyleSheet("color: green; margin: 20px;")
            
        except Exception as e:
            self.status_label.setText(f"❌ Error en tour guiado: {str(e)}")
            self.status_label.setStyleSheet("color: red; margin: 20px;")


def main():
    """Función principal para ejecutar las pruebas."""
    app = QApplication(sys.argv)
    
    # Aplicar estilo básico
    app.setStyleSheet("""
        QMainWindow {
            background-color: #f5f5f5;
        }
        QPushButton {
            background-color: #007acc;
            color: white;
            border: none;
            padding: 10px;
            margin: 5px;
            border-radius: 5px;
            font-size: 14px;
        }
        QPushButton:hover {
            background-color: #005a9e;
        }
        QPushButton:pressed {
            background-color: #004578;
        }
    """)
    
    # Crear y mostrar la ventana de prueba
    window = TestWindow()
    window.show()
    
    print("🚀 Aplicación de prueba iniciada!")
    print("📋 Usa los botones para probar cada funcionalidad")
    print("🔍 Revisa el estado en la parte inferior de la ventana")
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())