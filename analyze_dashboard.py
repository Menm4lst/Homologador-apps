#!/usr/bin/env python
# type: ignore
"""
Script de análisis y optimización del código del dashboard
Identifica problemas de rendimiento, errores lógicos y oportunidades de mejora
"""

import os
import sys
sys.path.insert(0, os.getcwd())


from datetime import datetime, timedelta

import homologador.core.storage as storage
def analyze_dashboard_issues():
    """Analiza los problemas específicos del dashboard"""
    
    print("🔍 ANÁLISIS DE PROBLEMAS DEL DASHBOARD")
    print("=" * 50)
    
    # 1. Analizar datos en la base de datos
    print("\n1. 📊 Análisis de datos:")
    repo = storage.get_homologation_repository()
    
    try:
        all_homologations_raw = repo.get_all()
        all_homologations = [dict(h) for h in all_homologations_raw]
        
        print(f"   ✓ Total homologaciones: {len(all_homologations)}")
        
        # Verificar estructura de datos
        if all_homologations:
            sample = all_homologations[0]
            print(f"   ✓ Campos disponibles: {list(sample.keys())}")
            
            # Verificar fechas
            created_at_values = [h.get('created_at') for h in all_homologations[:5]]
            print(f"   📅 Muestras de created_at: {created_at_values}")
            
            # Verificar estados
            statuses = set(h.get('status') for h in all_homologations)
            print(f"   📈 Estados encontrados: {statuses}")
            
            # Verificar URLs de repositorio
            repos = [h.get('repository_url') for h in all_homologations if h.get('repository_url')]
            print(f"   🔗 Repositorios con URL: {len(repos)}")
            
        else:
            print("   ❌ No hay homologaciones en la base de datos")
            
    except Exception as e:
        print(f"   ❌ Error accediendo a datos: {e}")
    
    # 2. Probar cálculo de métricas
    print("\n2. 🧮 Prueba de cálculo de métricas:")
    
    try:
        # Simular cálculo de métricas manualmente
        
        # Obtener datos

        from datetime import datetime, timedelta
        all_homologations_raw = repo.get_all()
        all_homologations = [dict(h) for h in all_homologations_raw]
        
        # Calcular métricas básicas
        days_back = 30
        date_limit = datetime.now() - timedelta(days=days_back)
        
        recent_homologations = []
        for h in all_homologations:
            try:
                created_date = datetime.fromisoformat(h.get('created_at', '2000-01-01'))
                if created_date >= date_limit:
                    recent_homologations.append(h)
            except ValueError:
                # Fecha malformada
                pass
        
        metrics = {
            'total_count': len(all_homologations),
            'recent_count': len(recent_homologations),
            'growth_rate': 0.0,
            'status_counts': {},
            'top_repositories': [],
            'daily_trends': {}
        }
        
        print(f"   ✓ Total count: {metrics.get('total_count')}")
        print(f"   ✓ Recent count: {metrics.get('recent_count')}")
        print(f"   ✓ Growth rate: {metrics.get('growth_rate'):.2f}%")
        print(f"   ✓ Status counts: {metrics.get('status_counts')}")
        print(f"   ✓ Top repositories: {metrics.get('top_repositories')}")
        print(f"   ✓ Daily trends: {len(metrics.get('daily_trends', {}))}")
        
        # Verificar cálculos lógicos
        if metrics.get('total_count', 0) < metrics.get('recent_count', 0):
            print("   ⚠️  PROBLEMA: Recent count > Total count")
        
        if metrics.get('growth_rate', 0) > 1000:
            print("   ⚠️  PROBLEMA: Growth rate anormalmente alto")
            
    except Exception as e:
        print(f"   ❌ Error calculando métricas: {e}")
        import traceback
        traceback.print_exc()

def identify_optimization_opportunities():
    """Identifica oportunidades de optimización"""
    
    print("\n3. ⚡ Oportunidades de optimización:")
    
    # Analizar consultas de base de datos
    print("   📊 Consultas de base de datos:")
    print("     - get_all() puede ser lenta con muchos registros")
    print("     - Conversión dict() en cada métrica es ineficiente")
    print("     - Múltiples iteraciones sobre los mismos datos")
    
    # Analizar lógica de fechas
    print("   📅 Manejo de fechas:")
    print("     - datetime.fromisoformat() puede fallar con fechas malformadas")
    print("     - Comparaciones de fechas repetitivas")
    
    # Analizar cálculos
    print("   🧮 Cálculos:")
    print("     - Growth rate calculation puede ser imprecisa")
    print("     - Daily trends solo para 7 días pero period puede ser mayor")

def suggest_fixes():
    """Sugiere correcciones específicas"""
    
    print("\n4. 🔧 Correcciones sugeridas:")
    
    fixes = [
        "1. Agregar índices en created_at para consultas más rápidas",
        "2. Implementar cache de métricas con TTL",
        "3. Usar consultas SQL agregadas en lugar de filtros Python",
        "4. Manejar fechas None/malformadas más robustamente",
        "5. Normalizar estados de homologaciones",
        "6. Optimizar extracción de nombres de repositorio",
        "7. Corregir lógica de daily trends para coincidir con period",
        "8. Agregar validación de datos antes de cálculos"
    ]
    
    for fix in fixes:
        print(f"   ✅ {fix}")

if __name__ == "__main__":
    analyze_dashboard_issues()
    identify_optimization_opportunities()
    suggest_fixes()
    
    print("\n" + "=" * 50)
    print("📝 RESUMEN:")
    print("   - El dashboard tiene varios problemas de rendimiento")
    print("   - Los cálculos pueden ser imprecisos con datos reales")
    print("   - Se necesita optimización de consultas y cache")
    print("   - Mejores validaciones y manejo de errores")