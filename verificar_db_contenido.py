#!/usr/bin/env python3
"""
Script para verificar qué datos hay realmente en la base de datos.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_database_content():
    """Verifica el contenido real de la base de datos."""
    print("🔍 VERIFICANDO CONTENIDO REAL DE LA BASE DE DATOS")
    print("=" * 60)
    
    try:
        from homologador.core.storage import get_database_manager
        
        db_manager = get_database_manager()
        
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            
            # Verificar homologaciones
            print("📋 HOMOLOGACIONES:")
            cursor.execute("SELECT COUNT(*) FROM homologations")
            total_homologations = cursor.fetchone()[0]
            print(f"   Total: {total_homologations}")
            
            if total_homologations > 0:
                print("\n   Primeras 5 homologaciones:")
                cursor.execute("""
                    SELECT id, real_name, logical_name, homologation_date 
                    FROM homologations 
                    ORDER BY id 
                    LIMIT 5
                """)
                for row in cursor.fetchall():
                    print(f"   - ID: {row[0]}, Real: {row[1]}, Lógico: {row[2]}, Fecha: {row[3]}")
            
            # Verificar usuarios
            print(f"\n👥 USUARIOS:")
            cursor.execute("SELECT COUNT(*) FROM users")
            total_users = cursor.fetchone()[0]
            print(f"   Total: {total_users}")
            
            cursor.execute("SELECT username, role, is_active FROM users")
            for row in cursor.fetchall():
                status = "✅ Activo" if row[2] else "❌ Inactivo"
                print(f"   - {row[0]} ({row[1]}) - {status}")
            
            # Verificar auditoría
            print(f"\n📊 AUDITORÍA:")
            cursor.execute("SELECT COUNT(*) FROM audit_logs")
            total_audit = cursor.fetchone()[0]
            print(f"   Total logs: {total_audit}")
            
            if total_audit > 0:
                cursor.execute("""
                    SELECT action, created_at 
                    FROM audit_logs 
                    ORDER BY created_at DESC 
                    LIMIT 3
                """)
                print("   Últimas 3 acciones:")
                for row in cursor.fetchall():
                    print(f"   - {row[0]} - {row[1]}")
            
            # Verificar estructura de tabla de homologaciones
            print(f"\n🏗️ ESTRUCTURA DE TABLA HOMOLOGATIONS:")
            cursor.execute("PRAGMA table_info(homologations)")
            columns = cursor.fetchall()
            for col in columns:
                print(f"   - {col[1]} ({col[2]})")
            
        print(f"\n✅ Verificación completada")
        return total_homologations
        
    except Exception as e:
        print(f"❌ Error verificando base de datos: {e}")
        import traceback
        traceback.print_exc()
        return 0

def main():
    """Función principal."""
    total_homologations = check_database_content()
    
    print(f"\n🎯 CONCLUSIÓN:")
    if total_homologations == 0:
        print("   ✅ No hay homologaciones en la base de datos")
        print("   🔧 El dashboard debería mostrar 0, no 45")
        print("   💡 Necesitamos arreglar el código hardcodeado")
    else:
        print(f"   📊 Hay {total_homologations} homologaciones reales")
        print("   ✅ El dashboard debería mostrar este número")

if __name__ == "__main__":
    main()