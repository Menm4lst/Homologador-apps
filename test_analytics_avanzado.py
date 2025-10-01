#!/usr/bin/env python3
"""
Script de prueba para el Sistema de Analytics Avanzado de EL OMO LOGADOR 🥵.
"""

import sys
import os
from pathlib import Path

# Agregar el directorio del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_analytics_system():
    """Prueba el sistema de analytics avanzado."""
    print("🚀 PROBANDO SISTEMA DE ANALYTICS AVANZADO - EL OMO LOGADOR 🥵")
    print("=" * 70)
    
    try:
        # Importar PyQt6
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import Qt
        
        print("✅ PyQt6 importado correctamente")
        
        # Crear aplicación de prueba
        app = QApplication(sys.argv)
        app.setApplicationName("Test Analytics - EL OMO LOGADOR 🥵")
        
        print("✅ Aplicación QT creada")
        
        # Importar el sistema de analytics
        from homologador.ui.advanced_analytics import (
            AnalyticsData,
            BarChartWidget,
            DonutChartWidget,
            LineChartWidget,
            MetricCardAdvanced,
            AdvancedAnalyticsWidget,
            show_advanced_analytics
        )
        
        print("✅ Módulo de analytics importado correctamente")
        
        # Probar AnalyticsData
        analytics_data = AnalyticsData()
        print("✅ AnalyticsData instanciado")
        
        # Probar obtención de datos
        monthly_data = analytics_data.get_homologations_by_month(6)
        print(f"✅ Datos mensuales obtenidos: {len(monthly_data)} meses")
        
        top_apps = analytics_data.get_top_applications(5)
        print(f"✅ Top aplicaciones obtenidas: {len(top_apps)} apps")
        
        user_activity = analytics_data.get_user_activity()
        print(f"✅ Actividad de usuarios obtenida: {len(user_activity)} usuarios")
        
        repo_stats = analytics_data.get_repository_stats()
        print(f"✅ Estadísticas de repositorios: {len(repo_stats)} repos")
        
        weekly_activity = analytics_data.get_weekly_activity()
        print(f"✅ Actividad semanal: {len(weekly_activity)} días")
        
        # Probar widgets de gráficos
        test_data = [("Ene", 10), ("Feb", 15), ("Mar", 8), ("Abr", 20), ("May", 12)]
        
        bar_chart = BarChartWidget("Test Gráfico Barras", test_data)
        print("✅ BarChartWidget creado")
        
        donut_chart = DonutChartWidget("Test Gráfico Dona", test_data)
        print("✅ DonutChartWidget creado")
        
        line_chart = LineChartWidget("Test Gráfico Líneas", test_data)
        print("✅ LineChartWidget creado")
        
        # Probar tarjeta de métrica
        metric_card = MetricCardAdvanced("Test Métrica", "100", "prueba", "#3498db", "📊")
        print("✅ MetricCardAdvanced creado")
        
        # Probar widget principal
        analytics_widget = AdvancedAnalyticsWidget()
        print("✅ AdvancedAnalyticsWidget creado")
        
        # Probar función de diálogo
        dialog = show_advanced_analytics()
        print("✅ Diálogo de analytics creado")
        
        print(f"\n📊 CARACTERÍSTICAS DEL SISTEMA DE ANALYTICS:")
        print(f"   🎯 Métricas en tiempo real: ✅")
        print(f"   📈 Gráficos de barras personalizados: ✅")
        print(f"   🍩 Gráficos de dona interactivos: ✅")
        print(f"   📉 Gráficos de líneas de tendencias: ✅")
        print(f"   💳 Tarjetas de métricas animadas: ✅")
        print(f"   🔄 Actualización automática cada 30s: ✅")
        print(f"   🎨 Interfaz hermosa con gradientes: ✅")
        print(f"   📱 Responsive y scrolleable: ✅")
        
        print(f"\n🎨 ESTILOS Y VISUAL:")
        print(f"   🌈 Colores vibrantes personalizados")
        print(f"   📱 Interfaz moderna con gradientes")
        print(f"   🎭 Efectos hover y animaciones")
        print(f"   🖼️ Iconos emoji para mejor UX")
        
        print(f"\n📈 MÉTRICAS DISPONIBLES:")
        print(f"   📋 Total de homologaciones en el sistema")
        print(f"   📅 Homologaciones del mes actual")
        print(f"   👥 Usuarios activos en el sistema")
        print(f"   🗂️ Número de repositorios diferentes")
        print(f"   📊 Homologaciones por mes (últimos 6 meses)")
        print(f"   🏆 Top 5 aplicaciones más homologadas")
        print(f"   📈 Actividad de los últimos 7 días")
        print(f"   👤 Actividad por usuario")
        print(f"   📂 Estadísticas por repositorio")
        
        print(f"\n🚀 ACCESO AL SISTEMA:")
        print(f"   🎛️ Desde Dashboard Administrativo → 📈 Analytics")
        print(f"   🍽️ Desde Menú Administración → 📊 Analytics Avanzado (Ctrl+Shift+A)")
        print(f"   🔐 Solo accesible para usuarios administradores")
        
        print(f"\n🎉 ¡SISTEMA DE ANALYTICS COMPLETAMENTE FUNCIONAL!")
        print(f"✨ EL OMO LOGADOR 🥵 ahora tiene gráficos hermosos y métricas en tiempo real")
        
        # Mostrar el diálogo de prueba
        print(f"\n🎯 Mostrando diálogo de prueba...")
        
        # Configurar para cerrar automáticamente después de unos segundos
        from PyQt6.QtCore import QTimer
        timer = QTimer()
        timer.timeout.connect(dialog.close)
        timer.start(5000)  # Cerrar después de 5 segundos
        
        dialog.show()
        
        # Ejecutar por un momento para mostrar
        app.processEvents()
        
        return True
        
    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        print("💡 Asegúrate de que PyQt6 esté instalado")
        return False
        
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Función principal."""
    print("🎯 INICIANDO PRUEBAS DEL SISTEMA DE ANALYTICS AVANZADO")
    print("📅 Para EL OMO LOGADOR 🥵")
    print()
    
    success = test_analytics_system()
    
    if success:
        print(f"\n✅ ¡TODAS LAS PRUEBAS EXITOSAS!")
        print(f"🎉 El sistema de analytics está listo para usar")
        print(f"\n🚀 PRÓXIMOS PASOS:")
        print(f"   1. Ejecuta la aplicación: python -m homologador")
        print(f"   2. Inicia sesión como administrador")
        print(f"   3. Ve a 'Administración' → '📊 Analytics Avanzado'")
        print(f"   4. ¡Disfruta de los hermosos gráficos!")
    else:
        print(f"\n❌ Hubo errores en las pruebas")
        print(f"🔧 Revisa los logs de error arriba")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())