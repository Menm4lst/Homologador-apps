#!/usr/bin/env python3
"""
Script para verificar la estructura de la base de datos y corregir autenticación
"""

import sqlite3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from homologador.core.auth import verify_password

def check_database_structure():
    """Verifica la estructura de la base de datos"""
    
    # Conectar a la base de datos
    db_path = r"C:\Users\Antware/OneDrive/homologador.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("=== ESTRUCTURA DE BASE DE DATOS ===\n")
        
        # Ver todas las tablas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print("Tablas encontradas:")
        for table in tables:
            print(f"  - {table[0]}")
        
        print("\n" + "="*50 + "\n")
        
        # Verificar estructura de tabla users
        if ('users',) in tables:
            print("ESTRUCTURA DE TABLA 'users':")
            cursor.execute("PRAGMA table_info(users)")
            columns = cursor.fetchall()
            
            for col in columns:
                print(f"  {col[1]} ({col[2]}) - {'NOT NULL' if col[3] else 'NULL'}")
            
            print("\nCONTENIDO DE TABLA 'users':")
            cursor.execute("SELECT * FROM users")
            users = cursor.fetchall()
            
            for user in users:
                print(f"  {user}")
        
        # También verificar otras tablas relacionadas con usuarios
        for table_name in ['usuarios', 'user', 'auth_users']:
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
            if cursor.fetchone():
                print(f"\nESTRUCTURA DE TABLA '{table_name}':")
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()
                
                for col in columns:
                    print(f"  {col[1]} ({col[2]}) - {'NOT NULL' if col[3] else 'NULL'}")
                
                print(f"\nCONTENIDO DE TABLA '{table_name}':")
                cursor.execute(f"SELECT * FROM {table_name}")
                data = cursor.fetchall()
                
                for row in data:
                    print(f"  {row}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_database_structure()