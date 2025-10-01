"""
Formulario para crear y editar homologaciones de aplicaciones.
"""

from __future__ import annotations

from datetime import date, datetime
import logging
import sys
from typing import Any, Dict, Optional, cast

from PyQt6.QtCore import QDate, Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDateEdit,
    QDialog,
    QFormLayout,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)



from .notification_system import send_error, send_warning
from .theme import ThemeType, get_current_theme
logger = logging.getLogger(__name__)

class HomologationFormDialog(QDialog):
    """Dialog para crear o editar una homologación."""
    
    def __init__(
        self,
        parent: Optional[QWidget] = None,
        homologation_data: Optional[Dict[str, Any]] = None,
        user_info: Optional[Dict[str, Any]] = None,
        repo: Optional[Any] = None,
    ):
        """Inicializa el formulario."""
        super().__init__(parent)
        
        self.homologation_data: Optional[Dict[str, Any]] = homologation_data
        self.user_info: Optional[Dict[str, Any]] = user_info
        self.repo: Optional[Any] = repo
        
        # Determinar modo (crear/editar)
        self.is_edit_mode = homologation_data is not None
        
        self.setup_ui()
        self.setup_styles()
        self.setup_validation()
        
        if self.is_edit_mode:
            self.load_data()
    
    def setup_ui(self):
        """Configura la interfaz del formulario."""
        # Configuración de ventana
        title = "Editar Homologación" if self.is_edit_mode else "Nueva Homologación"
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumSize(600, 500)
        self.resize(700, 600)
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        
        # Título
        title_label = QLabel(title)
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Separador
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        main_layout.addWidget(line)
        
        # Área de scroll para el formulario
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        form_widget = QWidget()
        form_layout = QVBoxLayout(form_widget)
        form_layout.setSpacing(20)
        
        # Campos requeridos
        self.setup_required_fields(form_layout)
        
        # Campos opcionales
        self.setup_optional_fields(form_layout)
        
        # Campos adicionales
        self.setup_additional_fields(form_layout)
        
        scroll_area.setWidget(form_widget)
        main_layout.addWidget(scroll_area)
        
        # Botones
        self.setup_buttons(main_layout)
        
        # Estilos
        self.setup_styles()
    
    def setup_required_fields(self, layout):
        """Configura los campos obligatorios."""
        group = QGroupBox("Información Básica (Obligatoria)")
        group_layout = QFormLayout(group)
        group_layout.setSpacing(15)
        
        # Nombre Real (obligatorio)
        self.real_name_edit = QLineEdit()
        self.real_name_edit.setPlaceholderText("Ingrese el nombre real de la aplicación")
        self.real_name_edit.setMaxLength(200)
        required_label = QLabel("Nombre Real: *")
        required_label.setStyleSheet("font-weight: bold;")
        group_layout.addRow(required_label, self.real_name_edit)
        
        layout.addWidget(group)
    
    def setup_optional_fields(self, layout):
        """Configura los campos opcionales."""
        group = QGroupBox("Información Adicional")
        group_layout = QFormLayout(group)
        group_layout.setSpacing(15)
        
        # Nombre Lógico (opcional)
        self.logical_name_edit = QLineEdit()
        self.logical_name_edit.setPlaceholderText("Nombre lógico o alias de la aplicación")
        self.logical_name_edit.setMaxLength(200)
        group_layout.addRow("Nombre Lógico:", self.logical_name_edit)
        
        # URL de Knowledge Base
        self.kb_url_edit = QLineEdit()
        self.kb_url_edit.setPlaceholderText("https://wiki.empresa.com/app/documentacion")
        group_layout.addRow("URL Documentación:", self.kb_url_edit)
        
        # KB SYNC
        self.kb_sync_check = QCheckBox("Sincronizar con base de conocimiento")
        group_layout.addRow("KB SYNC:", self.kb_sync_check)
        
        # Repositorio
        self.repo_combo = QComboBox()
        self.repo_combo.addItem("-- Seleccione --", "")
        self.repo_combo.addItem("AESA", "AESA")
        self.repo_combo.addItem("APPS$", "APPS$")
        self.repo_combo.setCurrentIndex(0)
        group_layout.addRow("Repositorio:", self.repo_combo)
        
        # Fecha de homologación
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        group_layout.addRow("Fecha Homologación:", self.date_edit)
        
        layout.addWidget(group)
    
    def setup_additional_fields(self, layout):
        """Configura los campos adicionales."""
        group = QGroupBox("Detalles")
        group_layout = QFormLayout(group)
        group_layout.setSpacing(15)
        
        # Detalles
        self.details_edit = QTextEdit()
        self.details_edit.setPlaceholderText(
            "Ingrese detalles adicionales sobre la aplicación:\n"
            "- Propósito\n"
            "- Características\n"
            "- Información técnica\n"
            "- Otros datos relevantes"
        )
        self.details_edit.setMinimumHeight(150)
        group_layout.addRow("Descripción:", self.details_edit)
        
        # Información de usuario
        if not self.is_edit_mode:
            if self.user_info:
                user_info_text = f"Creado por: {self.user_info.get('username', 'Usuario')} ({self.user_info.get('full_name', '')})"
                user_info_label = QLabel(user_info_text)
                user_info_label.setStyleSheet("color: #666; font-size: 11px;")
                group_layout.addRow("", user_info_label)
        
        layout.addWidget(group)
    
    def setup_buttons(self, layout):
        """Configura los botones del formulario."""
        button_layout = QHBoxLayout()
        
        # Espaciador
        button_layout.addStretch()
        
        # Botón cancelar
        cancel_button = QPushButton("Cancelar")
        cancel_button.clicked.connect(self.reject)
        
        # Botón guardar
        save_button = QPushButton("Guardar")
        save_button.setProperty("primary", True)
        save_button.clicked.connect(self.accept_form)
        
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(save_button)
        
        layout.addLayout(button_layout)
    
    def setup_styles(self):
        """Configura estilos CSS según el tema actual."""
        current_theme = get_current_theme()
        is_dark = current_theme == ThemeType.DARK
        
        if is_dark:
            # Tema oscuro
            self.setStyleSheet("""
                QDialog {
                    background-color: #222222;
                    color: #ffffff;
                }
                
                QLabel {
                    color: #e0e0e0;
                    font-weight: normal;
                }
                
                QGroupBox {
                    font-weight: bold;
                    border: 1px solid #555555;
                    border-radius: 4px;
                    margin-top: 10px;
                    padding-top: 10px;
                    color: #e0e0e0;
                }
                
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px 0 5px;
                    color: #e0e0e0;
                }
                
                QLineEdit, QTextEdit {
                    padding: 8px;
                    border: 1px solid #555555;
                    border-radius: 4px;
                    background-color: #333333;
                    color: #ffffff;
                }
                
                QLineEdit:focus, QTextEdit:focus, QDateEdit:focus, QComboBox:focus {
                    border: 2px solid #0078d4;
                }
                
                QPushButton {
                    background-color: #3c3c3c;
                    border: 1px solid #555555;
                    border-radius: 4px;
                    padding: 8px 16px;
                    color: #ffffff;
                }
                
                QPushButton:hover {
                    background-color: #4c4c4c;
                }
                
                QPushButton:pressed {
                    background-color: #2c2c2c;
                }
                
                QPushButton[primary=true] {
                    background-color: #0078d4;
                    color: white;
                    border: none;
                }
                
                QPushButton[primary=true]:hover {
                    background-color: #106ebe;
                }
                
                QPushButton[primary=true]:pressed {
                    background-color: #005a9e;
                }
                
                QDateEdit, QComboBox {
                    background-color: #333333;
                    border: 1px solid #555555;
                    border-radius: 4px;
                    padding: 6px;
                    color: #ffffff;
                }
                
                QCheckBox {
                    font-size: 11pt;
                    color: #e0e0e0;
                }
                
                QCheckBox::indicator {
                    width: 18px;
                    height: 18px;
                }
                
                QCheckBox::indicator:unchecked {
                    border: 1px solid #666666;
                    background-color: #333333;
                    border-radius: 3px;
                }
                
                QCheckBox::indicator:checked {
                    border: 1px solid #0078d4;
                    background-color: #0078d4;
                    border-radius: 3px;
                }
            """)
        else:
            # Tema claro
            self.setStyleSheet("""
                QDialog {
                    background-color: #f8f8f8;
                    color: #333333;
                }
                
                QLabel {
                    color: #333333;
                    font-weight: normal;
                }
                
                QGroupBox {
                    font-weight: bold;
                    border: 1px solid #d0d0d0;
                    border-radius: 4px;
                    margin-top: 10px;
                    padding-top: 10px;
                    color: #333333;
                }
                
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px 0 5px;
                    color: #333333;
                }
                
                QLineEdit, QTextEdit {
                    padding: 8px;
                    border: 1px solid #d0d0d0;
                    border-radius: 4px;
                    background-color: white;
                    color: #333333;
                }
                
                QLineEdit:focus, QTextEdit:focus, QDateEdit:focus, QComboBox:focus {
                    border: 2px solid #0078d4;
                }
                
                QPushButton {
                    background-color: #f0f0f0;
                    border: 1px solid #d0d0d0;
                    border-radius: 4px;
                    padding: 8px 16px;
                    color: #333333;
                }
                
                QPushButton:hover {
                    background-color: #e0e0e0;
                }
                
                QPushButton:pressed {
                    background-color: #d0d0d0;
                }
                
                QPushButton[primary=true] {
                    background-color: #0078d4;
                    color: white;
                    border: none;
                }
                
                QPushButton[primary=true]:hover {
                    background-color: #106ebe;
                }
                
                QPushButton[primary=true]:pressed {
                    background-color: #005a9e;
                }
                
                QDateEdit, QComboBox {
                    background-color: white;
                    border: 1px solid #d0d0d0;
                    border-radius: 4px;
                    padding: 6px;
                    color: #333333;
                }
                
                QCheckBox {
                    font-size: 11pt;
                    color: #333333;
                }
                
                QCheckBox::indicator {
                    width: 18px;
                    height: 18px;
                }
                
                QCheckBox::indicator:unchecked {
                    border: 1px solid #d0d0d0;
                    background-color: white;
                    border-radius: 3px;
                }
                
                QCheckBox::indicator:checked {
                    border: 1px solid #0078d4;
                    background-color: #0078d4;
                    border-radius: 3px;
                }
            """)
    
    def setup_validation(self):
        """Configura validaciones para los campos del formulario."""
        # Validación para URL de KB
        self.kb_url_edit.textChanged.connect(self.validate_kb_url)
    
    def validate_kb_url(self):
        """Valida que la URL de KB tenga un formato correcto."""
        url = self.kb_url_edit.text().strip()
        
        if url and not (url.startswith('http://') or url.startswith('https://')):
            self.kb_url_edit.setStyleSheet("""
                QLineEdit {
                    border: 2px solid #ffc107;
                    background-color: #fffbf0;
                    color: #333333;
                }
            """)
        else:
            # Usar el color adecuado según el tema
            current_theme = get_current_theme()
            is_dark = current_theme == ThemeType.DARK
            
            if is_dark:
                self.kb_url_edit.setStyleSheet("""
                    QLineEdit {
                        background-color: #333333;
                        color: #ffffff;
                    }
                """)
            else:
                self.kb_url_edit.setStyleSheet("""
                    QLineEdit {
                        background-color: white;
                        color: #333333;
                    }
                """)
    
    def load_data(self):
        """Carga los datos existentes en el formulario."""
        data_opt = self.homologation_data
        if not data_opt:
            return
        data = cast(Dict[str, Any], data_opt)
        
        # Campos básicos
        self.real_name_edit.setText(data.get('real_name', ''))
        self.logical_name_edit.setText(data.get('logical_name', '') or '')
        self.kb_url_edit.setText(data.get('kb_url', '') or '')
        self.kb_sync_check.setChecked(data.get('kb_sync', False) or False)
        
        # Repositorio
        repo_idx = self.repo_combo.findData(data.get('repository_location'))
        if repo_idx >= 0:
            self.repo_combo.setCurrentIndex(repo_idx)
        
        # Fecha
        if data.get('homologation_date'):
            try:
                date_obj = datetime.strptime(data['homologation_date'], '%Y-%m-%d').date()
                self.date_edit.setDate(QDate(date_obj.year, date_obj.month, date_obj.day))
            except ValueError:
                pass
        
        # Detalles
        self.details_edit.setPlainText(data.get('details', '') or '')
    
    def validate_form(self):
        """Valida el formulario antes de guardar."""
        # Nombre real es obligatorio
        real_name = self.real_name_edit.text().strip()
        
        # Visual feedback para campo obligatorio
        if real_name:
            current_theme = get_current_theme()
            is_dark = current_theme == ThemeType.DARK
            
            if is_dark:
                self.real_name_edit.setStyleSheet("""
                    QLineEdit {
                        background-color: #333333;
                        color: #ffffff;
                    }
                """)
            else:
                self.real_name_edit.setStyleSheet("""
                    QLineEdit {
                        background-color: white;
                        color: #333333;
                    }
                """)
        else:
            self.real_name_edit.setStyleSheet("""
                QLineEdit {
                    border: 2px solid #dc3545;
                    background-color: #fff5f5;
                    color: #333333;
                }
            """)
            send_warning("Advertencia", "Nombre Real es un campo obligatorio.", "main_window")
            return False
        
        # Validar URL de KB si está presente
        url = self.kb_url_edit.text().strip()
        if url and not (url.startswith('http://') or url.startswith('https://')):
            send_warning("Advertencia", "La URL de documentación debe comenzar con http:// o https://", "main_window")
            return False
        
        return True
    
    def accept_form(self):
        """Valida y acepta el formulario."""
        if self.validate_form():
            self.accept()
    
    def get_form_data(self):
        """Extrae los datos del formulario."""
        data = {
            'real_name': self.real_name_edit.text().strip(),
            'logical_name': self.logical_name_edit.text().strip() or None,
            'kb_url': self.kb_url_edit.text().strip() or None,
            'kb_sync': self.kb_sync_check.isChecked(),
            'repository_location': self.repo_combo.currentData() or None,
            'homologation_date': self.date_edit.date().toString('yyyy-MM-dd'),
            'details': self.details_edit.toPlainText().strip() or None
        }
        
        if self.is_edit_mode and self.homologation_data:
            # Para edición, mantener el ID original
            data['id'] = self.homologation_data['id']
        
        return data