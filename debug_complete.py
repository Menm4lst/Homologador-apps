#!/usr/bin/env python3
"""
Script de diagnóstico avanzado para la aplicación Homologador.
"""

import sys
import os
import traceback

# Agregar paths
project_root = os.path.dirname(os.path.abspath(__file__))
homologador_path = os.path.join(project_root, 'homologador')
sys.path.insert(0, project_root)
sys.path.insert(0, homologador_path)

def debug_application():
    """Ejecuta diagnóstico completo de la aplicación."""
    try:
        print("🔍 DIAGNÓSTICO COMPLETO DE LA APLICACIÓN")
        print("=" * 50)
        
        # Paso 1: Verificar PyQt6
        print("📦 Verificando PyQt6...")
        try:
            from PyQt6.QtWidgets import QApplication
            print("✅ PyQt6 importado correctamente")
        except ImportError as e:
            print(f"❌ Error importando PyQt6: {e}")
            return False
        
        # Paso 2: Crear aplicación Qt
        print("🖥️ Creando aplicación Qt...")
        app = QApplication(sys.argv)
        print("✅ QApplication creada")
        
        # Paso 3: Importar tema
        print("🎨 Importando sistema de temas...")
        try:
            from homologador.ui.theme import apply_dark_theme
            apply_dark_theme(app)
            print("✅ Tema negro-azul aplicado")
        except Exception as e:
            print(f"⚠️ Error aplicando tema: {e}")
        
        # Paso 4: Importar ventana de login
        print("🔐 Importando ventana de login...")
        try:
            from homologador.ui.final_login import FinalLoginWindow
            print("✅ Ventana de login importada")
        except Exception as e:
            print(f"❌ Error importando login: {e}")
            traceback.print_exc()
            return False
        
        # Paso 5: Crear ventana de login
        print("🏗️ Creando ventana de login...")
        try:
            login_window = FinalLoginWindow()
            print("✅ Ventana de login creada")
        except Exception as e:
            print(f"❌ Error creando ventana: {e}")
            traceback.print_exc()
            return False
        
        # Paso 6: Mostrar ventana
        print("👁️ Mostrando ventana de login...")
        try:
            login_window.show()
            login_window.raise_()
            login_window.activateWindow()
            print("✅ Ventana mostrada")
            
            # Conectar señal de cierre para debug
            def on_login_success(user_info):
                print(f"✅ Login exitoso: {user_info}")
                print("🚀 Procediendo a ventana principal...")
            
            def on_login_close():
                print("🔒 Ventana de login cerrada")
                app.quit()
            
            login_window.login_successful.connect(on_login_success)
            login_window.finished.connect(on_login_close)
            
        except Exception as e:
            print(f"❌ Error mostrando ventana: {e}")
            traceback.print_exc()
            return False
        
        # Paso 7: Ejecutar loop de eventos
        print("🔄 Iniciando loop de eventos Qt...")
        print("💡 Credenciales: admin / admin123")
        print("🎯 La ventana debería estar visible ahora")
        print("-" * 50)
        
        try:
            result = app.exec()
            print(f"🏁 Aplicación cerrada con código: {result}")
            return result == 0
        except Exception as e:
            print(f"❌ Error en loop de eventos: {e}")
            traceback.print_exc()
            return False
            
    except Exception as e:
        print(f"❌ Error general: {e}")
        traceback.print_exc()
        return False

def main():
    """Función principal."""
    success = debug_application()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Diagnóstico completado exitosamente")
    else:
        print("❌ Se encontraron problemas durante el diagnóstico")
    
    print("📝 Si la ventana no aparece, verifica:")
    print("   - Que no esté minimizada")
    print("   - Que no esté detrás de otras ventanas")
    print("   - El administrador de ventanas del sistema")

if __name__ == "__main__":
    main()