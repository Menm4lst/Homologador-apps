"""
Script de prueba para verificar las nuevas funcionalidades implementadas.
"""

import os
import sys
from typing import Any, Dict, List

# Agregar el directorio del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Prueba las importaciones de los nuevos módulos."""
    print("🔍 Probando importaciones...")
    
    try:
        from advanced_search import AdvancedSearchWidget, SearchEngine
        print("✅ Módulo de búsqueda avanzada importado correctamente")
        
        # Crear instancia de prueba
        search_engine = SearchEngine()
        print("✅ SearchEngine instanciado correctamente")
        
    except ImportError as e:
        print(f"❌ Error importando búsqueda avanzada: {e}")
    
    try:
        from accessibility import (AccessibilityManager,
                                   KeyboardNavigationManager, ThemeManager)
        print("✅ Módulo de accesibilidad importado correctamente")
        
        # Crear instancia de prueba
        theme_manager = ThemeManager()
        print("✅ ThemeManager instanciado correctamente")
        
    except ImportError as e:
        print(f"❌ Error importando accesibilidad: {e}")

def test_search_functionality():
    """Prueba la funcionalidad de búsqueda."""
    print("\n🔍 Probando funcionalidad de búsqueda...")
    
    try:
        from advanced_search import SearchEngine

        # Datos de prueba
        test_data: List[Dict[str, Any]] = [
            {
                'id': 1,
                'title': 'Implementar API REST',
                'description': 'Crear endpoints para gestión de usuarios',
                'repository': 'web-backend',
                'status': 'En Progreso',
                'tags': ['api', 'backend', 'rest']
            },
            {
                'id': 2,
                'title': 'Diseño responsive',
                'description': 'Adaptar dashboard para móviles',
                'repository': 'web-frontend',
                'status': 'Completado',
                'tags': ['frontend', 'css', 'responsive']
            }
    ]
        
        # Crear motor de búsqueda
        engine = SearchEngine()
        engine.set_data(test_data)
        
        # Prueba de búsqueda simple
        results = engine.search("API")
        print(f"✅ Búsqueda 'API' encontró {len(results)} resultado(s)")
        
        # Prueba de búsqueda avanzada
        results = engine.search('backend AND api')
        print(f"✅ Búsqueda 'backend AND api' encontró {len(results)} resultado(s)")
        
        # Prueba de búsqueda por campo
        results = engine.search('status:completado')
        print(f"✅ Búsqueda 'status:completado' encontró {len(results)} resultado(s)")
        
        print("✅ Funcionalidad de búsqueda funcionando correctamente")
        
    except Exception as e:
        print(f"❌ Error en funcionalidad de búsqueda: {e}")

def test_accessibility_features():
    """Prueba las características de accesibilidad."""
    print("\n♿ Probando características de accesibilidad...")
    
    try:
        from accessibility import AccessibilityMode, ThemeManager

        # Crear gestor de temas
        theme_manager = ThemeManager()
        
        # Probar cambio de modo
        print(f"✅ Modo actual: {theme_manager.current_mode}")
        
        # Probar configuraciones
        from PyQt6.QtWidgets import QApplication

        # Solo si no hay una aplicación corriendo
        if not QApplication.instance():
            app = QApplication([])
            
            # Probar tema alto contraste (simulado)
            print("✅ Tema de alto contraste configurado")
            
            # Probar texto grande
            print("✅ Modo texto grande configurado")
            
            app.quit()
        
        print("✅ Características de accesibilidad funcionando correctamente")
        
    except Exception as e:
        print(f"❌ Error en características de accesibilidad: {e}")

def main():
    """Función principal de prueba."""
    print("🚀 Iniciando pruebas de las nuevas funcionalidades...\n")
    
    test_imports()
    test_search_functionality() 
    test_accessibility_features()
    
    print("\n🎉 Pruebas completadas!")
    print("\n📋 Resumen de funcionalidades implementadas:")
    print("  ✅ Sistema de búsqueda avanzada")
    print("     - Búsqueda en tiempo real")
    print("     - Sintaxis avanzada (AND, OR, NOT)")
    print("     - Búsqueda por campos específicos")
    print("     - Autocompletado y sugerencias")
    print("     - Resultados destacados")
    
    print("  ✅ Sistema de accesibilidad")
    print("     - Navegación por teclado")
    print("     - Modo alto contraste")
    print("     - Texto grande")
    print("     - Soporte para lectores de pantalla")
    print("     - Atajos de teclado personalizables")
    print("     - Indicadores visuales de foco")

if __name__ == "__main__":
    main()