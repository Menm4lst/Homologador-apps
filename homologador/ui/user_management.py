"""
Módulo de Administración de Usuarios para el Homologador.

Este módulo proporciona una interfaz completa para que los administradores
puedan gestionar usuarios, permisos, contraseñas y accesos del sistema.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, cast

from ..core.auth import generate_password
from ..core.storage import get_audit_repository, get_user_repository
from ..data.seed import get_auth_service
from PyQt6.QtCore import QDate, Qt, QThread, QTimer, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QAction, QColor, QFont, QIcon, QPalette, QPixmap
from PyQt6.QtWidgets import (QButtonGroup, QCalendarWidget, QCheckBox,
                             QComboBox, QDateEdit, QDialog, QDialogButtonBox,
                             QFormLayout, QFrame, QGridLayout, QGroupBox,
                             QHBoxLayout, QHeaderView, QLabel, QLineEdit,
                             QListWidget, QListWidgetItem, QMessageBox,
                             QProgressBar, QPushButton, QRadioButton,
                             QScrollArea, QSlider, QSpinBox, QSplitter,
                             QTableWidget, QTableWidgetItem, QTabWidget,
                             QTextEdit, QVBoxLayout, QWidget)

logger = logging.getLogger(__name__)


class UserRole:
    """Definición de roles de usuario."""
    ADMIN = "admin"
    MANAGER = "manager"
    EDITOR = "editor"
    VIEWER = "viewer"
    GUEST = "guest"
    
    ROLES = {
        ADMIN: "Administrador",
        MANAGER: "Gerente", 
        EDITOR: "Editor",
        VIEWER: "Visualizador",
        GUEST: "Invitado"
    }
    
    PERMISSIONS = {
        ADMIN: ["create", "read", "update", "delete", "manage_users", "export", "backup"],
        MANAGER: ["create", "read", "update", "delete", "export"],
        EDITOR: ["create", "read", "update"],
        VIEWER: ["read"],
        GUEST: ["read"]
    }


class CreateUserDialog(QDialog):
    """Diálogo para crear nuevos usuarios."""
    
    user_created = pyqtSignal(dict)
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setWindowTitle("Crear Nuevo Usuario")
        self.setModal(True)
        self.resize(500, 600)
        
        self.user_repo = get_user_repository()
        self.setup_ui()
        
    def setup_ui(self):
        """Configura la interfaz del diálogo."""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        
        # Título
        title_label = QLabel("👤 Crear Nuevo Usuario")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setWeight(QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        main_layout.addWidget(title_label)
        
        # Información básica
        basic_group = QGroupBox("Información Básica")
        basic_layout = QFormLayout(basic_group)
        
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("Nombre de usuario único")
        self.username_edit.textChanged.connect(self.validate_form)
        basic_layout.addRow("Usuario:", self.username_edit)
        
        self.full_name_edit = QLineEdit()
        self.full_name_edit.setPlaceholderText("Nombre completo del usuario")
        basic_layout.addRow("Nombre Completo:", self.full_name_edit)
        
        self.email_edit = QLineEdit()
        self.email_edit.setPlaceholderText("correo@empresa.com")
        basic_layout.addRow("Email:", self.email_edit)
        
        self.department_edit = QLineEdit()
        self.department_edit.setPlaceholderText("Departamento o área")
        basic_layout.addRow("Departamento:", self.department_edit)
        
        main_layout.addWidget(basic_group)
        
        # Configuración de acceso
        access_group = QGroupBox("Configuración de Acceso")
        access_layout = QFormLayout(access_group)
        
        self.role_combo = QComboBox()
        for role, description in UserRole.ROLES.items():
            self.role_combo.addItem(f"{description} ({role})", role)
        self.role_combo.setCurrentIndex(3)  # Viewer por defecto
        self.role_combo.currentTextChanged.connect(self.update_permissions_preview)
        access_layout.addRow("Rol:", self.role_combo)
        
        self.active_check = QCheckBox("Usuario activo")
        self.active_check.setChecked(True)
        access_layout.addRow("Estado:", self.active_check)
        
        self.force_password_change = QCheckBox("Forzar cambio de contraseña en primer login")
        self.force_password_change.setChecked(True)
        access_layout.addRow("Seguridad:", self.force_password_change)
        
        main_layout.addWidget(access_group)
        
        # Configuración de contraseña
        password_group = QGroupBox("Contraseña")
        password_layout = QVBoxLayout(password_group)
        
        password_form = QFormLayout()
        
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_edit.textChanged.connect(self.validate_form)
        password_form.addRow("Contraseña:", self.password_edit)
        
        self.confirm_password_edit = QLineEdit()
        self.confirm_password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_password_edit.textChanged.connect(self.validate_form)
        password_form.addRow("Confirmar:", self.confirm_password_edit)
        
        password_layout.addLayout(password_form)
        
        # Botón generar contraseña
        generate_layout = QHBoxLayout()
        self.generate_password_btn = QPushButton("🎲 Generar Contraseña Segura")
        self.generate_password_btn.clicked.connect(self.generate_password)
        generate_layout.addWidget(self.generate_password_btn)
        generate_layout.addStretch()
        password_layout.addLayout(generate_layout)
        
        # Indicador de fortaleza
        self.password_strength_label = QLabel("Fortaleza: -")
        self.password_strength_label.setStyleSheet("font-weight: bold;")
        password_layout.addWidget(self.password_strength_label)
        
        main_layout.addWidget(password_group)
        
        # Vista previa de permisos
        permissions_group = QGroupBox("Vista Previa de Permisos")
        permissions_layout = QVBoxLayout(permissions_group)
        
        self.permissions_list = QListWidget()
        self.permissions_list.setMaximumHeight(120)
        permissions_layout.addWidget(self.permissions_list)
        
        main_layout.addWidget(permissions_group)
        
        # Botones
        buttons_layout = QHBoxLayout()
        
        self.create_button = QPushButton("✅ Crear Usuario")
        self.create_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px 24px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """)
        self.create_button.clicked.connect(self.create_user)
        self.create_button.setEnabled(False)
        
        cancel_button = QPushButton("❌ Cancelar")
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px 24px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        cancel_button.clicked.connect(self.reject)
        
        buttons_layout.addWidget(self.create_button)
        buttons_layout.addWidget(cancel_button)
        buttons_layout.addStretch()
        
        main_layout.addLayout(buttons_layout)
        
        # Inicializar vista previa
        self.update_permissions_preview()
    
    def generate_password(self):
        """Genera una contraseña segura."""
        password = cast(str, generate_password(12))
        self.password_edit.setText(password)
        self.confirm_password_edit.setText(password)
        
        QMessageBox.information(
            self,
            "Contraseña Generada",
            f"Contraseña generada: {password}\n\n"
            "⚠️ Asegúrese de comunicar esta contraseña al usuario de forma segura."
        )
    
    def update_permissions_preview(self):
        """Actualiza la vista previa de permisos."""
        self.permissions_list.clear()
        
        role = self.role_combo.currentData()
        if role in UserRole.PERMISSIONS:
            permissions = UserRole.PERMISSIONS[role]
            
            permission_descriptions = {
                "create": "✅ Crear nuevos registros",
                "read": "👁️ Ver registros existentes", 
                "update": "✏️ Modificar registros",
                "delete": "🗑️ Eliminar registros",
                "manage_users": "👥 Gestionar usuarios",
                "export": "📤 Exportar datos",
                "backup": "💾 Crear respaldos"
            }
            
            for permission in permissions:
                if permission in permission_descriptions:
                    item = QListWidgetItem(permission_descriptions[permission])
                    self.permissions_list.addItem(item)
    
    def validate_form(self):
        """Valida el formulario y habilita/deshabilita el botón crear."""
        username = self.username_edit.text().strip()
        password = self.password_edit.text()
        confirm_password = self.confirm_password_edit.text()
        
        # Validaciones
        valid = True
        
        # Usuario no vacío y único
        if not username:
            valid = False
        elif len(username) < 3:
            valid = False
        
        # Contraseñas coinciden y son seguras
        if not password or len(password) < 6:
            valid = False
        elif password != confirm_password:
            valid = False
        
        self.create_button.setEnabled(valid)
        
        # Actualizar indicador de fortaleza
        if password:
            strength = self.calculate_password_strength(password)
            self.password_strength_label.setText(f"Fortaleza: {strength}")
            
            if strength == "Muy Débil":
                self.password_strength_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
            elif strength == "Débil":
                self.password_strength_label.setStyleSheet("color: #f39c12; font-weight: bold;")
            elif strength == "Media":
                self.password_strength_label.setStyleSheet("color: #f1c40f; font-weight: bold;")
            elif strength == "Fuerte":
                self.password_strength_label.setStyleSheet("color: #27ae60; font-weight: bold;")
            else:  # Muy Fuerte
                self.password_strength_label.setStyleSheet("color: #2ecc71; font-weight: bold;")
        else:
            self.password_strength_label.setText("Fortaleza: -")
            self.password_strength_label.setStyleSheet("color: #7f8c8d; font-weight: bold;")
    
    def calculate_password_strength(self, password: str) -> str:
        """Calcula la fortaleza de la contraseña."""
        score = 0
        
        # Longitud
        if len(password) >= 8:
            score += 1
        if len(password) >= 12:
            score += 1
        
        # Caracteres
        if any(c.islower() for c in password):
            score += 1
        if any(c.isupper() for c in password):
            score += 1
        if any(c.isdigit() for c in password):
            score += 1
        if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            score += 1
        
        if score <= 2:
            return "Muy Débil"
        elif score == 3:
            return "Débil"
        elif score == 4:
            return "Media"
        elif score == 5:
            return "Fuerte"
        else:
            return "Muy Fuerte"
    
    def create_user(self):
        """Crea el nuevo usuario."""
        try:
            # Verificar que el usuario no exista
            existing_user = self.user_repo.get_user_by_username(self.username_edit.text().strip())
            if existing_user:
                QMessageBox.warning(
                    self,
                    "Error",
                    "Ya existe un usuario con ese nombre de usuario."
                )
                return
            
            # Crear datos del usuario
            auth_service = get_auth_service()
            user_data = {
                'username': self.username_edit.text().strip(),
                'password': auth_service.hash_password(self.password_edit.text()),
                'full_name': self.full_name_edit.text().strip(),
                'email': self.email_edit.text().strip(),
                'department': self.department_edit.text().strip(),
                'role': self.role_combo.currentData(),
                'is_active': self.active_check.isChecked(),
                'force_password_change': self.force_password_change.isChecked(),
                'created_at': datetime.now().isoformat(),
                'last_login': None
            }
            
            # Crear usuario en la base de datos
            user_id = self.user_repo.create_user(user_data)
            
            if user_id:
                self.user_created.emit(user_data)
                
                QMessageBox.information(
                    self,
                    "Usuario Creado",
                    f"El usuario '{user_data['username']}' ha sido creado exitosamente."
                )
                
                self.accept()
            else:
                QMessageBox.critical(
                    self,
                    "Error",
                    "No se pudo crear el usuario. Intente nuevamente."
                )
                
        except Exception as e:
            logger.error(f"Error creando usuario: {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"Error creando usuario: {str(e)}"
            )


