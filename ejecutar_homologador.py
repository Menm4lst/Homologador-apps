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
        # Configurar manejo global de errores
        from homologador.core.error_handler import get_error_handler, ErrorSeverity
        error_handler = get_error_handler()
        
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
        print("   ✓ Sistema de manejo de errores")
        print("   ✓ Validación de formularios mejorada")
        print()
        
        # Importar y crear la aplicación completa con sistema de login
        try:
            from homologador.app import HomologadorApplication
            print("✓ HomologadorApplication importada correctamente")
            
            # Crear la aplicación con sistema de autenticación
            homologador_app = HomologadorApplication()
            print("✓ Aplicación creada con sistema de login")
            print("✓ Sistema de manejo de errores configurado")
            
            # Ejecutar la aplicación (esto mostrará el login primero)
            result = homologador_app.run()
            print("✓ Aplicación iniciada exitosamente!")
            print()
            print("🎉 ¡Disfruta probando las nuevas funcionalidades!")
            print("💡 Tip: Ingresa con admin/admin123 para probar las notificaciones")
            
            return result
            
        except ImportError as e:
            print(f"❌ Error importando MainWindow: {e}")
            print("🔧 Intentando importación alternativa...")
            
            # Importación alternativa
            sys.path.insert(0, os.path.join(project_root, 'homologador'))
            
            try:
                from app import HomologadorApplication
                
                print("✓ HomologadorApplication importada con método alternativo")
                
                # Crear la aplicación con sistema de autenticación
                homologador_app = HomologadorApplication()
                result = homologador_app.run()
                
                print("✓ Aplicación iniciada exitosamente!")
                return result
                
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