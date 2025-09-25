#!/usr/bin/env python3
"""
🎨 LANZADOR FINAL - HOMOLOGADOR CON TEMA NEGRO-AZUL
"""

import subprocess
import sys
import os

def main():
    """Lanzador principal con instrucciones claras."""
    
    print("🎨" + "=" * 60 + "🎨")
    print("  🚀 HOMOLOGADOR DE APLICACIONES - TEMA MODERNO NEGRO-AZUL")
    print("🎨" + "=" * 60 + "🎨")
    print()
    print("✨ CARACTERÍSTICAS IMPLEMENTADAS:")
    print("   🎨 Tema visual negro-azul consistente")
    print("   📊 Dashboard optimizado con métricas corregidas")
    print("   🌐 Web preview integrado")
    print("   🔧 Sistema de notificaciones avanzado")
    print("   📋 Gestión completa de homologaciones")
    print()
    print("🔐 CREDENCIALES DE ACCESO:")
    print("   👤 Usuario: admin")
    print("   🔑 Contraseña: admin123")
    print()
    print("🎯 INSTRUCCIONES:")
    print("   1️⃣  La ventana de LOGIN aparecerá automáticamente")
    print("   2️⃣  Ingresa las credenciales mostradas arriba")
    print("   3️⃣  Explora el nuevo diseño negro-azul moderno")
    print("   4️⃣  Prueba todas las funcionalidades optimizadas")
    print()
    print("🚀 Iniciando aplicación...")
    print("-" * 60)
    
    # Ejecutar aplicación
    project_root = "C:\\Users\\Antware\\OneDrive\\Desktop\\PROYECTOS DEV\\APP HOMOLOGACIONES"
    python_exe = f"{project_root}\\.venv\\Scripts\\python.exe"
    script_path = f"{project_root}\\ejecutar_homologador.py"
    
    try:
        # Ejecutar de forma que se mantenga visible
        result = subprocess.run([python_exe, script_path], 
                              cwd=project_root,
                              capture_output=False)
        
        print("-" * 60)
        if result.returncode == 0:
            print("✅ Aplicación cerrada correctamente")
        else:
            print(f"⚠️ Aplicación cerrada con código: {result.returncode}")
            
    except KeyboardInterrupt:
        print("\n🛑 Aplicación interrumpida por el usuario")
    except Exception as e:
        print(f"❌ Error ejecutando aplicación: {e}")
    
    print()
    print("🎉 ¡Gracias por usar el Homologador con tema moderno!")
    print("💡 Si tienes problemas, las credenciales son: admin / admin123")
    
    input("\nPresiona Enter para salir...")

if __name__ == "__main__":
    main()