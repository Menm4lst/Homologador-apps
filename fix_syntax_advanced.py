#!/usr/bin/env python3
# type: ignore
"""
Script mejorado para corregir errores de sintaxis en imports.
"""

import ast
import re
from pathlib import Path

def fix_python_syntax_errors(file_path: Path) -> bool:
    """Corrige errores de sintaxis en archivos Python."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Dividir en líneas para trabajar línea por línea
    lines = content.split('\n')
    fixed_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Detectar imports multilinea rotos
        if 'from PyQt6.QtWidgets import (' in line:
            # Encontrar el final del import
            import_lines = [line]
            i += 1
            
            # Buscar hasta encontrar el cierre del paréntesis
            while i < len(lines) and ')' not in import_lines[-1]:
                next_line = lines[i]
                
                # Si encontramos un import local en el medio, separarlo
                if next_line.strip().startswith('from ..'):
                    # Cerrar el import de PyQt6 si no está cerrado
                    if ')' not in import_lines[-1]:
                        import_lines[-1] += ')'
                    
                    # Agregar línea vacía y el import local
                    fixed_lines.extend(import_lines)
                    fixed_lines.append('')
                    fixed_lines.append(next_line)
                    
                    # Buscar el resto del import PyQt6 si existe
                    i += 1
                    while i < len(lines) and lines[i].strip() and not lines[i].startswith('from') and not lines[i].startswith('import'):
                        # Estas son líneas que pertenecen al import de PyQt6
                        # Las vamos a ignorar por ahora para evitar duplicados
                        i += 1
                    i -= 1  # Retroceder uno para que el bucle principal avance correctamente
                    break
                else:
                    import_lines.append(next_line)
                i += 1
            else:
                # Import normal, agregar todas las líneas
                fixed_lines.extend(import_lines)
        
        # Detectar patrones específicos problemáticos
        elif (line.strip().startswith('from') and 
              i + 1 < len(lines) and 
              lines[i + 1].strip() and 
              not lines[i + 1].strip().startswith(('from ', 'import '))):
            
            # Línea de import seguida de contenido que podría ser parte del import anterior
            fixed_lines.append(line)
        
        else:
            fixed_lines.append(line)
        
        i += 1
    
    # Reconstruir el contenido
    new_content = '\n'.join(fixed_lines)
    
    # Limpieza adicional con regex
    # Corregir imports de PyQt6 mal formateados
    new_content = re.sub(
        r'(from PyQt6\.QtWidgets import \([^)]*)\n\nfrom (\.\.[^\n]*)\n([^)]*\))',
        r'\1,\n\3\n\nfrom \2',
        new_content,
        flags=re.MULTILINE
    )
    
    # Remover líneas vacías múltiples
    new_content = re.sub(r'\n\n\n+', '\n\n', new_content)
    
    if new_content != original_content:
        # Verificar que el resultado sea válido Python
        try:
            ast.parse(new_content)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return True
        except SyntaxError as e:
            print(f"⚠️  {file_path.name}: El resultado aún tiene errores de sintaxis: {e}")
            return False
    
    return False

def fix_all_files():
    """Corrige todos los archivos Python en el proyecto."""
    project_root = Path(__file__).parent / "homologador"
    fixed_files = []
    error_files = []
    
    for py_file in project_root.rglob("*.py"):
        try:
            # Verificar si el archivo tiene errores de sintaxis
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            try:
                ast.parse(content)
                # No hay errores de sintaxis
                continue
            except SyntaxError:
                # Hay errores, intentar corregir
                if fix_python_syntax_errors(py_file):
                    fixed_files.append(py_file.name)
                    print(f"✅ Corregido: {py_file.name}")
                else:
                    error_files.append(py_file.name)
                    print(f"❌ Error en: {py_file.name}")
                    
        except Exception as e:
            error_files.append(py_file.name)
            print(f"❌ Error inesperado en {py_file.name}: {e}")
    
    return fixed_files, error_files

if __name__ == "__main__":
    print("🔧 CORRECTOR AVANZADO DE SINTAXIS")
    print("=" * 40)
    
    fixed, errors = fix_all_files()
    
    print(f"\n📊 RESUMEN:")
    print(f"✅ Archivos corregidos: {len(fixed)}")
    print(f"❌ Archivos con errores: {len(errors)}")
    
    if fixed:
        print(f"\n✅ Corregidos: {', '.join(fixed)}")
    
    if errors:
        print(f"\n❌ Con errores: {', '.join(errors)}")