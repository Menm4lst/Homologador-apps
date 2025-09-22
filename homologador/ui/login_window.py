"""
Ventana de login para el Homologador de Aplicaciones.
Interfaz gráfica con PyQt6 para autenticación de usuarios.
"""

import sys
import logging
from typing import Dict, Any, cast, Optional
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QPushButton, QMessageBox, QDialog,
    QDialogButtonBox, QFrame, QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread, pyqtSlot
from PyQt6.QtGui import QFont, QPixmap, QIcon

from data.seed import get_auth_service, AuthenticationError
from .simple_theme import apply_simple_theme

logger = logging.getLogger(__name__)


class LoginWorker(QThread):
    """Worker thread para realizar autenticación sin bloquear la UI."""
    
    login_success = pyqtSignal(dict)
    login_failed = pyqtSignal(str)
    
    def __init__(self, username: str, password: str):
        super().__init__()
        self.username = username
        self.password = password
    
    def run(self):
        """Ejecuta la autenticación en segundo plano."""
        try:
            auth_service = get_auth_service()
            user_info = auth_service.authenticate(self.username, self.password)
            self.login_success.emit(user_info)
        except AuthenticationError as e:
            self.login_failed.emit(str(e))
        except Exception as e:
            logger.error(f"Error inesperado en login: {e}")
            self.login_failed.emit("Error interno del sistema")


class ChangePasswordDialog(QDialog):
    """Dialog para cambio obligatorio de contraseña."""
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setWindowTitle("Cambio de Contraseña Requerido")
        self.setFixedSize(400, 250)
        self.setModal(True)
        
        self.setup_ui()
        self.apply_theme()
    
    def apply_theme(self):
        """Aplica el tema simple al diálogo."""
        apply_simple_theme(self)
    
    def setup_ui(self):
        """Configura la interfaz del dialog."""
        layout = QVBoxLayout(self)
        
        # Mensaje informativo
        info_label = QLabel(
            "Su contraseña debe ser cambiada antes de continuar.\n"
            "Por favor ingrese su nueva contraseña:"
        )
        info_label.setWordWrap(True)
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info_label)
        
        # Espaciador
        layout.addItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        
        # Formulario
        form_layout = QFormLayout()
        
        self.old_password_edit = QLineEdit()
        self.old_password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.old_password_edit.setPlaceholderText("Contraseña actual")
        form_layout.addRow("Contraseña actual:", self.old_password_edit)
        
        self.new_password_edit = QLineEdit()
        self.new_password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.new_password_edit.setPlaceholderText("Nueva contraseña (mín. 6 caracteres)")
        form_layout.addRow("Nueva contraseña:", self.new_password_edit)
        
        self.confirm_password_edit = QLineEdit()
        self.confirm_password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_password_edit.setPlaceholderText("Confirmar nueva contraseña")
        form_layout.addRow("Confirmar:", self.confirm_password_edit)
        
        layout.addLayout(form_layout)
        
        # Espaciador
        layout.addItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        
        # Botones
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.validate_and_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        # Focus inicial
        self.old_password_edit.setFocus()
    
    def validate_and_accept(self):
        """Valida las contraseñas antes de aceptar."""
        old_password = self.old_password_edit.text()
        new_password = self.new_password_edit.text()
        confirm_password = self.confirm_password_edit.text()
        
        # Validaciones
        if not old_password:
            QMessageBox.warning(self, "Error", "Ingrese su contraseña actual")
            return
        
        if len(new_password) < 6:
            QMessageBox.warning(self, "Error", "La nueva contraseña debe tener al menos 6 caracteres")
            return
        
        if new_password != confirm_password:
            QMessageBox.warning(self, "Error", "Las contraseñas no coinciden")
            return
        
        self.accept()
    
    def get_passwords(self):
        """Retorna las contraseñas ingresadas."""
        return (
            self.old_password_edit.text(),
            self.new_password_edit.text()
        )


