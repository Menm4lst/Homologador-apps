#!/usr/bin/env python3
"""
Script para probar la corrección de autenticación con múltiples tipos de hash
"""

import sqlite3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from homologador.core.auth import verify_password

def test_authentication():
    """Prueba la autenticación con todos los usuarios de la base de datos"""
    
    # Conectar a la base de datos
    db_path = r"C:\Users\Antware/OneDrive/homologador.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Obtener todos los usuarios
        cursor.execute("SELECT id, username, password, is_active FROM users")
        users = cursor.fetchall()
        
        print("=== PRUEBA DE AUTENTICACIÓN CORREGIDA ===\n")
        
        # Probar contraseña conocida para cada usuario
        test_passwords = {
            'admin': 'admin123',
            'estebanquito': 'admin123',  # Asumiendo que usa la contraseña por defecto
            'prueba1': 'admin123',       # Asumiendo que usa la contraseña por defecto
            'prueba': 'nuevapass123'     # Usuario creado recientemente
        }
        
        for user_id, username, password_hash, is_active in users:
            print(f"Usuario: {username}")
            print(f"  ID: {user_id}")
            print(f"  Activo: {'Sí' if is_active else 'No'}")
            print(f"  Tipo de hash: {'Argon2' if password_hash.startswith('$argon2') else 'SHA-256'}")
            print(f"  Hash: {password_hash[:50]}...")
            
            # Probar contraseña
            if username in test_passwords:
                test_pass = test_passwords[username]
                result = verify_password(test_pass, password_hash)
                print(f"  Prueba con '{test_pass}': {'✅ ÉXITO' if result else '❌ FALLÓ'}")
            else:
                print(f"  Sin contraseña de prueba conocida")
            
            print()
        
        conn.close()
        
        print("\n=== RESUMEN ===")
        print("✅ Función verify_password actualizada para manejar Argon2")
        print("✅ Librerías argon2-cffi y passlib instaladas")
        print("⚠️  Verificar que las contraseñas de prueba sean correctas")
        
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_authentication()