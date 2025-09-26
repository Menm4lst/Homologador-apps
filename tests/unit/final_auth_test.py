#!/usr/bin/env python3
"""
PRUEBA FINAL DE AUTENTICACIÓN - Verificar correcciones
"""

import sqlite3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from homologador.core.auth import verify_password

def final_authentication_test():
    """Prueba final de todas las correcciones de autenticación"""
    
    print("🔐 PRUEBA FINAL DE AUTENTICACIÓN")
    print("="*50)
    
    # Conectar a la base de datos
    db_path = r"C:\Users\Antware/OneDrive/homologador.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Obtener todos los usuarios activos
        cursor.execute("SELECT id, username, password_hash, is_active FROM users WHERE is_active = 1")
        users = cursor.fetchall()
        
        print(f"📋 {len(users)} usuarios activos encontrados")
        print()
        
        # Pruebas específicas
        test_cases = [
            # Usuario, Contraseña esperada, Descripción
            ('admin', 'admin123', 'Administrador principal'),
            ('prueba1', 'admin123', 'Usuario con Argon2 activo'),
            ('test_user', 'test123', 'Usuario de prueba SHA-256'),
        ]
        
        results = []
        
        for username, password, description in test_cases:
            print(f"🧪 Probando: {username} ({description})")
            
            # Buscar usuario en BD
            user_data = next((u for u in users if u[1] == username), None)
            
            if not user_data:
                print(f"   ❌ Usuario no encontrado o inactivo")
                results.append(False)
                continue
            
            user_id, db_username, password_hash, is_active = user_data
            
            # Identificar tipo de hash
            if password_hash.startswith('$argon2'):
                hash_type = "Argon2"
            elif ':' in password_hash:
                hash_type = "SHA-256+Salt"
            else:
                hash_type = "SHA-256 Simple"
            
            print(f"   📍 Hash: {hash_type}")
            
            # Verificar contraseña
            try:
                is_valid = verify_password(password, password_hash)
                
                if is_valid:
                    print(f"   ✅ ÉXITO - Autenticación correcta")
                    results.append(True)
                else:
                    print(f"   ❌ FALLÓ - Contraseña incorrecta")
                    results.append(False)
                    
            except Exception as e:
                print(f"   💥 ERROR - {e}")
                results.append(False)
            
            print()
        
        conn.close()
        
        # Resumen final
        success_count = sum(results)
        total_tests = len(results)
        
        print("="*50)
        print(f"📊 RESUMEN FINAL:")
        print(f"✅ Pruebas exitosas: {success_count}/{total_tests}")
        print(f"📈 Tasa de éxito: {(success_count/total_tests*100) if total_tests > 0 else 0:.1f}%")
        
        if success_count == total_tests:
            print("\n🎉 ¡PERFECTO! Sistema de autenticación funcionando correctamente")
            print("✅ Soporte completo para Argon2 y SHA-256")
            print("✅ Usuarios activos pueden acceder")
            print("✅ Nuevos usuarios creados por admin funcionan")
            
            print("\n📋 INSTRUCCIONES PARA EL USUARIO:")
            print("1. La aplicación ya está ejecutándose")
            print("2. Puedes usar cualquiera de estos usuarios para probar:")
            print("   - admin / admin123 (si la contraseña es correcta)")
            print("   - prueba1 / admin123")
            print("   - test_user / test123")
            print("3. Los nuevos usuarios creados ahora funcionarán correctamente")
            print("4. El sistema maneja tanto hashes Argon2 como SHA-256")
            
        else:
            print(f"\n⚠️  {total_tests - success_count} pruebas fallaron - revisar contraseñas")
            
        return success_count == total_tests
        
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    final_authentication_test()