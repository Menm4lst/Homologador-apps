#!/usr/bin/env python3
"""
Script para corregir imports en secciones __main__ de archivos del proyecto.
"""

import os
import re
from pathlib import Path

def fix_main_imports():
    """Corrige imports directos en secciones __main__ para usar imports relativos."""
    
    project_root = Path("homologador")
    
    # Patrones de imports a corregir
    patterns = [
        (r'from core\.(\w+)', r'from ..core.\1'),
        (r'from data\.(\w+)', r'from ..data.\1'),
        (r'from ui\.(\w+)', r'from ..ui.\1'),
        (r'from \.core\.(\w+)', r'from ..core.\1'),
        (r'from \.data\.(\w+)', r'from ..data.\1'),
        (r'from \.ui\.(\w+)', r'from ..ui.\1'),
    ]
    
    files_fixed = 0
    
    for file_path in project_root.rglob("*.py"):
        if file_path.name == "__main__.py":
            continue  # Skip el archivo principal
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            in_main = False
            lines = content.splitlines()
            modified = False
            
            for i, line in enumerate(lines):
                # Detectar si estamos en una sección __main__
                if 'if __name__ == "__main__":' in line:
                    in_main = True
                    continue
                    
                # Solo procesar imports en sección __main__
                if in_main and line.strip().startswith('from '):
                    for pattern, replacement in patterns:
                        new_line = re.sub(pattern, replacement, line)
                        if new_line != line:
                            lines[i] = new_line
                            modified = True
                            print(f"  Corrigiendo: {line.strip()} -> {new_line.strip()}")
            
            if modified:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(lines) + '\n')
                print(f"✓ Corregido: {file_path}")
                files_fixed += 1
                
        except Exception as e:
            print(f"✗ Error procesando {file_path}: {e}")
    
    print(f"\n✓ Completado: {files_fixed} archivos corregidos")

if __name__ == "__main__":
    print("Corrigiendo imports en secciones __main__...")
    fix_main_imports()