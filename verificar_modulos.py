#!/usr/bin/env python3
"""
Script de verificación para confirmar que el dashboard y gestión de usuarios están disponibles.
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

def verificar_disponibilidad_modulos():
    """Verifica que los módulos estén disponibles correctamente."""
    
    print("🔍 VERIFICANDO DISPONIBILIDAD DE MÓDULOS...")
    print("="*60)
    
    try:
        # Simular la importación como lo hace main_window
        from homologador.ui.main_window import (
            ADMIN_DASHBOARD_AVAILABLE,
            USER_MANAGEMENT_AVAILABLE,
            AUDIT_PANEL_AVAILABLE,
            BACKUP_SYSTEM_AVAILABLE,
            get_admin_dashboard,
            get_user_management,
            get_audit_panel,
            get_backup_panel
        )
        
        print("✅ Imports de main_window exitosos")
        
        # Verificar disponibilidad
        print("\n📊 VERIFICANDO DISPONIBILIDAD:")
        print(f"🎛️ Dashboard Administrativo: {'✅ DISPONIBLE' if ADMIN_DASHBOARD_AVAILABLE() else '❌ NO DISPONIBLE'}")
        print(f"👥 Gestión de Usuarios: {'✅ DISPONIBLE' if USER_MANAGEMENT_AVAILABLE() else '❌ NO DISPONIBLE'}")
        print(f"📋 Panel de Auditoría: {'✅ DISPONIBLE' if AUDIT_PANEL_AVAILABLE() else '❌ NO DISPONIBLE'}")
        print(f"💾 Sistema de Respaldos: {'✅ DISPONIBLE' if BACKUP_SYSTEM_AVAILABLE() else '❌ NO DISPONIBLE'}")
        
        # Verificar funciones
        print("\n🔧 VERIFICANDO FUNCIONES:")
        dashboard_func = get_admin_dashboard()
        user_mgmt_func = get_user_management()
        audit_func = get_audit_panel()
        backup_func = get_backup_panel()
        
        print(f"🎛️ Función show_admin_dashboard: {'✅ ENCONTRADA' if dashboard_func else '❌ NO ENCONTRADA'}")
        print(f"👥 Función show_user_management: {'✅ ENCONTRADA' if user_mgmt_func else '❌ NO ENCONTRADA'}")
        print(f"📋 Función show_audit_panel: {'✅ ENCONTRADA' if audit_func else '❌ NO ENCONTRADA'}")
        print(f"💾 Función show_backup_system: {'✅ ENCONTRADA' if backup_func else '❌ NO ENCONTRADA'}")
        
        # Verificar imports directos
        print("\n📦 VERIFICANDO IMPORTS DIRECTOS:")
        try:
            from homologador.ui import admin_dashboard
            print("✅ admin_dashboard importado correctamente")
            
            # Verificar función específica
            if hasattr(admin_dashboard, 'show_admin_dashboard'):
                print("✅ show_admin_dashboard encontrada en admin_dashboard")
            else:
                print("❌ show_admin_dashboard NO encontrada en admin_dashboard")
                
        except ImportError as e:
            print(f"❌ Error importando admin_dashboard: {e}")
            
        try:
            from homologador.ui import user_management
            print("✅ user_management importado correctamente")
            
            # Verificar función específica
            if hasattr(user_management, 'show_user_management'):
                print("✅ show_user_management encontrada en user_management")
            else:
                print("❌ show_user_management NO encontrada en user_management")
                
        except ImportError as e:
            print(f"❌ Error importando user_management: {e}")
        
        # Verificar menús
        print("\n🍽️ VERIFICANDO CONFIGURACIÓN DE MENÚS:")
        
        # Datos del usuario admin de prueba
        admin_user = {
            'id': 1,
            'username': 'admin',
            'role': 'admin',
            'full_name': 'Administrador del Sistema'
        }
        
        # Verificar condiciones para mostrar menús
        print(f"📝 Usuario de prueba: {admin_user}")
        print(f"🔑 Rol del usuario: {admin_user.get('role')}")
        print(f"🎛️ ¿Debe mostrar Dashboard? {'✅ SÍ' if admin_user.get('role') == 'admin' and ADMIN_DASHBOARD_AVAILABLE() else '❌ NO'}")
        print(f"👥 ¿Debe mostrar Gestión Usuarios? {'✅ SÍ' if admin_user.get('role') == 'admin' and USER_MANAGEMENT_AVAILABLE() else '❌ NO'}")
        
        print("\n" + "="*60)
        
        # Resultado final
        dashboard_ok = ADMIN_DASHBOARD_AVAILABLE() and dashboard_func is not None
        users_ok = USER_MANAGEMENT_AVAILABLE() and user_mgmt_func is not None
        
        if dashboard_ok and users_ok:
            print("🎉 ¡TODOS LOS MÓDULOS ESTÁN DISPONIBLES Y FUNCIONANDO!")
            print("🎯 El dashboard administrativo y gestión de usuarios deberían aparecer en el menú 'Administración'")
            return True
        else:
            print("⚠️ ALGUNOS MÓDULOS NO ESTÁN DISPONIBLES:")
            if not dashboard_ok:
                print("   ❌ Dashboard Administrativo")
            if not users_ok:
                print("   ❌ Gestión de Usuarios")
            return False
            
    except Exception as e:
        print(f"❌ ERROR DURANTE LA VERIFICACIÓN: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    exito = verificar_disponibilidad_modulos()
    
    if exito:
        print("\n🚀 INSTRUCCIONES PARA ACCEDER:")
        print("1. Ejecuta la aplicación: python -m homologador")
        print("2. Ingresa con usuario: admin / contraseña: admin123")
        print("3. Ve al menú 'Administración' en la barra de menús")
        print("4. Verás las opciones:")
        print("   🎛️ Dashboard Administrativo (Ctrl+D)")
        print("   👥 Gestión de Usuarios (Ctrl+U)")
        print("   📋 Panel de Auditoría (Ctrl+A)")
        
    sys.exit(0 if exito else 1)