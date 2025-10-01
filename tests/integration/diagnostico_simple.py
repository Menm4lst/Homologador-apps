#!/usr/bin/env python3
"""
Script simple para diagnosticar problemas con usuarios nuevos.
"""


# Agregar el directorio del proyecto al path

import os
import sys

import hashlib
import sqlite3
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)
sys.path.insert(0, os.path.join(project_dir, 'homologador'))

def check_users_in_database():
    """Revisa directamente la base de datos de usuarios."""
    
    print("🔍 DIAGNÓSTICO DIRECTO DE BASE DE DATOS")
    print("=" * 50)
    
    # Buscar la base de datos en diferentes ubicaciones posibles
    possible_paths = [
        os.path.join(project_dir, 'homologador', 'data', 'homologador.db'),
        os.path.join(project_dir, 'homologador.db'),
        os.path.join(project_dir, 'data', 'homologador.db'),
        os.path.expanduser('~/OneDrive/homologador.db'),
        'homologador.db'
    ]
    
    db_path = None
    for path in possible_paths:
        if os.path.exists(path):
            db_path = path
            break
    
    if not db_path:
        print("❌ Base de datos no encontrada en ninguna ubicación:")
        for path in possible_paths:
            print(f"   - {path}")
        return
    
    print("✅ Base de datos encontrada:", db_path)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar estructura de la tabla
        print("\n📋 Estructura de la tabla users:")
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        for col in columns:
            print(f"   {col[1]} ({col[2]})")
        
        # Obtener todos los usuarios
        print("\n👥 Usuarios en la base de datos:")
        cursor.execute("SELECT id, username, password_hash, is_active FROM users")
        users = cursor.fetchall()
        
        for user in users:
            user_id, username, password_hash, is_active = user
            print(f"\n   🔹 ID: {user_id}")
            print(f"     Usuario: {username}")
            print(f"     Hash: {password_hash[:50]}..." if password_hash else "Sin contraseña")
            print(f"     Activo: {'Sí' if is_active else 'No'}")
            
            # Probar si el hash tiene formato correcto
            if password_hash and ':' in password_hash:
                print(f"     Formato: ✓ Con salt")
            elif password_hash:
                print(f"     Formato: ⚠️ Sin salt (formato antiguo)")
            else:
                print(f"     Formato: ❌ Sin contraseña")
        
        # Probar autenticación manual con admin123
        print(f"\n🔐 Probando autenticación manual...")
        test_password = "admin123"
        
        for user in users:
            user_id, username, password_hash, is_active = user
            if not password_hash or not is_active:
                continue
                
            print(f"\n   Probando {username} con '{test_password}':")
            
            try:
                if ':' in password_hash:
                    # Formato con salt
                    salt, stored_hash = password_hash.split(':', 1)
                    test_hash = hashlib.sha256((test_password + salt).encode()).hexdigest()
                    matches = test_hash == stored_hash
                else:
                    # Formato sin salt
                    test_hash = hashlib.sha256(test_password.encode()).hexdigest()
                    matches = test_hash == password_hash
                
                print(f"     Resultado: {'✅ CORRECTO' if matches else '❌ INCORRECTO'}")
                
                if matches:
                    print(f"     ✓ {username} puede autenticarse con {test_password}")
                
            except Exception as e:
                print(f"     ❌ Error verificando: {e}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error accediendo a la base de datos: {e}")
        import traceback
        traceback.print_exc()


def test_hash_function():
    """Prueba la función de hash directamente."""
    
    print(f"\n🧪 PRUEBA DE FUNCIÓN HASH")
    print("=" * 50)
    
    password = "admin123"
    print(f"Contraseña de prueba: {password}")
    
    # Hash simple (formato antiguo)
    simple_hash = hashlib.sha256(password.encode()).hexdigest()
    print(f"Hash simple: {simple_hash}")
    
    # Hash con salt (formato nuevo)
    import secrets
    salt = secrets.token_hex(32)
    salted_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    combined = f"{salt}:{salted_hash}"
    print(f"Hash con salt: {combined[:50]}...")
    
    # Verificación
    stored_salt, stored_hash = combined.split(':', 1)
    verify_hash = hashlib.sha256((password + stored_salt).encode()).hexdigest()
    matches = verify_hash == stored_hash
    print(f"Verificación: {'✅ CORRECTA' if matches else '❌ FALLIDA'}")


if __name__ == "__main__":
    test_hash_function()
    check_users_in_database()