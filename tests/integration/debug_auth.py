#!/usr/bin/env python3
"""
Script para verificar y corregir el sistema de autenticación.
"""


# Agregar paths

import os
import sys
project_root = os.path.dirname(os.path.abspath(__file__))
homologador_path = os.path.join(project_root, 'homologador')
sys.path.insert(0, project_root)
sys.path.insert(0, homologador_path)

def check_authentication():
    """Verifica el estado del sistema de autenticación."""
    try:
        print("🔍 Verificando sistema de autenticación...")
        
        # Importar servicios
        
        # Inicializar base de datos

        from homologador.core.storage import get_database_manager
        from homologador.data.seed import get_auth_service, create_seed_data
        print("📁 Inicializando base de datos...")
        db_manager = get_database_manager()
        
        # Crear datos semilla si no existen
        print("🌱 Creando datos semilla...")
        create_seed_data()
        
        # Obtener servicio de autenticación
        auth_service = get_auth_service()
        
        print("👥 Verificando usuarios existentes...")
        
        # Intentar autenticar con credenciales por defecto
        test_users = [
            ("admin", "admin123"),
            ("user", "user123"),
            ("test", "test123")
        ]
        
        for username, password in test_users:
            try:
                print(f"🧪 Probando: {username} / {password}")
                user_info = auth_service.authenticate(username, password)
                print(f"✅ Login exitoso para {username}: {user_info}")
                return True
            except Exception as e:
                print(f"❌ Fallo login para {username}: {e}")
        
        return False
        
    except Exception as e:
        print(f"❌ Error verificando autenticación: {e}")
        import traceback
        traceback.print_exc()
        return False

def fix_authentication():
    """Intenta corregir problemas de autenticación."""
    try:
        print("🔧 Reparando sistema de autenticación...")
        
        
        # Reinicializar base de datos

        from homologador.core.storage import get_database_manager
        from homologador.data.seed import create_seed_data
        db_manager = get_database_manager()
        
        # Recrear datos semilla
        create_seed_data()
        
        print("✅ Sistema de autenticación reparado")
        return True
        
    except Exception as e:
        print(f"❌ Error reparando autenticación: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Función principal."""
    print("🔐 DIAGNÓSTICO DEL SISTEMA DE AUTENTICACIÓN")
    print("=" * 50)
    
    # Verificar autenticación
    if check_authentication():
        print("\n✅ Sistema de autenticación funcionando correctamente!")
        print("💡 Credenciales válidas encontradas")
    else:
        print("\n⚠️ Problemas detectados en autenticación")
        print("🔧 Intentando reparar...")
        
        if fix_authentication():
            print("\n🎉 Reparación completada!")
            print("🔄 Verificando nuevamente...")
            
            if check_authentication():
                print("✅ Sistema de autenticación ahora funciona!")
            else:
                print("❌ No se pudo reparar el sistema")
        else:
            print("❌ Fallo en la reparación")
    
    print("\n" + "=" * 50)
    print("🚀 Ahora puedes ejecutar la aplicación con:")
    print("   Usuario: admin")
    print("   Contraseña: admin123")

if __name__ == "__main__":
    main()