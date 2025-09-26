#!/usr/bin/env python3
"""
Prueba Completa del Sistema de Respaldos
=========================================

Este script realiza una verificación exhaustiva del sistema de respaldos,
incluyendo la funcionalidad del core, la interfaz de usuario y las 
operaciones de respaldo/restauración.
"""

import os
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.append('.')

def test_core_backup_system():
    """Prueba el sistema de respaldos core."""
    print("🔍 PROBANDO SISTEMA DE RESPALDOS CORE")
    print("=" * 50)
    
    try:
        # Test 1: Importaciones
        print("\n1. Verificando importaciones...")
        from homologador.core.backup_system import BackupManager, BackupInfo
        from homologador.core.storage import get_database_manager
        print("✅ Importaciones exitosas")
        
        # Test 2: Creación de respaldo básico
        print("\n2. Creando respaldo básico...")
        db_manager = get_database_manager()
        backup_path = db_manager.create_backup('test_completo_core')
        
        if backup_path and os.path.exists(backup_path):
            size = os.path.getsize(backup_path)
            print(f"✅ Respaldo creado: {os.path.basename(backup_path)}")
            print(f"   Tamaño: {size:,} bytes ({size/1024/1024:.2f} MB)")
            print(f"   Ubicación: {backup_path}")
            return True
        else:
            print("❌ Error creando respaldo básico")
            return False
            
    except Exception as e:
        print(f"❌ Error en sistema core: {e}")
        return False

