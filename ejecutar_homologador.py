#!/usr/bin/env python3
"""
Script para ejecutar la aplicación Homologador con todas las nuevas funcionalidades.
Este script evita problemas de importaciones relativas.
"""

import sys
import os

# Agregar el directorio principal al path
project_root = os.path.dirname(os.path.abspath(__file__))
homologador_path = os.path.join(project_root, 'homologador')
sys.path.insert(0, project_root)
sys.path.insert(0, homologador_path)

# Cambiar al directorio homologador para imports relativos
os.chdir(homologador_path)

def main():
    """Función principal para ejecutar la aplicación."""
    try:
        # Importar PyQt6
        from PyQt6.QtWidgets import QApplication, QMessageBox
        from PyQt6.QtCore import Qt
        
        print("🚀 Iniciando Homologador de Aplicaciones...")
        print("📋 Con nuevas funcionalidades implementadas:")
        print("   ✓ Panel de métricas y estadísticas")
        print("   ✓ Filtros avanzados")
        print("   ✓ Sistema de exportación")
        print("   ✓ Tooltips contextuales")
        print("   ✓ Tour guiado")
        print()
        
        # Crear aplicación
        app = QApplication(sys.argv)
        app.setApplicationName("Homologador")
        app.setApplicationVersion("1.0.0")
        
        # Configurar estilo básico
        app.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QMenuBar {
                background-color: #e0e0e0;
                border: 1px solid #c0c0c0;
            }
            QMenuBar::item {
                padding: 4px 8px;
            }
            QMenuBar::item:selected {
                background-color: #d0d0d0;
            }
            QPushButton {
                background-color: #007acc;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
            QPushButton:pressed {
                background-color: #004578;
            }
            QToolTip {
                background-color: #2b2b2b;
                color: white;
                border: 1px solid #555;
                padding: 4px;
                border-radius: 3px;
            }
        """)
        
        # Importar y crear la ventana principal
        try:
            from homologador.ui.main_window import MainWindow
            print("✓ MainWindow importada correctamente")
            
            # Crear la ventana principal
            window = MainWindow()
            print("✓ Ventana principal creada")
            
            # Verificar que las nuevas funcionalidades estén disponibles
            new_features = []
            if hasattr(window, 'show_metrics_panel'):
                new_features.append("Panel de métricas")
            if hasattr(window, 'show_export_dialog'):
                new_features.append("Sistema de exportación")
            if hasattr(window, 'show_user_tour'):
                new_features.append("Tour guiado")
            
            if new_features:
                print(f"✓ Nuevas funcionalidades disponibles: {', '.join(new_features)}")
            
            # Mostrar la ventana
            window.show()
            print("✓ Aplicación iniciada exitosamente!")
            print()
            print("🎉 ¡Disfruta probando las nuevas funcionalidades!")
            print("💡 Tip: Busca el menú 'Métricas' y 'Ayuda' para acceder a las nuevas features")
            
            # Ejecutar la aplicación
            return app.exec()
            
        except ImportError as e:
            print(f"❌ Error importando MainWindow: {e}")
            print("🔧 Intentando importación alternativa...")
            
            # Importación alternativa
            sys.path.insert(0, os.path.join(project_root, 'homologador'))
            
            try:
                from ui.main_window import MainWindow
                from core.settings import setup_logging
                from core.storage import get_database_manager
                
                # Configurar logging
                setup_logging()
                
                # Inicializar base de datos
                db_manager = get_database_manager()
                
                print("✓ Módulos importados con método alternativo")
                
                # Crear la ventana principal
                window = MainWindow()
                window.show()
                
                print("✓ Aplicación iniciada exitosamente!")
                return app.exec()
                
            except Exception as e2:
                print(f"❌ Error en importación alternativa: {e2}")
                
                # Mostrar mensaje de error
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Icon.Critical)
                msg.setWindowTitle("Error de Importación")
                msg.setText("No se pudo iniciar la aplicación")
                msg.setDetailedText(f"Error original: {e}\nError alternativo: {e2}")
                msg.exec()
                
                return 1
    
    except ImportError:
        print("❌ Error: PyQt6 no está instalado.")
        print("📦 Instale las dependencias con:")
        print("   pip install PyQt6")
        return 1
    
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())