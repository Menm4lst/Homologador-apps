#!/usr/bin/env python3
"""
Script de prueba simple para verificar el nuevo tema negro-azul.
"""


# Agregar paths

import os
import sys
project_root = os.path.dirname(os.path.abspath(__file__))
homologador_path = os.path.join(project_root, 'homologador')
sys.path.insert(0, project_root)
sys.path.insert(0, homologador_path)

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QTableWidget, QTableWidgetItem,
    QComboBox, QTextEdit, QScrollArea
)


from PyQt6.QtCore import Qt
def main():
    """Función principal."""
    app = QApplication(sys.argv)
    
    # Importar y aplicar el nuevo tema
    from homologador.ui.theme import apply_dark_theme
    apply_dark_theme(app)
    
    # Crear ventana de prueba
    window = QMainWindow()
    window.setWindowTitle("🎨 Prueba del Nuevo Tema Negro-Azul")
    window.resize(800, 600)
    
    # Widget central
    central_widget = QWidget()
    window.setCentralWidget(central_widget)
    
    layout = QVBoxLayout(central_widget)
    layout.setSpacing(15)
    layout.setContentsMargins(20, 20, 20, 20)
    
    # Título
    title = QLabel("🚀 TEMA NEGRO-AZUL MODERNO IMPLEMENTADO")
    title.setAlignment(Qt.AlignmentFlag.AlignCenter)
    title.setStyleSheet("font-size: 18px; font-weight: bold; color: #58a6ff; margin: 10px;")
    layout.addWidget(title)
    
    # Botones de prueba
    button_layout = QHBoxLayout()
    
    btn1 = QPushButton("✅ Botón Primario")
    btn2 = QPushButton("🔧 Botón Secundario")
    btn3 = QPushButton("⚠️ Botón de Acción")
    
    button_layout.addWidget(btn1)
    button_layout.addWidget(btn2)
    button_layout.addWidget(btn3)
    layout.addLayout(button_layout)
    
    # Campos de entrada
    form_layout = QHBoxLayout()
    
    input1 = QLineEdit()
    input1.setPlaceholderText("Campo de texto con tema aplicado")
    
    combo1 = QComboBox()
    combo1.addItems(["Opción 1", "Opción 2", "Opción 3"])
    
    form_layout.addWidget(QLabel("Entrada:"))
    form_layout.addWidget(input1)
    form_layout.addWidget(QLabel("ComboBox:"))
    form_layout.addWidget(combo1)
    layout.addLayout(form_layout)
    
    # Tabla de prueba
    table = QTableWidget(5, 3)
    table.setHorizontalHeaderLabels(["ID", "Nombre", "Estado"])
    
    # Datos de prueba
    for row in range(5):
        table.setItem(row, 0, QTableWidgetItem(f"00{row+1}"))
        table.setItem(row, 1, QTableWidgetItem(f"Elemento {row+1}"))
        table.setItem(row, 2, QTableWidgetItem(f"Activo" if row % 2 == 0 else "Inactivo"))
    
    layout.addWidget(QLabel("📋 Tabla con nuevo estilo:"))
    layout.addWidget(table)
    
    # Área de texto
    text_area = QTextEdit()
    text_area.setPlainText("""
🎨 CARACTERÍSTICAS DEL NUEVO TEMA:

✓ Paleta de colores negro-azul profesional
✓ Gradientes modernos en botones y elementos
✓ Scrollbars estilizados con colores de acento
✓ Tablas con headers elegantes y selección mejorada
✓ ComboBox con efectos hover y transiciones
✓ Consistencia visual en toda la aplicación

🚀 El tema se aplica automáticamente a todos los componentes PyQt6.
""")
    text_area.setMaximumHeight(150)
    
    layout.addWidget(QLabel("📝 Información del tema:"))
    layout.addWidget(text_area)
    
    # Mostrar ventana
    window.show()
    
    # Ejecutar aplicación
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())