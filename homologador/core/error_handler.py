"""
Sistema centralizado de manejo de errores para la aplicación de homologaciones.
"""
import traceback
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from PyQt6.QtWidgets import QMessageBox, QWidget
from PyQt6.QtCore import QObject, pyqtSignal


class ErrorSeverity:
    """Niveles de severidad de errores."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ErrorHandler(QObject):
    """
    Manejador centralizado de errores con logging y notificaciones al usuario.
    """
    error_occurred = pyqtSignal(str, str)  # severity, message
    
    def __init__(self):
        super().__init__()
        self.setup_logging()
        
    def setup_logging(self):
        """Configura el sistema de logging."""
        try:
            # Crear directorio de logs si no existe
            log_dir = Path("logs")
            log_dir.mkdir(exist_ok=True)
            
            # Configurar el logger
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                handlers=[
                    logging.FileHandler(log_dir / "homologaciones.log"),
                    logging.StreamHandler()  # También en consola
                ]
            )
            
            self.logger = logging.getLogger("HomologacionesApp")
            
        except Exception as e:
            print(f"Error configurando logging: {e}")
            # Crear logger básico si falla
            self.logger = logging.getLogger("HomologacionesApp")
    
    def handle_error(self, 
                    error: Exception, 
                    severity: str = ErrorSeverity.MEDIUM,
                    context: str = "Operación desconocida",
                    show_user: bool = True,
                    parent_widget: Optional[QWidget] = None) -> Dict[str, Any]:
        """
        Maneja un error de forma centralizada.
        
        Args:
            error: La excepción que ocurrió
            severity: Nivel de severidad del error
            context: Contexto donde ocurrió el error
            show_user: Si mostrar mensaje al usuario
            parent_widget: Widget padre para el diálogo
            
        Returns:
            Dict con información del error procesado
        """
        try:
            # Obtener información del error
            error_info = self._extract_error_info(error, context)
            
            # Registrar en logs
            self._log_error(error_info, severity)
            
            # Notificar al usuario si es necesario
            if show_user:
                self._show_user_notification(error_info, severity, parent_widget)
                
            # Emitir señal para otros componentes
            self.error_occurred.emit(severity, error_info['message'])
            
            return error_info
            
        except Exception as handler_error:
            # Error en el manejador de errores - fallback básico
            print(f"Error en ErrorHandler: {handler_error}")
            if show_user and parent_widget:
                QMessageBox.critical(
                    parent_widget,
                    "Error crítico",
                    f"Ocurrió un error inesperado: {str(error)}"
                )
            return {'error': str(error), 'handled': False}
    
    def _extract_error_info(self, error: Exception, context: str) -> Dict[str, Any]:
        """Extrae información detallada del error."""
        return {
            'timestamp': datetime.now().isoformat(),
            'error_type': type(error).__name__,
            'message': str(error),
            'context': context,
            'traceback': traceback.format_exc(),
            'handled': True
        }
    
    def _log_error(self, error_info: Dict[str, Any], severity: str):
        """Registra el error en los logs."""
        log_message = (
            f"[{severity}] {error_info['context']}: "
            f"{error_info['error_type']} - {error_info['message']}"
        )
        
        if severity == ErrorSeverity.CRITICAL:
            self.logger.critical(log_message)
            self.logger.critical(f"Traceback:\n{error_info['traceback']}")
        elif severity == ErrorSeverity.HIGH:
            self.logger.error(log_message)
            self.logger.error(f"Traceback:\n{error_info['traceback']}")
        elif severity == ErrorSeverity.MEDIUM:
            self.logger.warning(log_message)
        else:  # LOW
            self.logger.info(log_message)
    
    def _show_user_notification(self, 
                              error_info: Dict[str, Any], 
                              severity: str,
                              parent_widget: Optional[QWidget]):
        """Muestra notificación apropiada al usuario."""
        if not parent_widget:
            return
            
        title, icon = self._get_message_config(severity)
        
        # Generar mensaje amigable para el usuario
        user_message = self._generate_user_message(error_info, severity)
        
        # Mostrar mensaje según severidad
        if severity == ErrorSeverity.CRITICAL:
            QMessageBox.critical(parent_widget, title, user_message)
        elif severity == ErrorSeverity.HIGH:
            QMessageBox.critical(parent_widget, title, user_message)
        elif severity == ErrorSeverity.MEDIUM:
            QMessageBox.warning(parent_widget, title, user_message)
        else:  # LOW
            QMessageBox.information(parent_widget, title, user_message)
    
    def _get_message_config(self, severity: str) -> tuple[str, str]:
        """Obtiene configuración del mensaje según severidad."""
        config = {
            ErrorSeverity.CRITICAL: ("Error Crítico", "critical"),
            ErrorSeverity.HIGH: ("Error", "error"), 
            ErrorSeverity.MEDIUM: ("Advertencia", "warning"),
            ErrorSeverity.LOW: ("Información", "info")
        }
        return config.get(severity, ("Error", "error"))
    
    def _generate_user_message(self, error_info: Dict[str, Any], severity: str) -> str:
        """Genera un mensaje amigable para el usuario."""
        context = error_info['context']
        error_type = error_info['error_type']
        message = error_info['message']
        
        # Mensajes específicos para errores comunes
        if "DatabaseError" in error_type or "sqlite" in message.lower():
            return (
                f"Error de base de datos durante: {context}\n\n"
                f"La operación no pudo completarse debido a un problema "
                f"con la base de datos. Por favor, inténtelo nuevamente."
            )
        
        elif "FileNotFound" in error_type:
            return (
                f"Archivo no encontrado durante: {context}\n\n"
                f"El sistema no pudo localizar un archivo necesario. "
                f"Verifique que todos los archivos estén en su lugar."
            )
        
        elif "PermissionError" in error_type:
            return (
                f"Error de permisos durante: {context}\n\n"
                f"La aplicación no tiene los permisos necesarios "
                f"para completar esta operación."
            )
        
        elif "ConnectionError" in error_type or "network" in message.lower():
            return (
                f"Error de conexión durante: {context}\n\n"
                f"No se pudo establecer conexión. Verifique su "
                f"conexión de red e inténtelo nuevamente."
            )
        
        else:
            # Mensaje genérico
            if severity in [ErrorSeverity.CRITICAL, ErrorSeverity.HIGH]:
                return (
                    f"Error durante: {context}\n\n"
                    f"Ocurrió un error inesperado que impidió completar "
                    f"la operación. Si el problema persiste, reinicie la aplicación.\n\n"
                    f"Detalles técnicos: {message}"
                )
            else:
                return (
                    f"Problema durante: {context}\n\n"
                    f"{message}"
                )
    
    def log_info(self, message: str, context: str = "General"):
        """Registra información general."""
        self.logger.info(f"{context}: {message}")
    
    def log_warning(self, message: str, context: str = "General"):
        """Registra una advertencia."""
        self.logger.warning(f"{context}: {message}")


# Instancia global del manejador de errores
_error_handler = None


def get_error_handler() -> ErrorHandler:
    """Obtiene la instancia global del manejador de errores."""
    global _error_handler
    if _error_handler is None:
        _error_handler = ErrorHandler()
    return _error_handler


def handle_error(error: Exception, 
                severity: str = ErrorSeverity.MEDIUM,
                context: str = "Operación desconocida", 
                show_user: bool = True,
                parent_widget: Optional[QWidget] = None) -> Dict[str, Any]:
    """
    Función de conveniencia para manejar errores.
    
    Args:
        error: La excepción que ocurrió
        severity: Nivel de severidad 
        context: Contexto donde ocurrió
        show_user: Si mostrar al usuario
        parent_widget: Widget padre para diálogo
        
    Returns:
        Información del error procesado
    """
    return get_error_handler().handle_error(
        error, severity, context, show_user, parent_widget
    )


def log_info(message: str, context: str = "General"):
    """Función de conveniencia para registrar información."""
    get_error_handler().log_info(message, context)


def log_warning(message: str, context: str = "General"):
    """Función de conveniencia para registrar advertencias."""
    get_error_handler().log_warning(message, context)