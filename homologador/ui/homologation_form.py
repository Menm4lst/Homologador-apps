"""
Formulario para crear y editar homologaciones.
Interfaz completa con validaciones y manejo de datos.
"""
import logging
import tempfile
from pathlib import Path
from datetime import datetime, date
from typing import Optional, Dict, Any

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QGridLayout,
    QLabel, QLineEdit, QTextEdit, QDateEdit, QComboBox, QCheckBox,
    QPushButton, QDialogButtonBox, QMessageBox, QFrame, QScrollArea,
    QWidget, QSizePolicy, QSpacerItem, QGroupBox
)
from PyQt6.QtCore import Qt, QDate, pyqtSignal, QThread, pyqtSlot, QTimer
from PyQt6.QtGui import QFont

from core.storage import get_homologation_repository
from data.seed import get_auth_service
from .theme import set_widget_style_class
from .autosave_manager import AutoSaveManager

logger = logging.getLogger(__name__)


class HomologationSaveWorker(QThread):
    """Worker thread para guardar homologaciones sin bloquear la UI."""
    
    save_successful = pyqtSignal(int)
    save_failed = pyqtSignal(str)
    
    def __init__(self, homologation_data: Dict[str, Any], homologation_id: int = None):
        super().__init__()
        self.homologation_data = homologation_data
        self.homologation_id = homologation_id  # None para crear, ID para editar
        self.repo = get_homologation_repository()
    
    def run(self):
        """Guarda la homologación en segundo plano."""
        try:
            if self.homologation_id:
                # Editar existente
                success = self.repo.update(self.homologation_id, self.homologation_data)
                if success:
                    self.save_successful.emit(self.homologation_id)
                else:
                    self.save_failed.emit("Error actualizando homologación")
            else:
                # Crear nueva
                new_id = self.repo.create(self.homologation_data)
                self.save_successful.emit(new_id)
                
        except Exception as e:
            logger.error(f"Error guardando homologación: {e}")
            self.save_failed.emit(str(e))


