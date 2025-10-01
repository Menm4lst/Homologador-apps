"""
Ventana de login final con estilo básico y compatible.
"""

import logging
import sys

from ..data.seed import AuthenticationError, get_auth_service
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QPalette
from PyQt6.QtWidgets import (QApplication, QFormLayout, QFrame, QHBoxLayout,
                             QLabel, QLineEdit, QMessageBox, QPushButton,
                             QVBoxLayout, QWidget)

# Importar sistema de notificaciones
try:
    from ui.notification_system import (send_error, send_info, send_success,
                                        send_system, send_warning)
    NOTIFICATIONS_AVAILABLE = True
except ImportError:
    NOTIFICATIONS_AVAILABLE = False
    print("Sistema de notificaciones no disponible")

logger = logging.getLogger(__name__)

class FinalLoginWindow(QWidget):
    """Ventana de login final con estilo compatible."""
    
    login_successful = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.auth_service = get_auth_service()
        self.setup_ui()
        self.apply_compatible_styles()
    
    def setup_ui(self):
        """Configura la interfaz de usuario."""
        self.setWindowTitle("EL OMO LOGADOR 🥵 - Login")
        self.resize(450, 350)
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # Título
        title = QLabel("EL OMO LOGADOR 🥵")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Subtítulo
        subtitle = QLabel("Homologador de Aplicaciones")
        subtitle.setFont(QFont("Arial", 10))
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        main_layout.addWidget(title)
        main_layout.addWidget(subtitle)
        
        # Separador
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        main_layout.addWidget(separator)
        
        # Formulario
        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        
        # Usuario
        self.username_edit = QLineEdit()
        self.username_edit.setText("admin")
        user_label = QLabel("Usuario:")
        user_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        form_layout.addRow(user_label, self.username_edit)
        
        # Contraseña
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_edit.setText("admin123")
        self.password_edit.returnPressed.connect(self.handle_login)
        pass_label = QLabel("Contraseña:")
        pass_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        form_layout.addRow(pass_label, self.password_edit)
        
        main_layout.addLayout(form_layout)
        
        # Botones
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        self.login_button = QPushButton("Iniciar Sesión")
        self.login_button.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.login_button.clicked.connect(self.handle_login)
        button_layout.addWidget(self.login_button)
        
        exit_button = QPushButton("Salir")
        exit_button.setFont(QFont("Arial", 10))
        exit_button.clicked.connect(self.close)
        button_layout.addWidget(exit_button)
        
        main_layout.addLayout(button_layout)
        
        # Status
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setFont(QFont("Arial", 10))
        main_layout.addWidget(self.status_label)
    
    def apply_compatible_styles(self):
        """Aplica estilos básicos y compatibles."""
        # Establecer el fondo blanco
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(240, 240, 240))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(0, 0, 0))
        palette.setColor(QPalette.ColorRole.Base, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.Text, QColor(0, 0, 0))
        self.setPalette(palette)
        
        # Estilos simples e independientes
        self.username_edit.setStyleSheet("background-color: white; color: black; padding: 5px;")
        self.password_edit.setStyleSheet("background-color: white; color: black; padding: 5px;")
        self.login_button.setStyleSheet("background-color: #0066cc; color: white; padding: 8px;")
        # Aplicar estilo al botón de salir directamente
        exit_buttons = [btn for btn in self.findChildren(QPushButton) if btn != self.login_button]
        if exit_buttons:
            exit_buttons[0].setStyleSheet("background-color: #f0f0f0; color: black; padding: 8px;")
        self.status_label.setStyleSheet("color: #cc0000; font-weight: bold;")
    
    def handle_login(self):
        """Maneja el proceso de login."""
        username = self.username_edit.text().strip()
        password = self.password_edit.text()
        
        if not username:
            self.status_label.setText("Ingrese su nombre de usuario")
            return
        
        if not password:
            self.status_label.setText("Ingrese su contraseña")
            return
        
        self.login_button.setEnabled(False)
        self.login_button.setText("Autenticando...")
        
        try:
            user_info = self.auth_service.authenticate(username, password)
            self.status_label.setText("Autenticación exitosa")
            self.status_label.setStyleSheet("color: green; font-weight: bold;")
            logger.info(f"Login exitoso para: {user_info['username']}")
            
            # Enviar notificación de login exitoso
            if NOTIFICATIONS_AVAILABLE:
                username_display = user_info.get('username', 'Usuario')
                role = user_info.get('role', 'usuario')
                send_success(
                    "Sesión Iniciada",
                    f"Bienvenido {username_display}! Has iniciado sesión correctamente como {role}.",
                    "auth_system"
                )
            
            self.login_successful.emit(user_info)
        except AuthenticationError as e:
            self.status_label.setText(str(e))
            self.status_label.setStyleSheet("color: red; font-weight: bold;")
            self.login_button.setEnabled(True)
            self.login_button.setText("Iniciar Sesión")
            
            # Enviar notificación de error de login
            if NOTIFICATIONS_AVAILABLE:
                send_error(
                    "Error de Autenticación",
                    f"No se pudo iniciar sesión: {str(e)}",
                    "auth_system"
                )
                
        except Exception as e:
            logger.error(f"Error inesperado en login: {e}")
            self.status_label.setText("Error interno del sistema")
            self.status_label.setStyleSheet("color: red; font-weight: bold;")
            self.login_button.setEnabled(True)
            self.login_button.setText("Iniciar Sesión")
            
            # Enviar notificación de error del sistema
            if NOTIFICATIONS_AVAILABLE:
                send_error(
                    "Error del Sistema",
                    f"Error interno durante la autenticación: {str(e)}",
                    "auth_system"
                )