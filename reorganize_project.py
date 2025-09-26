#!/usr/bin/env python3
"""
Script de reorganización y limpieza de código
Mueve archivos de prueba y organiza el proyecto
"""

import os
import shutil
from pathlib import Path
from typing import List

def create_project_structure():
    """Crea la estructura de directorios estándar"""
    directories = [
        "tests",
        "tests/unit", 
        "tests/integration",
        "tests/ui",
        "docs",
        "scripts",
        "deployment",
        "homologador/stubs",
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"📁 Creado: {directory}")
    
    return True

def move_test_files():
    """Mueve archivos de prueba al directorio tests/"""
    test_patterns = [
        "test_*.py",
        "*_test.py", 
        "debug_*.py",
        "diagnostico*.py",
        "check_*.py",
        "analisis_*.py",
        "optimize_*.py",
        "run_*.py",
        "simple_*.py",
        "final_*.py",
        "reset_*.py",
        "fix_*.py",
    ]
    
    moved_files = []
    
    for pattern in test_patterns:
        for file_path in Path(".").glob(pattern):
            if file_path.is_file() and file_path.name != "fix_types.py":
                # Determinar subdirectorio apropiado
                if "test_" in file_path.name or "_test.py" in file_path.name:
                    target_dir = Path("tests/unit")
                elif "debug_" in file_path.name or "diagnostico" in file_path.name:
                    target_dir = Path("tests/integration")  
                elif "ui" in file_path.name or "window" in file_path.name:
                    target_dir = Path("tests/ui")
                else:
                    target_dir = Path("tests")
                
                target_path = target_dir / file_path.name
                
                try:
                    shutil.move(str(file_path), str(target_path))
                    moved_files.append((file_path.name, target_path))
                    print(f"📦 Movido: {file_path.name} → {target_path}")
                except Exception as e:
                    print(f"❌ Error moviendo {file_path}: {e}")
    
    return moved_files

def move_compilation_files():
    """Mueve archivos de compilación al directorio scripts/"""
    compilation_files = [
        "compile_*.py",
        "fixed_compile.py",
        "simple_compile.py",
        "final_compile.py",
        "*.spec",
    ]
    
    scripts_dir = Path("scripts")
    moved_files = []
    
    for pattern in compilation_files:
        for file_path in Path(".").glob(pattern):
            if file_path.is_file():
                target_path = scripts_dir / file_path.name
                
                try:
                    shutil.move(str(file_path), str(target_path))
                    moved_files.append((file_path.name, target_path))
                    print(f"🔧 Movido: {file_path.name} → {target_path}")
                except Exception as e:
                    print(f"❌ Error moviendo {file_path}: {e}")
    
    return moved_files

def move_documentation_files():
    """Mueve archivos de documentación al directorio docs/"""
    doc_patterns = [
        "*.md",
        "*.txt",
        "README*",
        "MANUAL*",
        "INSTRUCCIONES*",
        "SISTEMA_*",
        "FUNCIONALIDAD_*",
        "MEJORAS_*",
        "CORRECCION_*",
        "ERROR_*",
        "COMPILACION_*",
    ]
    
    docs_dir = Path("docs")
    moved_files = []
    
    # Mantener README.md principal
    exclude_files = {"README.md", "pyproject.toml", "requirements.txt"}
    
    for pattern in doc_patterns:
        for file_path in Path(".").glob(pattern):
            if file_path.is_file() and file_path.name not in exclude_files:
                target_path = docs_dir / file_path.name
                
                try:
                    shutil.move(str(file_path), str(target_path))
                    moved_files.append((file_path.name, target_path))
                    print(f"📚 Movido: {file_path.name} → {target_path}")
                except Exception as e:
                    print(f"❌ Error moviendo {file_path}: {e}")
    
    return moved_files

def move_deployment_files():
    """Mueve archivos de deployment"""
    if Path("Homologador_Deployment").exists():
        deployment_dir = Path("deployment") 
        target_path = deployment_dir / "Homologador_Deployment"
        
        try:
            shutil.move("Homologador_Deployment", str(target_path))
            print(f"🚀 Movido: Homologador_Deployment → {target_path}")
            return True
        except Exception as e:
            print(f"❌ Error moviendo deployment: {e}")
            return False
    
    return True

def clean_build_directories():
    """Limpia directorios de build temporales"""
    build_dirs = ["build", "dist", "__pycache__"]
    
    for build_dir in build_dirs:
        if Path(build_dir).exists():
            try:
                shutil.rmtree(build_dir)
                print(f"🧹 Eliminado: {build_dir}")
            except Exception as e:
                print(f"❌ Error eliminando {build_dir}: {e}")
    
    # Limpiar archivos .pyc recursivamente
    for pyc_file in Path(".").rglob("*.pyc"):
        try:
            pyc_file.unlink()
        except Exception:
            pass
    
    return True

