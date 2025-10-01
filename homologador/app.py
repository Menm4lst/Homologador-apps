#!/usr/bin/env python3
"""
Homologador de Aplicaciones - Punto de entrada principal.
Aplicación de escritorio para gestión de homologaciones corporativas.

Autor: Sistema Homologador
Versión: 1.0.0
Fecha: 2024
"""


# Agregar el directorio actual al path para imports relativos

from typing import Any, Dict, Optional, cast
import logging
import os
import sys
import traceback
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from PyQt6.QtCore import Qt, QTimer
    from PyQt6.QtGui import QColor, QFont, QPainter, QPixmap
    from PyQt6.QtWidgets import QApplication, QMessageBox, QSplashScreen
except ImportError as e:
    print("Error: PyQt6 no está instalado.")
    print("Instale las dependencias con: pip install -r requirements.txt")
    sys.exit(1)



from .core.audit import get_audit_logger
from .core.backup_system import get_backup_manager
from .core.settings import get_settings, setup_logging
from .core.storage import get_database_manager
from .data.seed import create_seed_data, get_auth_service
from .ui.details_view import HomologationDetailsDialog
from .ui.final_login import FinalLoginWindow
from .ui.homologation_form import HomologationFormDialog
from .ui.icons import apply_icons_to_application
from .ui.main_window import MainWindow
from .ui.theme import apply_dark_theme
from .ui.theme_effects import WindowCustomizer, apply_theme_customizations
logger = logging.getLogger(__name__)

# Información de la aplicación
APP_NAME = "Homologador de Aplicaciones"
APP_VERSION = "1.0.0"
APP_AUTHOR = "Sistema Corporativo"
APP_DESCRIPTION = "Sistema de gestión de homologaciones de aplicaciones"


