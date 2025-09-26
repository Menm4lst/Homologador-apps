#!/usr/bin/env python3
"""
Script para corregir imports relativos en el proyecto homologador.
"""

import os
import re
from pathlib import Path

def fix_imports_in_file(file_path: Path) -> bool:
    """Corrige los imports en un archivo específico."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Determinar la profundidad del archivo para saber cuántos ../ usar
        relative_path = file_path.relative_to(Path(__file__).parent / "homologador")
        depth = len(relative_path.parts) - 1  # -1 porque el archivo mismo no cuenta
        
        if depth == 0:  # Archivos en la raíz de homologador/
            # Cambiar imports directos a relativos
            content = re.sub(r'^from (core|data|ui)\.', r'from .\1.', content, flags=re.MULTILINE)
        else:  # Archivos en subdirectorios
            prefix = "." * (depth + 1)  # Un punto extra para subir al nivel correcto
            content = re.sub(r'^from (core|data|ui)\.', fr'from {prefix}\1.', content, flags=re.MULTILINE)
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✓ Corregido: {file_path}")
            return True
        else:
            return False
            
    except Exception as e:
        print(f"✗ Error en {file_path}: {e}")
        return False

def main():
    """Función principal."""
    project_root = Path(__file__).parent
    homologador_path = project_root / "homologador"
    
    if not homologador_path.exists():
        print("Error: No se encontró el directorio homologador/")
        return
    
    # Encontrar todos los archivos Python
    python_files = list(homologador_path.rglob("*.py"))
    
    fixed_count = 0
    total_count = len(python_files)
    
    print(f"Procesando {total_count} archivos Python...")
    
    for file_path in python_files:
        if fix_imports_in_file(file_path):
            fixed_count += 1
    
    print(f"\n✓ Completado: {fixed_count}/{total_count} archivos corregidos")

if __name__ == "__main__":
    main()