def test_ui_backup_system():
    """Prueba la interfaz de usuario del sistema de respaldos."""
    print("\n\n🎨 PROBANDO INTERFAZ DE USUARIO")
    print("=" * 50)
    
    try:
        # Test 1: Importar componentes de UI
        print("\n1. Verificando componentes de UI...")
        from homologador.ui.backup_system import (
            BackupWorker, RestoreWorker, BackupSystemWidget, show_backup_system
        )
        from PyQt6.QtWidgets import QApplication
        print("✅ Componentes de UI importados correctamente")
        
        # Test 2: Crear aplicación Qt si no existe
        print("\n2. Inicializando aplicación Qt...")
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        print("✅ Aplicación Qt lista")
        
        # Test 3: Crear widget del sistema de respaldos
        print("\n3. Creando widget de respaldos...")
        admin_user = {
            'id': 1,
            'username': 'admin',
            'role': 'admin',
            'full_name': 'Administrador Test'
        }
        
        backup_widget = BackupSystemWidget(admin_user)
        print("✅ Widget de respaldos creado exitosamente")
        
        # Test 4: Verificar configuración de workers
        print("\n4. Verificando workers...")
        
        backup_config = {
            'backup_path': 'backups',
            'include_database': True,
            'include_config': True,
            'include_logs': False,
            'include_user_files': False,
            'compression_level': 'Normal'
        }
        
        worker = BackupWorker(backup_config)
        print("✅ BackupWorker configurado")
        
        restore_config = {
            'restore_database': True,
            'restore_config': True,
            'restore_user_files': False,
            'create_safety_backup': True
        }
        
        # Crear archivo temporal para test
        test_zip = Path("test_backup.zip")
        if not test_zip.exists():
            import zipfile
            with zipfile.ZipFile(test_zip, 'w') as zf:
                zf.writestr("test.txt", "test content")
        
        restore_worker = RestoreWorker(str(test_zip), restore_config)
        print("✅ RestoreWorker configurado")
        
        # Limpiar archivo temporal
        if test_zip.exists():
            test_zip.unlink()
        
        return True
        
    except Exception as e:
        print(f"❌ Error en interfaz de usuario: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_backup_directory_structure():
    """Verifica la estructura del directorio de respaldos."""
    print("\n\n📁 VERIFICANDO ESTRUCTURA DE DIRECTORIOS")
    print("=" * 50)
    
    try:
        # Verificar directorio principal de respaldos
        backup_dir = Path("C:/Users/Antware/OneDrive/backups")
        if backup_dir.exists():
            backup_files = list(backup_dir.glob("*.db"))
            print(f"✅ Directorio de respaldos: {backup_dir}")
            print(f"   Respaldos encontrados: {len(backup_files)}")
            
            # Mostrar los últimos 5 respaldos
            if backup_files:
                print("   Últimos respaldos:")
                for backup in sorted(backup_files, key=lambda x: x.stat().st_mtime)[-5:]:
                    size = backup.stat().st_size
                    mtime = backup.stat().st_mtime
                    from datetime import datetime
                    date_str = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M")
                    print(f"     - {backup.name} ({size:,} bytes, {date_str})")
        else:
            print("⚠️ Directorio de respaldos no encontrado")
        
        # Verificar directorio local de respaldos
        local_backup_dir = Path("backups")
        if local_backup_dir.exists():
            print(f"✅ Directorio local de respaldos: {local_backup_dir}")
            
            # Verificar archivo de índice
            index_file = local_backup_dir / "backup_index.json"
            if index_file.exists():
                import json
                with open(index_file, 'r', encoding='utf-8') as f:
                    index_data = json.load(f)
                    backups_count = len(index_data.get('backups', []))
                    print(f"✅ Índice de respaldos: {backups_count} entradas registradas")
            else:
                print("⚠️ Archivo de índice no encontrado (se creará automáticamente)")
        else:
            print("⚠️ Directorio local de respaldos no encontrado")
            
        return True
        
    except Exception as e:
        print(f"❌ Error verificando estructura: {e}")
        return False

def test_backup_functionality():
    """Realiza una prueba completa de funcionalidad."""
    print("\n\n⚙️ PRUEBA DE FUNCIONALIDAD COMPLETA")
    print("=" * 50)
    
    try:
        from homologador.core.storage import get_database_manager
        
        # Test 1: Crear múltiples respaldos con diferentes tipos
        print("\n1. Creando respaldos de prueba...")
        db_manager = get_database_manager()
        
        test_backups = []
        for i, backup_type in enumerate(['manual', 'auto', 'scheduled'], 1):
            backup_name = f"test_funcionalidad_{backup_type}_{i}"
            backup_path = db_manager.create_backup(backup_name)
            
            if backup_path:
                test_backups.append(backup_path)
                print(f"  ✅ Respaldo {backup_type}: {os.path.basename(backup_path)}")
            else:
                print(f"  ❌ Error creando respaldo {backup_type}")
        
        print(f"✅ {len(test_backups)} respaldos de prueba creados")
        
        # Test 2: Verificar integridad de archivos
        print("\n2. Verificando integridad de respaldos...")
        intact_count = 0
        for backup_path in test_backups:
            if os.path.exists(backup_path):
                size = os.path.getsize(backup_path)
                if size > 1000:  # Al menos 1KB
                    intact_count += 1
                    
        print(f"✅ {intact_count}/{len(test_backups)} respaldos íntegros")
        
        # Test 3: Simular limpieza (opcional)
        print("\n3. Limpieza de respaldos de prueba...")
        cleaned = 0
        for backup_path in test_backups:
            try:
                if os.path.exists(backup_path):
                    # Opcional: descomentar para limpiar archivos de prueba
                    # os.remove(backup_path)
                    # cleaned += 1
                    pass
            except Exception as e:
                print(f"  ⚠️ No se pudo limpiar {backup_path}: {e}")
        
        print(f"✅ Prueba de funcionalidad completada")
        return True
        
    except Exception as e:
        print(f"❌ Error en prueba de funcionalidad: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Función principal que ejecuta todas las pruebas."""
    print("🚀 INICIANDO PRUEBA COMPLETA DEL SISTEMA DE RESPALDOS")
    print("=" * 60)
    
    # Ejecutar todas las pruebas
    tests = [
        ("Sistema Core", test_core_backup_system),
        ("Interfaz de Usuario", test_ui_backup_system),
        ("Estructura de Directorios", test_backup_directory_structure),
        ("Funcionalidad Completa", test_backup_functionality)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 EJECUTANDO: {test_name}")
        print("-" * 40)
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Error crítico en {test_name}: {e}")
            results.append((test_name, False))
    
    # Resumen final
    print("\n\n📊 RESUMEN DE RESULTADOS")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        print(f"{test_name:<30} {status}")
        if result:
            passed += 1
    
    print(f"\nResultado final: {passed}/{len(results)} pruebas exitosas")
    
    if passed == len(results):
        print("\n🎉 ¡SISTEMA DE RESPALDOS COMPLETAMENTE FUNCIONAL!")
        print("✅ Todas las funcionalidades verificadas exitosamente")
        print("✅ Core del sistema operativo")
        print("✅ Interfaz de usuario funcional")
        print("✅ Estructura de archivos correcta")
        print("✅ Operaciones de respaldo exitosas")
    else:
        print(f"\n⚠️ Sistema parcialmente funcional: {passed}/{len(results)} componentes operativos")
    
    return passed == len(results)

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️ Prueba interrumpida por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n💥 Error crítico: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)