class HomologadorApplication:
    """Clase principal de la aplicación."""
    
    def __init__(self):
        self.app: Optional[QApplication] = None
        self.login_window: Optional[FinalLoginWindow] = None
        self.main_window: Optional[MainWindow] = None
        self.current_user: Optional[Dict[str, Any]] = None
        self.settings = get_settings()
        self.audit_logger = get_audit_logger()
        self.backup_manager = None
        
    def initialize(self):
        """Inicializa la aplicación."""
        try:
            # Configurar logging
            setup_logging()
            logger.info(f"Iniciando {APP_NAME} v{APP_VERSION}")
            
            # Crear aplicación Qt
            self.app = QApplication(sys.argv)
            self.app.setApplicationName(APP_NAME)
            self.app.setApplicationVersion(APP_VERSION)
            self.app.setOrganizationName(APP_AUTHOR)
            
            # Configurar estilo
            self.setup_application_style()
            
            # Mostrar splash screen
            splash = self.create_splash_screen()
            splash.show()
            self.app.processEvents()
            
            # Inicializar base de datos
            splash.showMessage("Inicializando base de datos...", Qt.AlignmentFlag.AlignBottom, QColor("white"))
            self.app.processEvents()
            
            db_manager = get_database_manager()
            logger.info(f"Base de datos inicializada en: {db_manager.db_path}")
            
            # Crear datos iniciales si es necesario
            splash.showMessage("Verificando datos iniciales...", Qt.AlignmentFlag.AlignBottom, QColor("white"))
            self.app.processEvents()
            
            create_seed_data()
            
            # Inicializar sistema de respaldos
            splash.showMessage("Inicializando sistema de respaldos...", Qt.AlignmentFlag.AlignBottom, QColor("white"))
            self.app.processEvents()
            
            self.backup_manager = get_backup_manager()
            logger.info("Sistema de respaldos inicializado")
            
            # Log de inicio del sistema
            self.audit_logger.log_system_event("STARTUP", {
                "version": APP_VERSION,
                "db_path": db_manager.db_path
            })
            
            # Cerrar splash inmediatamente
            splash.close()
            
            return True
            
        except Exception as e:
            error_msg = f"Error inicializando aplicación: {e}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            
            if self.app:
                QMessageBox.critical(None, "Error de Inicialización", error_msg)
            else:
                print(error_msg)
            
            return False
    
    def setup_application_style(self):
        """Configura el estilo global de la aplicación."""
        if self.app is None:
            return
            
        self.app.setStyle('Fusion')
        
        # NO aplicar ningún stylesheet global para evitar conflictos
        # La ventana de login aplicará sus propios estilos
        
        # Configurar fuente por defecto
        font = QFont("Arial", 10)
        self.app.setFont(font)
    
    def create_splash_screen(self) -> QSplashScreen:
        """Crea la pantalla de splash con tema oscuro."""
        # Crear imagen de splash oscura
        pixmap = QPixmap(400, 300)
        pixmap.fill(QColor("#1e1e1e"))  # Fondo oscuro
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Título principal
        title_font = QFont("Segoe UI", 18, QFont.Weight.Bold)
        painter.setFont(title_font)
        painter.setPen(QColor("#ffffff"))  # Texto blanco
        title_rect = pixmap.rect()
        title_rect.setTop(title_rect.center().y() - 50)
        painter.drawText(title_rect, Qt.AlignmentFlag.AlignCenter, APP_NAME)
        
        # Versión
        version_font = QFont("Segoe UI", 10)
        painter.setFont(version_font)
        painter.setPen(QColor("#e0e0e0"))  # Texto gris claro
        version_rect = pixmap.rect()
        version_rect.setTop(version_rect.center().y() + 30)
        painter.drawText(version_rect, Qt.AlignmentFlag.AlignCenter, f"Versión {APP_VERSION}")
        
        # Descripción
        painter.setPen(QColor("#a0a0a0"))  # Texto gris más claro
        desc_rect = pixmap.rect()
        desc_rect.setTop(desc_rect.center().y() + 50)
        painter.drawText(desc_rect, Qt.AlignmentFlag.AlignCenter, APP_DESCRIPTION)
        
        # Borde elegante
        painter.setPen(QColor("#555555"))
        painter.drawRect(pixmap.rect().adjusted(2, 2, -2, -2))
        
        painter.end()
        
        splash = QSplashScreen(pixmap)
        splash.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.SplashScreen)
        
        return splash
    
    def show_login(self):
        """Muestra la ventana de login."""
        try:
            self.login_window = FinalLoginWindow()
            self.login_window.login_successful.connect(self.on_login_successful)
            
            # Mostrar ventana de login
            self.login_window.show()
            self.login_window.raise_()  # Asegurar que esté en primer plano
            self.login_window.activateWindow()  # Activar ventana
            
            logger.info("Ventana de login mostrada")
            
        except Exception as e:
            error_msg = f"Error mostrando login: {e}"
            logger.error(error_msg)
            QMessageBox.critical(None, "Error", error_msg)
    
    def on_login_successful(self, user_info: Dict[str, Any]) -> None:
        """Maneja login exitoso."""
        try:
            self.current_user = user_info
            logger.info(f"Login exitoso para usuario: {user_info['username']}")
            
            # Cerrar ventana de login
            if self.login_window:
                self.login_window.close()
                self.login_window = None
            
            # Mostrar ventana principal
            self.show_main_window()
            
        except Exception as e:
            error_msg = f"Error después del login: {e}"
            logger.error(error_msg)
            QMessageBox.critical(None, "Error", error_msg)
    
    def show_main_window(self) -> None:
        """Muestra la ventana principal."""
        try:
            if self.current_user is None:
                logger.error("No hay usuario autenticado para abrir la ventana principal")
                return

            self.main_window = MainWindow(cast(Dict[str, Any], self.current_user))
            
            # Conectar integraciones entre ventanas
            self.setup_main_window_connections()
            
            # Aplicar efectos visuales
            WindowCustomizer.setup_main_window_effects(self.main_window)
            
            self.main_window.show()
            
            logger.info("Ventana principal mostrada")
            
        except Exception as e:
            error_msg = f"Error mostrando ventana principal: {e}"
            logger.error(error_msg)
            QMessageBox.critical(None, "Error", error_msg)
    
    def setup_main_window_connections(self):
        """Configura las conexiones de la ventana principal."""
        if not self.main_window:
            return
        
        # Reemplazar métodos placeholder con implementaciones reales
        self.main_window.new_homologation = self.show_new_homologation_form
        self.main_window.edit_homologation = self.show_edit_homologation_form
        self.main_window.view_details = self.show_homologation_details
    
    def show_new_homologation_form(self):
        """Muestra formulario para nueva homologación."""
        try:
            if self.current_user is None:
                logger.error("No hay usuario logueado")
                return
                
            dialog = HomologationFormDialog(
                parent=self.main_window,
                user_info=cast(Dict[str, Any], self.current_user) if self.current_user else {}
            )
            
            # Aplicar efectos de diálogo
            WindowCustomizer.setup_dialog_effects(dialog)
            
            dialog.homologation_saved.connect(self.on_homologation_saved)
            dialog.exec()
            
        except Exception as e:
            error_msg = f"Error mostrando formulario: {e}"
            logger.error(error_msg)
            QMessageBox.critical(self.main_window, "Error", error_msg)
    
    def show_edit_homologation_form(self):
        """Muestra formulario para editar homologación."""
        try:
            if not self.main_window:
                return
            
            record = self.main_window.table_widget.get_selected_record()
            if not record:
                QMessageBox.warning(self.main_window, "Advertencia", "Seleccione una homologación para editar")
                return
            
            dialog = HomologationFormDialog(
                parent=self.main_window,
                homologation_data=cast(Dict[str, Any], record) if record else {},
                user_info=cast(Dict[str, Any], self.current_user) if self.current_user else {}
            )
            
            # Aplicar efectos de diálogo
            WindowCustomizer.setup_dialog_effects(dialog)
            
            dialog.homologation_saved.connect(self.on_homologation_saved)
            dialog.exec()
            
        except Exception as e:
            error_msg = f"Error mostrando formulario de edición: {e}"
            logger.error(error_msg)
            QMessageBox.critical(self.main_window, "Error", error_msg)
    
    def show_homologation_details(self):
        """Muestra detalles de homologación."""
        try:
            if not self.main_window or self.current_user is None:
                if self.current_user is None:
                    logger.error("No hay usuario logueado")
                return
            
            record = self.main_window.table_widget.get_selected_record()
            if not record:
                QMessageBox.warning(self.main_window, "Advertencia", "Seleccione una homologación para ver detalles")
                return
            
            dialog = HomologationDetailsDialog(
                parent=self.main_window,
                homologation_data=cast(Dict[str, Any], record) if record else {},
                user_info=cast(Dict[str, Any], self.current_user) if self.current_user else {}
            )
            
            dialog.edit_requested.connect(self.on_edit_requested_from_details)
            dialog.exec()
            
        except Exception as e:
            error_msg = f"Error mostrando detalles: {e}"
            logger.error(error_msg)
            QMessageBox.critical(self.main_window, "Error", error_msg)
    
    def on_homologation_saved(self, homologation_id):
        """Maneja homologación guardada."""
        if self.main_window:
            self.main_window.refresh_data()
    
    def on_edit_requested_from_details(self, homologation_data):
        """Maneja solicitud de edición desde vista de detalles."""
        try:
            if self.current_user is None:
                logger.error("No hay usuario logueado")
                return
                
            dialog = HomologationFormDialog(
                parent=self.main_window,
                homologation_data=cast(Dict[str, Any], homologation_data) if homologation_data else {},
                user_info=cast(Dict[str, Any], self.current_user) if self.current_user else {}
            )
            
            dialog.homologation_saved.connect(self.on_homologation_saved)
            dialog.exec()
            
        except Exception as e:
            error_msg = f"Error en edición desde detalles: {e}"
            logger.error(error_msg)
            QMessageBox.critical(self.main_window, "Error", error_msg)
    
    def run(self):
        """Ejecuta la aplicación."""
        if not self.app:
            return 1
        
        try:
            # Mostrar login
            self.show_login()
            
            # Ejecutar loop principal
            result = self.app.exec()
            
            # Log de cierre
            self.audit_logger.log_system_event("SHUTDOWN", {"version": APP_VERSION})
            logger.info("Aplicación cerrada")
            
            return result
            
        except Exception as e:
            error_msg = f"Error ejecutando aplicación: {e}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            
            QMessageBox.critical(None, "Error Fatal", error_msg)
            return 1
    
    def cleanup(self):
        """Limpia recursos antes del cierre."""
        try:
            if self.current_user:
                auth_service = get_auth_service()
                auth_service.logout(cast(Dict[str, Any], self.current_user).get('user_id'))
            
            logger.info("Limpieza de recursos completada")
            
        except Exception as e:
            logger.error(f"Error en limpieza: {e}")


