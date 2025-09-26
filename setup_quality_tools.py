#!/usr/bin/env python3
"""
Script de configuración de herramientas de calidad
Instala y configura linters, formateadores y type checkers
"""

import subprocess
import sys
from pathlib import Path

def install_dev_dependencies():
    """Instala dependencias de desarrollo"""
    dev_packages = [
        "mypy>=1.8.0",
        "black>=24.0.0", 
        "isort>=5.13.0",
        "flake8>=7.0.0",
        "pytest>=8.0.0",
        "pytest-qt>=4.4.0", 
        "pytest-cov>=4.0.0",
        "pre-commit>=3.6.0",
    ]
    
    print("📦 Instalando dependencias de desarrollo...")
    
    for package in dev_packages:
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", package], 
                         check=True, capture_output=True, text=True)
            print(f"✅ Instalado: {package}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error instalando {package}: {e}")
            return False
    
    return True

def create_mypy_config():
    """Crea configuración para mypy"""
    config_content = """[tool.mypy]
python_version = "3.9"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = false  # Gradual adoption
disallow_incomplete_defs = false
check_untyped_defs = true
disallow_untyped_decorators = false
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
warn_unreachable = true
strict_equality = true
show_error_codes = true

[[tool.mypy.overrides]]
module = "PyQt6.*"
ignore_missing_imports = true

[[tool.mypy.overrides]]
module = "argon2.*"
ignore_missing_imports = true

[[tool.mypy.overrides]]
module = "portalocker.*"
ignore_missing_imports = true

[[tool.mypy.overrides]]
module = "pandas.*"
ignore_missing_imports = true

[[tool.mypy.overrides]]
module = "openpyxl.*"
ignore_missing_imports = true
"""
    
    # Actualizar pyproject.toml si existe, si no crear mypy.ini
    pyproject_path = Path("pyproject.toml")
    if pyproject_path.exists():
        with open(pyproject_path, 'a', encoding='utf-8') as f:
            f.write("\n" + config_content)
        print("✅ Configuración mypy agregada a pyproject.toml")
    else:
        with open("mypy.ini", 'w', encoding='utf-8') as f:
            f.write(config_content.replace("[tool.mypy]", "[mypy]").replace("[[tool.mypy.overrides]]", "[mypy-"))
        print("✅ Creado: mypy.ini")
    
    return True

def create_flake8_config():
    """Crea configuración para flake8"""
    config_content = """[flake8]
max-line-length = 100
extend-ignore = 
    # E203: whitespace before ':'  (conflicts with black)
    E203,
    # W503: line break before binary operator (conflicts with black)  
    W503,
    # F401: imported but unused (handled by isort/mypy)
    F401
exclude = 
    .git,
    __pycache__,
    build,
    dist,
    *.egg-info,
    .venv,
    tests/fixtures

per-file-ignores =
    # Tests can have longer lines and unused imports
    tests/*:E501,F401,F811
    # Init files can have unused imports
    __init__.py:F401
    # UI files can be longer
    homologador/ui/*:E501
"""
    
    with open("setup.cfg", 'w', encoding='utf-8') as f:
        f.write(config_content)
    
    print("✅ Creado: setup.cfg (flake8)")
    return True

def create_pytest_config():
    """Crea configuración para pytest"""
    config_content = """[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]  
python_functions = ["test_*"]
addopts = [
    "--strict-markers",
    "--strict-config", 
    "--verbose",
    "--tb=short",
    "--cov=homologador",
    "--cov-report=term-missing:skip-covered",
    "--cov-report=html:htmlcov",
    "--cov-report=xml",
    "--cov-fail-under=60",
]
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: marks tests as integration tests",
    "ui: marks tests as UI tests (require display)",
]
filterwarnings = [
    "ignore::DeprecationWarning",
    "ignore::PendingDeprecationWarning",
]

[tool.coverage.run]
source = ["homologador"]
omit = [
    "*/tests/*",
    "*/test_*.py",
    "*/__init__.py",
    "*/stubs/*",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__", 
    "if self.debug:",
    "if settings.DEBUG",
    "raise AssertionError",
    "raise NotImplementedError",
    "if 0:",
    "if __name__ == .__main__.:",
    "class .*\\bProtocol\\):",
    "@(abc\\.)?abstractmethod",
]
"""
    
    # Agregar a pyproject.toml
    pyproject_path = Path("pyproject.toml")
    if pyproject_path.exists():
        with open(pyproject_path, 'a', encoding='utf-8') as f:
            f.write("\n" + config_content)
        print("✅ Configuración pytest agregada a pyproject.toml")
    else:
        with open("pytest.ini", 'w', encoding='utf-8') as f:
            f.write(config_content.replace("[tool.pytest.ini_options]", "[pytest]"))
        print("✅ Creado: pytest.ini")
    
    return True

def create_precommit_config():
    """Crea configuración para pre-commit hooks"""
    config_content = """repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-case-conflict
      - id: check-merge-conflict
      
  - repo: https://github.com/psf/black
    rev: 24.1.1
    hooks:
      - id: black
        language_version: python3
        
  - repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
      - id: isort
      
  - repo: https://github.com/pycqa/flake8
    rev: 7.0.0
    hooks:
      - id: flake8
      
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
        exclude: ^tests/
"""
    
    with open(".pre-commit-config.yaml", 'w', encoding='utf-8') as f:
        f.write(config_content)
    
    print("✅ Creado: .pre-commit-config.yaml")
    return True

