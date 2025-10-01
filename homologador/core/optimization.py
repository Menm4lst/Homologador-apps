#!/usr/bin/env python3
"""
Módulo de optimización del sistema Homologador.
Proporciona herramientas para mejorar el rendimiento y eliminar redundancias.
"""


from functools import lru_cache, wraps
from typing import Any, Callable, Dict, List, Optional, TypeVar, Union, cast
import logging
import time

from weakref import WeakKeyDictionary
logger = logging.getLogger(__name__)

# Type variables para generics
T = TypeVar('T')
F = TypeVar('F', bound=Callable[..., Any])

class PerformanceMonitor:
    """Monitor de rendimiento para optimización de funciones críticas."""
    
    def __init__(self):
        self._metrics: Dict[str, List[float]] = {}
        self._call_counts: Dict[str, int] = {}
    
    def measure_time(self, func_name: Optional[str] = None):
        """Decorador para medir tiempo de ejecución de funciones."""
        def decorator(func: F) -> F:
            name = func_name or f"{func.__module__}.{func.__qualname__}"
            
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.perf_counter()
                try:
                    result = func(*args, **kwargs)
                    return result
                finally:
                    end_time = time.perf_counter()
                    execution_time = end_time - start_time
                    
                    # Registrar métricas
                    if name not in self._metrics:
                        self._metrics[name] = []
                        self._call_counts[name] = 0
                    
                    self._metrics[name].append(execution_time)
                    self._call_counts[name] += 1
                    
                    # Log si la función es lenta
                    if execution_time > 0.1:  # 100ms
                        logger.debug(f"Función lenta detectada: {name} - {execution_time:.3f}s")
            
            return cast(F, wrapper)
        return decorator
    
    def get_stats(self, func_name: str) -> Dict[str, float]:
        """Obtiene estadísticas de rendimiento para una función."""
        if func_name not in self._metrics:
            return {}
        
        times = self._metrics[func_name]
        return {
            'calls': self._call_counts[func_name],
            'total_time': sum(times),
            'avg_time': sum(times) / len(times),
            'min_time': min(times),
            'max_time': max(times)
        }
    
    def get_all_stats(self) -> Dict[str, Dict[str, float]]:
        """Obtiene estadísticas de todas las funciones monitoreadas."""
        return {name: self.get_stats(name) for name in self._metrics.keys()}

