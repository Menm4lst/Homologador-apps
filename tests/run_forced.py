#!/usr/bin/env python3
"""
Ejecutor forzado de la aplicación Homologador - Versión que garantiza que se mantenga visible.
"""

import sys
import os

# Agregar paths
project_root = os.path.dirname(os.path.abspath(__file__))
homologador_path = os.path.join(project_root, 'homologador')
sys.path.insert(0, project_root)
sys.path.insert(0, homologador_path)

def force_run_homologador():
    """Ejecuta la aplicación forzando que se mantenga visible."""
    try:
        print("🚀 INICIANDO HOMOLOGADOR - MODO FORZADO")
        print("=" * 50)
        
        # Importar PyQt6
        from PyQt6.QtWidgets import QApplication, QMessageBox
        from PyQt6.QtCore import QTimer, Qt
        
        # Crear aplicación Qt
        app = QApplication(sys.argv)
        app.setQuitOnLastWindowClosed(True)
        
        print("✅ Aplicación Qt creada")
        
        # Aplicar tema
        from homologador.ui.theme import apply_dark_theme
        apply_dark_theme(app)
        
        print("🎨 Tema negro-azul aplicado")
        
        # Importar y crear ventana de login
        from homologador.ui.final_login import FinalLoginWindow
        
        login_window = FinalLoginWindow()
        
        print("🔐 Ventana de login creada")
        
        # Variable para mantener referencia a la ventana principal
        main_window = None
        
        def on_login_successful(user_info):
            """Maneja login exitoso y abre ventana principal."""
            nonlocal main_window
            try:
                print(f"✅ Login exitoso para: {user_info['username']}")
                
                # Cerrar ventana de login
                login_window.close()
                
                # Importar y crear ventana principal
                from homologador.ui.main_window import MainWindow
                
                main_window = MainWindow(user_info)
                
                # Aplicar efectos si están disponibles
                try:
                    from homologador.ui.theme_effects import WindowCustomizer
                    WindowCustomizer.setup_main_window_effects(main_window)
                except:
                    pass  # No es crítico si no está disponible
                
                # Mostrar ventana principal
                main_window.show()
                main_window.raise_()
                main_window.activateWindow()
                
                print("🏠 Ventana principal mostrada")
                print("🎨 Disfruta del nuevo tema negro-azul!")
                
            except Exception as e:
                print(f"❌ Error abriendo ventana principal: {e}")
                import traceback
                traceback.print_exc()
                
                # Mostrar error al usuario
                QMessageBox.critical(
                    None, 
                    "Error", 
                    f"No se pudo abrir la aplicación principal:\\n{e}"
                )
                app.quit()
        
        # Conectar señal de login exitoso
        login_window.login_successful.connect(on_login_successful)
        
        # Configurar ventana de login
        login_window.setWindowFlags(
            Qt.WindowType.Window | 
            Qt.WindowType.WindowTitleHint | 
            Qt.WindowType.WindowCloseButtonHint
        )
        
        # Mostrar ventana de login
        login_window.show()
        login_window.raise_()
        login_window.activateWindow()
        
        print("👁️ Ventana de login visible")
        print("🎯 Credenciales: admin / admin123")
        print("⏳ Esperando inicio de sesión...")
        print("-" * 50)
        
        # Timer para mantener la aplicación activa
        keep_alive_timer = QTimer()
        keep_alive_timer.timeout.connect(lambda: None)  # No hace nada, solo mantiene eventos
        keep_alive_timer.start(1000)  # Cada segundo
        
        # Ejecutar aplicación
        return app.exec()
        
    except Exception as e:
        print(f"❌ Error crítico: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    result = force_run_homologador()
    
    print(f"\n🏁 Aplicación terminada con código: {result}")
    
    if result == 0:
        print("✅ Ejecución completada correctamente")
    else:
        print("⚠️ La aplicación se cerró con errores")
    
    print("\n💡 Si no viste la ventana, puede estar:")
    print("   - Minimizada en la barra de tareas")
    print("   - Detrás de otras ventanas")
    print("   - Bloqueada por el sistema operativo")
    
    input("\\nPresiona Enter para salir...")