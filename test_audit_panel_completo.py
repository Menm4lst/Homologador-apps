"""
Test completo del panel de auditoría - EL OMO LOGADOR 🥵
"""

import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(), 'homologador'))

from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QTimer
from homologador.ui.audit_panel import show_audit_panel
from homologador.core.storage import get_audit_repository, get_user_repository, DatabaseManager
import logging

def test_audit_panel():
    """Prueba completa del panel de auditoría."""
    
    app = QApplication(sys.argv)
    
    try:
        # Configurar logging
        logging.basicConfig(level=logging.INFO)
        
        # Inicializar base de datos
        db_manager = DatabaseManager()
        audit_repo = get_audit_repository()
        user_repo = get_user_repository()
        
        # Crear usuario de prueba admin
        admin_user = {
            'id': 1,
            'username': 'admin_test',
            'role': 'admin',
            'full_name': 'Administrador de Prueba'
        }
        
        print("=== TEST DEL PANEL DE AUDITORIA ===")
        print("1. Verificando configuración...")
        
        # Verificar que se pueden crear registros de auditoría
        try:
            audit_repo.log_action(
                user_id=admin_user['id'],
                action="TEST",
                table_name="test_table",
                record_id=1
            )
            print("✅ Sistema de auditoría funcionando - registros guardados correctamente")
        except Exception as e:
            print(f"❌ Error en sistema de auditoría: {e}")
            return False
        
        # Verificar que se pueden obtener los logs
        try:
            logs = audit_repo.get_recent_logs(limit=10)
            print(f"✅ Recuperación de logs funcionando - {len(logs)} registros encontrados")
        except Exception as e:
            print(f"❌ Error obteniendo logs: {e}")
            return False
        
        print("\n2. Abriendo panel de auditoría...")
        
        # Mostrar el panel de auditoría
        dialog = show_audit_panel(admin_user)
        
        print("✅ Panel de auditoría abierto correctamente")
        print("\n=== INSTRUCCIONES ===")
        print("- El panel debería mostrar los logs de auditoría")
        print("- Puedes filtrar por fecha, usuario, acción, etc.")
        print("- Verifica que la tabla muestra los datos correctamente")
        print("- Cierra el diálogo cuando hayas terminado la verificación")
        
        # Cerrar automáticamente después de 10 segundos para pruebas automatizadas
        timer = QTimer()
        timer.singleShot(10000, dialog.close)  # 10 segundos
        
        result = dialog.exec()
        
        if result:
            print("\n✅ Test completado - Panel de auditoría funciona correctamente")
            return True
        else:
            print("\n❌ Test cancelado por el usuario")
            return False
            
    except Exception as e:
        print(f"\n❌ Error durante el test: {e}")
        import traceback
        traceback.print_exc()
        
        QMessageBox.critical(
            None,
            "Error en Test",
            f"Error durante la prueba del panel de auditoría:\n{str(e)}"
        )
        return False
    
    finally:
        app.quit()

if __name__ == "__main__":
    print("EL OMO LOGADOR 🥵 - Test del Panel de Auditoría")
    print("=" * 50)
    
    success = test_audit_panel()
    
    if success:
        print("\n🎉 ¡TEST EXITOSO! El panel de auditoría está completamente configurado.")
    else:
        print("\n💥 Test falló. Revisa los errores arriba.")
    
    sys.exit(0 if success else 1)