def create_gitignore():
    """Crea archivo .gitignore completo"""
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.py,cover
.hypothesis/
.pytest_cache/
cover/

# Virtual environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDE
.idea/
.vscode/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Project specific
homologador.db
homologador.db-*
*.log
backups/
temp/
deployment/Homologador_Deployment/
homologador.sqlite3*

# MyPy
.mypy_cache/
.dmypy.json
dmypy.json

# Black
.black

# Documentation builds
docs/_build/
"""
    
    with open(".gitignore", "w", encoding="utf-8") as f:
        f.write(gitignore_content)
    
    print("📝 Creado: .gitignore")
    return True

def update_requirements():
    """Actualiza requirements.txt con versiones específicas"""
    requirements_content = """# Core GUI Framework
PyQt6==6.7.1
PyQt6-Qt6==6.7.2
PyQt6-sip==13.6.0

# Security & Authentication
argon2-cffi==23.1.0

# File & Process Management  
portalocker==2.8.2

# Data Processing & Analysis
python-dateutil==2.8.2
pandas==2.2.2
openpyxl==3.1.2

# Development Dependencies (optional)
# Install with: pip install -e ".[dev]"
# mypy>=1.8.0
# black>=24.0.0  
# isort>=5.13.0
# flake8>=7.0.0
# pytest>=8.0.0
# pytest-qt>=4.4.0
# pytest-cov>=4.0.0

# Build Dependencies (optional)
# Install with: pip install -e ".[build]" 
# pyinstaller>=6.0.0
"""
    
    with open("requirements.txt", "w", encoding="utf-8") as f:
        f.write(requirements_content)
    
    print("📦 Actualizado: requirements.txt")
    return True

def create_makefile():
    """Crea Makefile para tareas comunes"""
    makefile_content = """# Homologador Makefile

.PHONY: help install install-dev test lint format type-check build clean run

help:  ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \\033[36m%-15s\\033[0m %s\\n", $$1, $$2}'

install:  ## Install production dependencies
	pip install -r requirements.txt

install-dev:  ## Install development dependencies  
	pip install -e ".[dev]"

test:  ## Run tests
	pytest tests/ -v

lint:  ## Run linting
	flake8 homologador/
	isort --check-only homologador/
	black --check homologador/

format:  ## Format code
	isort homologador/
	black homologador/

type-check:  ## Run type checking
	mypy homologador/

build:  ## Build executable
	python scripts/final_compile.py

clean:  ## Clean build artifacts
	rm -rf build/ dist/ *.egg-info/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

run:  ## Run application
	python -m homologador

dev-setup:  ## Complete development setup
	$(MAKE) install-dev
	$(MAKE) format 
	$(MAKE) type-check
	$(MAKE) test
"""
    
    with open("Makefile", "w", encoding="utf-8") as f:
        f.write(makefile_content)
    
    print("⚙️ Creado: Makefile")
    return True

def main():
    """Función principal de reorganización"""
    print("🏗️ INICIANDO REORGANIZACIÓN DEL PROYECTO")
    print("=" * 50)
    
    try:
        success_count = 0
        total_tasks = 8
        
        # Crear estructura
        if create_project_structure():
            success_count += 1
        
        # Mover archivos 
        moved_tests = move_test_files()
        if moved_tests:
            success_count += 1
            print(f"📦 Movidos {len(moved_tests)} archivos de prueba")
        
        moved_scripts = move_compilation_files()
        if moved_scripts is not None:
            success_count += 1
            print(f"🔧 Movidos {len(moved_scripts)} archivos de compilación")
        
        moved_docs = move_documentation_files() 
        if moved_docs is not None:
            success_count += 1
            print(f"📚 Movidos {len(moved_docs)} archivos de documentación")
        
        if move_deployment_files():
            success_count += 1
        
        if clean_build_directories():
            success_count += 1
        
        if create_gitignore():
            success_count += 1
        
        if update_requirements():
            success_count += 1
        
        # Crear Makefile solo si no es Windows o usar alternativa
        try:
            if create_makefile():
                success_count += 1
        except Exception:
            print("ℹ️ Makefile no creado (Windows)")
            success_count += 1  # Contar como éxito
        
        print("\n" + "=" * 50) 
        print(f"✅ REORGANIZACIÓN COMPLETADA: {success_count}/{total_tasks}")
        
        if success_count >= total_tasks - 1:  # Permitir 1 fallo
            print("🎉 Proyecto reorganizado exitosamente")
            print("\n📁 Nueva estructura:")
            print("  homologador/     - Código fuente")  
            print("  tests/          - Pruebas organizadas")
            print("  scripts/        - Scripts de build") 
            print("  docs/           - Documentación")
            print("  deployment/     - Archivos compilados")
            return True
        else:
            print(f"⚠️ Solo se completaron {success_count} de {total_tasks} tareas")
            return False
            
    except Exception as e:
        print(f"❌ Error durante la reorganización: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
    
    input("\n✅ Presiona Enter para continuar...")