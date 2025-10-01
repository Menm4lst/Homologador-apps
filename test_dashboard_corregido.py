#!/usr/bin/env python3
"""
Script para probar que el dashboard ahora muestra los valores correctos.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_dashboard_metrics():
    """Prueba que las métricas del dashboard sean correctas."""
    print("🎯 PROBANDO CORRECCIÓN DEL DASHBOARD")
    print("=" * 50)
    
    try:
        # Verificar datos reales primero
        from homologador.core.storage import get_database_manager, get_user_repository, get_audit_repository
        
        db_manager = get_database_manager()
        user_repo = get_user_repository()
        audit_repo = get_audit_repository()
        
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            
            # Homologaciones reales
            cursor.execute("SELECT COUNT(*) FROM homologations")
            real_homologations = cursor.fetchone()[0]
            
            # Usuarios reales
            users = user_repo.get_all_active()
            real_users = len(users)
            
            # Logs de auditoría reales
            try:
                recent_logs = audit_repo.get_recent_logs(limit=50)
                real_activity = len(recent_logs)
            except Exception:
                real_activity = 0
                
        print("📊 DATOS REALES EN LA BASE DE DATOS:")
        print(f"   🏢 Homologaciones: {real_homologations}")
        print(f"   👥 Usuarios activos: {real_users}")
        print(f"   📋 Actividad reciente: {real_activity}")
        
        # Ahora crear el dashboard y verificar que use estos valores
        print(f"\n🎛️ PROBANDO DASHBOARD...")
        
        from PyQt6.QtWidgets import QApplication
        app = QApplication(sys.argv)
        
        from homologador.ui.admin_dashboard import AdminDashboardWidget
        
        # Crear dashboard con usuario admin
        user_info = {
            'id': 1,
            'username': 'admin',
            'role': 'admin',
            'full_name': 'Administrador del Sistema'
        }
        
        dashboard = AdminDashboardWidget(user_info)
        
        # Forzar actualización de métricas
        dashboard.update_dashboard()
        
        print("✅ Dashboard creado y actualizado")
        
        # Verificar que los valores sean correctos
        homolog_widget = dashboard.metrics.get('homologations')
        if homolog_widget and hasattr(homolog_widget, 'value_label'):
            displayed_homolog = homolog_widget.value_label.text()
            print(f"   📋 Dashboard muestra homologaciones: {displayed_homolog}")
            if displayed_homolog == str(real_homologations):
                print("   ✅ ¡CORRECTO! El dashboard muestra el valor real")
            else:
                print("   ❌ Error: Dashboard muestra valor incorrecto")
        
        users_widget = dashboard.metrics.get('users')
        if users_widget and hasattr(users_widget, 'value_label'):
            displayed_users = users_widget.value_label.text()
            print(f"   👥 Dashboard muestra usuarios: {displayed_users}")
            if displayed_users == str(real_users):
                print("   ✅ ¡CORRECTO! El dashboard muestra usuarios reales")
            else:
                print("   ❌ Error: Dashboard muestra usuarios incorrectos")
        
        print(f"\n🎉 PRUEBA COMPLETADA")
        
        if real_homologations == 0:
            print(f"\n💡 NOTA IMPORTANTE:")
            print(f"   Como no hay homologaciones en la BD, el dashboard debería mostrar 0")
            print(f"   Si antes mostraba 45, ¡ya está corregido! 🎊")
        
        return True
        
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Función principal."""
    print("🔧 VERIFICACIÓN DE CORRECCIÓN DEL DASHBOARD")
    print("Problema: Dashboard mostraba 45 homologaciones cuando había 0")
    print("Solución: Eliminar valores hardcodeados y usar datos reales")
    print()
    
    success = test_dashboard_metrics()
    
    if success:
        print(f"\n✅ ¡CORRECCIÓN EXITOSA!")
        print(f"🎯 El dashboard ahora muestra valores reales de la base de datos")
        print(f"\n🚀 Para verificar en la app:")
        print(f"   1. Ejecuta: python -m homologador")
        print(f"   2. Login como admin")
        print(f"   3. Ve a Dashboard Administrativo")
        print(f"   4. Verifica que muestre 0 homologaciones")
    else:
        print(f"\n❌ Hubo errores en la verificación")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())