#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de prueba simple para validar que la aplicación funciona correctamente.
"""


# Agregar el directorio actual al path para importar módulos

from datetime import datetime
from typing import Any, Dict
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_simple():
    """Prueba básica de funcionalidades"""
    print("🔍 PROBANDO FUNCIONALIDADES BÁSICAS")
    print("=" * 50)
    
    # Test 1: Importaciones
    print("\n1. Probando importaciones...")
    try:
        from core.settings import Settings, get_settings
        from core.storage import DatabaseManager
        print("✅ Importaciones exitosas")
    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        return False
    
    # Test 2: Configuración
    print("\n2. Probando configuración...")
    try:
        settings = get_settings()
        db_path = settings.get_db_path()
        backups_dir = settings.get_backups_dir()
        print(f"✅ DB Path: {db_path}")
        print(f"✅ Backups Dir: {backups_dir}")
    except Exception as e:
        print(f"❌ Error en configuración: {e}")
        return False
    
    # Test 3: Base de datos
    print("\n3. Probando base de datos...")
    try:
        db_manager = DatabaseManager()
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            print(f"✅ Tablas encontradas: {', '.join(tables)}")
            
            # Verificar usuario admin
            cursor.execute("SELECT username, role FROM users WHERE username = 'admin'")
            admin_user = cursor.fetchone()
            if admin_user:
                print(f"✅ Usuario admin encontrado con rol: {admin_user[1]}")
            else:
                print("❌ Usuario admin no encontrado")
                return False
                
    except Exception as e:
        print(f"❌ Error en base de datos: {e}")
        return False
    
    # Test 4: Autenticación
    print("\n4. Probando autenticación...")
    try:
        from data.seed import get_auth_service
        auth_service = get_auth_service()
        user = auth_service.authenticate('admin', 'admin123')
        if user:
            print(f"✅ Autenticación exitosa para: {user['username']}")
        else:
            print("❌ Fallo en autenticación")
            return False
    except Exception as e:
        print(f"❌ Error en autenticación: {e}")
        return False
    
    # Test 5: CRUD básico
    print("\n5. Probando operaciones CRUD...")
    try:
        from core.storage import get_homologation_repository
        homol_repo = get_homologation_repository()
        
        # Contar registros existentes
        homologations = homol_repo.get_all()
        initial_count = len(homologations)
        print(f"✅ Registros existentes: {initial_count}")
        
        # Crear un registro de prueba
        test_data: Dict[str, Any] = {
            'real_name': 'Test App Validation',
            'logical_name': 'test-app-validation',
            'kb_url': 'https://example.com/kb/test-app',
            'homologation_date': datetime.now().date(),
            'has_previous_versions': False,
            'repository_location': 'APPS$',
            'details': 'Registro de prueba automática del sistema',
            'created_by': 1  # Usuario admin
        }
        
        new_id = homol_repo.create(test_data)
        if new_id:
            print(f"✅ Registro creado con ID: {new_id}")
            
            # Verificar que se creó
            new_homol = homol_repo.get_by_id(new_id)
            if new_homol and new_homol['real_name'] == test_data['real_name']:
                print("✅ Registro verificado correctamente")
            else:
                print("❌ Error al verificar registro creado")
                return False
        else:
            print("❌ Error al crear registro")
            return False
            
    except Exception as e:
        print(f"❌ Error en CRUD: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 ¡TODAS LAS PRUEBAS PASARON!")
    print("La aplicación está funcionando correctamente.")
    print("=" * 50)
    
    return True

if __name__ == "__main__":
    success = test_simple()
    if success:
        print("\n✅ Resultado: ÉXITO - La aplicación está lista para usar")
        print("\nPara ejecutar la aplicación completa:")
        print("python app.py")
        print("\nCredenciales iniciales:")
        print("Usuario: admin")
        print("Contraseña: admin123")
    else:
        print("\n❌ Resultado: FALLA - Revisar errores anteriores")
    
    sys.exit(0 if success else 1)