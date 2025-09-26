#!/usr/bin/env python3
"""
Script para resetear la contraseña del usuario admin.
"""

import sys
import os

# Agregar paths
project_root = os.path.dirname(os.path.abspath(__file__))
homologador_path = os.path.join(project_root, 'homologador')
sys.path.insert(0, project_root)
sys.path.insert(0, homologador_path)

def reset_admin_password():
    """Resetea la contraseña del usuario admin."""
    try:
        print("🔧 Reseteando contraseña del usuario admin...")
        
        # Importar servicios
        from homologador.data.seed import get_auth_service
        from homologador.core.storage import get_database_manager
        
        # Inicializar base de datos
        db_manager = get_database_manager()
        
        # Obtener servicio de autenticación
        auth_service = get_auth_service()
        
        # Obtener repositorio de usuarios
        user_repo = auth_service.user_repo
        
        # Buscar usuario admin
        admin_user = user_repo.get_by_username('admin')
        
        if not admin_user:
            print("❌ Usuario admin no existe. Creando...")
            
            # Crear usuario admin
            admin_data = {
                'username': 'admin',
                'password_hash': auth_service.hash_password('admin123'),
                'role': 'admin',
                'full_name': 'Administrador del Sistema',
                'email': 'admin@empresa.com',
                'must_change_password': False
            }
            
            admin_id = user_repo.create(admin_data)
            print(f"✅ Usuario admin creado con ID: {admin_id}")
        else:
            print(f"👤 Usuario admin encontrado con ID: {admin_user['id']}")
            
            # Actualizar contraseña
            new_password_hash = auth_service.hash_password('admin123')
            
            # Actualizar directamente en la base de datos
            with db_manager.get_connection() as connection:
                cursor = connection.cursor()
                
                cursor.execute("""
                    UPDATE users 
                    SET password_hash = ?, must_change_password = 0
                    WHERE id = ?
                """, (new_password_hash, admin_user['id']))
                
                connection.commit()
            
            print("✅ Contraseña del usuario admin actualizada")
        
        # Verificar que funciona
        print("🧪 Probando autenticación...")
        
        try:
            user_info = auth_service.authenticate('admin', 'admin123')
            print(f"✅ Autenticación exitosa: {user_info}")
            return True
        except Exception as e:
            print(f"❌ Fallo autenticación: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Error reseteando contraseña: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Función principal."""
    print("🔐 RESETEO DE CONTRASEÑA ADMIN")
    print("=" * 40)
    
    if reset_admin_password():
        print("\n🎉 ¡Reseteo completado exitosamente!")
        print("📝 Credenciales de acceso:")
        print("   Usuario: admin")
        print("   Contraseña: admin123")
        print("\n🚀 Ahora puedes ejecutar la aplicación normalmente.")
    else:
        print("\n❌ No se pudo resetear la contraseña")
        print("🔧 Puede ser necesario recrear la base de datos")

if __name__ == "__main__":
    main()