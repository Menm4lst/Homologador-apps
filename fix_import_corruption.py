#!/usr/bin/env python3
# type: ignore
"""
Script para corregir corrupciones de imports causadas por el optimizador.
"""

import os
import re
from pathlib import Path
from typing import List, Tuple

def fix_corrupted_imports(file_path: Path) -> bool:
    """Corrige imports corruptos en un archivo específico."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Patrón para detectar imports mezclados dentro de imports multilinea
        # Ejemplo: from PyQt6.QtWidgets import (Clase1, import sys, Clase2)
        pattern1 = r'from\s+[\w\.]+\s+import\s*\([^)]*?import\s+\w+[^)]*?\)'
        matches = re.findall(pattern1, content, re.DOTALL)
        
        for match in matches:
            print(f"⚠️ Import corrupto detectado en {file_path}:")
            print(f"   {match[:100]}...")
            
            # Extraer imports individuales del bloque corrupto
            fixed_import = fix_multiline_import(match)
            content = content.replace(match, fixed_import)
        
        # Patrón para detectar import statements malformados
        # Ejemplo: QClass, import module, OtherClass
        pattern2 = r'([A-Z]\w+,\s*import\s+\w+,\s*[A-Z]\w+)'
        content = re.sub(pattern2, lambda m: fix_inline_import(m.group(1)), content)
        
        # Patrón para imports con paréntesis no cerrados
        pattern3 = r'from\s+[\w\.]+\s+import\s*\([^)]+$'
        lines = content.split('\n')
        fixed_lines = []
        in_multiline_import = False
        import_buffer = []
        
        for line in lines:
            if re.match(pattern3, line.strip()):
                in_multiline_import = True
                import_buffer = [line]
            elif in_multiline_import:
                import_buffer.append(line)
                if ')' in line:
                    # Fin del import multilinea
                    fixed_import_block = fix_import_block(import_buffer)
                    fixed_lines.extend(fixed_import_block)
                    in_multiline_import = False
                    import_buffer = []
            else:
                fixed_lines.append(line)
        
        if import_buffer:  # Si quedó un import sin cerrar
            fixed_import_block = fix_import_block(import_buffer)
            fixed_lines.extend(fixed_import_block)
        
        content = '\n'.join(fixed_lines)
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Corregido: {file_path}")
            return True
        
        return False
        
    except Exception as e:
        print(f"❌ Error procesando {file_path}: {e}")
        return False

def fix_multiline_import(corrupted_import: str) -> str:
    """Corrige un import multilinea corrupto."""
    # Extraer el módulo base
    module_match = re.search(r'from\s+([\w\.]+)\s+import', corrupted_import)
    if not module_match:
        return corrupted_import
    
    module = module_match.group(1)
    
    # Extraer todos los elementos importados, excluyendo import statements
    import_items = []
    standalone_imports = []
    
    # Dividir por comas y procesar cada elemento
    content = corrupted_import[corrupted_import.find('('):corrupted_import.rfind(')')].strip('()')
    items = [item.strip() for item in content.split(',')]
    
    for item in items:
        if item.startswith('import '):
            # Es un import standalone
            standalone_imports.append(item)
        elif item and not item.startswith('import'):
            # Es un elemento válido del import
            import_items.append(item)
    
    # Reconstruir imports
    result_lines = []
    
    # Agregar imports standalone primero
    for standalone in standalone_imports:
        result_lines.append(standalone)
    
    # Agregar import multilinea reconstruido
    if import_items:
        if len(import_items) == 1:
            result_lines.append(f"from {module} import {import_items[0]}")
        else:
            result_lines.append(f"from {module} import ({', '.join(import_items)})")
    
    return '\n'.join(result_lines)

def fix_inline_import(corrupted_line: str) -> str:
    """Corrige imports inline corruptos."""
    parts = [part.strip() for part in corrupted_line.split(',')]
    valid_imports = []
    standalone_imports = []
    
    for part in parts:
        if part.startswith('import '):
            standalone_imports.append(part)
        elif part and not part.startswith('import'):
            valid_imports.append(part)
    
    result = []
    if standalone_imports:
        result.extend(standalone_imports)
    if valid_imports:
        result.append(', '.join(valid_imports))
    
    return '\n'.join(result)

def fix_import_block(import_lines: List[str]) -> List[str]:
    """Corrige un bloque de import multilinea."""
    full_import = ' '.join(line.strip() for line in import_lines)
    
    # Extraer partes
    match = re.match(r'from\s+([\w\.]+)\s+import\s*\((.+)\)', full_import.replace('\n', ' '), re.DOTALL)
    if not match:
        return import_lines  # No se puede parsear, devolver como está
    
    module = match.group(1)
    items_str = match.group(2)
    
    # Separar items válidos de imports standalone
    items = [item.strip() for item in items_str.split(',')]
    valid_items = []
    standalone_imports = []
    
    for item in items:
        if 'import ' in item and not item.startswith('Q'):
            # Probablemente un import standalone mezclado
            parts = item.split()
            if 'import' in parts:
                idx = parts.index('import')
                if idx > 0:
                    # Hay algo antes de import
                    valid_items.extend(parts[:idx])
                if idx < len(parts) - 1:
                    # Hay algo después de import
                    standalone_imports.append(' '.join(parts[idx:]))
            else:
                standalone_imports.append(item)
        elif item.strip():
            valid_items.append(item.strip())
    
    # Reconstruir
    result_lines = []
    
    # Imports standalone primero
    for standalone in standalone_imports:
        if standalone.strip():
            result_lines.append(standalone.strip())
    
    # Import multilinea reconstruido
    if valid_items:
        clean_items = [item for item in valid_items if item.strip()]
        if len(clean_items) == 1:
            result_lines.append(f"from {module} import {clean_items[0]}")
        else:
            # Formatear nicamente
            if len(clean_items) <= 3:
                result_lines.append(f"from {module} import {', '.join(clean_items)}")
            else:
                result_lines.append(f"from {module} import (")
                for i, item in enumerate(clean_items):
                    if i == len(clean_items) - 1:
                        result_lines.append(f"    {item})")
                    else:
                        result_lines.append(f"    {item},")
    
    return result_lines

def main():
    """Función principal."""
    print("🔧 CORRIGIENDO CORRUPCIONES DE IMPORTS")
    print("=" * 50)
    
    # Buscar archivos Python en el proyecto
    project_root = Path("homologador")
    python_files = list(project_root.rglob("*.py"))
    
    files_fixed = 0
    total_files = len(python_files)
    
    for file_path in python_files:
        if fix_corrupted_imports(file_path):
            files_fixed += 1
    
    print(f"\n📊 RESUMEN:")
    print(f"  📁 Archivos analizados: {total_files}")
    print(f"  ✅ Archivos corregidos: {files_fixed}")
    print(f"  📈 Archivos sin cambios: {total_files - files_fixed}")
    
    if files_fixed > 0:
        print(f"\n✅ Corrupciones corregidas exitosamente!")
    else:
        print(f"\n✨ No se encontraron corrupciones.")

if __name__ == "__main__":
    main()