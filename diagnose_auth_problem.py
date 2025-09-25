#!/usr/bin/env python3
"""
Diagnóstico específico del problema de autenticación de usuarios creados por admin
"""

import sqlite3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def diagnose_user_authentication():
    """Diagnostica el problema específico de autenticación"""
    
    db_path = r"C:\Users\Antware/OneDrive/homologador.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔍 DIAGNÓSTICO DE AUTENTICACIÓN - USUARIO CREADO POR ADMIN")
        print("=" * 60)
        
        # Obtener el usuario más reciente (probablemente el que acabas de crear)
        cursor.execute("""
            SELECT id, username, password_hash, is_active, created_at, role 
            FROM users 
            ORDER BY created_at DESC 
            LIMIT 5
        """)
        recent_users = cursor.fetchall()
        
        print("🕐 Usuarios más recientes:")
        for i, (user_id, username, password_hash, is_active, created_at, role) in enumerate(recent_users):
            print(f"{i+1}. Usuario: {username}")
            print(f"   ID: {user_id}")
            print(f"   Activo: {'✅' if is_active else '❌'}")
            print(f"   Rol: {role}")
            print(f"   Creado: {created_at}")
            
            # Analizar tipo de hash
            if password_hash.startswith('$argon2'):
                hash_type = "🔐 Argon2 (CORRECTO)"
                print(f"   Hash: {hash_type}")
            elif ':' in password_hash:
                hash_type = "🔑 SHA-256+Salt (PROBLEMÁTICO)"
                print(f"   Hash: {hash_type}")
            else:
                hash_type = "🗝️ SHA-256 Simple (PROBLEMÁTICO)"
                print(f"   Hash: {hash_type}")
            
            print(f"   Hash completo: {password_hash[:50]}...")
            print()
        
        # Preguntarle al usuario cuál es el usuario que creó
        print("📝 ¿Cuál es el nombre del usuario que acabas de crear?")
        print("(Presiona Enter si es el primero de la lista)")
        
        target_username = input("Nombre del usuario: ").strip()
        
        if not target_username and recent_users:
            # Usar el más reciente
            target_username = recent_users[0][1]
            print(f"Usando el usuario más reciente: {target_username}")
        
        # Buscar el usuario específico
        cursor.execute("SELECT * FROM users WHERE username = ?", (target_username,))
        user_data = cursor.fetchone()
        
        if not user_data:
            print(f"❌ Usuario '{target_username}' no encontrado")
            return
        
        user_id, username, password_hash, role, full_name, email, is_active, last_login, created_at, department, must_change_password = user_data
        
        print(f"\n🎯 ANÁLISIS DEL USUARIO: {username}")
        print("-" * 40)
        print(f"ID: {user_id}")
        print(f"Activo: {'✅ Sí' if is_active else '❌ No'}")
        print(f"Rol: {role}")
        print(f"Debe cambiar contraseña: {'Sí' if must_change_password else 'No'}")
        
        # Determinar el tipo de hash
        if password_hash.startswith('$argon2'):
            print("🔐 Tipo de hash: Argon2 ✅ (CORRECTO)")
            hash_format = "argon2"
        elif ':' in password_hash:
            print("🔑 Tipo de hash: SHA-256 + Salt ⚠️ (Puede ser problemático)")
            hash_format = "sha256_salt"
        else:
            print("🗝️ Tipo de hash: SHA-256 Simple ❌ (PROBLEMÁTICO)")
            hash_format = "sha256_simple"
        
        print(f"Hash: {password_hash[:50]}...")
        
        # Probar autenticación con diferentes contraseñas
        print(f"\n🧪 PRUEBA DE AUTENTICACIÓN")
        print("-" * 30)
        
        test_passwords = ["admin123", "prueba123", "123456", "password"]
        
        print("¿Cuál es la contraseña que asignaste a este usuario?")
        user_password = input("Contraseña: ").strip()
        
        if user_password:
            test_passwords.insert(0, user_password)
        
        # Importar función de verificación
        try:
            # Intentar usar la función corregida
            from homologador.core.auth import verify_password
            
            print(f"\n🔍 Probando contraseñas para '{username}':")
            
            for password in test_passwords:
                try:
                    result = verify_password(password, password_hash)
                    status = "✅ ÉXITO" if result else "❌ FALLÓ"
                    print(f"   '{password}': {status}")
                    
                    if result:
                        print(f"\n🎉 ¡CONTRASEÑA ENCONTRADA!")
                        print(f"Usuario: {username}")
                        print(f"Contraseña: {password}")
                        break
                except Exception as e:
                    print(f"   '{password}': 💥 ERROR - {e}")
            
        except ImportError as e:
            print(f"❌ Error importando verify_password: {e}")
        
        conn.close()
        
        print(f"\n📋 RECOMENDACIONES:")
        if hash_format == "argon2":
            print("✅ El hash es Argon2 (correcto)")
            print("✅ La corrección está funcionando")
            print("⚠️  Verifica que uses la contraseña correcta")
        else:
            print("❌ El usuario tiene hash SHA-256 (problemático)")
            print("🔧 Necesita ser recreado con hash Argon2")
            print("💡 Elimina el usuario y créalo de nuevo")
        
        if not is_active:
            print("⚠️  El usuario está INACTIVO - activarlo primero")
        
    except Exception as e:
        print(f"❌ Error durante el diagnóstico: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    diagnose_user_authentication()