#!/usr/bin/env python3
"""
Script para probar la autenticación corregida con la estructura real de la BD
"""

import os
import sys

import sqlite3
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))



from homologador.core.auth import verify_password
def test_authentication_fixed():
    """Prueba la autenticación con todos los usuarios usando la estructura correcta"""
    
    # Conectar a la base de datos
    db_path = r"C:\Users\Antware/OneDrive/homologador.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Obtener todos los usuarios (columna correcta: password_hash)
        cursor.execute("SELECT id, username, password_hash, is_active FROM users")
        users = cursor.fetchall()
        
        print("=== PRUEBA DE AUTENTICACIÓN CORREGIDA ===\n")
        
        # Contraseñas de prueba conocidas
        test_passwords = {
            'admin': 'admin123',
            'estebanquito': 'admin123',  
            'prueba1': 'admin123',       
            'prueba': 'nuevapass123'     # Usuario creado con SHA-256
        }
        
        success_count = 0
        total_tests = 0
        
        for user_id, username, password_hash, is_active in users:
            print(f"👤 Usuario: {username}")
            print(f"   ID: {user_id}")
            print(f"   Activo: {'✅ Sí' if is_active else '❌ No'}")
            
            # Identificar tipo de hash
            if password_hash.startswith('$argon2'):
                hash_type = "🔐 Argon2"
            elif ':' in password_hash:
                hash_type = "🔑 SHA-256 + Salt"
            else:
                hash_type = "🗝️ SHA-256 Simple"
            
            print(f"   Tipo de hash: {hash_type}")
            print(f"   Hash: {password_hash[:50]}...")
            
            # Probar contraseña si está disponible
            if username in test_passwords:
                test_pass = test_passwords[username]
                print(f"   Probando contraseña: '{test_pass}'")
                
                try:
                    result = verify_password(test_pass, password_hash)
                    total_tests += 1
                    
                    if result:
                        print(f"   ✅ ÉXITO - Autenticación correcta")
                        success_count += 1
                    else:
                        print(f"   ❌ FALLÓ - Contraseña incorrecta")
                        
                except Exception as e:
                    print(f"   💥 ERROR - {e}")
                    total_tests += 1
            else:
                print(f"   ⚠️  Sin contraseña de prueba")
            
            print("-" * 50)
        
        conn.close()
        
        print(f"\n📊 RESUMEN DE RESULTADOS:")
        print(f"✅ Autenticaciones exitosas: {success_count}")
        print(f"❌ Autenticaciones fallidas: {total_tests - success_count}")
        print(f"📈 Tasa de éxito: {(success_count/total_tests*100) if total_tests > 0 else 0:.1f}%")
        
        if success_count == total_tests and total_tests > 0:
            print("\n🎉 ¡PERFECTO! Todos los usuarios pueden autenticarse correctamente")
        elif success_count > 0:
            print(f"\n⚠️  Algunos usuarios funcionan, otros necesitan verificación de contraseña")
        else:
            print(f"\n🚨 PROBLEMA: Ningún usuario pudo autenticarse correctamente")
            
        return success_count == total_tests and total_tests > 0
        
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_authentication_fixed()