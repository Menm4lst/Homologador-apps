#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de prueba para validar las funcionalidades principales
de la aplicación Homologador de Aplicaciones.
"""

import os
import sys
from datetime import datetime

# Agregar el directorio actual al path para importar módulos
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import argon2
    from core.settings import Settings
    from core.storage import DatabaseManager
    from data.seed import create_seed_data
    print("✅ Todas las importaciones exitosas")
except ImportError as e:
    print(f"❌ Error de importación: {e}")
    sys.exit(1)

def test_configuracion():
    """Probar la configuración del sistema"""
    print("\n=== Probando Configuración ===")
    try:
        settings = Settings()
        print(f"✅ Base de datos: {settings.database_path}")
        print(f"✅ Directorio de backups: {settings.backup_dir}")
        print(f"✅ OneDrive detectado: {settings.onedrive_path}")
        return True
    except Exception as e:
        print(f"❌ Error en configuración: {e}")
        return False

def test_base_datos():
    """Probar conexión y operaciones de base de datos"""
    print("\n=== Probando Base de Datos ===")
    try:
        settings = Settings()
        db_manager = DatabaseManager()
        
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            
            # Verificar tablas
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            expected_tables = ['users', 'homologations', 'audit_logs']
            
            for table in expected_tables:
                if table in tables:
                    print(f"✅ Tabla '{table}' existe")
                else:
                    print(f"❌ Tabla '{table}' no encontrada")
                    return False
            
            # Verificar usuario admin
            cursor.execute("SELECT username, role FROM users WHERE id = 1")
            user = cursor.fetchone()
            if user and user[0] == 'admin':
                print(f"✅ Usuario admin encontrado con rol: {user[1]}")
            else:
                print("❌ Usuario admin no encontrado")
                return False
                
        return True
    except Exception as e:
        print(f"❌ Error en base de datos: {e}")
        return False

def test_autenticacion():
    """Probar el sistema de autenticación"""
    print("\n=== Probando Autenticación ===")
    try:
        settings = Settings()
        db_manager = DatabaseManager()
        user_repo = db_manager.get_user_repository()
        
        # Verificar autenticación del admin
        user = user_repo.authenticate_user('admin', 'admin123')
        if user:
            print(f"✅ Autenticación exitosa para usuario: {user['username']}")
            print(f"✅ Rol del usuario: {user['role']}")
            return True
        else:
            print("❌ Fallo en autenticación")
            return False
    except Exception as e:
        print(f"❌ Error en autenticación: {e}")
        return False

def test_homologaciones():
    """Probar operaciones CRUD de homologaciones"""
    print("\n=== Probando Homologaciones ===")
    try:
        settings = Settings()
        db_manager = DatabaseManager()
        homol_repo = db_manager.get_homologation_repository()
        
        # Crear una homologación de prueba
        test_data = {
            'aplicacion': 'App de Prueba',
            'version': '1.0.0',
            'fabricante': 'Test Corp',
            'tipo_instalacion': 'Standalone',
            'sistema_operativo': 'Windows 10',
            'arquitectura': 'x64',
            'fecha_homologacion': datetime.now().date(),
            'resultado': 'Aprobado',
            'observaciones': 'Prueba automática del sistema',
            'responsable_pruebas': 'Sistema',
            'area_solicitante': 'TI'
        }
        
        homol_id = homol_repo.create_homologation(test_data, user_id=1)
        if homol_id:
            print(f"✅ Homologación creada con ID: {homol_id}")
            
            # Leer la homologación
            homologation = homol_repo.get_homologation(homol_id)
            if homologation:
                print(f"✅ Homologación leída: {homologation['aplicacion']}")
                
                # Actualizar la homologación
                test_data['version'] = '1.0.1'
                test_data['observaciones'] = 'Actualizada por prueba automática'
                success = homol_repo.update_homologation(homol_id, test_data, user_id=1)
                if success:
                    print("✅ Homologación actualizada exitosamente")
                    return True
                else:
                    print("❌ Error al actualizar homologación")
                    return False
            else:
                print("❌ Error al leer homologación")
                return False
        else:
            print("❌ Error al crear homologación")
            return False
    except Exception as e:
        print(f"❌ Error en homologaciones: {e}")
        return False

def test_auditoria():
    """Probar el sistema de auditoría"""
    print("\n=== Probando Auditoría ===")
    try:
        settings = Settings()
        db_manager = DatabaseManager()
        audit_repo = db_manager.get_audit_repository()
        
        # Obtener registros de auditoría
        audit_logs = audit_repo.get_audit_logs(limit=5)
        if audit_logs:
            print(f"✅ Se encontraron {len(audit_logs)} registros de auditoría")
            for log in audit_logs:
                print(f"   - {log['timestamp']}: {log['action']} por usuario {log['user_id']}")
            return True
        else:
            print("⚠️  No se encontraron registros de auditoría (esto puede ser normal)")
            return True
    except Exception as e:
        print(f"❌ Error en auditoría: {e}")
        return False

def main():
    """Ejecutar todas las pruebas"""
    print("🔍 INICIANDO PRUEBAS DE FUNCIONALIDADES")
    print("=" * 50)
    
    tests = [
        ("Configuración", test_configuracion),
        ("Base de Datos", test_base_datos),
        ("Autenticación", test_autenticacion),
        ("Homologaciones", test_homologaciones),
        ("Auditoría", test_auditoria)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ Error inesperado en {name}: {e}")
            results.append((name, False))
    
    # Resumen final
    print("\n" + "=" * 50)
    print("📊 RESUMEN DE PRUEBAS")
    print("=" * 50)
    
    passed = 0
    for name, result in results:
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        print(f"{name:15} : {status}")
        if result:
            passed += 1
    
    print(f"\nResultado: {passed}/{len(results)} pruebas exitosas")
    
    if passed == len(results):
        print("🎉 ¡Todas las pruebas pasaron! La aplicación está funcionando correctamente.")
    else:
        print("⚠️  Algunas pruebas fallaron. Revise los errores anteriores.")
        
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)