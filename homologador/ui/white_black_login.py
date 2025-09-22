"""
Login window con colores blanco y negro para máxima visibilidad.
"""

import sys
import logging
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QPushButton, QMessageBox, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPalette, QColor

from data.seed import get_auth_service, AuthenticationError

logger = logging.getLogger(__name__)

class WhiteBlackLoginWindow(QWidget):
    """Ventana de login con colores blanco y negro contrastantes."""
    
    login_successful = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.auth_service = get_auth_service()
        self.setup_ui()
        self.apply_white_black_theme()
    
    def setup_ui(self):
        """Configura la interfaz de usuario."""
        self.setWindowTitle("Homologador de Aplicaciones - Login")
        self.setFixedSize(500, 400)
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowCloseButtonHint)
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(25)
        main_layout.setContentsMargins(50, 50, 50, 50)
        
        # Título
        title = QLabel("HOMOLOGADOR DE APLICACIONES")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #000000; background-color: #ffffff; font-weight: bold;")
        title.setObjectName("title")
        main_layout.addWidget(title)
        
        # Subtítulo
        subtitle = QLabel("Sistema de Gestión de Homologaciones")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setFont(QFont("Arial", 12))
        subtitle.setStyleSheet("color: #000000; background-color: #ffffff;")
        subtitle.setObjectName("subtitle")
        main_layout.addWidget(subtitle)
        
        # Separador visual
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setObjectName("separator")
        main_layout.addWidget(separator)
        
        # Formulario
        form_frame = QFrame()
        form_frame.setStyleSheet("background-color: #f0f0f0; border: 3px solid #000000; border-radius: 10px;")
        form_frame.setObjectName("formFrame")
        form_layout = QFormLayout(form_frame)
        form_layout.setSpacing(20)
        form_layout.setContentsMargins(30, 30, 30, 30)
        
        # Labels del formulario
        user_label = QLabel("USUARIO:")
        user_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        user_label.setStyleSheet("color: #000000; background-color: transparent;")
        user_label.setObjectName("formLabel")
        
        pass_label = QLabel("CONTRASEÑA:")
        pass_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        pass_label.setStyleSheet("color: #000000; background-color: transparent;")
        pass_label.setObjectName("formLabel")
        
        # Usuario
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("Ingrese su usuario")
        self.username_edit.setText("admin")  # Pre-llenar
        self.username_edit.setMinimumHeight(30)
        self.username_edit.setStyleSheet("background-color: #ffffff; color: #000000; border: 2px solid #000000; padding: 5px; font-size: 14px;")
        self.username_edit.setObjectName("input")
        
        # Contraseña
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_edit.setPlaceholderText("Ingrese su contraseña")
        self.password_edit.setText("admin123")  # Pre-llenar
        self.password_edit.setMinimumHeight(30)
        self.password_edit.setStyleSheet("background-color: #ffffff; color: #000000; border: 2px solid #000000; padding: 5px; font-size: 14px;")
        self.password_edit.setObjectName("input")
        self.password_edit.returnPressed.connect(self.handle_login)
        
        form_layout.addRow(user_label, self.username_edit)
        form_layout.addRow(pass_label, self.password_edit)
        
        main_layout.addWidget(form_frame)
        
        # Botones
        button_layout = QHBoxLayout()
        button_layout.setSpacing(20)
        
        self.login_button = QPushButton("INICIAR SESIÓN")
        self.login_button.clicked.connect(self.handle_login)
        self.login_button.setDefault(True)
        self.login_button.setMinimumHeight(40)
        self.login_button.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.login_button.setStyleSheet("background-color: #000000; color: #ffffff; border: 2px solid #000000; padding: 10px; border-radius: 5px;")
        self.login_button.setObjectName("primaryButton")
        button_layout.addWidget(self.login_button)
        
        exit_button = QPushButton("SALIR")
        exit_button.clicked.connect(self.close)
        exit_button.setMinimumHeight(40)
        exit_button.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        exit_button.setStyleSheet("background-color: #ffffff; color: #000000; border: 2px solid #000000; padding: 10px; border-radius: 5px;")
        exit_button.setObjectName("secondaryButton")
        button_layout.addWidget(exit_button)
        
        main_layout.addLayout(button_layout)
        
        # Status
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setObjectName("status")
        main_layout.addWidget(self.status_label)
    
    def apply_white_black_theme(self):
        """Aplica tema blanco y negro contrastante."""
        # Fondo blanco para toda la ventana
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor("#ffffff"))
        palette.setColor(QPalette.ColorRole.WindowText, QColor("#000000"))
        palette.setColor(QPalette.ColorRole.Base, QColor("#ffffff"))
        palette.setColor(QPalette.ColorRole.Text, QColor("#000000"))
        palette.setColor(QPalette.ColorRole.Button, QColor("#000000"))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor("#ffffff"))
        self.setPalette(palette)
        
        # Stylesheet con máximo contraste
        self.setStyleSheet("""
            /* Ventana principal */
            WhiteBlackLoginWindow {
                background-color: #ffffff;
                color: #000000;
                font-family: Arial, sans-serif;
                font-size: 12pt;
            }
            
            /* Título principal */
            QLabel#title {
                color: #000000;
                background-color: #ffffff;
                font-size: 24pt;
                font-weight: bold;
                padding: 20px;
                border: 3px solid #000000;
                margin: 10px;
            }
            
            /* Subtítulo */
            QLabel#subtitle {
                color: #333333;
                background-color: #ffffff;
                font-size: 14pt;
                font-weight: normal;
                padding: 10px;
                margin: 5px;
            }
            
            /* Separador */
            QFrame#separator {
                color: #000000;
                background-color: #000000;
                border: 2px solid #000000;
            }
            
            /* Marco del formulario */
            QFrame#formFrame {
                background-color: #f0f0f0;
                border: 4px solid #000000;
                border-radius: 10px;
                margin: 10px;
            }
            
            /* Labels del formulario */
            QLabel#formLabel {
                color: #000000;
                background-color: transparent;
                font-size: 14pt;
                font-weight: bold;
                padding: 5px;
            }
            
            /* Campos de entrada */
            QLineEdit#input {
                background-color: #ffffff;
                color: #000000;
                border: 3px solid #000000;
                border-radius: 8px;
                padding: 15px;
                font-size: 16pt;
                font-weight: bold;
                min-height: 20px;
            }
            
            QLineEdit#input:focus {
                border-color: #0000ff;
                background-color: #f8f8ff;
                border-width: 4px;
            }
            
            /* Botón principal */
            QPushButton#primaryButton {
                background-color: #000000;
                color: #ffffff;
                border: 3px solid #000000;
                border-radius: 8px;
                padding: 15px 30px;
                font-size: 16pt;
                font-weight: bold;
                min-width: 150px;
                min-height: 25px;
            }
            
            QPushButton#primaryButton:hover {
                background-color: #333333;
                border-color: #0000ff;
                border-width: 4px;
            }
            
            QPushButton#primaryButton:pressed {
                background-color: #666666;
            }
            
            QPushButton#primaryButton:disabled {
                background-color: #cccccc;
                color: #666666;
                border-color: #cccccc;
            }
            
            /* Botón secundario */
            QPushButton#secondaryButton {
                background-color: #ffffff;
                color: #000000;
                border: 3px solid #000000;
                border-radius: 8px;
                padding: 15px 30px;
                font-size: 16pt;
                font-weight: bold;
                min-width: 150px;
                min-height: 25px;
            }
            
            QPushButton#secondaryButton:hover {
                background-color: #f0f0f0;
                border-color: #ff0000;
                border-width: 4px;
            }
            
            QPushButton#secondaryButton:pressed {
                background-color: #e0e0e0;
            }
            
            /* Status */
            QLabel#status {
                color: #000000;
                background-color: #ffffff;
                font-size: 14pt;
                font-weight: bold;
                padding: 10px;
                border: 2px solid #cccccc;
                border-radius: 5px;
                margin: 10px;
            }
            
            QLabel#status[error="true"] {
                color: #ffffff;
                background-color: #ff0000;
                border-color: #ff0000;
            }
            
            QLabel#status[success="true"] {
                color: #ffffff;
                background-color: #008000;
                border-color: #008000;
            }
        """)
    
    def handle_login(self):
        """Maneja el proceso de login."""
        username = self.username_edit.text().strip()
        password = self.password_edit.text()
        
        if not username:
            self.show_status("INGRESE SU NOMBRE DE USUARIO", is_error=True)
            return
        
        if not password:
            self.show_status("INGRESE SU CONTRASEÑA", is_error=True)
            return
        
        self.login_button.setEnabled(False)
        self.login_button.setText("AUTENTICANDO...")
        
        try:
            user_info = self.auth_service.authenticate(username, password)
            self.show_status("AUTENTICACIÓN EXITOSA", is_error=False)
            logger.info(f"Login exitoso para: {user_info['username']}")
            self.login_successful.emit(user_info)
        except AuthenticationError as e:
            self.show_status(f"ERROR: {str(e).upper()}", is_error=True)
            self.reset_login_state()
        except Exception as e:
            logger.error(f"Error inesperado en login: {e}")
            self.show_status("ERROR INTERNO DEL SISTEMA", is_error=True)
            self.reset_login_state()
    
    def show_status(self, message: str, is_error: bool = False):
        """Muestra mensaje de estado."""
        self.status_label.setText(message)
        if is_error:
            self.status_label.setProperty("error", "true")
            self.status_label.setProperty("success", "false")
        else:
            self.status_label.setProperty("error", "false")
            self.status_label.setProperty("success", "true")
        
        # Refrescar el estilo
        style = self.status_label.style()
        if style:
            style.unpolish(self.status_label)
            style.polish(self.status_label)
    
    def reset_login_state(self):
        """Resetea el estado del botón de login."""
        self.login_button.setEnabled(True)
        self.login_button.setText("INICIAR SESIÓN")