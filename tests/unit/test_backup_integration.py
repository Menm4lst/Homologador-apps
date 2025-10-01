#!/usr/bin/env python3
"""
Script de prueba para verificar la integración del sistema de respaldos.
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))



from homologador.core.backup_system import get_backup_manager
from homologador.core.settings import get_settings
def test_backup_system():
    """Prueba básica del sistema de respaldos."""
    print("=== Prueba del Sistema de Respaldos ===")
    
    try:
        # Probar configuración
        settings = get_settings()
        print(f"✅ Configuración cargada")
        print(f"   - Directorio de respaldos: {settings.get_backups_dir()}")
        print(f"   - Respaldos automáticos: {settings.is_auto_backup_enabled()}")
        print(f"   - Días de retención: {settings.get_backup_retention_days()}")
        
        # Probar backup manager
        backup_manager = get_backup_manager()
        print(f"✅ BackupManager inicializado")
        print(f"   - Directorio: {backup_manager.backup_dir}")
        print(f"   - Respaldos automáticos: {backup_manager.auto_backup_enabled}")
        print(f"   - Máximo respaldos: {backup_manager.max_backups}")
        
        # Listar respaldos existentes
        backups = backup_manager.list_backups()
        print(f"✅ Respaldos existentes: {len(backups)}")
        
        for backup in backups[:3]:  # Mostrar solo los primeros 3
            print(f"   - {backup.filename} ({backup.size_mb:.2f} MB) - {backup.timestamp}")
        
        print("\n🎉 ¡Sistema de respaldos funcionando correctamente!")
        return True
        
    except Exception as e:
        print(f"❌ Error en prueba de respaldos: {e}")
        return False

if __name__ == "__main__":
    success = test_backup_system()
    sys.exit(0 if success else 1)