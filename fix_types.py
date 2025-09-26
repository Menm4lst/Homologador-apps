#!/usr/bin/env python3
"""
Script de corrección de tipos para Homologador
Corrige los problemas de tipado más críticos identificados
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Any

def fix_storage_types():
    """Corrige tipos en storage.py"""
    storage_path = Path("homologador/core/storage.py")
    
    if not storage_path.exists():
        print(f"❌ No se encontró {storage_path}")
        return False
    
    # Leer contenido actual
    with open(storage_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Correcciones específicas de tipos
    fixes = [
        # Corregir argumentos de conexión
        ('def _apply_smart_migration(self, conn, filename: str, migration_sql: str) -> bool:',
         'def _apply_smart_migration(self, conn: sqlite3.Connection, filename: str, migration_sql: str) -> bool:'),
        
        ('def _apply_column_migration(self, conn, filename: str, migration_sql: str) -> bool:',
         'def _apply_column_migration(self, conn: sqlite3.Connection, filename: str, migration_sql: str) -> bool:'),
        
        ('def _column_exists(self, conn, table_name: str, column_name: str) -> bool:',
         'def _column_exists(self, conn: sqlite3.Connection, table_name: str, column_name: str) -> bool:'),
        
        # Corregir listas con tipos específicos
        ('where_clauses = []',
         'where_clauses: List[str] = []'),
        
        ('details = []',
         'details: List[str] = []'),
    ]
    
    modified = False
    for old, new in fixes:
        if old in content:
            content = content.replace(old, new)
            modified = True
            print(f"✅ Corregido: {old[:50]}...")
    
    if modified:
        # Verificar imports necesarios
        if 'import sqlite3' not in content:
            # Agregar import al inicio
            lines = content.split('\n')
            import_index = -1
            for i, line in enumerate(lines):
                if line.startswith('import ') or line.startswith('from '):
                    import_index = i
                elif line.startswith('from typing import'):
                    # Agregar sqlite3 a typing si existe
                    if ', cast' in line:
                        lines[i] = line.replace('from typing import', 'import sqlite3\nfrom typing import')
                    break
            
            if import_index >= 0:
                lines.insert(import_index + 1, 'import sqlite3')
                content = '\n'.join(lines)
        
        # Guardar cambios
        with open(storage_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Archivo {storage_path} actualizado")
        return True
    
    print(f"ℹ️ No se requirieron cambios en {storage_path}")
    return True

def fix_homologation_form_types():
    """Corrige tipos en homologation_form.py"""
    form_path = Path("homologador/ui/homologation_form.py")
    
    if not form_path.exists():
        print(f"❌ No se encontró {form_path}")
        return False
    
    with open(form_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Correcciones para Optional types
    fixes = [
        # Corregir constructores con Optional
        ('def __init__(self, homologation_data: Dict[str, Any], homologation_id: int = None):',
         'def __init__(self, homologation_data: Dict[str, Any], homologation_id: Optional[int] = None):'),
        
        ('def __init__(self, parent=None, homologation_data: Dict[str, Any] = None, user_info: Dict[str, Any] = None):',
         'def __init__(self, parent: Optional[QWidget] = None, homologation_data: Optional[Dict[str, Any]] = None, user_info: Optional[Dict[str, Any]] = None):'),
        
        # Corregir listas tipadas
        ('validation_errors = []',
         'validation_errors: List[str] = []'),
    ]
    
    modified = False
    for old, new in fixes:
        if old in content:
            content = content.replace(old, new)
            modified = True
            print(f"✅ Corregido: {old[:50]}...")
    
    if modified:
        with open(form_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Archivo {form_path} actualizado")
    
    return True

def fix_main_window_types():
    """Corrige tipos en main_window.py"""
    window_path = Path("homologador/ui/main_window.py")
    
    if not window_path.exists():
        print(f"❌ No se encontró {window_path}")
        return False
    
    with open(window_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Correcciones específicas
    fixes = [
        # Corregir listas tipadas
        ('issues = []',
         'issues: List[str] = []'),
        
        # Agregar imports necesarios para QPoint
        ('from PyQt6.QtCore import Qt, QTimer, pyqtSignal',
         'from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QPoint'),
    ]
    
    modified = False
    for old, new in fixes:
        if old in content:
            content = content.replace(old, new)
            modified = True
            print(f"✅ Corregido: {old[:50]}...")
    
    if modified:
        with open(window_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Archivo {window_path} actualizado")
    
    return True

def create_type_stubs():
    """Crea stub files para mejorar el tipado"""
    stubs_dir = Path("homologador/py.typed")
    stubs_dir.touch()
    
    # Crear stub para PyQt6 si es necesario
    pyqt_stub = Path("homologador/stubs/PyQt6.pyi")
    if not pyqt_stub.exists():
        pyqt_stub.parent.mkdir(exist_ok=True)
        with open(pyqt_stub, 'w', encoding='utf-8') as f:
            f.write("""# Type stubs for PyQt6
from typing import Any, Optional, Union

class QWidget:
    def __init__(self, parent: Optional['QWidget'] = None) -> None: ...
    def mapToGlobal(self, point: 'QPoint') -> 'QPoint': ...

class QPoint:
    def __init__(self, x: int = 0, y: int = 0) -> None: ...

class QApplication:
    def __init__(self, argv: list[str]) -> None: ...
""")
        print("✅ Created PyQt6 type stubs")
    
    return True

def fix_theme_effects_types():
    """Corrige tipos en theme_effects.py"""
    theme_path = Path("homologador/ui/theme_effects.py")
    
    if not theme_path.exists():
        print(f"❌ No se encontró {theme_path}")
        return False
    
    with open(theme_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Corrección para dict con Optional
    old_func = 'def apply_theme_customizations(app, config: dict = None):'
    new_func = 'def apply_theme_customizations(app: QApplication, config: Optional[Dict[str, Any]] = None):'
    
    if old_func in content:
        content = content.replace(old_func, new_func)
        
        with open(theme_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Archivo {theme_path} actualizado")
    
    return True

def main():
    """Función principal de corrección de tipos"""
    print("🔧 INICIANDO CORRECCIÓN DE TIPOS")
    print("=" * 50)
    
    try:
        # Verificar que estamos en el directorio correcto
        if not Path("homologador").exists():
            print("❌ Error: No se encuentra el directorio 'homologador'")
            print("Ejecute este script desde el directorio raíz del proyecto")
            return False
        
        success_count = 0
        total_fixes = 5
        
        # Ejecutar correcciones
        if fix_storage_types():
            success_count += 1
        
        if fix_homologation_form_types():
            success_count += 1
        
        if fix_main_window_types():
            success_count += 1
        
        if fix_theme_effects_types():
            success_count += 1
        
        if create_type_stubs():
            success_count += 1
        
        print("\n" + "=" * 50)
        print(f"✅ CORRECCIÓN COMPLETADA: {success_count}/{total_fixes}")
        
        if success_count == total_fixes:
            print("🎉 Todas las correcciones aplicadas exitosamente")
            print("\nPróximos pasos:")
            print("1. Ejecutar: mypy homologador/ (para verificar tipos)")
            print("2. Ejecutar: python -m homologador (para probar)")
            return True
        else:
            print(f"⚠️ Solo se completaron {success_count} de {total_fixes} correcciones")
            return False
            
    except Exception as e:
        print(f"❌ Error durante la corrección: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
    
    input("\n✅ Presiona Enter para continuar...")