def create_github_workflows():
    """Crea workflows de GitHub Actions"""
    workflows_dir = Path(".github/workflows")
    workflows_dir.mkdir(parents=True, exist_ok=True)
    
    # Workflow de CI
    ci_workflow = """name: CI

on:
  push:
    branches: [ main, master ]
  pull_request:
    branches: [ main, master ]

jobs:
  test:
    runs-on: windows-latest
    strategy:
      matrix:
        python-version: [3.9, "3.10", "3.11", "3.12"]
        
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
        
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov mypy black isort flake8
        
    - name: Lint with flake8
      run: |
        flake8 homologador/ --count --select=E9,F63,F7,F82 --show-source --statistics
        flake8 homologador/ --count --exit-zero --max-complexity=10 --statistics
        
    - name: Check formatting with black
      run: black --check homologador/
      
    - name: Check import sorting with isort  
      run: isort --check-only homologador/
      
    - name: Type check with mypy
      run: mypy homologador/ --ignore-missing-imports
      
    - name: Test with pytest
      run: |
        pytest tests/ --cov=homologador --cov-report=xml
        
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
"""
    
    with open(workflows_dir / "ci.yml", 'w', encoding='utf-8') as f:
        f.write(ci_workflow)
    
    # Workflow de build
    build_workflow = """name: Build

on:
  release:
    types: [published]
    
jobs:
  build:
    runs-on: windows-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: "3.11"
        
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pyinstaller
        
    - name: Build executable
      run: python scripts/final_compile.py
      
    - name: Upload executable
      uses: actions/upload-artifact@v3
      with:
        name: homologador-executable
        path: deployment/Homologador_Deployment/
"""
    
    with open(workflows_dir / "build.yml", 'w', encoding='utf-8') as f:
        f.write(build_workflow)
    
    print("✅ Creados: GitHub Actions workflows")
    return True

def run_initial_formatting():
    """Ejecuta formateo inicial del código"""
    commands = [
        # Ordenar imports
        [sys.executable, "-m", "isort", "homologador/"],
        # Formatear código
        [sys.executable, "-m", "black", "homologador/"],
    ]
    
    for cmd in commands:
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            print(f"✅ Ejecutado: {' '.join(cmd[2:])}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error ejecutando {' '.join(cmd)}: {e}")
            print(f"   Output: {e.stdout}")
            print(f"   Error: {e.stderr}")
    
    return True

def create_simple_test():
    """Crea un test simple para validar la configuración"""
    test_content = """#!/usr/bin/env python3
\"\"\"
Test básico para validar que la aplicación se importa correctamente
\"\"\"

import pytest
import sys
from pathlib import Path

# Agregar el directorio padre al path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_imports():
    \"\"\"Test que las importaciones básicas funcionen\"\"\"
    try:
        # Test de importaciones críticas
        from homologador.core.settings import get_settings
        from homologador.core.storage import get_database_manager  
        from homologador.data.seed import get_auth_service
        
        # Verificar que los singletons funcionen
        settings = get_settings()
        assert settings is not None
        
        db_manager = get_database_manager()
        assert db_manager is not None
        
        auth_service = get_auth_service()
        assert auth_service is not None
        
        print("✅ Todas las importaciones críticas exitosas")
        
    except ImportError as e:
        pytest.fail(f"Error de importación: {e}")
    except Exception as e:
        pytest.fail(f"Error inesperado: {e}")

def test_pyqt6_available():
    \"\"\"Test que PyQt6 esté disponible\"\"\"
    try:
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import Qt
        
        # Crear aplicación temporal (sin mostrar)
        import sys
        if not QApplication.instance():
            app = QApplication([])
            app.setQuitOnLastWindowClosed(False)
        
        print("✅ PyQt6 disponible y funcional")
        
    except ImportError as e:
        pytest.fail(f"PyQt6 no disponible: {e}")

if __name__ == "__main__":
    test_imports()
    test_pyqt6_available()
    print("🎉 Todos los tests básicos pasaron")
"""
    
    test_path = Path("tests/test_basic.py")
    with open(test_path, 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    print(f"✅ Creado: {test_path}")
    return True

def main():
    """Función principal de configuración"""
    print("⚙️ CONFIGURANDO HERRAMIENTAS DE CALIDAD")
    print("=" * 50)
    
    try:
        success_count = 0
        total_tasks = 8
        
        # Instalar dependencias
        if install_dev_dependencies():
            success_count += 1
        
        # Crear configuraciones
        if create_mypy_config():
            success_count += 1
            
        if create_flake8_config():
            success_count += 1
            
        if create_pytest_config():
            success_count += 1
            
        if create_precommit_config():
            success_count += 1
            
        if create_github_workflows():
            success_count += 1
            
        if create_simple_test():
            success_count += 1
            
        # Formatear código inicial
        if run_initial_formatting():
            success_count += 1
        
        print("\n" + "=" * 50)
        print(f"✅ CONFIGURACIÓN COMPLETADA: {success_count}/{total_tasks}")
        
        if success_count >= total_tasks - 1:
            print("🎉 Herramientas de calidad configuradas exitosamente")
            print("\n🛠️ Herramientas disponibles:")
            print("  mypy homologador/           - Type checking")
            print("  black homologador/          - Code formatting")
            print("  isort homologador/          - Import sorting") 
            print("  flake8 homologador/         - Linting")
            print("  pytest tests/               - Testing")
            print("  pre-commit install          - Git hooks")
            
            print("\n📋 Próximos pasos:")
            print("1. Ejecutar: pytest tests/test_basic.py")
            print("2. Configurar pre-commit: pre-commit install")
            print("3. Ejecutar pipeline: python -m pytest && mypy homologador/")
            return True
        else:
            print(f"⚠️ Solo se completaron {success_count} de {total_tasks} configuraciones")
            return False
            
    except Exception as e:
        print(f"❌ Error durante la configuración: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
    
    input("\n✅ Presiona Enter para continuar...")