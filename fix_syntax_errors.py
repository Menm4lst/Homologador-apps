#!/usr/bin/env python3
# type: ignore
"""
Script para corregir errores de sintaxis en imports causados por el optimizador.
"""

import re
import logging
from pathlib import Path

def fix_multiline_imports(file_path: Path) -> bool:
    """Corrige imports multilinea mal formateados."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Patrón para detectar imports multilinea rotos
    pattern = r'from PyQt6\.QtWidgets import \([^)]*\n\nfrom \.\.[^)]*\n([^)]*\))'
    
    def fix_import_block(match):
        full_match = match.group(0)
        # Separar el import de PyQt6 del import local
        lines = full_match.split('\n')
        
        qt_import_lines = []
        local_import_lines = []
        in_qt_import = True
        
        for line in lines:
            if line.strip().startswith('from ..'):
                in_qt_import = False
                local_import_lines.append(line)
            elif in_qt_import:
                qt_import_lines.append(line)
            else:
                # Esto es parte del import de PyQt6 que se mezcló
                if line.strip() and not line.strip().startswith('from'):
                    qt_import_lines.append('                             ' + line.strip())
        
        # Reconstruir los imports correctamente
        qt_import = '\n'.join(qt_import_lines)
        if not qt_import.strip().endswith(')'):
            qt_import += ')'
            
        local_import = '\n'.join(local_import_lines)
        
        return qt_import + '\n\n' + local_import
    
    # Aplicar la corrección
    content = re.sub(pattern, fix_import_block, content, flags=re.MULTILINE | re.DOTALL)
    
    # Patrón más específico para casos como details_view.py
    pattern2 = r'(from PyQt6\.QtWidgets import \([^)]*),\n\nfrom (\.\.[^)]*)\n([^)]*\))'
    
    def fix_specific_case(match):
        qt_part = match.group(1)
        local_import = f"from {match.group(2)}"
        remaining_qt = match.group(3)
        
        return f"{qt_part},\n{remaining_qt}\n\n{local_import}"
    
    content = re.sub(pattern2, fix_specific_case, content)
    
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    
    return False

def fix_all_syntax_errors():
    """Corrige errores de sintaxis en todos los archivos Python."""
    project_root = Path(__file__).parent / "homologador"
    fixed_files = []
    
    for py_file in project_root.rglob("*.py"):
        try:
            if fix_multiline_imports(py_file):
                fixed_files.append(py_file.name)
                print(f"✅ Corregido: {py_file.name}")
        except Exception as e:
            print(f"❌ Error en {py_file.name}: {e}")
    
    return fixed_files

if __name__ == "__main__":
    print("🔧 Corrigiendo errores de sintaxis en imports...")
    fixed = fix_all_syntax_errors()
    print(f"\n✅ Corregidos {len(fixed)} archivos: {', '.join(fixed)}")  # type: ignore[arg-type]