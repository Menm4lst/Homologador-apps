"""
Diálogo para que el usuario actual cambie su propia contraseña.
"""

import re
import secrets
import string
from typing import Optional, Dict, Any, TYPE_CHECKING

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QPushButton, QCheckBox, QMessageBox,
    QDialogButtonBox, QFrame, QProgressBar, QWidget
)

if TYPE_CHECKING:
    from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPalette, QColor

from data.seed import get_auth_service


class ChangeMyPasswordDialog(QDialog):
    """Diálogo para que el usuario cambie su propia contraseña."""
    
    password_changed = pyqtSignal()
    
    def __init__(self, user_info: Dict[str, Any], parent: Optional['QWidget'] = None):
        super().__init__(parent)
        self.user_info = user_info
        self.auth_service = get_auth_service()
        
        self.setWindowTitle("🔑 Cambiar Mi Contraseña")
        self.setModal(True)
        self.resize(450, 400)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowCloseButtonHint)
        
        self.setup_ui()
        self.apply_theme()
    
    def setup_ui(self):
        """Configura la interfaz de usuario."""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Título y usuario
        header_frame = QFrame()
        header_layout = QVBoxLayout(header_frame)
        
        title_label = QLabel("🔑 Cambiar Mi Contraseña")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setWeight(QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        user_label = QLabel(f"Usuario: {self.user_info.get('username', '')}")
        user_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        user_font = QFont()
        user_font.setPointSize(10)
        user_label.setFont(user_font)
        
        header_layout.addWidget(title_label)
        header_layout.addWidget(user_label)
        layout.addWidget(header_frame)
        
        # Separador
        separator = QFrame()
        separator.setFrameStyle(QFrame.Shape.HLine | QFrame.Shadow.Sunken)
        layout.addWidget(separator)
        
        # Formulario de contraseñas
        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        
        # Contraseña actual
        self.current_password_edit = QLineEdit()
        self.current_password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.current_password_edit.setPlaceholderText("Ingresa tu contraseña actual")
        self.current_password_edit.textChanged.connect(self.validate_form)
        form_layout.addRow("🔒 Contraseña Actual:", self.current_password_edit)
        
        # Nueva contraseña
        self.new_password_edit = QLineEdit()
        self.new_password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.new_password_edit.setPlaceholderText("Nueva contraseña (mín. 8 caracteres)")
        self.new_password_edit.textChanged.connect(self.validate_form)
        self.new_password_edit.textChanged.connect(self.update_strength)
        form_layout.addRow("🔑 Nueva Contraseña:", self.new_password_edit)
        
        # Confirmar contraseña
        self.confirm_password_edit = QLineEdit()
        self.confirm_password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_password_edit.setPlaceholderText("Confirma la nueva contraseña")
        self.confirm_password_edit.textChanged.connect(self.validate_form)
        form_layout.addRow("✅ Confirmar:", self.confirm_password_edit)
        
        layout.addLayout(form_layout)
        
        # Indicador de fortaleza de contraseña
        strength_frame = QFrame()
        strength_layout = QVBoxLayout(strength_frame)
        
        self.strength_label = QLabel("Fortaleza de la contraseña:")
        strength_layout.addWidget(self.strength_label)
        
        self.strength_bar = QProgressBar()
        self.strength_bar.setMaximum(5)
        self.strength_bar.setValue(0)
        self.strength_bar.setTextVisible(False)
        strength_layout.addWidget(self.strength_bar)
        
        self.strength_text = QLabel("Ingresa una nueva contraseña")
        self.strength_text.setStyleSheet("font-size: 10pt; color: #666;")
        strength_layout.addWidget(self.strength_text)
        
        layout.addWidget(strength_frame)
        
        # Botón para generar contraseña
        generate_btn = QPushButton("🎲 Generar Contraseña Segura")
        generate_btn.clicked.connect(self.generate_secure_password)
        layout.addWidget(generate_btn)
        
        # Checkbox para mostrar contraseñas
        self.show_passwords_check = QCheckBox("👁️ Mostrar contraseñas")
        self.show_passwords_check.toggled.connect(self.toggle_password_visibility)
        layout.addWidget(self.show_passwords_check)
        
        # Requisitos de contraseña
        requirements_frame = QFrame()
        requirements_layout = QVBoxLayout(requirements_frame)
        
        req_label = QLabel("📋 Requisitos de contraseña:")
        req_font = QFont()
        req_font.setWeight(QFont.Weight.Bold)
        req_label.setFont(req_font)
        requirements_layout.addWidget(req_label)
        
        requirements_text = QLabel("""
• Al menos 8 caracteres
• Al menos una letra minúscula
• Al menos una letra mayúscula  
• Al menos un número
• Se recomienda usar símbolos (!@#$%^&*)
        """.strip())
        requirements_text.setStyleSheet("font-size: 9pt; color: #666; margin-left: 10px;")
        requirements_layout.addWidget(requirements_text)
        
        layout.addWidget(requirements_frame)
        
        # Botones
        buttons_layout = QHBoxLayout()
        
        self.change_btn = QPushButton("🔄 Cambiar Contraseña")
        self.change_btn.setEnabled(False)
        self.change_btn.clicked.connect(self.change_password)
        
        cancel_btn = QPushButton("❌ Cancelar")
        cancel_btn.clicked.connect(self.reject)
        
        buttons_layout.addWidget(cancel_btn)
        buttons_layout.addWidget(self.change_btn)
        layout.addLayout(buttons_layout)
    
    def apply_theme(self):
        """Aplica el tema negro-azul al diálogo."""
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, 
                    stop: 0 #161b22, stop: 1 #0d1117);
                color: #f0f6fc;
            }
            
            QLabel {
                color: #f0f6fc;
                background: transparent;
            }
            
            QLineEdit {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, 
                    stop: 0 #30363d, stop: 1 #21262d);
                color: #f0f6fc;
                border: 2px solid #388bfd;
                border-radius: 6px;
                padding: 8px;
                font-size: 10pt;
            }
            
            QLineEdit:focus {
                border: 2px solid #58a6ff;
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, 
                    stop: 0 #1f6feb, stop: 1 #0969da);
                color: white;
            }
            
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, 
                    stop: 0 #1f6feb, stop: 1 #0969da);
                color: white;
                border: 2px solid #388bfd;
                border-radius: 8px;
                padding: 10px 15px;
                font-weight: bold;
                font-size: 10pt;
            }
            
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, 
                    stop: 0 #4fc3f7, stop: 1 #29b6f6);
                border: 2px solid #58a6ff;
            }
            
            QPushButton:pressed {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, 
                    stop: 0 #21262d, stop: 1 #161b22);
            }
            
            QPushButton:disabled {
                background: #30363d;
                color: #7d8590;
                border: 2px solid #21262d;
            }
            
            QCheckBox {
                color: #f0f6fc;
                spacing: 8px;
            }
            
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 2px solid #388bfd;
                border-radius: 3px;
                background: #21262d;
            }
            
            QCheckBox::indicator:checked {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, 
                    stop: 0 #1f6feb, stop: 1 #0969da);
                border: 2px solid #58a6ff;
            }
            
            QProgressBar {
                border: 2px solid #388bfd;
                border-radius: 4px;
                background: #21262d;
                height: 8px;
            }
            
            QProgressBar::chunk {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, 
                    stop: 0 #f85149, stop: 0.5 #d29922, stop: 1 #238636);
                border-radius: 2px;
            }
            
            QFrame {
                background: transparent;
            }
        """)
    
    def toggle_password_visibility(self, show: bool):
        """Alterna la visibilidad de las contraseñas."""
        echo_mode = QLineEdit.EchoMode.Normal if show else QLineEdit.EchoMode.Password
        
        self.current_password_edit.setEchoMode(echo_mode)
        self.new_password_edit.setEchoMode(echo_mode)
        self.confirm_password_edit.setEchoMode(echo_mode)
    
    def generate_secure_password(self):
        """Genera una contraseña segura automáticamente."""
        # Generar contraseña con diferentes tipos de caracteres
        chars_lower = string.ascii_lowercase
        chars_upper = string.ascii_uppercase  
        chars_digits = string.digits
        chars_special = "!@#$%^&*"
        
        # Asegurar al menos un carácter de cada tipo
        password_parts = [
            secrets.choice(chars_lower),
            secrets.choice(chars_upper),
            secrets.choice(chars_digits),
            secrets.choice(chars_special)
        ]
        
        # Completar con caracteres aleatorios
        all_chars = chars_lower + chars_upper + chars_digits + chars_special
        for _ in range(8):  # Total 12 caracteres
            password_parts.append(secrets.choice(all_chars))
        
        # Mezclar la contraseña
        secrets.SystemRandom().shuffle(password_parts)
        password = ''.join(password_parts)
        
        # Establecer en los campos
        self.new_password_edit.setText(password)
        self.confirm_password_edit.setText(password)
        
        # Mostrar mensaje con la contraseña
        msg = QMessageBox(self)
        msg.setWindowTitle("🔐 Contraseña Generada")
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setText("Se ha generado una contraseña segura:")
        msg.setDetailedText(f"Contraseña: {password}")
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()
    
    def update_strength(self):
        """Actualiza el indicador de fortaleza de contraseña."""
        try:
            password = self.new_password_edit.text()
            
            if not password:
                self.strength_bar.setValue(0)
                self.strength_text.setText("Ingresa una nueva contraseña")
                return
            
            # Calcular puntuación de fortaleza
            score = 0
            feedback: list[str] = []
            
            if len(password) >= 8:
                score += 1
            else:
                feedback.append("al menos 8 caracteres")
            
            if re.search(r'[a-z]', password):
                score += 1
            else:
                feedback.append("una letra minúscula")
            
            if re.search(r'[A-Z]', password):
                score += 1
            else:
                feedback.append("una letra mayúscula")
            
            if re.search(r'\d', password):
                score += 1
            else:
                feedback.append("un número")
            
            # Patrón simplificado para símbolos especiales
            if re.search(r'[!@#$%^&*()_+=\-\[\]{};\':"\\|,.<>/?]', password):
                score += 1
        
        except Exception as e:
            # En caso de error en regex, usar validación básica
            print(f"Error en validación de contraseña: {e}")
            score = 1 if len(password) >= 8 else 0
            feedback = ["validación básica aplicada"]
        
        # Actualizar barra de progreso
        self.strength_bar.setValue(score)
        
        # Actualizar texto de retroalimentación
        if score == 0:
            self.strength_text.setText("Muy débil - Necesita: " + ", ".join(feedback[:2]))
        elif score == 1:
            self.strength_text.setText("Débil - Necesita: " + ", ".join(feedback[:2]))
        elif score == 2:
            self.strength_text.setText("Regular - Necesita: " + ", ".join(feedback[:1]))
        elif score == 3:
            self.strength_text.setText("Buena - Se recomienda añadir símbolos")
        elif score == 4:
            self.strength_text.setText("Fuerte - Excelente contraseña")
        else:
            self.strength_text.setText("Muy fuerte - Contraseña muy segura")
        
        # Cambiar color de la barra según fortaleza
        if score <= 1:
            color = "#f85149"  # Rojo
        elif score <= 2:
            color = "#d29922"  # Amarillo
        elif score <= 3:
            color = "#0969da"  # Azul
        else:
            color = "#238636"  # Verde
        
        self.strength_bar.setStyleSheet(f"""
            QProgressBar::chunk {{
                background: {color};
                border-radius: 2px;
            }}
        """)
    
    def validate_form(self):
        """Valida que todos los campos estén correctos."""
        current = self.current_password_edit.text()
        new_pass = self.new_password_edit.text()
        confirm = self.confirm_password_edit.text()
        
        # Validaciones
        valid = (
            len(current) > 0 and
            len(new_pass) >= 8 and
            new_pass == confirm and
            current != new_pass  # No puede ser igual a la actual
        )
        
        self.change_btn.setEnabled(valid)
        
        # Feedback adicional
        if current and new_pass and current == new_pass:
            self.strength_text.setText("⚠️ La nueva contraseña debe ser diferente a la actual")
    
    def change_password(self):
        """Cambia la contraseña del usuario."""
        current_password = self.current_password_edit.text()
        new_password = self.new_password_edit.text()
        
        try:
            # Verificar contraseña actual
            try:
                self.auth_service.authenticate(
                    self.user_info['username'], 
                    current_password
                )
            except Exception:
                QMessageBox.critical(
                    self,
                    "❌ Error", 
                    "La contraseña actual es incorrecta."
                )
                return
            
            # Cambiar contraseña
            success = self.auth_service.change_password(
                self.user_info['user_id'],
                current_password,
                new_password
            )
            
            if success:
                QMessageBox.information(
                    self,
                    "✅ Éxito",
                    "Tu contraseña ha sido cambiada exitosamente.\\n\\n"
                    "Por favor, úsala en tu próximo inicio de sesión."
                )
                self.password_changed.emit()
                self.accept()
            else:
                QMessageBox.critical(
                    self,
                    "❌ Error",
                    "No se pudo cambiar la contraseña.\\n"
                    "Por favor, intenta de nuevo."
                )
        
        except Exception as e:
            QMessageBox.critical(
                self,
                "❌ Error",
                f"Error inesperado: {str(e)}"
            )