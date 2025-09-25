#!/usr/bin/env python3
"""
Prueba específica del usuario prueba2
"""

import sqlite3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_prueba2_user():
    """Prueba específica del usuario prueba2"""
    
    db_path = r"C:\Users\Antware/OneDrive/homologador.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔍 PRUEBA ESPECÍFICA - USUARIO 'prueba2'")
        print("=" * 45)
        
        # Obtener datos del usuario prueba2
        cursor.execute("SELECT * FROM users WHERE username = 'prueba2'")
        user_data = cursor.fetchone()
        
        if not user_data:
            print("❌ Usuario 'prueba2' no encontrado")
            return
        
        user_id, username, password_hash, role, full_name, email, is_active, last_login, created_at, department, must_change_password = user_data
        
        print(f"👤 Usuario encontrado: {username}")
        print(f"   ID: {user_id}")
        print(f"   Activo: {'✅ Sí' if is_active else '❌ No'}")
        print(f"   Rol: {role}")
        print(f"   Tipo de hash: {'Argon2 ✅' if password_hash.startswith('$argon2') else 'SHA-256 ⚠️'}")
        print(f"   Hash: {password_hash[:60]}...")
        
        # Importar función de verificación corregida
        from homologador.core.auth import verify_password
        
        # Lista de contraseñas comunes para probar
        test_passwords = [
            "admin123", 
            "prueba123", 
            "123456", 
            "password", 
            "prueba2",
            "prueba",
            "test123"
        ]
        
        print(f"\n🧪 PROBANDO CONTRASEÑAS:")
        print("-" * 25)
        
        found_password = None
        
        for password in test_passwords:
            try:
                result = verify_password(password, password_hash)
                status = "✅ ÉXITO" if result else "❌ FALLÓ"
                print(f"   '{password}': {status}")
                
                if result:
                    found_password = password
                    break
                    
            except Exception as e:
                print(f"   '{password}': 💥 ERROR - {e}")
        
        conn.close()
        
        if found_password:
            print(f"\n🎉 ¡CONTRASEÑA ENCONTRADA!")
            print(f"Usuario: {username}")
            print(f"Contraseña correcta: {found_password}")
            print(f"\n✅ El sistema de autenticación funciona correctamente")
            print(f"🔐 Hash Argon2 verificado exitosamente")
        else:
            print(f"\n❌ Ninguna contraseña de prueba funcionó")
            print(f"\n💡 POSIBLES CAUSAS:")
            print(f"1. La contraseña asignada no está en la lista de prueba")
            print(f"2. Problema con la función verify_password")
            print(f"3. Hash corrupto en la base de datos")
            
            print(f"\n🔧 SOLUCIONES:")
            print(f"1. Intenta con la contraseña exacta que asignaste")
            print(f"2. Recrea el usuario desde el panel de admin")
            print(f"3. Verifica que la aplicación use la versión corregida")
    
    except ImportError as e:
        print(f"❌ Error importando verify_password: {e}")
        print(f"La corrección no se está aplicando correctamente")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_prueba2_user()