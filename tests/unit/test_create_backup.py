#!/usr/bin/env python3
"""
Script para crear un respaldo de prueba.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from homologador.core.backup_system import get_backup_manager

def create_test_backup():
    """Crea un respaldo de prueba."""
    print("=== Creando Respaldo de Prueba ===")
    
    try:
        backup_manager = get_backup_manager()
        
        print("📦 Iniciando creación de respaldo...")
        backup_info = backup_manager.create_backup("Respaldo de prueba - Integración completa")
        
        if backup_info:
            print("✅ ¡Respaldo creado exitosamente!")
            print(f"   📁 Archivo: {backup_info.filename}")
            print(f"   📏 Tamaño: {backup_info.size_mb:.2f} MB")
            print(f"   📅 Fecha: {backup_info.timestamp}")
            print(f"   📍 Ubicación: {backup_manager.backup_dir}")
            
            # Verificar que el archivo existe
            backup_path = backup_manager.backup_dir / backup_info.filename
            if backup_path.exists():
                print("✅ ¡Archivo de respaldo verificado!")
            else:
                print("❌ Error: archivo de respaldo no encontrado")
                return False
                
        else:
            print("❌ Error creando respaldo")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = create_test_backup()
    sys.exit(0 if success else 1)