def show_error_dialog(title: str, message: str):
    """Muestra un dialog de error independiente."""
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    
    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Icon.Critical)
    msg_box.setWindowTitle(title)
    msg_box.setText(message)
    msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
    msg_box.exec()


def check_dependencies():
    """Verifica que todas las dependencias estén instaladas."""
    missing_deps = []
    
    try:
        import PyQt6
    except ImportError:
        missing_deps.append("PyQt6")
    
    try:
        import argon2
    except ImportError:
        missing_deps.append("argon2-cffi")
    
    try:
        import portalocker
    except ImportError:
        missing_deps.append("portalocker")
    
    try:
        import pandas
    except ImportError:
        missing_deps.append("pandas")
    
    if missing_deps:
        error_msg = f"Dependencias faltantes: {', '.join(cast(list[str], missing_deps))}\n\n"
        error_msg += "Instale las dependencias con:\n"
        error_msg += "pip install -r requirements.txt"
        
        print(error_msg)
        show_error_dialog("Dependencias Faltantes", error_msg)
        return False
    
    return True


def main():
    """Función principal de entrada."""
    print(f"=== {APP_NAME} v{APP_VERSION} ===")
    print("Iniciando aplicación...")
    
    try:
        # Verificar dependencias
        if not check_dependencies():
            return 1
        
        # Crear y ejecutar aplicación
        homologador = HomologadorApplication()
        
        if not homologador.initialize():
            return 1
        
        exit_code = homologador.run()
        
        # Limpieza
        homologador.cleanup()
        
        return exit_code
        
    except KeyboardInterrupt:
        print("\nAplicación interrumpida por el usuario")
        return 0
        
    except Exception as e:
        error_msg = f"Error fatal no manejado: {e}"
        print(error_msg)
        print(traceback.format_exc())
        
        show_error_dialog("Error Fatal", error_msg)
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)