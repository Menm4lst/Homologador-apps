#!/usr/bin/env python3
"""
Verificar estructura de la tabla users y probar prueba2
"""

import sqlite3

def check_user_structure():
    """Verifica la estructura y prueba el usuario prueba2"""
    
    db_path = r"C:\Users\Antware/OneDrive/homologador.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔍 ESTRUCTURA DE LA TABLA USERS")
        print("=" * 40)
        
        # Ver estructura de la tabla
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        
        print("Columnas de la tabla 'users':")
        for i, col in enumerate(columns):
            print(f"{i}: {col[1]} ({col[2]})")
        
        # Obtener datos del usuario prueba2
        print(f"\n👤 DATOS DEL USUARIO 'prueba2'")
        print("-" * 30)
        
        cursor.execute("SELECT * FROM users WHERE username = 'prueba2'")
        user_data = cursor.fetchone()
        
        if not user_data:
            print("❌ Usuario 'prueba2' no encontrado")
        else:
            print(f"Datos encontrados ({len(user_data)} campos):")
            for i, value in enumerate(user_data):
                col_name = columns[i][1] if i < len(columns) else f"campo_{i}"
                print(f"  {i}: {col_name} = {value}")
            
            # Extraer los datos importantes
            user_id = user_data[0]
            username = user_data[1] 
            password_hash = user_data[2]
            
            print(f"\n🔐 ANÁLISIS DEL HASH")
            print(f"Usuario: {username}")
            print(f"Tipo: {'Argon2' if password_hash.startswith('$argon2') else 'SHA-256'}")
            print(f"Hash: {password_hash[:60]}...")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_user_structure()