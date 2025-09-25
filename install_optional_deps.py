"""
Script de instalación opcional para dependencias avanzadas.

Este script instala las dependencias opcionales para funcionalidades avanzadas
como gráficos en el sistema de reportes.
"""

import subprocess
import sys
import os
from pathlib import Path


def install_package(package: str) -> bool:
    """Instala un paquete usando pip."""
    try:
        print(f"📦 Instalando {package}...")
        result = subprocess.run([sys.executable, "-m", "pip", "install", package], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ {package} instalado correctamente")
            return True
        else:
            print(f"❌ Error instalando {package}: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error instalando {package}: {e}")
        return False


def check_package(package: str) -> bool:
    """Verifica si un paquete está instalado."""
    try:
        __import__(package)
        return True
    except ImportError:
        return False


def main():
    """Función principal del instalador."""
    print("🚀 INSTALADOR DE DEPENDENCIAS AVANZADAS")
    print("=" * 50)
    print()
    
    # Lista de dependencias opcionales
    optional_packages = [
        ("matplotlib", "Gráficos en reportes"),
        ("pillow", "Procesamiento de imágenes"),
        ("openpyxl", "Exportación a Excel"),
        ("reportlab", "Generación de PDFs"),
        ("requests", "Conexiones HTTP"),
        ("cryptography", "Encriptación avanzada")
    ]
    
    print("📋 Dependencias opcionales disponibles:")
    print()
    
    # Verificar estado actual
    for package, description in optional_packages:
        status = "✅ Instalado" if check_package(package) else "❌ No instalado"
        print(f"{package:15} - {description:25} [{status}]")
    
    print()
    
    # Preguntar qué instalar
    print("¿Qué desea instalar?")
    print("1. 📊 Todas las dependencias (recomendado)")
    print("2. 📈 Solo matplotlib (para gráficos)")
    print("3. 🛠️ Instalación personalizada")
    print("4. ❌ Salir")
    
    try:
        choice = input("\\nSeleccione una opción (1-4): ").strip()
        
        if choice == "1":
            print("\\n🔄 Instalando todas las dependencias...")
            success_count = 0
            for package, _ in optional_packages:
                if install_package(package):
                    success_count += 1
            
            print(f"\\n✅ Instalación completada: {success_count}/{len(optional_packages)} paquetes")
        
        elif choice == "2":
            print("\\n🔄 Instalando matplotlib...")
            install_package("matplotlib")
        
        elif choice == "3":
            print("\\n📝 Seleccione los paquetes a instalar:")
            for i, (package, description) in enumerate(optional_packages, 1):
                print(f"{i}. {package} - {description}")
            
            selection = input("\\nIngrese los números separados por comas (ej: 1,2,3): ").strip()
            
            try:
                indices = [int(x.strip()) - 1 for x in selection.split(",")]
                for idx in indices:
                    if 0 <= idx < len(optional_packages):
                        package, _ = optional_packages[idx]
                        install_package(package)
            except ValueError:
                print("❌ Selección inválida")
        
        elif choice == "4":
            print("👋 Saliendo...")
            return
        
        else:
            print("❌ Opción inválida")
    
    except KeyboardInterrupt:
        print("\\n\\n❌ Instalación cancelada por el usuario")
    except Exception as e:
        print(f"\\n❌ Error durante la instalación: {e}")
    
    print("\\n" + "=" * 50)
    print("ℹ️  Las funcionalidades que requieren estas dependencias")
    print("   se activarán automáticamente al reiniciar la aplicación.")
    print("=" * 50)


if __name__ == "__main__":
    main()