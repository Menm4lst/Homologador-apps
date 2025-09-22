"""
Módulo de auditoría avanzada para el Homologador de Aplicaciones.
Funciones adicionales para logging y reporting de auditoría.
"""

import logging
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from core.storage import get_audit_repository, get_user_repository

logger = logging.getLogger(__name__)


@dataclass
class AuditEvent:
    """Clase para representar un evento de auditoría."""
    user_id: int
    action: str
    table_name: Optional[str] = None
    record_id: Optional[int] = None
    old_values: Optional[Dict[str, Any]] = None
    new_values: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    session_id: Optional[str] = None
    details: Optional[str] = None


class AuditLogger:
    """Logger especializado para eventos de auditoría."""
    
    def __init__(self):
        self.audit_repo = get_audit_repository()
        self.user_repo = get_user_repository()
    
    def log_login_attempt(self, username: str, success: bool, ip_address: Optional[str] = None, 
                         failure_reason: Optional[str] = None):
        """Registra intentos de login."""
        user = self.user_repo.get_by_username(username)
        user_id = user['id'] if user else None
        
        action = "LOGIN_SUCCESS" if success else "LOGIN_FAILED"
        details = {"username": username}
        
        if not success and failure_reason:
            details["failure_reason"] = failure_reason
        
        if user_id is not None:
            self.audit_repo.log_action(
                user_id=user_id,
                action=action,
                new_values=details,
                ip_address=ip_address
            )
    
    def log_password_change(self, user_id: int, forced: bool = False, ip_address: Optional[str] = None):
        """Registra cambios de contraseña."""
        self.audit_repo.log_action(
            user_id=user_id,
            action="PASSWORD_CHANGED",
            new_values={"forced": forced},
            ip_address=ip_address
        )
    
    def log_data_export(self, user_id: int, export_type: str, record_count: int, 
                       filters: Optional[Dict[str, Any]] = None, ip_address: Optional[str] = None):
        """Registra exportaciones de datos."""
        details = {
            "export_type": export_type,
            "record_count": record_count,
            "filters": filters or {}
        }
        
        self.audit_repo.log_action(
            user_id=user_id,
            action="DATA_EXPORT",
            new_values=details,
            ip_address=ip_address
        )
    
    def log_system_event(self, event_type: str, details: Optional[Dict[str, Any]] = None, 
                        user_id: Optional[int] = None):
        """Registra eventos del sistema."""
        if user_id is not None:
            self.audit_repo.log_action(
                user_id=user_id,
                action=f"SYSTEM_{event_type}",
                new_values=details or {},
            )
    
    def log_permission_denied(self, user_id: int, attempted_action: str, 
                            resource: Optional[str] = None, ip_address: Optional[str] = None):
        """Registra intentos de acceso denegados."""
        details = {
            "attempted_action": attempted_action,
            "resource": resource
        }
        
        self.audit_repo.log_action(
            user_id=user_id,
            action="PERMISSION_DENIED",
            new_values=details,
            ip_address=ip_address
        )


