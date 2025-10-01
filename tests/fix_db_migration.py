
# Conectar a la base de datos

import os

import sqlite3
db_path = os.path.expanduser('~/OneDrive/homologador.db')
conn = sqlite3.connect(db_path)

try:
    # Agregar columna department si no existe
    try:
        conn.execute("ALTER TABLE users ADD COLUMN department VARCHAR(100) DEFAULT ''")
        print('✅ Columna department agregada')
    except sqlite3.OperationalError as e:
        if 'duplicate column name' in str(e).lower():
            print('ℹ️ Columna department ya existe')
        else:
            print(f'❌ Error agregando department: {e}')
    
    # Verificar estructura actual
    cursor = conn.execute('PRAGMA table_info(users)')
    columns = cursor.fetchall()
    print('\n📋 Estructura de tabla users:')
    for col in columns:
        print(f'  - {col[1]} ({col[2]})')
    
    conn.commit()
    print('\n✅ Migración completada')
    
except Exception as e:
    print(f'❌ Error durante migración: {e}')
finally:
    conn.close()