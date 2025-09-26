#!/usr/bin/env python3
"""
Script para actualizar todas las llamadas del sistema de notificaciones obsoleto
al nuevo sistema unificado.
"""

import re
import os
from pathlib import Path

def update_notification_calls():
    """Actualiza todas las llamadas de notificaciones."""
    
    project_path = Path(r"c:\Users\Antware\OneDrive\Desktop\PROYECTOS DEV\APP HOMOLOGACIONES\homologador")
    
    # Archivos a actualizar
    files_to_update = [
        project_path / "ui" / "main_window.py",
        project_path / "ui" / "homologation_form_fix.py", 
        project_path / "ui" / "advanced_filters.py",
        project_path / "ui" / "export_dialog.py"
    ]
    
    print("🔧 Actualizando sistema de notificaciones...")
    
    for file_path in files_to_update:
        if file_path.exists():
            print(f"\n📝 Procesando: {file_path.name}")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Patrón para encontrar llamadas a las funciones antiguas
            patterns = [
                # show_success(self, "mensaje") -> send_success("Título", "mensaje", "source")
                (r'show_success\(self,\s*"([^"]+)"\)', r'send_success("Operación Exitosa", "\1", "main_window")'),
                (r"show_success\(self,\s*'([^']+)'\)", r"send_success('Operación Exitosa', '\1', 'main_window')"),
                
                # show_error(self, "mensaje") -> send_error("Título", "mensaje", "source")  
                (r'show_error\(self,\s*"([^"]+)"\)', r'send_error("Error", "\1", "main_window")'),
                (r"show_error\(self,\s*'([^']+)'\)", r"send_error('Error', '\1', 'main_window')"),
                
                # show_warning(self, "mensaje") -> send_warning("Título", "mensaje", "source")
                (r'show_warning\(self,\s*"([^"]+)"\)', r'send_warning("Advertencia", "\1", "main_window")'),  
                (r"show_warning\(self,\s*'([^']+)'\)", r"send_warning('Advertencia', '\1', 'main_window')"),
                
                # show_info(self, "mensaje") -> send_info("Título", "mensaje", "source")
                (r'show_info\(self,\s*"([^"]+)"\)', r'send_info("Información", "\1", "main_window")'),
                (r"show_info\(self,\s*'([^']+)'\)", r"send_info('Información', '\1', 'main_window')"),
            ]
            
            # Aplicar patrones
            updated_content = content
            changes = 0
            
            for old_pattern, new_pattern in patterns:
                matches = re.findall(old_pattern, updated_content)
                if matches:
                    updated_content = re.sub(old_pattern, new_pattern, updated_content)
                    changes += len(matches)
                    
            if changes > 0:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(updated_content)
                print(f"  ✅ {changes} llamadas actualizadas")
            else:
                print(f"  ℹ️ No necesita cambios")
    
    print("\n🎉 Actualización completada!")

if __name__ == "__main__":
    update_notification_calls()