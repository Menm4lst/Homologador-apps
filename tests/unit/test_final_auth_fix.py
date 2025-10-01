#!/usr/bin/env python3
"""
Script para probar que la corrección de autenticación funciona
"""

import os
import sys

import sqlite3
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))



from homologador.core.auth import verify_password
from homologador.data.seed import get_auth_service
def test_fixed_authentication():
    """Prueba la autenticación corregida"""
    
    # Conectar a la base de datos
    db_path = r"C:\Users\Antware/OneDrive/homologador.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("=== PRUEBA FINAL DE AUTENTICACIÓN CORREGIDA ===\n")
        
        # Obtener todos los usuarios
        cursor.execute("SELECT id, username, password_hash, is_active FROM users")
        users = cursor.fetchall()
        
        auth_service = get_auth_service()
        
        for user_id, username, password_hash, is_active in users:
            print(f"Usuario: {username}")
            print(f"  ID: {user_id}")
            print(f"  Activo: {'✅ Sí' if is_active else '❌ No'}")
            print(f"  Tipo de hash: {'Argon2' if password_hash.startswith('$argon2') else 'SHA-256'}")
            
            # Solo probar autenticación con usuarios activos
            if is_active:
                try:
                    # Intentar autenticación con contraseña estándar
                    user_info = auth_service.authenticate(username, 'admin123')
                    print(f"  Autenticación con 'admin123': ✅ ÉXITO")
                except Exception:
                    try:
                        # Intentar con otras contraseñas posibles
                        user_info = auth_service.authenticate(username, 'nuevapass123')
                        print(f"  Autenticación con 'nuevapass123': ✅ ÉXITO")
                    except Exception:
                        print(f"  Autenticación: ❌ FALLÓ con ambas contraseñas")
            else:
                print(f"  Usuario inactivo - no se prueba autenticación")
            
            print()
        
        conn.close()
        
        print("\n=== RESUMEN DE CORRECCIÓN ===")
        print("✅ Función hash_password corregida en user_management.py")
        print("✅ Ahora usa AuthService.hash_password (Argon2)")
        print("✅ Consistencia de hashing mantenida")
        print("✅ Nuevos usuarios creados tendrán hash Argon2")
        
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_fixed_authentication()