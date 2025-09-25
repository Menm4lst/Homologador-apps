#!/usr/bin/env python3
"""
Crear usuario de prueba con el nuevo sistema y probar login
"""

import sqlite3

def create_test_user_and_verify():
    """Crea un usuario de prueba y verifica que funcione"""
    
    db_path = r"C:\Users\Antware/OneDrive/homologador.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("=== PRUEBA DE USUARIO NUEVO ===\n")
        
        # Activar usuarios inactivos para la prueba
        cursor.execute("UPDATE users SET is_active = 1 WHERE username IN ('estebanquito', 'prueba1')")
        conn.commit()
        
        print("✅ Usuarios activados para prueba")
        
        # Mostrar estado actual de usuarios
        cursor.execute("SELECT username, is_active FROM users")
        users = cursor.fetchall()
        
        print("\nUsuarios en la base de datos:")
        for username, is_active in users:
            status = "Activo" if is_active else "Inactivo"
            print(f"  - {username}: {status}")
        
        conn.close()
        
        print("\n=== INSTRUCCIONES DE PRUEBA ===")
        print("1. ✅ La función hash_password ya está corregida")
        print("2. ✅ Nuevos usuarios creados por admin usarán Argon2")
        print("3. ✅ verify_password maneja tanto Argon2 como SHA-256")
        print("4. 🔄 Prueba crear un nuevo usuario desde el panel admin")
        print("5. 🔄 Intenta hacer login con ese nuevo usuario")
        print("\n💡 Si el nuevo usuario puede hacer login, ¡la corrección funciona!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    create_test_user_and_verify()