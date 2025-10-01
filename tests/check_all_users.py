#!/usr/bin/env python3
"""
Script para verificar y diagnosticar usuarios en la base de datos.
"""


# Agregar paths

import os
import sys
project_root = os.path.dirname(os.path.abspath(__file__))
homologador_path = os.path.join(project_root, 'homologador')
sys.path.insert(0, project_root)
sys.path.insert(0, homologador_path)

def check_all_users():
    """Verifica todos los usuarios en la base de datos."""
    try:
        print("👥 VERIFICANDO USUARIOS EN LA BASE DE DATOS")
        print("=" * 50)
        
        # Importar servicios
        
        # Inicializar base de datos

        from homologador.core.storage import get_database_manager
        from homologador.data.seed import get_auth_service
        db_manager = get_database_manager()
        auth_service = get_auth_service()
        user_repo = auth_service.user_repo
        
        # Obtener conexión directa para consultas
        with db_manager.get_connection() as connection:
            cursor = connection.cursor()
            
            # Consultar todos los usuarios
            cursor.execute("""
                SELECT id, username, role, full_name, email, must_change_password, 
                       created_at, last_login, is_active
                FROM users 
                ORDER BY id
            """)
            
            users = cursor.fetchall()
            
            if not users:
                print("❌ No se encontraron usuarios en la base de datos")
                return []
            
            print(f"📋 Se encontraron {len(users)} usuarios:")
            print("-" * 50)
            
            user_list = []
            for user in users:
                user_data = {
                    'id': user[0],
                    'username': user[1], 
                    'role': user[2],
                    'full_name': user[3],
                    'email': user[4],
                    'must_change_password': user[5],
                    'created_at': user[6],
                    'last_login': user[7],
                    'is_active': user[8]
                }
                user_list.append(user_data)
                
                print(f"👤 Usuario #{user_data['id']}:")
                print(f"   📛 Username: {user_data['username']}")
                print(f"   🏷️  Role: {user_data['role']}")
                print(f"   👨‍💼 Nombre: {user_data['full_name']}")
                print(f"   📧 Email: {user_data['email']}")
                print(f"   🔄 Debe cambiar password: {user_data['must_change_password']}")
                print(f"   ✅ Activo: {user_data['is_active']}")
                print(f"   📅 Creado: {user_data['created_at']}")
                print(f"   🕒 Último login: {user_data['last_login']}")
                print()
            
            return user_list
            
    except Exception as e:
        print(f"❌ Error verificando usuarios: {e}")
        import traceback
        traceback.print_exc()
        return []

def test_user_authentication(username, password):
    """Prueba autenticación de un usuario específico."""
    try:
        print(f"🧪 Probando autenticación para: {username}")
        
        from homologador.data.seed import get_auth_service
        auth_service = get_auth_service()
        
        # Intentar autenticar
        user_info = auth_service.authenticate(username, password)
        print(f"✅ Autenticación exitosa: {user_info}")
        return True
        
    except Exception as e:
        print(f"❌ Fallo autenticación para {username}: {e}")
        return False

def reset_user_password(username, new_password):
    """Resetea la contraseña de un usuario específico."""
    try:
        print(f"🔧 Reseteando contraseña para: {username}")
        
        
        # Servicios

        from homologador.core.storage import get_database_manager
        from homologador.data.seed import get_auth_service
        auth_service = get_auth_service()
        db_manager = get_database_manager()
        
        # Buscar usuario
        user_repo = auth_service.user_repo
        user = user_repo.get_by_username(username)
        
        if not user:
            print(f"❌ Usuario {username} no encontrado")
            return False
        
        # Generar nuevo hash
        new_hash = auth_service.hash_password(new_password)
        
        # Actualizar en base de datos
        with db_manager.get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("""
                UPDATE users 
                SET password_hash = ?, must_change_password = 0
                WHERE username = ?
            """, (new_hash, username))
            connection.commit()
        
        print(f"✅ Contraseña actualizada para {username}")
        
        # Verificar que funciona
        if test_user_authentication(username, new_password):
            print(f"✅ Verificación exitosa para {username}")
            return True
        else:
            print(f"❌ Verificación falló para {username}")
            return False
            
    except Exception as e:
        print(f"❌ Error reseteando contraseña: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Función principal."""
    print("🔐 DIAGNÓSTICO DE USUARIOS Y CREDENCIALES")
    print("=" * 60)
    
    # Verificar todos los usuarios
    users = check_all_users()
    
    if not users:
        print("⚠️ No hay usuarios para diagnosticar")
        return
    
    print("🔍 DIAGNÓSTICO DE AUTENTICACIÓN")
    print("-" * 30)
    
    # Probar autenticación para cada usuario con contraseñas comunes
    common_passwords = ['admin123', 'user123', 'test123', 'password', '123456']
    
    for user in users:
        username = user['username']
        print(f"\\n👤 Probando usuario: {username}")
        
        authenticated = False
        for password in common_passwords:
            if test_user_authentication(username, password):
                print(f"✅ {username} funciona con contraseña: {password}")
                authenticated = True
                break
        
        if not authenticated:
            print(f"⚠️ {username} no autentica con contraseñas comunes")
            print("🔧 Reseteando contraseña a 'admin123'...")
            
            if reset_user_password(username, 'admin123'):
                print(f"✅ {username} ahora funciona con: admin123")
            else:
                print(f"❌ No se pudo resetear {username}")
    
    print("\\n" + "=" * 60)
    print("📝 RESUMEN FINAL:")
    print("   Todos los usuarios deberían funcionar con: admin123")
    print("   Si creaste usuarios nuevos, prueba con esa contraseña")
    print("   Si siguen sin funcionar, hay un problema en el hash")

if __name__ == "__main__":
    main()