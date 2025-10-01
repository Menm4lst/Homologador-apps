#!/usr/bin/env python3
"""
Script para activar usuarios y verificar contraseñas
"""

import os
import sys

import sqlite3
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))



from homologador.core.auth import verify_password
def fix_user_access():
    """Activa usuarios y verifica acceso"""
    
    # Conectar a la base de datos
    db_path = r"C:\Users\Antware/OneDrive/homologador.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("=== ACTIVANDO USUARIOS Y VERIFICANDO ACCESO ===\n")
        
        # 1. Activar todos los usuarios
        print("🔧 Activando todos los usuarios...")
        cursor.execute("UPDATE users SET is_active = 1 WHERE is_active = 0")
        activated = cursor.rowcount
        print(f"✅ {activated} usuarios activados\n")
        
        # 2. Verificar usuarios con diferentes contraseñas comunes
        common_passwords = [
            'admin123', 'admin', '123456', 'password', 
            'Admin123', 'nuevapass123', 'prueba123'
        ]
        
        cursor.execute("SELECT id, username, password_hash FROM users")
        users = cursor.fetchall()
        
        for user_id, username, password_hash in users:
            print(f"👤 Usuario: {username}")
            
            found_password = False
            for test_pass in common_passwords:
                try:
                    if verify_password(test_pass, password_hash):
                        print(f"   ✅ Contraseña encontrada: '{test_pass}'")
                        found_password = True
                        break
                except Exception as e:
                    print(f"   ❌ Error probando '{test_pass}': {e}")
            
            if not found_password:
                print(f"   ⚠️  Contraseña no encontrada en lista común")
            
            print()
        
        # 3. Crear usuario de prueba con contraseña conocida si no existe
        print("🔧 Verificando usuario de prueba...")
        cursor.execute("SELECT id FROM users WHERE username = 'test_user'")
        if not cursor.fetchone():
            from homologador.core.auth import hash_password
            hashed = hash_password('test123')
            
            cursor.execute("""
                INSERT INTO users (username, password_hash, role, full_name, is_active, must_change_password)
                VALUES (?, ?, ?, ?, ?, ?)
            """, ('test_user', hashed, 'editor', 'Usuario de Prueba', 1, 0))
            
            print("✅ Usuario de prueba creado:")
            print("   Username: test_user")
            print("   Password: test123")
        else:
            print("✅ Usuario de prueba ya existe")
        
        # Guardar cambios
        conn.commit()
        conn.close()
        
        print(f"\n🎉 PROCESO COMPLETADO:")
        print(f"✅ Todos los usuarios están activos")
        print(f"✅ Usuario de prueba disponible (test_user / test123)")
        print(f"✅ Función de autenticación soporta Argon2 y SHA-256")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    fix_user_access()