class HomologationFormDialog(QDialog):
    """Dialog para crear/editar homologaciones."""
    
    homologation_saved = pyqtSignal(int)
    
    def __init__(self, parent=None, homologation_data: Dict[str, Any] = None, user_info: Dict[str, Any] = None):
        super().__init__(parent)
        self.homologation_data = homologation_data  # None para crear, datos para editar
        self.user_info = user_info
        self.auth_service = get_auth_service()
        
        # Inicializar administrador de autoguardado
        self.autosave_manager = AutoSaveManager(self)
        
        # Etiqueta de estado para mensajes informativos
        self.status_label = None
        self.save_worker = None
        
        # Determinar modo (crear/editar)
        self.is_edit_mode = homologation_data is not None
        
        self.setup_ui()
        self.setup_styles()
        self.setup_validation()
        
        # Cargar datos - primero intentar recuperar un borrador
        if not self.is_edit_mode:
            # Para nueva homologación, verificar si hay borradores
            draft = self.autosave_manager.get_latest_draft()
            if draft:
                # Preguntar al usuario si desea cargar el borrador
                if self.confirm_load_draft():
                    self.homologation_data = draft
        
        # Cargar datos (del borrador o existentes)
        if self.homologation_data:
            self.load_data()
        
        # Iniciar autoguardado después de cargar datos
        self.autosave_manager.start()
    
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
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        
        # Widget contenedor del formulario
        form_widget = QWidget()
        form_layout = QVBoxLayout(form_widget)
        
        # Campos obligatorios
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
        """Configura los campos opcionales de información."""
        group = QGroupBox("Información Adicional")
        group_layout = QFormLayout(group)
        group_layout.setSpacing(15)
        
        # Nombre Lógico
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
        
        # Fecha de Homologación
        self.homologation_date_edit = QDateEdit()
        self.homologation_date_edit.setDate(QDate.currentDate())
        self.homologation_date_edit.setCalendarPopup(True)
        self.homologation_date_edit.setDisplayFormat("dd/MM/yyyy")
        group_layout.addRow("Fecha Homologación:", self.homologation_date_edit)
        
        layout.addWidget(group)
    
    def setup_additional_fields(self, layout):
        """Configura campos adicionales y metadatos."""
        group = QGroupBox("Configuración y Detalles")
        group_layout = QFormLayout(group)
        group_layout.setSpacing(15)
        
        # Versiones Previas
        self.has_previous_versions_check = QCheckBox("La aplicación tiene versiones previas")
        group_layout.addRow("Versiones Previas:", self.has_previous_versions_check)
        
        # Ubicación del Repositorio
        self.repository_location_combo = QComboBox()
        self.repository_location_combo.addItems(["Seleccionar...", "AESA", "APPS$"])
        group_layout.addRow("Repositorio:", self.repository_location_combo)
        
        # Detalles / Observaciones
        self.details_edit = QTextEdit()
        self.details_edit.setPlaceholderText(
            "Ingrese observaciones, detalles técnicos, notas de configuración, "
            "requisitos especiales, o cualquier información relevante sobre la homologación..."
        )
        self.details_edit.setMaximumHeight(120)
        group_layout.addRow("Detalles:", self.details_edit)
        
        layout.addWidget(group)
    
    def setup_buttons(self, layout):
        """Configura los botones del dialog."""
        button_layout = QHBoxLayout()
        
        # Información de usuario
        if self.user_info:
            user_info_label = QLabel(f"Usuario: {self.user_info['username']} | Rol: {self.user_info['role']}")
            user_info_label.setStyleSheet("color: #666; font-size: 11px;")
            button_layout.addWidget(user_info_label)
        
        # Etiqueta para mensajes de estado (autoguardado, validación, etc.)
        self.status_label = QLabel()
        self.status_label.setStyleSheet("color: #0078d4; font-size: 11px;")
        button_layout.addWidget(self.status_label)
        
        button_layout.addStretch()
        
        # Botón Guardar
        self.save_button = QPushButton("Guardar")
        self.save_button.clicked.connect(self.save_homologation)
        self.save_button.setDefault(True)
        button_layout.addWidget(self.save_button)
        
        # Botón Cancelar
        cancel_button = QPushButton("Cancelar")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
    
    def setup_styles(self):
        """Configura estilos CSS según el tema actual."""
        from .theme import get_current_theme, ThemeType
        
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
                color: #ffffff;
                font-size: 11pt;
                selection-background-color: #0078d4;
            }
            
            QDateEdit, QComboBox {
                padding: 8px;
                border: 1px solid #555555;
                border-radius: 4px;
                background-color: #333333;
                color: #ffffff;
                font-size: 11pt;
            }
            
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 15px;
                border-left: 1px solid #555555;
            }
            
            QComboBox QAbstractItemView {
                background-color: #333333;
                color: #ffffff;
                selection-background-color: #0078d4;
            }
            
            QLineEdit:focus, QTextEdit:focus, QDateEdit:focus, QComboBox:focus {
                border-color: #0078d4;
                outline: none;
            }
            
            QPushButton {
                padding: 10px 20px;
                border: none;
                border-radius: 4px;
                font-size: 11pt;
                font-weight: bold;
                min-width: 100px;
            }
            
            QPushButton[default="true"] {
                background-color: #0078d4;
                color: white;
            }
            
            QPushButton[default="true"]:hover {
                background-color: #106ebe;
            }
            
            QPushButton:not([default="true"]) {
                background-color: #555555;
                color: white;
            }
            
            QPushButton:not([default="true"]):hover {
                background-color: #666666;
            }
            
            QPushButton:disabled {
                background-color: #333333;
                color: #777777;
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
            
            QSpinBox, QDoubleSpinBox {
                background-color: #333333;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 6px;
            }
            
            QSpinBox::up-button, QDoubleSpinBox::up-button {
                subcontrol-origin: border;
                subcontrol-position: top right;
                border-left: 1px solid #555555;
                border-bottom: 1px solid #555555;
            }
            
            QSpinBox::down-button, QDoubleSpinBox::down-button {
                subcontrol-origin: border;
                subcontrol-position: bottom right;
                border-left: 1px solid #555555;
            }
        """)
    
    def setup_validation(self):
        """Configura validaciones en tiempo real."""
        # Conectar eventos de cambio de texto para validación completa
        self.real_name_edit.textChanged.connect(lambda: self.validate_form())
        self.logical_name_edit.textChanged.connect(lambda: self.validate_form())
        self.details_edit.textChanged.connect(lambda: self.validate_form())
        
        # Validación específica de URL
        self.kb_url_edit.textChanged.connect(self.validate_url)
        self.kb_url_edit.textChanged.connect(lambda: self.validate_form())
        
        # Validación inicial
        self.validate_form()        # Aplicar estilos iniciales según el tema actual
        self.apply_theme_styles()
        
    def apply_theme_styles(self):
        """Aplica estilos adaptados al tema actual a todos los campos."""
        from .theme import get_current_theme, ThemeType
        current_theme = get_current_theme()
        is_dark = current_theme == ThemeType.DARK
        
        # Definir estilos según el tema
        if is_dark:
            input_style = """
                background-color: #333333;
                color: #ffffff;
            """
            text_area_style = """
                background-color: #333333;
                color: #ffffff;
            """
        else:
            input_style = """
                background-color: white;
                color: #333333;
            """
            text_area_style = """
                background-color: white;
                color: #333333;
            """
        
        # Aplicar estilos a campos de entrada (excepto real_name que se maneja en validate_form)
        if self.real_name_edit.text().strip():  # Solo si no está en estado de error
            self.real_name_edit.setStyleSheet(f"QLineEdit {{ {input_style} }}")
            
        self.logical_name_edit.setStyleSheet(f"QLineEdit {{ {input_style} }}")
        
        # No aplicar al kb_url_edit ya que se maneja en validate_url
        
        # Área de texto
        self.details_edit.setStyleSheet(f"QTextEdit {{ {text_area_style} }}")
    
    def validate_form(self):
        """Valida el formulario completo y habilita/deshabilita el botón guardar."""
        # Validar campos requeridos
        real_name = self.real_name_edit.text().strip()
        
        # Validaciones adicionales
        validation_errors = []
        
        # 1. Nombre real es obligatorio
        is_real_name_valid = bool(real_name)
        if not is_real_name_valid:
            validation_errors.append("El nombre real es obligatorio")
        elif len(real_name) < 2:
            validation_errors.append("El nombre real debe tener al menos 2 caracteres")
            is_real_name_valid = False
        elif len(real_name) > 255:
            validation_errors.append("El nombre real no puede exceder 255 caracteres")
            is_real_name_valid = False
        
        # 2. Validar URL si se proporciona
        kb_url = self.kb_url_edit.text().strip()
        is_url_valid = True
        if kb_url:
            is_url_valid = self._is_valid_url(kb_url)
            if not is_url_valid:
                validation_errors.append("La URL de KB no tiene un formato válido")
        
        # 3. Validar nombre lógico si se proporciona
        logical_name = self.logical_name_edit.text().strip()
        is_logical_name_valid = True
        if logical_name and len(logical_name) > 255:
            validation_errors.append("El nombre lógico no puede exceder 255 caracteres")
            is_logical_name_valid = False
        
        # 4. Validar detalles si se proporcionan
        details = self.details_edit.toPlainText().strip()
        is_details_valid = True
        if details and len(details) > 5000:
            validation_errors.append("Los detalles no pueden exceder 5000 caracteres")
            is_details_valid = False
        
        # El formulario es válido si no hay errores críticos
        is_form_valid = is_real_name_valid and is_url_valid and is_logical_name_valid and is_details_valid
        
        # Habilitar/deshabilitar botón guardar
        self.save_button.setEnabled(is_form_valid)
        
        # Aplicar estilos visuales
        self._apply_validation_styles(is_real_name_valid, is_url_valid, is_logical_name_valid, is_details_valid)
        
        # Mostrar errores en tooltip si los hay
        if validation_errors:
            self.save_button.setToolTip("\n".join(validation_errors))
        else:
            self.save_button.setToolTip("Guardar homologación")
            
        return is_form_valid, validation_errors
    
    def validate_url(self):
        """Valida formato de URL."""
        import re
        url = self.kb_url_edit.text().strip()
        
        # Regex para validar URLs básicas
        url_pattern = r'^(https?:\/\/)?(www\.)?([a-zA-Z0-9]+(-[a-zA-Z0-9]+)*\.)+[a-zA-Z]{2,}(\/[a-zA-Z0-9\-._~:/?#[\]@!$&\'()*+,;=]*)?$'
        
        if url:
            if not (url.startswith('http://') or url.startswith('https://')):
                # URL sin protocolo
                self.kb_url_edit.setStyleSheet("""
                    QLineEdit {
                        border: 2px solid #ffc107;
                        background-color: #fffbf0;
                        color: #333333;
                    }
                """)
                # Mostrar tooltip con sugerencia
                self.kb_url_edit.setToolTip("Sugerencia: Añada 'https://' al principio de la URL")
            elif not re.match(url_pattern, url):
                # URL con formato inválido
                self.kb_url_edit.setStyleSheet("""
                    QLineEdit {
                        border: 2px solid #dc3545;
                        background-color: #fff5f5;
                        color: #333333;
                    }
                """)
                self.kb_url_edit.setToolTip("La URL parece no tener un formato válido")
            else:
                # URL válida - aplicar estilo normal según el tema
                from .theme import get_current_theme, ThemeType
                current_theme = get_current_theme()
                is_dark = current_theme == ThemeType.DARK
                
                if is_dark:
                    self.kb_url_edit.setStyleSheet("""
                        QLineEdit {
                            background-color: #333333;
                            color: #ffffff;
                            border: 1px solid #0078d4;
                        }
                    """)
                else:
                    self.kb_url_edit.setStyleSheet("""
                        QLineEdit {
                            background-color: white;
                            color: #333333;
                            border: 1px solid #0078d4;
                        }
                    """)
                self.kb_url_edit.setToolTip("URL válida")
        else:
            # Campo vacío - estilo normal según el tema
            from .theme import get_current_theme, ThemeType
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
            self.kb_url_edit.setToolTip("")  # Quitar tooltip
    
    def _is_valid_url(self, url: str) -> bool:
        """Valida si una URL tiene formato correcto."""
        import re
        try:
            # Patrón más robusto para URLs
            url_pattern = r'^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$'
            return bool(re.match(url_pattern, url))
        except Exception:
            return False
    
    def _apply_validation_styles(self, is_real_name_valid: bool, is_url_valid: bool, 
                               is_logical_name_valid: bool, is_details_valid: bool):
        """Aplica estilos visuales según el estado de validación."""
        try:
            from .theme import get_current_theme, ThemeType
            current_theme = get_current_theme()
            is_dark = current_theme == ThemeType.DARK
            
            # Estilos base según tema
            if is_dark:
                normal_style = """
                    QLineEdit, QTextEdit {
                        background-color: #333333;
                        color: #ffffff;
                        border: 1px solid #555555;
                    }
                """
                valid_style = """
                    QLineEdit, QTextEdit {
                        background-color: #333333;
                        color: #ffffff;
                        border: 1px solid #0078d4;
                    }
                """
            else:
                normal_style = """
                    QLineEdit, QTextEdit {
                        background-color: white;
                        color: #333333;
                        border: 1px solid #cccccc;
                    }
                """
                valid_style = """
                    QLineEdit, QTextEdit {
                        background-color: white;
                        color: #333333;
                        border: 1px solid #0078d4;
                    }
                """
            
            error_style = """
                QLineEdit, QTextEdit {
                    border: 2px solid #dc3545;
                    background-color: #fff5f5;
                    color: #333333;
                }
            """
            
            # Aplicar estilos según validación
            self.real_name_edit.setStyleSheet(error_style if not is_real_name_valid else valid_style)
            
            # URL solo si tiene contenido
            if self.kb_url_edit.text().strip():
                self.kb_url_edit.setStyleSheet(error_style if not is_url_valid else valid_style)
            else:
                self.kb_url_edit.setStyleSheet(normal_style)
                
            # Nombre lógico solo si tiene contenido
            if self.logical_name_edit.text().strip():
                self.logical_name_edit.setStyleSheet(error_style if not is_logical_name_valid else valid_style)
            else:
                self.logical_name_edit.setStyleSheet(normal_style)
                
            # Detalles solo si tiene contenido
            if self.details_edit.toPlainText().strip():
                self.details_edit.setStyleSheet(error_style if not is_details_valid else valid_style)
            else:
                self.details_edit.setStyleSheet(normal_style)
                
        except Exception as e:
            print(f"Error aplicando estilos de validación: {e}")
    
    def _check_duplicate_name(self, real_name: str) -> int | None:
        """Verifica si ya existe una homologación con el mismo nombre real."""
        try:
            from ..core.storage import DatabaseManager
            db = DatabaseManager()
            
            # Buscar homologaciones con el mismo nombre real
            results = db.search_homologations(search_text=real_name, exact_match=True)
            
            # Filtrar por coincidencia exacta del nombre real
            for homolog in results:
                if homolog.get('real_name', '').lower() == real_name.lower():
                    return homolog.get('id')
                    
            return None
            
        except Exception as e:
            print(f"Error verificando nombre duplicado: {e}")
            return None
    
    def load_data(self):
        """Carga datos existentes en el formulario (modo edición)."""
        if not self.homologation_data:
            return
        
        data = self.homologation_data
        
        # Cargar campos
        self.real_name_edit.setText(data.get('real_name', ''))
        self.logical_name_edit.setText(data.get('logical_name', ''))
        self.kb_url_edit.setText(data.get('kb_url', ''))
        self.kb_sync_check.setChecked(bool(data.get('kb_sync')))
        
        # Fecha
        if data.get('homologation_date'):
            try:
                from datetime import datetime
                date_obj = datetime.strptime(data['homologation_date'], '%Y-%m-%d').date()
                self.homologation_date_edit.setDate(QDate(date_obj))
            except ValueError:
                pass  # Usar fecha actual por defecto
        
        # Checkbox
        self.has_previous_versions_check.setChecked(bool(data.get('has_previous_versions')))
        
        # Repositorio
        repo_location = data.get('repository_location', '')
        if repo_location in ['AESA', 'APPS$']:
            index = self.repository_location_combo.findText(repo_location)
            if index >= 0:
                self.repository_location_combo.setCurrentIndex(index)
        
        # Detalles
        self.details_edit.setPlainText(data.get('details', ''))
        
        # Validar formulario
        self.validate_form()
    
    def get_form_data(self) -> Dict[str, Any]:
        """Extrae los datos del formulario."""
        data = {
            'real_name': self.real_name_edit.text().strip(),
            'logical_name': self.logical_name_edit.text().strip() or None,
            'kb_url': self.kb_url_edit.text().strip() or None,
            'kb_sync': self.kb_sync_check.isChecked(),
            'homologation_date': self.homologation_date_edit.date().toString(Qt.DateFormat.ISODate),
            'has_previous_versions': self.has_previous_versions_check.isChecked(),
            'details': self.details_edit.toPlainText().strip() or None
        }
        
        # Repositorio
        repo = self.repository_location_combo.currentText()
        if repo in ['AESA', 'APPS$']:
            data['repository_location'] = repo
        else:
            data['repository_location'] = None
        
        # Usuario creador (solo para nuevas homologaciones)
        if not self.is_edit_mode and self.user_info:
            data['created_by'] = self.user_info['user_id']
        
        return data
    
    def confirm_load_draft(self):
        """Pregunta al usuario si desea cargar un borrador guardado."""
        from PyQt6.QtWidgets import QMessageBox
        response = QMessageBox.question(
            self, 
            "Borrador disponible",
            "Existe un borrador guardado automáticamente.\n¿Desea cargarlo?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes
        )
        return response == QMessageBox.StandardButton.Yes
    
    def showEvent(self, event):
        """Se ejecuta cuando se muestra el formulario."""
        super().showEvent(event)
        # Aplicar estilos según el tema actual
        self.apply_theme_styles()
    
    def save_homologation(self):
        """Guarda la homologación con validación completa."""
        try:
            # Validación final completa
            is_valid, validation_errors = self.validate_form()
            
            if not is_valid:
                # Mostrar errores específicos
                error_message = "Se encontraron los siguientes errores:\n\n" + "\n• ".join(validation_errors)
                QMessageBox.warning(self, "Errores de validación", error_message)
                
                # Enfocar el primer campo con error
                if "nombre real" in validation_errors[0].lower():
                    self.real_name_edit.setFocus()
                elif "url" in validation_errors[0].lower():
                    self.kb_url_edit.setFocus()
                elif "lógico" in validation_errors[0].lower():
                    self.logical_name_edit.setFocus()
                elif "detalles" in validation_errors[0].lower():
                    self.details_edit.setFocus()
                    
                return
            
            # Validaciones adicionales de negocio
            form_data = self.get_form_data()
            
            # Verificar que no exista ya una homologación con el mismo nombre real
            if not self.is_edit_mode:
                existing_id = self._check_duplicate_name(form_data['real_name'])
                if existing_id:
                    response = QMessageBox.question(
                        self, 
                        "Nombre duplicado",
                        f"Ya existe una homologación con el nombre '{form_data['real_name']}'.\n"
                        "¿Desea continuar de todas formas?",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                        QMessageBox.StandardButton.No
                    )
                    if response != QMessageBox.StandardButton.Yes:
                        return
            
            # Deshabilitar botón y mostrar progreso
            self.save_button.setEnabled(False)
            self.save_button.setText("Guardando...")
            
            # Guardar en worker thread
            homologation_id = self.homologation_data.get('id') if self.is_edit_mode else None
            self.save_worker = HomologationSaveWorker(form_data, homologation_id)
            self.save_worker.save_successful.connect(self.on_save_successful)
            self.save_worker.save_failed.connect(self.on_save_failed)
            self.save_worker.start()
            
        except Exception as e:
            # Manejo de errores inesperados
            QMessageBox.critical(
                self, 
                "Error inesperado", 
                f"Ocurrió un error inesperado al intentar guardar:\n{str(e)}"
            )
            self.save_button.setEnabled(True)
            self.save_button.setText("Guardar")
    
    @pyqtSlot(int)
    def on_save_successful(self, homologation_id):
        """Maneja guardado exitoso."""
        action = "actualizada" if self.is_edit_mode else "creada"
        QMessageBox.information(self, "Éxito", f"Homologación {action} exitosamente")
        
        # Emitir señal y cerrar
        self.homologation_saved.emit(homologation_id)
        self.accept()
    
    @pyqtSlot(str)
    def on_save_failed(self, error_message):
        """Maneja error de guardado."""
        QMessageBox.critical(self, "Error", f"Error guardando homologación: {error_message}")
        
        # Rehabilitar botón
        self.save_button.setEnabled(True)
        self.save_button.setText("Guardar")
    
    def closeEvent(self, event):
        """Maneja el cierre del dialog."""
        if self.save_worker and self.save_worker.isRunning():
            self.save_worker.terminate()
            self.save_worker.wait()
        
        # Detener el autoguardado
        if self.autosave_manager:
            self.autosave_manager.stop()
            
        event.accept()
        
    def reject(self):
        """Se llama cuando se cierra el diálogo con 'Cancelar'."""
        # Si hay cambios sustanciales, mostrar diálogo de confirmación
        real_name = self.real_name_edit.text().strip()
        if real_name:
            from PyQt6.QtWidgets import QMessageBox
            response = QMessageBox.question(
                self, 
                "Confirmar cancelación",
                "¿Está seguro de que desea salir sin guardar?\nLos datos se guardarán automáticamente como borrador.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if response == QMessageBox.StandardButton.No:
                return
            
            # Forzar un autoguardado antes de cerrar
            if self.autosave_manager:
                self.autosave_manager.auto_save()
        
        # Cerrar el diálogo
        super().reject()


def show_homologation_form(parent=None, homologation_data=None, user_info=None):
    """Función utilitaria para mostrar el formulario de homologación."""
    dialog = HomologationFormDialog(parent, homologation_data, user_info)
    return dialog


if __name__ == "__main__":
    # Test del formulario
    import sys
    from PyQt6.QtWidgets import QApplication
    from core.settings import setup_logging
    from data.seed import create_seed_data
    
    setup_logging()
    
    app = QApplication(sys.argv)
    
    try:
        # Crear seed data
        create_seed_data()
        
        # Mock user info
        user_info = {
            'user_id': 1,
            'username': 'admin',
            'role': 'admin'
        }
        
        # Mostrar formulario
        dialog = show_homologation_form(user_info=user_info)
        
        def on_saved(homologation_id):
            print(f"Homologación guardada con ID: {homologation_id}")
        
        dialog.homologation_saved.connect(on_saved)
        dialog.exec()
        
    except Exception as e:
        print(f"Error: {e}")
        logger.error(f"Error: {e}")