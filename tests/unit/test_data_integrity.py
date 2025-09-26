#!/usr/bin/env python3
"""
Script de prueba para verificar la funcionalidad de integridad de datos.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from homologador.core.storage import get_database_manager

def test_data_integrity():
    """Prueba la verificación de integridad de datos."""
    print("=== Prueba de Verificación de Integridad de Datos ===")
    
    try:
        # Obtener el gestor de base de datos
        db_manager = get_database_manager()
        
        # Realizar verificaciones básicas
        issues = []
        total_records = 0
        
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            
            # Verificar tabla principal de homologaciones
            cursor.execute("SELECT COUNT(*) FROM homologations")
            total_records = cursor.fetchone()[0]
            print(f"✅ Total de registros: {total_records}")
            
            # Verificar registros con datos faltantes críticos
            cursor.execute("""
                SELECT COUNT(*) FROM homologations 
                WHERE real_name IS NULL OR real_name = '' 
                OR logical_name IS NULL OR logical_name = ''
            """)
            missing_critical = cursor.fetchone()[0]
            
            if missing_critical > 0:
                issues.append(f"• {missing_critical} registros con datos críticos faltantes")
                print(f"⚠️ Datos críticos faltantes: {missing_critical}")
            else:
                print("✅ No hay datos críticos faltantes")
            
            # Verificar registros sin fecha de homologación
            cursor.execute("""
                SELECT COUNT(*) FROM homologations 
                WHERE homologation_date IS NULL
            """)
            missing_dates = cursor.fetchone()[0]
            
            if missing_dates > 0:
                issues.append(f"• {missing_dates} registros sin fecha de homologación")
                print(f"⚠️ Fechas de homologación faltantes: {missing_dates}")
            else:
                print("✅ Todas las fechas de homologación están presentes")
            
            # Verificar duplicados potenciales
            cursor.execute("""
                SELECT real_name, COUNT(*) as count 
                FROM homologations 
                GROUP BY real_name 
                HAVING count > 1
            """)
            duplicates = cursor.fetchall()
            
            if duplicates:
                issues.append(f"• {len(duplicates)} posibles aplicaciones duplicadas")
                print(f"⚠️ Aplicaciones duplicadas: {len(duplicates)}")
                for dup in duplicates[:3]:  # Mostrar solo las primeras 3
                    print(f"   - {dup[0]} ({dup[1]} veces)")
            else:
                print("✅ No hay aplicaciones duplicadas")
            
            # Verificar usuarios
            cursor.execute("SELECT COUNT(*) FROM users WHERE is_active = 1")
            active_users = cursor.fetchone()[0]
            print(f"✅ Usuarios activos: {active_users}")
            
            cursor.execute("SELECT COUNT(*) FROM users WHERE is_active = 0")
            inactive_users = cursor.fetchone()[0]
            if inactive_users > 0:
                print(f"ℹ️ Usuarios inactivos: {inactive_users}")
        
        # Mostrar resultados
        print("\n=== Resumen de Verificación ===")
        if not issues:
            print(f"🎉 ¡Verificación completada exitosamente!")
            print(f"   Total de registros verificados: {total_records}")
            print(f"   No se encontraron problemas de integridad.")
        else:
            print(f"⚠️ Se encontraron {len(issues)} problema(s):")
            for issue in issues:
                print(f"   {issue}")
                
        return True
        
    except Exception as e:
        print(f"❌ Error en verificación: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_data_integrity()
    sys.exit(0 if success else 1)