class AuditReporter:
    """Generador de reportes de auditoría."""
    
    def __init__(self):
        self.audit_repo = get_audit_repository()
        self.user_repo = get_user_repository()
    
    def get_login_report(self, days: int = 30) -> Dict[str, Any]:
        """Genera reporte de logins en los últimos N días."""
        date_from = (datetime.now() - timedelta(days=days)).isoformat()
        
        filters = {
            'action': 'LOGIN_SUCCESS',
            'date_from': date_from
        }
        
        successful_logins = self.audit_repo.get_audit_trail(filters)
        
        filters['action'] = 'LOGIN_FAILED'
        failed_logins = self.audit_repo.get_audit_trail(filters)
        
        # Estadísticas por usuario
        user_stats: Dict[int, Dict[str, Any]] = {}
        
        for login in successful_logins:
            user_id = login['user_id']
            if user_id not in user_stats:
                user_stats[user_id] = {
                    'username': login['username'],
                    'successful_logins': 0,
                    'failed_logins': 0,
                    'last_login': None
                }
            
            user_stats[user_id]['successful_logins'] += 1
            
            if not user_stats[user_id]['last_login'] or login['timestamp'] > user_stats[user_id]['last_login']:
                user_stats[user_id]['last_login'] = login['timestamp']
        
        for login in failed_logins:
            user_id = login['user_id']
            if user_id and user_id in user_stats:
                user_stats[user_id]['failed_logins'] += 1
        
        return {
            'period_days': days,
            'total_successful_logins': len(successful_logins),
            'total_failed_logins': len(failed_logins),
            'unique_users': len(user_stats),
            'user_statistics': list(user_stats.values()),
            'generated_at': datetime.now().isoformat()
        }
    
    def get_user_activity_report(self, user_id: int, days: int = 30) -> Dict[str, Any]:
        """Genera reporte de actividad de un usuario específico."""
        date_from = (datetime.now() - timedelta(days=days)).isoformat()
        
        filters = {
            'user_id': user_id,
            'date_from': date_from
        }
        
        activities = self.audit_repo.get_audit_trail(filters)
        
        # Categorizar actividades
        activity_counts: Dict[str, int] = {}
        recent_activities: List[Any] = []
        
        for activity in activities:
            action = activity['action']
            activity_counts[action] = activity_counts.get(action, 0) + 1
            
            # Guardar las 10 más recientes
            if len(recent_activities) < 10:
                recent_activities.append({
                    'action': action,
                    'timestamp': activity['timestamp'],
                    'table_name': activity['table_name'] if 'table_name' in activity else None,
                    'record_id': activity['record_id'] if 'record_id' in activity else None
                })
        
        user = self.user_repo.get_by_id(user_id)
        
        return {
            'user_id': user_id,
            'username': user['username'] if user else 'Desconocido',
            'period_days': days,
            'total_activities': len(activities),
            'activity_breakdown': activity_counts,
            'recent_activities': recent_activities,
            'generated_at': datetime.now().isoformat()
        }
    
    def get_data_changes_report(self, table_name: str = 'homologations', 
                               days: int = 30) -> Dict[str, Any]:
        """Genera reporte de cambios en los datos."""
        date_from = (datetime.now() - timedelta(days=days)).isoformat()
        
        filters = {
            'table_name': table_name,
            'date_from': date_from
        }
        
        changes = self.audit_repo.get_audit_trail(filters)
        
        # Estadísticas por tipo de acción
        action_stats: Dict[str, int] = {}
        records_affected: set[int] = set()
        users_involved: set[int] = set()
        
        for change in changes:
            action = change['action']
            action_stats[action] = action_stats.get(action, 0) + 1
            
            if change['record_id']:
                records_affected.add(change['record_id'])
            
            if change['user_id']:
                users_involved.add(change['user_id'])
        
        return {
            'table_name': table_name,
            'period_days': days,
            'total_changes': len(changes),
            'action_breakdown': action_stats,
            'unique_records_affected': len(records_affected),
            'users_involved': len(users_involved),
            'changes_by_day': self._group_changes_by_day([dict(change) for change in changes]),
            'generated_at': datetime.now().isoformat()
        }
    
    def _group_changes_by_day(self, changes: List[Dict[str, Any]]) -> Dict[str, int]:
        """Agrupa cambios por día."""
        daily_counts = {}
        
        for change in changes:
            try:
                timestamp = change['timestamp']
                date_key = timestamp.split('T')[0]  # Solo la fecha
                daily_counts[date_key] = daily_counts.get(date_key, 0) + 1
            except:
                continue
        
        return daily_counts
    
    def get_security_report(self, days: int = 7) -> Dict[str, Any]:
        """Genera reporte de seguridad con eventos sospechosos."""
        date_from = (datetime.now() - timedelta(days=days)).isoformat()
        
        # Buscar intentos de login fallidos
        failed_login_filters = {
            'action': 'LOGIN_FAILED',
            'date_from': date_from
        }
        
        failed_logins = self.audit_repo.get_audit_trail(failed_login_filters)
        
        # Buscar accesos denegados
        denied_filters = {
            'action': 'PERMISSION_DENIED',
            'date_from': date_from
        }
        
        denied_accesses = self.audit_repo.get_audit_trail(denied_filters)
        
        # Análisis de patrones sospechosos
        ip_failed_attempts = {}
        user_failed_attempts = {}
        
        for login in failed_logins:
            ip = login['ip_address'] if 'ip_address' in login and login['ip_address'] else 'Unknown'
            user = login['username'] if 'username' in login and login['username'] else 'Unknown'
            
            ip_failed_attempts[ip] = ip_failed_attempts.get(ip, 0) + 1
            user_failed_attempts[user] = user_failed_attempts.get(user, 0) + 1
        
        # IPs con múltiples intentos fallidos
        suspicious_ips = {ip: count for ip, count in ip_failed_attempts.items() if count >= 3}
        
        # Usuarios con múltiples fallos
        suspicious_users = {user: count for user, count in user_failed_attempts.items() if count >= 5}
        
        return {
            'period_days': days,
            'total_failed_logins': len(failed_logins),
            'total_denied_accesses': len(denied_accesses),
            'suspicious_ips': suspicious_ips,
            'suspicious_users': suspicious_users,
            'ip_attempt_summary': ip_failed_attempts,
            'user_attempt_summary': user_failed_attempts,
            'generated_at': datetime.now().isoformat()
        }