class LoginWindow(QWidget):
    """Ventana principal de login."""
    
    login_successful = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.auth_service = get_auth_service()
        self.login_worker = None
        
        self.setup_ui()
        self.apply_theme()
    
    def apply_theme(self):
        """Aplica el tema simple a la ventana."""
        apply_simple_theme(self)
        self.setObjectName("LoginWindow")
    
    def setup_ui(self):
        """Configura la interfaz de usuario."""
        self.setWindowTitle("Homologador de Aplicaciones - Login")
        self.setFixedSize(450, 350)
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowCloseButtonHint)
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(40, 40, 40, 40)
        
        # Header con título
        self.setup_header(main_layout)
        
        # Formulario de login
        self.setup_login_form(main_layout)
        
        # Botones
        self.setup_buttons(main_layout)
        
        # Status bar
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setObjectName("status")
        main_layout.addWidget(self.status_label)
    
    def setup_header(self, layout):
        """Configura el header con título y logo."""
        header_layout = QVBoxLayout()
        
        # Título principal
        title_label = QLabel("Homologador de Aplicaciones")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setObjectName("title")
        header_layout.addWidget(title_label)
        
        # Subtítulo
        subtitle_label = QLabel("Sistema de Gestión de Homologaciones")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setObjectName("subtitle")
        header_layout.addWidget(subtitle_label)
        
        layout.addLayout(header_layout)
        
        # Separador
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(line)
    
    def setup_login_form(self, layout):
        """Configura el formulario de login."""
        form_frame = QFrame()
        
        form_layout = QFormLayout(form_frame)
        form_layout.setSpacing(15)
        
        # Campo usuario
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("Nombre de usuario")
        self.username_edit.setText("admin")  # Pre-llenar para desarrollo
        form_layout.addRow("Usuario:", self.username_edit)
        
        # Campo contraseña
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_edit.setPlaceholderText("Contraseña")
        self.password_edit.setText("admin123")  # Pre-llenar para desarrollo
        form_layout.addRow("Contraseña:", self.password_edit)
        
        # Conectar Enter para login
        self.password_edit.returnPressed.connect(self.handle_login)
        
        layout.addWidget(form_frame)
    
    def setup_buttons(self, layout):
        """Configura los botones de acción."""
        button_layout = QHBoxLayout()
        
        # Botón de login
        self.login_button = QPushButton("Iniciar Sesión")
        self.login_button.clicked.connect(self.handle_login)
        self.login_button.setDefault(True)
        button_layout.addWidget(self.login_button)
        
        # Botón de salir
        exit_button = QPushButton("Salir")
        exit_button.setProperty("class", "secondary")
        exit_button.clicked.connect(self.close)
        button_layout.addWidget(exit_button)
        
        layout.addLayout(button_layout)
    
    def handle_login(self):
        """Maneja el proceso de login."""
        username = self.username_edit.text().strip()
        password = self.password_edit.text()
        
        # Validaciones básicas
        if not username:
            self.show_status("Ingrese su nombre de usuario", is_error=True)
            self.username_edit.setFocus()
            return
        
        if not password:
            self.show_status("Ingrese su contraseña", is_error=True)
            self.password_edit.setFocus()
            return
        
        # Deshabilitar botón y mostrar loading
        self.login_button.setEnabled(False)
        self.login_button.setText("Autenticando...")
        self.show_status("Verificando credenciales...", is_error=False)
        
        # Ejecutar autenticación en worker thread
        self.login_worker = LoginWorker(username, password)
        self.login_worker.login_success.connect(self.on_login_success)
        self.login_worker.login_failed.connect(self.on_login_failed)
        self.login_worker.start()
    
    @pyqtSlot(dict)
    def on_login_success(self, user_info):
        """Maneja login exitoso."""
        logger.info(f"Login exitoso para: {user_info['username']}")
        
        # Verificar si debe cambiar contraseña
        if user_info.get('must_change_password'):
            if self.handle_password_change(cast(Dict[str, Any], user_info)):
                # Contraseña cambiada exitosamente
                user_info['must_change_password'] = False
            else:
                # Usuario canceló cambio de contraseña
                self.reset_login_state()
                return
        
        # Emitir señal de login exitoso
        self.login_successful.emit(user_info)
        self.close()
    
    @pyqtSlot(str)
    def on_login_failed(self, error_message):
        """Maneja error de login."""
        logger.warning(f"Login fallido: {error_message}")
        self.show_status(cast(str, error_message), is_error=True)
        self.reset_login_state()
        
        # Limpiar contraseña y dar foco
        self.password_edit.clear()
        self.password_edit.setFocus()
    
    def handle_password_change(self, user_info):
        """Maneja el cambio obligatorio de contraseña."""
        dialog = ChangePasswordDialog(self)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            old_password, new_password = dialog.get_passwords()
            
            try:
                success = self.auth_service.change_password(
                    cast(int, user_info['user_id']), 
                    old_password, 
                    new_password
                )
                
                if success:
                    QMessageBox.information(
                        self, 
                        "Éxito", 
                        "Contraseña cambiada exitosamente"
                    )
                    return True
                else:
                    QMessageBox.critical(
                        self, 
                        "Error", 
                        "Error cambiando contraseña"
                    )
                    
            except AuthenticationError as e:
                QMessageBox.critical(self, "Error", str(e))
            except Exception as e:
                logger.error(f"Error cambiando contraseña: {e}")
                QMessageBox.critical(
                    self, 
                    "Error", 
                    "Error interno cambiando contraseña"
                )
        
        return False
    
    def show_status(self, message: str, is_error: bool = False):
        """Muestra un mensaje de estado."""
        self.status_label.setText(message)
        if is_error:
            self.status_label.setProperty("class", "error")
        else:
            self.status_label.setProperty("class", "success")
        # Refrescar el estilo
        style = self.status_label.style()
        if style:
            style.unpolish(self.status_label)
            style.polish(self.status_label)
    
    def reset_login_state(self):
        """Resetea el estado del botón de login."""
        self.login_button.setEnabled(True)
        self.login_button.setText("Iniciar Sesión")
    
    def closeEvent(self, event):
        """Maneja el cierre de la ventana."""
        if self.login_worker and self.login_worker.isRunning():
            self.login_worker.terminate()
            self.login_worker.wait()
        event.accept()


def show_login_window():
    """Función utilitaria para mostrar la ventana de login."""
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    # Configurar tema de la aplicación
    if isinstance(app, QApplication):
        app.setStyle('Fusion')
    
    login_window = LoginWindow()
    login_window.show()
    
    return login_window, app


if __name__ == "__main__":
    # Test de la ventana de login
    from core.settings import setup_logging
    from data.seed import create_seed_data
    
    setup_logging()
    
    try:
        # Crear seed data si no existe
        create_seed_data()
        
        # Mostrar ventana de login
        window, app = show_login_window()
        
        # Conectar señal para mostrar información de login
        def on_login_success(user_info):
            print(f"Login exitoso: {user_info}")
            app.quit()
        
        window.login_successful.connect(on_login_success)
        
        sys.exit(app.exec())
        
    except Exception as e:
        print(f"Error: {e}")
        logger.error(f"Error: {e}")