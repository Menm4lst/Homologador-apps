#!/usr/bin/env python3
"""
Script para diagnosticar problemas con la creación de usuarios nuevos.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from homologador.core.auth import hash_password, verify_password
from homologador.data.seed import get_auth_service, create_seed_data


def test_user_creation():
    """Prueba el proceso completo de creación de usuario."""
    
    print("🔍 DIAGNÓSTICO DE CREACIÓN DE USUARIOS")
    print("=" * 50)
    
    # Inicializar datos
    create_seed_data()
    auth_service = get_auth_service()
    
    # Datos de prueba
    test_username = "nuevo_usuario"
    test_password = "MiPassword123!"
    
    print(f"\n📝 Datos de prueba:")
    print(f"   Usuario: {test_username}")
    print(f"   Contraseña: {test_password}")
    
    # 1. Probar función de hash
    print(f"\n🔒 Probando función hash_password...")
    hashed = hash_password(test_password)
    print(f"   Hash generado: {hashed[:50]}...")
    
    # 2. Probar verificación
    print(f"\n✅ Probando verify_password...")
    is_valid = verify_password(test_password, hashed)
    print(f"   Verificación: {'✓ CORRECTA' if is_valid else '✗ FALLIDA'}")
    
    # 3. Probar con contraseña incorrecta
    print(f"\n❌ Probando con contraseña incorrecta...")
    is_invalid = verify_password("password_incorrecto", hashed)
    print(f"   Verificación incorrecta: {'✗ CORRECTA' if not is_invalid else '✓ FALLIDA'}")
    
    # 4. Verificar usuarios existentes
    print(f"\n👥 Verificando usuarios existentes...")
    try:
        # Intentar autenticación con usuarios conocidos
        admin_auth = auth_service.authenticate("admin", "admin123")
        print(f"   Admin (admin123): {'✓' if admin_auth else '✗'}")
        
        esteban_auth = auth_service.authenticate("estebanquito", "admin123")  
        print(f"   Estebanquito (admin123): {'✓' if esteban_auth else '✗'}")
        
    except Exception as e:
        print(f"   Error en autenticación: {e}")
    
    # 5. Simular creación de usuario
    print(f"\n🆕 Simulando creación de usuario...")
    try:
        from homologador.data.repositories import get_user_repository
        user_repo = get_user_repository()
        
        # Verificar si el usuario ya existe
        existing = user_repo.get_user_by_username(test_username)
        if existing:
            print(f"   ⚠️ Usuario {test_username} ya existe, eliminándolo...")
            # Aquí podrías eliminar el usuario si fuera necesario
        
        # Crear datos del usuario
        user_data = {
            'username': test_username,
            'password': hash_password(test_password),
            'full_name': 'Usuario de Prueba',
            'email': 'prueba@test.com',
            'department': 'IT',
            'role': 'viewer',
            'is_active': True,
            'force_password_change': False,
            'created_at': '2024-09-24T15:00:00',
            'last_login': None
        }
        
        # Intentar crear usuario
        user_id = user_repo.create_user(user_data)
        print(f"   Usuario creado con ID: {user_id}")
        
        # 6. Probar autenticación del nuevo usuario
        print(f"\n🔐 Probando autenticación del nuevo usuario...")
        try:
            new_user_auth = auth_service.authenticate(test_username, test_password)
            if new_user_auth:
                print(f"   ✅ Autenticación exitosa!")
                print(f"   Datos: {new_user_auth}")
            else:
                print(f"   ❌ Autenticación falló")
                
                # Verificar qué hay en la base de datos
                stored_user = user_repo.get_user_by_username(test_username)
                if stored_user:
                    print(f"   Usuario encontrado en BD:")
                    print(f"     ID: {stored_user.get('user_id')}")
                    print(f"     Username: {stored_user.get('username')}")
                    print(f"     Hash: {stored_user.get('password', '')[:50]}...")
                    print(f"     Active: {stored_user.get('is_active')}")
                    
                    # Probar verificación directa
                    direct_verify = verify_password(test_password, stored_user.get('password', ''))
                    print(f"     Verificación directa: {'✓' if direct_verify else '✗'}")
                else:
                    print(f"   ❌ Usuario no encontrado en BD")
        
        except Exception as e:
            print(f"   Error en autenticación: {e}")
            import traceback
            traceback.print_exc()
    
    except Exception as e:
        print(f"   Error en creación: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_user_creation()