class AuditAnalyzer:
    """Analizador de patrones en los datos de auditoría."""
    
    def __init__(self):
        self.audit_repo = get_audit_repository()
    
    def detect_unusual_activity(self, user_id: int, days: int = 7) -> List[Dict[str, Any]]:
        """Detecta actividad inusual para un usuario."""
        date_from = (datetime.now() - timedelta(days=days)).isoformat()
        
        filters = {
            'user_id': user_id,
            'date_from': date_from
        }
        
        activities = self.audit_repo.get_audit_trail(filters)
        
        anomalies: List[Dict[str, Any]] = []
        
        # Detectar actividad fuera del horario normal (ejemplo: noches/fines de semana)
        for activity in activities:
            try:
                timestamp = datetime.fromisoformat(activity['timestamp'].replace('Z', '+00:00'))
                
                # Actividad nocturna (22:00 - 06:00)
                if timestamp.hour >= 22 or timestamp.hour <= 6:
                    anomalies.append({
                        'type': 'NIGHT_ACTIVITY',
                        'timestamp': activity['timestamp'],
                        'action': activity['action'],
                        'severity': 'LOW'
                    })
                
                # Actividad en fin de semana
                if timestamp.weekday() >= 5:  # Sábado y domingo
                    anomalies.append({
                        'type': 'WEEKEND_ACTIVITY',
                        'timestamp': activity['timestamp'],
                        'action': activity['action'],
                        'severity': 'MEDIUM'
                    })
                
            except:
                continue
        
        # Detectar acciones múltiples en poco tiempo (posible script)
        action_times: Dict[str, List[str]] = {}
        for activity in activities:
            action = activity['action']
            if action not in action_times:
                action_times[action] = []
            action_times[action].append(activity['timestamp'])
        
        for action, timestamps in action_times.items():
            if len(timestamps) >= 10:  # 10 o más acciones del mismo tipo
                anomalies.append({
                    'type': 'RAPID_ACTIONS',
                    'action': action,
                    'count': len(timestamps),
                    'severity': 'HIGH'
                })
        
        return anomalies
    
    def get_usage_patterns(self, days: int = 30) -> Dict[str, Any]:
        """Analiza patrones de uso del sistema."""
        date_from = (datetime.now() - timedelta(days=days)).isoformat()
        
        filters = {
            'date_from': date_from
        }
        
        activities = self.audit_repo.get_audit_trail(filters)
        
        # Análisis por hora del día
        hourly_activity = [0] * 24
        daily_activity: Dict[str, int] = {}
        user_activity: Dict[int, int] = {}
        
        for activity in activities:
            try:
                timestamp = datetime.fromisoformat(activity['timestamp'].replace('Z', '+00:00'))
                
                # Por hora
                hourly_activity[timestamp.hour] += 1
                
                # Por día
                date_key = timestamp.strftime('%Y-%m-%d')
                daily_activity[date_key] = daily_activity.get(date_key, 0) + 1
                
                # Por usuario
                user_id = activity['user_id']
                if user_id:
                    user_activity[user_id] = user_activity.get(user_id, 0) + 1
                
            except:
                continue
        
        # Encontrar hora pico
        peak_hour = hourly_activity.index(max(hourly_activity))
        
        # Usuarios más activos
        top_users = sorted(user_activity.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            'period_days': days,
            'total_activities': len(activities),
            'peak_hour': peak_hour,
            'hourly_distribution': hourly_activity,
            'daily_activity': daily_activity,
            'top_active_users': top_users,
            'average_daily_activities': sum(daily_activity.values()) / len(daily_activity) if daily_activity else 0,
            'generated_at': datetime.now().isoformat()
        }


# Instancias globales
_audit_logger = None
_audit_reporter = None
_audit_analyzer = None


def get_audit_logger() -> AuditLogger:
    """Retorna la instancia global del logger de auditoría."""
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = AuditLogger()
    return _audit_logger


def get_audit_reporter() -> AuditReporter:
    """Retorna la instancia global del reportero de auditoría."""
    global _audit_reporter
    if _audit_reporter is None:
        _audit_reporter = AuditReporter()
    return _audit_reporter


def get_audit_analyzer() -> AuditAnalyzer:
    """Retorna la instancia global del analizador de auditoría."""
    global _audit_analyzer
    if _audit_analyzer is None:
        _audit_analyzer = AuditAnalyzer()
    return _audit_analyzer


if __name__ == "__main__":
    # Test del sistema de auditoría
    from core.settings import setup_logging
    from data.seed import create_seed_data
    
    setup_logging()
    
    print("=== Test del Sistema de Auditoría Avanzada ===")
    
    try:
        # Crear seed data
        create_seed_data()
        
        # Test de logger
        audit_logger = get_audit_logger()
        audit_logger.log_system_event("TEST", {"description": "Test del sistema de auditoría"})
        print("✓ Logger de auditoría funcionando")
        
        # Test de reporter
        reporter = get_audit_reporter()
        login_report = reporter.get_login_report(7)
        print(f"✓ Reporte de logins generado: {login_report['total_successful_logins']} exitosos")
        
        # Test de analyzer
        analyzer = get_audit_analyzer()
        usage_patterns = analyzer.get_usage_patterns(7)
        print(f"✓ Análisis de patrones: {usage_patterns['total_activities']} actividades")
        
        print("\n=== Test completado exitosamente ===")
        
    except Exception as e:
        print(f"Error en test: {e}")
        logger.error(f"Error en test: {e}")