class EditUserDialog(QDialog):
    """Diálogo para editar usuarios existentes."""
    
    user_updated = pyqtSignal(dict)
    
    def __init__(self, user_data: Dict[str, Any], parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        # Convertir sqlite3.Row a diccionario si es necesario
        if hasattr(user_data, 'keys'):
            self.user_data = dict(user_data)
        else:
            self.user_data = user_data
            
        self.user_repo = get_user_repository()
        
        self.setWindowTitle(f"Editar Usuario: {self.user_data.get('username', '')}")
        self.setModal(True)
        self.resize(500, 700)
        
        self.setup_ui()
        self.load_user_data()
    
    def setup_ui(self):
        """Configura la interfaz del diálogo."""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        
        # Título
        title_label = QLabel(f"✏️ Editar Usuario: {self.user_data.get('username', '')}")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setWeight(QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        main_layout.addWidget(title_label)
        
        # Pestañas
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        self.create_info_tab()
        self.create_permissions_tab()
        self.create_security_tab()
        self.create_activity_tab()
        
        # Botones
        buttons_layout = QHBoxLayout()
        
        self.save_button = QPushButton("💾 Guardar Cambios")
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px 24px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.save_button.clicked.connect(self.save_changes)
        
        cancel_button = QPushButton("❌ Cancelar")
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px 24px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        cancel_button.clicked.connect(self.reject)
        
        buttons_layout.addWidget(self.save_button)
        buttons_layout.addWidget(cancel_button)
        buttons_layout.addStretch()
        
        main_layout.addLayout(buttons_layout)
    
    def create_info_tab(self):
        """Crea la pestaña de información básica."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Información básica
        basic_group = QGroupBox("Información Personal")
        basic_layout = QFormLayout(basic_group)
        
        self.username_edit = QLineEdit()
        self.username_edit.setEnabled(False)  # Usuario no se puede cambiar
        basic_layout.addRow("Usuario:", self.username_edit)
        
        self.full_name_edit = QLineEdit()
        basic_layout.addRow("Nombre Completo:", self.full_name_edit)
        
        self.email_edit = QLineEdit()
        basic_layout.addRow("Email:", self.email_edit)
        
        self.department_edit = QLineEdit()
        basic_layout.addRow("Departamento:", self.department_edit)
        
        layout.addWidget(basic_group)
        
        # Estado de cuenta
        status_group = QGroupBox("Estado de Cuenta")
        status_layout = QFormLayout(status_group)
        
        self.active_check = QCheckBox("Usuario activo")
        status_layout.addRow("Estado:", self.active_check)
        
        self.role_combo = QComboBox()
        for role, description in UserRole.ROLES.items():
            self.role_combo.addItem(f"{description} ({role})", role)
        status_layout.addRow("Rol:", self.role_combo)
        
        layout.addWidget(status_group)
        
        layout.addStretch()
        self.tab_widget.addTab(tab, "📋 Información")
    
    def create_permissions_tab(self):
        """Crea la pestaña de permisos."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Permisos por rol
        role_group = QGroupBox("Permisos por Rol")
        role_layout = QVBoxLayout(role_group)
        
        info_label = QLabel("Los permisos se asignan automáticamente según el rol seleccionado:")
        role_layout.addWidget(info_label)
        
        self.permissions_display = QTextEdit()
        self.permissions_display.setReadOnly(True)
        self.permissions_display.setMaximumHeight(200)
        role_layout.addWidget(self.permissions_display)
        
        layout.addWidget(role_group)
        
        # Permisos especiales (futuro)
        special_group = QGroupBox("Permisos Especiales")
        special_layout = QVBoxLayout(special_group)
        
        self.export_permission = QCheckBox("Permitir exportación de datos")
        self.backup_permission = QCheckBox("Permitir crear respaldos")
        self.audit_permission = QCheckBox("Ver registros de auditoría")
        
        special_layout.addWidget(self.export_permission)
        special_layout.addWidget(self.backup_permission)
        special_layout.addWidget(self.audit_permission)
        
        layout.addWidget(special_group)
        
        layout.addStretch()
        self.tab_widget.addTab(tab, "🔐 Permisos")
    
    def create_security_tab(self):
        """Crea la pestaña de seguridad."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Cambio de contraseña
        password_group = QGroupBox("Contraseña")
        password_layout = QVBoxLayout(password_group)
        
        self.change_password_btn = QPushButton("🔑 Cambiar Contraseña")
        self.change_password_btn.clicked.connect(self.change_password)
        password_layout.addWidget(self.change_password_btn)
        
        self.force_password_change = QCheckBox("Forzar cambio de contraseña en próximo login")
        password_layout.addWidget(self.force_password_change)
        
        layout.addWidget(password_group)
        
        # Configuraciones de seguridad
        security_group = QGroupBox("Configuraciones de Seguridad")
        security_layout = QVBoxLayout(security_group)
        
        self.account_locked = QCheckBox("Cuenta bloqueada")
        self.account_locked.setEnabled(False)  # Solo lectura por ahora
        security_layout.addWidget(self.account_locked)
        
        # Información de seguridad
        security_info_layout = QFormLayout()
        
        self.last_login_label = QLabel("-")
        security_info_layout.addRow("Último Login:", self.last_login_label)
        
        self.login_attempts_label = QLabel("-")
        security_info_layout.addRow("Intentos Fallidos:", self.login_attempts_label)
        
        security_layout.addLayout(security_info_layout)
        
        layout.addWidget(security_group)
        
        layout.addStretch()
        self.tab_widget.addTab(tab, "🔒 Seguridad")
    
    def create_activity_tab(self):
        """Crea la pestaña de actividad."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Estadísticas
        stats_group = QGroupBox("Estadísticas de Actividad")
        stats_layout = QFormLayout(stats_group)
        
        self.created_at_label = QLabel("-")
        stats_layout.addRow("Creado:", self.created_at_label)
        
        self.last_activity_label = QLabel("-")
        stats_layout.addRow("Última Actividad:", self.last_activity_label)
        
        self.total_sessions_label = QLabel("-")
        stats_layout.addRow("Total Sesiones:", self.total_sessions_label)
        
        layout.addWidget(stats_group)
        
        # Actividad reciente
        activity_group = QGroupBox("Actividad Reciente")
        activity_layout = QVBoxLayout(activity_group)
        
        self.activity_list = QListWidget()
        activity_layout.addWidget(self.activity_list)
        
        layout.addWidget(activity_group)
        
        self.tab_widget.addTab(tab, "📊 Actividad")
    
    def load_user_data(self):
        """Carga los datos del usuario en los campos."""
        # Información básica
        self.username_edit.setText(self.user_data.get('username', ''))
        self.full_name_edit.setText(self.user_data.get('full_name', ''))
        self.email_edit.setText(self.user_data.get('email', ''))
        self.department_edit.setText(self.user_data.get('department', ''))
        
        # Estado
        self.active_check.setChecked(self.user_data.get('is_active', True))
        
        # Rol
        role = self.user_data.get('role', 'viewer')
        for i in range(self.role_combo.count()):
            if self.role_combo.itemData(i) == role:
                self.role_combo.setCurrentIndex(i)
                break
        
        # Seguridad
        self.force_password_change.setChecked(
            self.user_data.get('force_password_change', False)
        )
        
        # Fechas
        created_at = self.user_data.get('created_at', '')
        if created_at:
            self.created_at_label.setText(created_at)
        
        last_login = self.user_data.get('last_login', '')
        if last_login:
            self.last_login_label.setText(last_login)
        else:
            self.last_login_label.setText("Nunca")
    
    def change_password(self):
        """Abre diálogo para cambiar contraseña."""
        dialog = ChangePasswordDialog(self.user_data, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            QMessageBox.information(
                self,
                "Contraseña Cambiada",
                "La contraseña ha sido cambiada exitosamente."
            )
    
    def save_changes(self):
        """Guarda los cambios del usuario."""
        try:
            # Preparar datos actualizados
            updated_data = {
                'id': self.user_data.get('id'),
                'full_name': self.full_name_edit.text().strip(),
                'email': self.email_edit.text().strip(),
                'department': self.department_edit.text().strip(),
                'role': self.role_combo.currentData(),
                'is_active': self.active_check.isChecked(),
                'force_password_change': self.force_password_change.isChecked(),
                'updated_at': datetime.now().isoformat()
            }
            
            # Actualizar en base de datos
            success = self.user_repo.update_user(cast(Dict[str, Any], updated_data))
            
            if success:
                self.user_updated.emit(updated_data)
                
                QMessageBox.information(
                    self,
                    "Usuario Actualizado",
                    "Los cambios han sido guardados exitosamente."
                )
                
                self.accept()
            else:
                QMessageBox.critical(
                    self,
                    "Error",
                    "No se pudieron guardar los cambios."
                )
                
        except Exception as e:
            logger.error(f"Error actualizando usuario: {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"Error actualizando usuario: {str(e)}"
            )


class ChangePasswordDialog(QDialog):
    """Diálogo para cambiar contraseña de usuario."""
    
    def __init__(self, user_data: Dict[str, Any], parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        # Convertir sqlite3.Row a diccionario si es necesario
        if hasattr(user_data, 'keys'):
            self.user_data = dict(user_data)
        else:
            self.user_data = user_data
            
        self.user_repo = get_user_repository()
        
        self.setWindowTitle(f"Cambiar Contraseña: {self.user_data.get('username', '')}")
        self.setModal(True)
        self.resize(400, 300)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Configura la interfaz del diálogo."""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Título
        title_label = QLabel(f"🔑 Cambiar Contraseña")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setWeight(QFont.Weight.Bold)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # Formulario
        form_layout = QFormLayout()
        
        self.new_password_edit = QLineEdit()
        self.new_password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.new_password_edit.textChanged.connect(self.validate_form)
        form_layout.addRow("Nueva Contraseña:", self.new_password_edit)
        
        self.confirm_password_edit = QLineEdit()
        self.confirm_password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_password_edit.textChanged.connect(self.validate_form)
        form_layout.addRow("Confirmar:", self.confirm_password_edit)
        
        layout.addLayout(form_layout)
        
        # Generar contraseña
        generate_btn = QPushButton("🎲 Generar Contraseña Segura")
        generate_btn.clicked.connect(self.generate_password)
        layout.addWidget(generate_btn)
        
        # Fortaleza
        self.strength_label = QLabel("Fortaleza: -")
        self.strength_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.strength_label)
        
        # Opciones
        self.force_change_check = QCheckBox("Forzar cambio en próximo login")
        layout.addWidget(self.force_change_check)
        
        # Botones
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.ok_button = buttons.button(QDialogButtonBox.StandardButton.Ok)
        self.ok_button.setText("Cambiar Contraseña")
        self.ok_button.setEnabled(False)
        
        buttons.accepted.connect(self.change_password)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def generate_password(self):
        """Genera una contraseña segura."""
        password = cast(str, generate_password(12))
        self.new_password_edit.setText(password)
        self.confirm_password_edit.setText(password)
        
        QMessageBox.information(
            self,
            "Contraseña Generada",
            f"Contraseña generada: {password}\n\n"
            "⚠️ Asegúrese de comunicar esta contraseña al usuario."
        )
    
    def validate_form(self):
        """Valida el formulario."""
        password = self.new_password_edit.text()
        confirm = self.confirm_password_edit.text()
        
        valid = len(password) >= 6 and password == confirm
        self.ok_button.setEnabled(valid)
        
        # Actualizar fortaleza
        if password:
            strength = self.calculate_strength(password)
            self.strength_label.setText(f"Fortaleza: {strength}")
    
    def calculate_strength(self, password: str) -> str:
        """Calcula fortaleza de contraseña."""
        score = 0
        if len(password) >= 8: score += 1
        if any(c.islower() for c in password): score += 1
        if any(c.isupper() for c in password): score += 1
        if any(c.isdigit() for c in password): score += 1
        if any(c in "!@#$%^&*" for c in password): score += 1
        
        if score <= 2: return "Débil"
        elif score <= 3: return "Media"
        elif score <= 4: return "Fuerte"
        else: return "Muy Fuerte"
    
    def change_password(self):
        """Cambia la contraseña del usuario."""
        try:
            new_password = self.new_password_edit.text()
            auth_service = get_auth_service()
            hashed_password = auth_service.hash_password(new_password)
            
            success = self.user_repo.update_user({
                'id': self.user_data['id'],
                'password': hashed_password,
                'force_password_change': self.force_change_check.isChecked(),
                'updated_at': datetime.now().isoformat()
            })
            
            if success:
                self.accept()
            else:
                QMessageBox.critical(self, "Error", "No se pudo cambiar la contraseña.")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error: {str(e)}")


class UserManagementWidget(QWidget):
    """Widget principal de administración de usuarios."""
    
    def __init__(self, user_info: Dict[str, Any], parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.user_info = user_info
        self.user_repo = get_user_repository()
        self.audit_repo = get_audit_repository()
        
        # Verificar permisos de admin
        if user_info.get('role') != 'admin':
            raise PermissionError("Solo los administradores pueden acceder a este módulo")
        
        self.setup_ui()
        self.apply_dark_theme()
        self.load_users()
        
        logger.info(f"Módulo de administración de usuarios iniciado por: {user_info.get('username')}")
    
    def setup_ui(self):
        """Configura la interfaz principal."""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        
        # Encabezado
        header_layout = QHBoxLayout()
        
        title_label = QLabel("👥 Administración de Usuarios")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setWeight(QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #2c3e50;")
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        # Botones de acción
        self.create_user_btn = QPushButton("➕ Crear Usuario")
        self.create_user_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
        """)
        self.create_user_btn.clicked.connect(self.create_user)
        
        self.refresh_btn = QPushButton("🔄 Actualizar")
        self.refresh_btn.clicked.connect(self.load_users)
        
        header_layout.addWidget(self.create_user_btn)
        header_layout.addWidget(self.refresh_btn)
        
        main_layout.addLayout(header_layout)
        
        # Filtros
        filters_layout = QHBoxLayout()
        
        filters_layout.addWidget(QLabel("Filtrar:"))
        
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Buscar por nombre o usuario...")
        self.search_edit.textChanged.connect(self.filter_users)
        filters_layout.addWidget(self.search_edit)
        
        self.role_filter = QComboBox()
        self.role_filter.addItem("Todos los Roles", "")
        for role, description in UserRole.ROLES.items():
            self.role_filter.addItem(description, role)
        self.role_filter.currentTextChanged.connect(self.filter_users)
        filters_layout.addWidget(self.role_filter)
        
        self.status_filter = QComboBox()
        self.status_filter.addItem("Todos los Estados", "")
        self.status_filter.addItem("Activos", "active")
        self.status_filter.addItem("Inactivos", "inactive")
        self.status_filter.currentTextChanged.connect(self.filter_users)
        filters_layout.addWidget(self.status_filter)
        
        # Checkbox para mostrar usuarios inactivos
        self.show_inactive_check = QCheckBox("Mostrar usuarios eliminados")
        self.show_inactive_check.setToolTip("Mostrar usuarios que han sido eliminados (desactivados)")
        self.show_inactive_check.stateChanged.connect(self.on_show_inactive_changed)
        filters_layout.addWidget(self.show_inactive_check)
        
        filters_layout.addStretch()
        
        main_layout.addLayout(filters_layout)
        
        # Tabla de usuarios
        self.users_table = QTableWidget()
        self.users_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.users_table.setAlternatingRowColors(True)
        self.users_table.setStyleSheet("""
            QTableWidget {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #161b22, stop: 1 #0d1117);
                alternate-background-color: #21262d;
                gridline-color: #30363d;
                color: #f0f6fc;
                border: 2px solid #1f6feb;
                border-radius: 8px;
                selection-background-color: #1f6feb;
                font-size: 10pt;
                font-weight: 500;
            }
            QTableWidget::item {
                padding: 12px 8px;
                border-bottom: 1px solid #30363d;
                border-right: 1px solid #30363d;
                color: #f0f6fc;
                background: transparent;
            }
            QTableWidget::item:selected {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #1f6feb, stop: 1 #0969da);
                color: #ffffff;
                border: 1px solid #58a6ff;
                font-weight: bold;
            }
            QTableWidget::item:hover {
                background-color: rgba(88, 166, 255, 0.2);
                border: 1px solid #58a6ff;
                color: #ffffff;
            }
            QTableWidget::item:alternate {
                background-color: rgba(33, 38, 45, 0.8);
                color: #f0f6fc;
            }
            QTableWidget::item:alternate:selected {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #1f6feb, stop: 1 #0969da);
                color: #ffffff;
                font-weight: bold;
            }
            QHeaderView::section {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #30363d, stop: 1 #21262d);
                color: #ffffff;
                padding: 12px 8px;
                border: none;
                border-right: 2px solid #58a6ff;
                border-bottom: 2px solid #1f6feb;
                font-weight: bold;
                font-size: 11pt;
            }
            QHeaderView::section:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #1f6feb, stop: 1 #0969da);
                color: #ffffff;
            }
        """)
        
        # Configurar columnas
        columns = ["ID", "Usuario", "Nombre Completo", "Email", "Rol", "Estado", "Último Login", "Acciones"]
        self.users_table.setColumnCount(len(columns))
        self.users_table.setHorizontalHeaderLabels(columns)
        
        # Ajustar columnas
        header = self.users_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # Usuario
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)           # Nombre
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)           # Email
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Rol
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # Estado
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)  # Login
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)  # Acciones
        
        # Configurar altura de filas para que los botones se vean correctamente
        self.users_table.verticalHeader().setDefaultSectionSize(45)  # Altura mínima de 45px
        self.users_table.verticalHeader().setMinimumSectionSize(40)   # Altura mínima absoluta
        
        main_layout.addWidget(self.users_table)
        
        # Estadísticas
        stats_layout = QHBoxLayout()
        
        self.total_users_label = QLabel("Total: 0")
        self.active_users_label = QLabel("Activos: 0")
        self.inactive_users_label = QLabel("Inactivos: 0")
        
        stats_layout.addWidget(self.total_users_label)
        stats_layout.addWidget(self.active_users_label)
        stats_layout.addWidget(self.inactive_users_label)
        stats_layout.addStretch()
        
        main_layout.addLayout(stats_layout)
    
    def load_users(self, include_inactive: bool = False):
        """Carga la lista de usuarios."""
        try:
            users_rows = self.user_repo.get_all_users(include_inactive=include_inactive)
            # Convertir sqlite3.Row a diccionarios
            users: List[Dict[str, Any]] = []
            for row in users_rows:
                user_dict = dict(row)
                users.append(user_dict)
            
            self.display_users(users)
            self.update_statistics(users)
            
        except Exception as e:
            logger.error(f"Error cargando usuarios: {e}")
            QMessageBox.critical(self, "Error", f"Error cargando usuarios: {str(e)}")
    
    def on_show_inactive_changed(self, state):
        """Maneja el cambio del checkbox de mostrar inactivos."""
        include_inactive = state == 2  # Qt.CheckState.Checked = 2
        self.load_users(include_inactive=include_inactive)
    
    def display_users(self, users: List[Dict[str, Any]]):
        """Muestra los usuarios en la tabla."""
        self.users_table.setRowCount(len(users))
        
        for row, user in enumerate(users):
            # Convertir sqlite3.Row a diccionario si es necesario
            if hasattr(user, 'keys'):
                user_dict = dict(user)
            else:
                user_dict = user
            
            # ID
            self.users_table.setItem(row, 0, QTableWidgetItem(str(user_dict.get('id', ''))))
            
            # Usuario
            self.users_table.setItem(row, 1, QTableWidgetItem(user_dict.get('username', '')))
            
            # Nombre completo
            self.users_table.setItem(row, 2, QTableWidgetItem(user_dict.get('full_name', '')))
            
            # Email
            self.users_table.setItem(row, 3, QTableWidgetItem(user_dict.get('email', '')))
            
            # Rol
            role = user_dict.get('role', '')
            role_display = UserRole.ROLES.get(role, role)
            self.users_table.setItem(row, 4, QTableWidgetItem(role_display))
            
            # Estado
            is_active = user_dict.get('is_active', True)
            status_item = QTableWidgetItem("✅ Activo" if is_active else "❌ Inactivo")
            if not is_active:
                status_item.setForeground(QColor("#e74c3c"))
            self.users_table.setItem(row, 5, status_item)
            
            # Último login
            last_login = user_dict.get('last_login', '')
            if last_login:
                try:
                    login_date = datetime.fromisoformat(last_login.replace('Z', '+00:00'))
                    login_display = login_date.strftime('%d/%m/%Y %H:%M')
                except:
                    login_display = last_login
            else:
                login_display = "Nunca"
            self.users_table.setItem(row, 6, QTableWidgetItem(login_display))
            
            # Botones de acción
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(4, 4, 4, 4)
            actions_layout.setSpacing(4)
            
            edit_btn = QPushButton("✏️")
            edit_btn.setToolTip("Editar usuario")
            edit_btn.setFixedSize(30, 30)
            edit_btn.clicked.connect(lambda checked, u=user_dict: self.edit_user(cast(Dict[str, Any], u)))
            
            # Botón eliminar con diferentes estilos según el estado
            is_active = user_dict.get('is_active', 1)
            if is_active:
                delete_btn = QPushButton("🗑️")
                delete_btn.setToolTip("Desactivar usuario")
                delete_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #ff9800;
                        color: white;
                        border: none;
                        border-radius: 3px;
                    }
                    QPushButton:hover {
                        background-color: #f57c00;
                    }
                """)
            else:
                delete_btn = QPushButton("💀")
                delete_btn.setToolTip("Eliminar permanentemente")
                delete_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #d32f2f;
                        color: white;
                        border: none;
                        border-radius: 3px;
                    }
                    QPushButton:hover {
                        background-color: #b71c1c;
                    }
                """)
                
            delete_btn.setFixedSize(30, 30)
            delete_btn.clicked.connect(lambda checked, u=user_dict: self.delete_user(cast(Dict[str, Any], u)))
            
            # No permitir eliminar al admin actual
            if user_dict.get('username') == self.user_info.get('username'):
                delete_btn.setEnabled(False)
                delete_btn.setToolTip("No puedes eliminarte a ti mismo")
            
            actions_layout.addWidget(edit_btn)
            actions_layout.addWidget(delete_btn)
            
            # Agregar botón de reactivar para usuarios inactivos
            if not is_active:
                reactivate_btn = QPushButton("🔄")
                reactivate_btn.setToolTip("Reactivar usuario")
                reactivate_btn.setFixedSize(30, 30)
                reactivate_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #4caf50;
                        color: white;
                        border: none;
                        border-radius: 3px;
                    }
                    QPushButton:hover {
                        background-color: #388e3c;
                    }
                """)
                reactivate_btn.clicked.connect(lambda checked, u=user_dict: self.reactivate_user(cast(Dict[str, Any], u)))
                actions_layout.addWidget(reactivate_btn)
                
            actions_layout.addStretch()
            
            self.users_table.setCellWidget(row, 7, actions_widget)
            
            # Asegurar altura mínima para esta fila específicamente
            self.users_table.setRowHeight(row, 45)
    
    def update_statistics(self, users: List[Dict[str, Any]]):
        """Actualiza las estadísticas."""
        total = len(users)
        active = 0
        
        for user in users:
            # Convertir sqlite3.Row a diccionario si es necesario
            if hasattr(user, 'keys'):
                user_dict = dict(user)
            else:
                user_dict = user
            
            if user_dict.get('is_active', True):
                active += 1
        
        inactive = total - active
        
        self.total_users_label.setText(f"Total: {total}")
        self.active_users_label.setText(f"Activos: {active}")
        self.inactive_users_label.setText(f"Inactivos: {inactive}")
    
    def filter_users(self):
        """Filtra la tabla de usuarios."""
        search_text = self.search_edit.text().lower()
        role_filter = self.role_filter.currentData()
        status_filter = self.status_filter.currentData()
        
        for row in range(self.users_table.rowCount()):
            show_row = True
            
            # Filtro de búsqueda
            if search_text:
                username = self.users_table.item(row, 1).text().lower()
                full_name = self.users_table.item(row, 2).text().lower()
                email = self.users_table.item(row, 3).text().lower()
                
                if not (search_text in username or search_text in full_name or search_text in email):
                    show_row = False
            
            # Filtro de rol
            if role_filter and show_row:
                role_text = self.users_table.item(row, 4).text()
                if UserRole.ROLES.get(role_filter, '') not in role_text:
                    show_row = False
            
            # Filtro de estado
            if status_filter and show_row:
                status_text = self.users_table.item(row, 5).text()
                if status_filter == "active" and "Activo" not in status_text:
                    show_row = False
                elif status_filter == "inactive" and "Inactivo" not in status_text:
                    show_row = False
            
            self.users_table.setRowHidden(row, not show_row)
    
    def create_user(self):
        """Abre el diálogo para crear usuario."""
        dialog = CreateUserDialog(self)
        dialog.user_created.connect(self.on_user_created)
        dialog.exec()
    
    def edit_user(self, user_data: Dict[str, Any]):
        """Abre el diálogo para editar usuario."""
        dialog = EditUserDialog(user_data, self)
        dialog.user_updated.connect(self.on_user_updated)
        dialog.exec()
    
    def delete_user(self, user_data: Dict[str, Any]):
        """Elimina un usuario con opciones de eliminación."""
        username = user_data.get('username', '')
        is_active = user_data.get('is_active', 1)
        
        if is_active:
            # Usuario activo - ofrecer eliminación suave
            reply = QMessageBox.question(
                self,
                "Eliminar Usuario",
                f"¿Cómo desea eliminar al usuario '{username}'?\n\n"
                "• Sí: Desactivar usuario (recomendado)\n"
                "• No: Cancelar\n\n"
                "El usuario desactivado no podrá iniciar sesión pero se mantendrá "
                "en el historial para auditoría.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self._perform_user_deletion(user_data, permanent=False)
                
        else:
            # Usuario inactivo - ofrecer eliminación permanente
            reply = QMessageBox.question(
                self,
                "Eliminar Usuario Permanentemente",
                f"El usuario '{username}' ya está desactivado.\n\n"
                f"¿Desea eliminarlo PERMANENTEMENTE de la base de datos?\n\n"
                f"⚠️ ADVERTENCIA: Esta acción NO se puede deshacer.\n"
                f"Se perderá todo el historial de auditoría relacionado.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                # Confirmación adicional para eliminación permanente
                confirm = QMessageBox.critical(
                    self,
                    "CONFIRMACIÓN FINAL",
                    f"¿REALMENTE desea eliminar PERMANENTEMENTE al usuario '{username}'?\n\n"
                    f"Esta acción es IRREVERSIBLE.",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )
                
                if confirm == QMessageBox.StandardButton.Yes:
                    self._perform_user_deletion(user_data, permanent=True)
    
    def _perform_user_deletion(self, user_data: Dict[str, Any], permanent: bool = False):
        """Realiza la eliminación del usuario."""
        username = user_data.get('username', '')
        user_id = cast(int, user_data.get('id', 0))
        
        try:
            success = self.user_repo.delete_user(user_id, permanent=permanent)
            
            if success:
                action_type = "eliminado permanentemente" if permanent else "desactivado"
                QMessageBox.information(
                    self,
                    "Usuario Eliminado",
                    f"El usuario '{username}' ha sido {action_type} exitosamente."
                )
                
                # Recargar lista manteniendo el estado del checkbox
                include_inactive = self.show_inactive_check.isChecked()
                self.load_users(include_inactive=include_inactive)
                
                # Registrar en auditoría
                try:
                    admin_id = cast(int, self.user_info.get('id', 0))
                    action = "DELETE_USER_PERMANENT" if permanent else "DELETE_USER"
                    self.audit_repo.log_action(
                        user_id=admin_id,
                        action=action,
                        table_name="users",
                        record_id=user_id,
                        old_values=dict(user_data)
                    )
                except Exception as audit_error:
                    logger.error(f"Error registrando auditoría: {audit_error}")
                    
            else:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"No se pudo eliminar el usuario '{username}'."
                )
                
        except Exception as e:
            logger.error(f"Error eliminando usuario (permanent={permanent}): {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"Error eliminando usuario: {str(e)}"
            )
    
    def reactivate_user(self, user_data: Dict[str, Any]):
        """Reactiva un usuario desactivado."""
        username = user_data.get('username', '')
        user_id = cast(int, user_data.get('id', 0))
        
        reply = QMessageBox.question(
            self,
            "Reactivar Usuario",
            f"¿Está seguro de que desea reactivar al usuario '{username}'?\n\n"
            f"El usuario podrá volver a iniciar sesión en el sistema.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                success = self.user_repo.reactivate_user(user_id)
                
                if success:
                    QMessageBox.information(
                        self,
                        "Usuario Reactivado",
                        f"El usuario '{username}' ha sido reactivado exitosamente."
                    )
                    
                    # Recargar lista manteniendo el estado del checkbox
                    include_inactive = self.show_inactive_check.isChecked()
                    self.load_users(include_inactive=include_inactive)
                    
                    # Registrar en auditoría
                    try:
                        admin_id = cast(int, self.user_info.get('id', 0))
                        self.audit_repo.log_action(
                            user_id=admin_id,
                            action="REACTIVATE_USER",
                            table_name="users",
                            record_id=user_id,
                            new_values={'is_active': 1, 'reactivated_by': admin_id}
                        )
                    except Exception as audit_error:
                        logger.error(f"Error registrando auditoría: {audit_error}")
                        
                else:
                    QMessageBox.critical(
                        self,
                        "Error",
                        f"No se pudo reactivar el usuario '{username}'."
                    )
                    
            except Exception as e:
                logger.error(f"Error reactivando usuario: {e}")
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Error reactivando usuario: {str(e)}"
                )
    
    def on_user_created(self, user_data: Dict[str, Any]):
        """Maneja la creación de un nuevo usuario."""
        self.load_users()
        
        # Registrar en auditoría
        try:
            user_id = cast(int, self.user_info.get('id', 0))
            self.audit_repo.log_action(
                user_id=user_id,
                action="CREATE_USER",
                table_name="users",
                record_id=None,
                old_values=None,
                new_values={"description": f"Usuario creado: {user_data.get('username')}"}
            )
        except Exception as e:
            logger.error(f"Error registrando auditoría: {e}")
    
    def on_user_updated(self, user_data: Dict[str, Any]):
        """Maneja la actualización de un usuario."""
        self.load_users()
        
        # Registrar en auditoría
        try:
            user_id = cast(int, self.user_info.get('id', 0))
            self.audit_repo.log_action(
                user_id=user_id,
                action="UPDATE_USER",
                table_name="users",
                record_id=user_data.get('id'),
                old_values=None,
                new_values={"description": f"Usuario actualizado: {user_data.get('username', 'N/A')}"}
            )
        except Exception as e:
            logger.error(f"Error registrando auditoría: {e}")
    
    def apply_dark_theme(self):
        """Aplica el tema nocturno elegante al sistema de usuarios."""
        self.setStyleSheet("""
            QWidget {
                background-color: #1a1a1a;
                color: #e0e0e0;
            }
            
            QGroupBox {
                font-weight: bold;
                border: 2px solid #3a4b5c;
                border-radius: 12px;
                margin-top: 15px;
                padding-top: 15px;
                background-color: #2c3e50;
                color: #ecf0f1;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px 0 8px;
                color: #74b9ff;
                background-color: #1a1a1a;
                font-weight: bold;
            }
            
            QLabel {
                color: #e0e0e0;
                background-color: transparent;
            }
            
            QPushButton {
                padding: 12px 20px;
                border: 2px solid #34495e;
                border-radius: 8px;
                font-weight: bold;
                min-width: 120px;
                background-color: #34495e;
                color: #ecf0f1;
            }
            
            QPushButton:hover {
                background-color: #4a6741;
                border-color: #74b9ff;
                color: #ffffff;
            }
            
            QPushButton[default="true"] {
                background-color: #2980b9;
                border-color: #3498db;
            }
            
            QLineEdit, QComboBox, QTextEdit {
                background-color: #2c3e50;
                color: #ecf0f1;
                border: 2px solid #34495e;
                border-radius: 6px;
                padding: 8px;
            }
            
            QLineEdit:hover, QComboBox:hover {
                border-color: #74b9ff;
            }
        """)


def show_user_management(user_info: Dict[str, Any], parent: Optional[QWidget] = None) -> QDialog:
    """Muestra el diálogo de administración de usuarios."""
    dialog = QDialog(cast(QWidget, parent))
    dialog.setWindowTitle("Administración de Usuarios")
    dialog.setModal(True)
    dialog.resize(1200, 800)
    
    layout = QVBoxLayout(dialog)
    
    try:
        widget = UserManagementWidget(user_info)
        layout.addWidget(widget)
        
        # Botón cerrar
        close_button = QPushButton("Cerrar")
        close_button.clicked.connect(dialog.accept)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)
        
        return dialog
        
    except PermissionError as e:
        QMessageBox.warning(
            cast(QWidget, parent),
            "Acceso Denegado",
            str(e)
        )
        dialog.reject()
        return dialog
    except Exception as e:
        logger.error(f"Error inicializando administración de usuarios: {e}")
        QMessageBox.critical(
            cast(QWidget, parent),
            "Error",
            f"Error inicializando módulo: {str(e)}"
        )
        dialog.reject()
        return dialog


if __name__ == "__main__":
    import sys

    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # Datos de prueba para admin
    admin_user: Dict[str, Any] = {
        'id': 1,
        'username': 'admin',
        'role': 'admin',
        'full_name': 'Administrador del Sistema'
    }
    
    dialog = show_user_management(admin_user)
    dialog.exec()
    
    sys.exit(0)