class SmartCache:
    """Sistema de caché inteligente con limpieza automática."""
    
    def __init__(self, max_size: int = 1000, ttl_seconds: Optional[int] = None):
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self._cache: Dict[str, Any] = {}
        self._timestamps: Dict[str, float] = {}
        self._access_counts: Dict[str, int] = {}
    
    def get(self, key: str) -> Optional[Any]:
        """Obtiene un valor del caché."""
        if not self._is_valid(key):
            return None
        
        self._access_counts[key] = self._access_counts.get(key, 0) + 1
        return self._cache.get(key)
    
    def set(self, key: str, value: Any) -> None:
        """Almacena un valor en el caché."""
        self._cleanup_if_needed()
        
        self._cache[key] = value
        self._timestamps[key] = time.time()
        self._access_counts[key] = 1
    
    def _is_valid(self, key: str) -> bool:
        """Verifica si una entrada del caché es válida."""
        if key not in self._cache:
            return False
        
        if self.ttl_seconds:
            age = time.time() - self._timestamps[key]
            if age > self.ttl_seconds:
                self._remove(key)
                return False
        
        return True
    
    def _cleanup_if_needed(self) -> None:
        """Limpia el caché si es necesario."""
        if len(self._cache) >= self.max_size:
            # Remover entradas menos utilizadas
            sorted_keys = sorted(
                self._access_counts.keys(), 
                key=lambda k: self._access_counts[k]
            )
            for key in sorted_keys[:len(sorted_keys) // 2]:
                self._remove(key)
    
    def _remove(self, key: str) -> None:
        """Remueve una entrada del caché."""
        self._cache.pop(key, None)
        self._timestamps.pop(key, None)
        self._access_counts.pop(key, None)

class LazyLoader:
    """Cargador lazy de módulos y recursos pesados."""
    
    def __init__(self):
        self._loaded_modules: Dict[str, Any] = {}
        self._loading_errors: Dict[str, Exception] = {}
    
    def load_module(self, module_path: str, fallback: Any = None) -> Any:
        """Carga un módulo de forma lazy."""
        if module_path in self._loaded_modules:
            return self._loaded_modules[module_path]
        
        if module_path in self._loading_errors:
            logger.debug(f"Módulo {module_path} falló anteriormente: {self._loading_errors[module_path]}")
            return fallback
        
        try:
            if module_path.startswith('.'):
                # Import relativo
                module = __import__(module_path, fromlist=[''], level=1)
            else:
                # Import absoluto
                parts = module_path.split('.')
                module = __import__(module_path)
                for part in parts[1:]:
                    module = getattr(module, part)
            
            self._loaded_modules[module_path] = module
            return module
            
        except ImportError as e:
            self._loading_errors[module_path] = e
            logger.debug(f"No se pudo cargar módulo {module_path}: {e}")
            return fallback
    
    def get_class(self, module_path: str, class_name: str, fallback: Any = None) -> Any:
        """Obtiene una clase de un módulo de forma lazy."""
        module = self.load_module(module_path, None)
        if module:
            return getattr(module, class_name, fallback)
        return fallback

class ResourceOptimizer:
    """Optimizador de recursos del sistema."""
    
    def __init__(self):
        self.performance_monitor = PerformanceMonitor()
        self.cache = SmartCache(max_size=500, ttl_seconds=300)  # 5 minutos TTL
        self.lazy_loader = LazyLoader()
        self._weak_references: WeakKeyDictionary = WeakKeyDictionary()
    
    def cached_property(self, ttl_seconds: Optional[int] = None):
        """Decorador para propiedades con caché."""
        def decorator(func: Callable[..., Any]) -> property:
            cache_key = f"{func.__module__}.{func.__qualname__}"
            
            def getter(self):
                cached_value = self.cache.get(cache_key)
                if cached_value is not None:
                    return cached_value
                
                value = func(self)
                self.cache.set(cache_key, value)
                return value
            
            return property(getter)  # type: ignore[arg-type]
        return decorator
    
    def debounce(self, delay: float = 0.1):
        """Decorador para debounce de funciones."""
        def decorator(func: F) -> F:
            last_called = [0.0]
            
            @wraps(func)
            def wrapper(*args, **kwargs):
                now = time.time()
                if now - last_called[0] >= delay:
                    last_called[0] = now
                    return func(*args, **kwargs)
            
            return cast(F, wrapper)
        return decorator
    
    def memoize_with_size(self, max_size: int = 128):
        """Memoización con tamaño limitado."""
        def decorator(func: F) -> F:
            return cast(F, lru_cache(maxsize=max_size)(func))
        return decorator

# Instancia global del optimizador
_optimizer = ResourceOptimizer()

# Funciones de conveniencia
def get_optimizer() -> ResourceOptimizer:
    """Obtiene la instancia global del optimizador."""
    return _optimizer

def measure_performance(func_name: Optional[str] = None):
    """Decorador de conveniencia para medir rendimiento."""
    return _optimizer.performance_monitor.measure_time(func_name)

def smart_cache(key: str, value: Any = None) -> Any:
    """Acceso directo al caché inteligente."""
    if value is not None:
        _optimizer.cache.set(key, value)
    return _optimizer.cache.get(key)

def lazy_import(module_path: str, class_name: Optional[str] = None, fallback: Any = None) -> Any:
    """Import lazy de conveniencia."""
    if class_name:
        return _optimizer.lazy_loader.get_class(module_path, class_name, fallback)
    return _optimizer.lazy_loader.load_module(module_path, fallback)

# Decoradores específicos para optimización
def optimize_database_query(func: F) -> F:
    """Optimiza consultas a base de datos con caché y medición."""
    @measure_performance(f"db_query.{func.__name__}")
    @lru_cache(maxsize=100)
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return cast(F, wrapper)

def optimize_ui_operation(func: F) -> F:
    """Optimiza operaciones de UI con debounce y medición."""
    @measure_performance(f"ui_op.{func.__name__}")
    @_optimizer.debounce(delay=0.05)  # 50ms debounce
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return cast(F, wrapper)

def singleton(cls: type) -> type:
    """Decorador singleton optimizado con weak references."""
    instances = {}
    
    @wraps(cls)
    def get_instance(*args, **kwargs):
        key = (cls, args, tuple(sorted(kwargs.items(), key=lambda x: x[0])))  # type: ignore
        if key not in instances:
            instances[key] = cls(*args, **kwargs)
        return instances[key]
    
    return cast(type, get_instance)

class OptimizationReport:
    """Generador de reportes de optimización."""
    
    @staticmethod
    def generate_performance_report() -> str:
        """Genera un reporte de rendimiento del sistema."""
        stats = _optimizer.performance_monitor.get_all_stats()
        if not stats:
            return "No hay datos de rendimiento disponibles."
        
        report = ["🔍 REPORTE DE RENDIMIENTO", "=" * 50]
        
        # Ordenar por tiempo total
        sorted_stats = sorted(
            stats.items(), 
            key=lambda x: x[1].get('total_time', 0), 
            reverse=True
        )
        
        for func_name, func_stats in sorted_stats[:10]:  # Top 10
            report.extend([
                f"📍 {func_name}:",
                f"  • Llamadas: {func_stats.get('calls', 0)}",
                f"  • Tiempo total: {func_stats.get('total_time', 0):.3f}s",
                f"  • Tiempo promedio: {func_stats.get('avg_time', 0):.3f}s",
                f"  • Tiempo mínimo: {func_stats.get('min_time', 0):.3f}s",
                f"  • Tiempo máximo: {func_stats.get('max_time', 0):.3f}s",
                ""
            ])
        
        return "\n".join(report)
    
    @staticmethod
    def get_optimization_suggestions() -> List[str]:
        """Obtiene sugerencias de optimización basadas en métricas."""
        suggestions = []
        stats = _optimizer.performance_monitor.get_all_stats()
        
        for func_name, func_stats in stats.items():
            avg_time = func_stats.get('avg_time', 0)
            calls = func_stats.get('calls', 0)
            
            if avg_time > 0.5:  # Función lenta
                suggestions.append(
                    f"⚠️ Función lenta: {func_name} ({avg_time:.3f}s promedio)"
                )
            
            if calls > 1000:  # Función muy llamada
                suggestions.append(
                    f"🔄 Función muy utilizada: {func_name} ({calls} llamadas) - "
                    "Considerar optimización o caché"
                )
        
        return suggestions

# Exportar las funciones y clases principales
__all__ = [
    'PerformanceMonitor',
    'SmartCache', 
    'LazyLoader',
    'ResourceOptimizer',
    'OptimizationReport',
    'get_optimizer',
    'measure_performance',
    'smart_cache',
    'lazy_import',
    'optimize_database_query',
    'optimize_ui_operation',
    'singleton'
]