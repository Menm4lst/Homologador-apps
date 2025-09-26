"""
Vista de detalles para homologaciones.
Interfaz de solo lectura con información completa y auditoría.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, cast

from ..core.storage import get_audit_repository, get_homologation_repository
from PyQt6.QtCore import Qt, QThread, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QClipboard, QFont
from PyQt6.QtWidgets import (QDialog, QFormLayout, QFrame, QGridLayout,
                             QGroupBox, QHBoxLayout, QHeaderView, QLabel,
                             QMessageBox, QPushButton, QScrollArea,
                             QSizePolicy, QSpacerItem, QTableWidget,
                             QTableWidgetItem, QTabWidget, QTextEdit,
                             QVBoxLayout, QWidget)

from .theme import set_widget_style_class

logger = logging.getLogger(__name__)


class AuditLoadWorker(QThread):
    """Worker thread para cargar auditoría sin bloquear la UI."""
    
    audit_loaded = pyqtSignal(list)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, homologation_id: int):
        super().__init__()
        self.homologation_id = homologation_id
        self.audit_repo = get_audit_repository()
    
    def run(self):
        """Carga la auditoría en segundo plano."""
        try:
            filters = {
                'table_name': 'homologations',
                'record_id': self.homologation_id
            }
            results = self.audit_repo.get_audit_trail(cast(Dict[str, Any], filters))
            self.audit_loaded.emit([dict(row) for row in results])
            
        except Exception as e:
            logger.error(f"Error cargando auditoría: {e}")
            self.error_occurred.emit(str(e))


class AuditTableWidget(QTableWidget):
    """Widget para mostrar el historial de auditoría."""
    
    def __init__(self):
        super().__init__()
        self.setup_table()
    
    def setup_table(self):
        """Configura la tabla de auditoría."""
        # Columnas
        columns = [
            ("Fecha", 150),
            ("Usuario", 100),
            ("Acción", 80),
            ("Cambios", 300)
        ]
        
        self.setColumnCount(len(columns))
        self.setHorizontalHeaderLabels([col[0] for col in columns])
        
        # Configurar anchos
        header = self.horizontalHeader()
        if header:
            for i, (_, width) in enumerate(columns):
                header.resizeSection(i, width)
        
        # Configuraciones
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.setSortingEnabled(True)
        if header:
            header.setStretchLastSection(True)
        
        # Sin edición
        self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        # Estilos tema nocturno elegante
        self.setStyleSheet("""
            QTableWidget {
                gridline-color: #4a6741;
                background-color: #2c3e50;
                color: #ecf0f1;
                border: 2px solid #34495e;
                border-radius: 10px;
                selection-background-color: #74b9ff;
            }
            QTableWidget::item {
                padding: 12px;
                color: #ecf0f1;
                background-color: #2c3e50;
                border-bottom: 1px solid #34495e;
            }
            QTableWidget::item:alternate {
                background-color: #34495e;
                color: #ecf0f1;
            }
            QTableWidget::item:selected {
                background-color: #74b9ff;
                color: #ffffff;
                font-weight: bold;
            }
            QTableWidget::item:hover {
                background-color: #4a6741;
                color: #ffffff;
            }
            QHeaderView::section {
                background-color: #1a252f;
                color: #74b9ff;
                padding: 15px;
                border: none;
                font-weight: bold;
                font-size: 12px;
                border-bottom: 2px solid #74b9ff;
            }
            QHeaderView::section:hover {
                background-color: #2c3e50;
                color: #ffffff;
            }
        """)
    
    def load_audit_data(self, audit_data: List[Dict[str, Any]]):
        """Carga datos de auditoría en la tabla."""
        self.setRowCount(len(audit_data))
        
        for row_idx, record in enumerate(audit_data):
            # Fecha
            timestamp = record.get('timestamp', '')
            if timestamp:
                try:
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    formatted_date = dt.strftime('%d/%m/%Y %H:%M:%S')
                except:
                    formatted_date = timestamp
            else:
                formatted_date = ''
            
            self.setItem(row_idx, 0, QTableWidgetItem(formatted_date))
            
            # Usuario
            username = record.get('username', 'Sistema')
            self.setItem(row_idx, 1, QTableWidgetItem(username))
            
            # Acción
            action = record.get('action', '')
            action_item = QTableWidgetItem(action)
            
            # Color según acción
            if action == 'CREATE':
                action_item.setBackground(Qt.GlobalColor.green)
            elif action == 'UPDATE':
                action_item.setBackground(Qt.GlobalColor.yellow)
            elif action == 'DELETE':
                action_item.setBackground(Qt.GlobalColor.red)
            
            self.setItem(row_idx, 2, action_item)
            
            # Cambios
            changes = self.format_changes(record)
            self.setItem(row_idx, 3, QTableWidgetItem(changes))
        
        self.resizeRowsToContents()
    
    def format_changes(self, record: Dict[str, Any]) -> str:
        """Formatea los cambios para mostrar en la tabla."""
        old_values = record.get('old_values')
        new_values = record.get('new_values')
        
        if not old_values and not new_values:
            return "Sin detalles"
        
        changes = []
        
        if record.get('action') == 'CREATE' and new_values:
            import json
            try:
                data = json.loads(new_values)
                changes.append(f"Creada: {data.get('real_name', 'N/A')}")
            except:
                changes.append("Registro creado")
        
        elif record.get('action') == 'UPDATE' and old_values and new_values:
            import json
            try:
                old_data = json.loads(old_values)
                new_data = json.loads(new_values)
                
                for key in new_data:
                    if key in old_data and old_data[key] != new_data[key]:
                        changes.append(f"{key}: '{old_data[key]}' → '{new_data[key]}'")
                
            except:
                changes.append("Campos modificados")
        
        elif record.get('action') == 'DELETE' and old_values:
            import json
            try:
                data = json.loads(old_values)
                changes.append(f"Eliminada: {data.get('real_name', 'N/A')}")
            except:
                changes.append("Registro eliminado")
        
        return "; ".join(cast(List[str], changes)) if changes else "Sin cambios detectados"


class HomologationDetailsDialog(QDialog):
    """Dialog para mostrar detalles completos de una homologación."""
    
    edit_requested = pyqtSignal(dict)
    
    def __init__(self, parent: Optional[QWidget] = None, homologation_data: Optional[Dict[str, Any]] = None, user_info: Optional[Dict[str, Any]] = None):
        super().__init__(cast(QWidget, parent))
        self.homologation_data = homologation_data
        self.user_info = user_info
        self.audit_worker = None
        
        self.setup_ui()
        self.load_data()
        self.load_audit_data()
    
    def setup_ui(self):
        """Configura la interfaz de detalles."""
        self.setWindowTitle("Detalles de Homologación")
        self.setModal(True)
        self.setMinimumSize(800, 600)
        self.resize(900, 700)
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        
        # Título con nombre de la aplicación
        self.setup_header(main_layout)
        
        # Pestañas para organizar información
        tab_widget = QTabWidget()
        
        # Pestaña de información general
        self.setup_general_tab(tab_widget)
        
        # Pestaña de auditoría
        self.setup_audit_tab(tab_widget)
        
        main_layout.addWidget(tab_widget)
        
        # Botones
        self.setup_buttons(main_layout)
        
        # Estilos
        self.setup_styles()
    
    def setup_header(self, layout):
        """Configura el header con información principal."""
        header_frame = QFrame()
        header_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        header_layout = QVBoxLayout(header_frame)
        
        # Título principal
        self.title_label = QLabel()
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(self.title_label)
        
        # Información básica en una línea
        self.info_label = QLabel()
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.info_label.setStyleSheet("color: #bdc3c7; font-size: 12px; margin-top: 5px; background-color: transparent; font-style: italic;")
        header_layout.addWidget(self.info_label)
        
        layout.addWidget(header_frame)
    
    def setup_general_tab(self, tab_widget):
        """Configura la pestaña de información general."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        
        # Widget contenedor
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        
        # Información básica
        self.setup_basic_info_group(content_layout)
        
        # Información técnica
        self.setup_technical_info_group(content_layout)
        
        # Detalles y observaciones
        self.setup_details_group(content_layout)
        
        # Metadatos
        self.setup_metadata_group(content_layout)
        
        content_layout.addStretch()
        
        scroll_area.setWidget(content_widget)
        layout.addWidget(scroll_area)
        
        tab_widget.addTab(tab, "Información General")
    
    def setup_basic_info_group(self, layout):
        """Grupo de información básica."""
        group = QGroupBox("Información Básica")
        form_layout = QFormLayout(group)
        form_layout.setSpacing(12)
        
        # Nombre Real
        self.real_name_label = QLabel()
        self.real_name_label.setStyleSheet("font-weight: bold; font-size: 14pt; color: #74b9ff; background-color: transparent; text-decoration: underline;")
        form_layout.addRow("Nombre Real:", self.real_name_label)
        
        # Nombre Lógico
        self.logical_name_label = QLabel()
        form_layout.addRow("Nombre Lógico:", self.logical_name_label)
        
        # URL Knowledge Base
        self.kb_url_label = QLabel()
        self.kb_url_label.setOpenExternalLinks(True)
        form_layout.addRow("Documentación:", self.kb_url_label)
        
        # KB SYNC
        self.kb_sync_label = QLabel()
        form_layout.addRow("KB SYNC:", self.kb_sync_label)
        
        layout.addWidget(group)
    
    def setup_technical_info_group(self, layout):
        """Grupo de información técnica."""
        group = QGroupBox("Información Técnica")
        form_layout = QFormLayout(group)
        form_layout.setSpacing(12)
        
        # Fecha de Homologación
        self.homologation_date_label = QLabel()
        form_layout.addRow("Fecha Homologación:", self.homologation_date_label)
        
        # Repositorio
        self.repository_label = QLabel()
        form_layout.addRow("Repositorio:", self.repository_label)
        
        # Versiones Previas
        self.versions_label = QLabel()
        form_layout.addRow("Versiones Previas:", self.versions_label)
        
        layout.addWidget(group)
    
    def setup_details_group(self, layout):
        """Grupo de detalles y observaciones."""
        group = QGroupBox("Detalles y Observaciones")
        group_layout = QVBoxLayout(group)
        
        self.details_display = QTextEdit()
        self.details_display.setReadOnly(True)
        self.details_display.setMaximumHeight(150)
        group_layout.addWidget(self.details_display)
        
        layout.addWidget(group)
    
    def setup_metadata_group(self, layout):
        """Grupo de metadatos del sistema."""
        group = QGroupBox("Información del Sistema")
        form_layout = QFormLayout(group)
        form_layout.setSpacing(12)
        
        # Creado por
        self.created_by_label = QLabel()
        form_layout.addRow("Creado por:", self.created_by_label)
        
        # Fecha de creación
        self.created_at_label = QLabel()
        form_layout.addRow("Fecha creación:", self.created_at_label)
        
        # Última actualización
        self.updated_at_label = QLabel()
        form_layout.addRow("Última actualización:", self.updated_at_label)
        
        # ID interno
        self.id_label = QLabel()
        form_layout.addRow("ID:", self.id_label)
        
        layout.addWidget(group)
    
    def setup_audit_tab(self, tab_widget):
        """Configura la pestaña de auditoría."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Título
        title = QLabel("Historial de Cambios")
        title.setFont(QFont("", -1, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Tabla de auditoría
        self.audit_table = AuditTableWidget()
        layout.addWidget(self.audit_table)
        
        tab_widget.addTab(tab, "Auditoría")
    
    def setup_buttons(self, layout):
        """Configura los botones de acción."""
        button_layout = QHBoxLayout()
        
        # Botón copiar información
        copy_button = QPushButton("Copiar Info")
        copy_button.clicked.connect(self.copy_to_clipboard)
        button_layout.addWidget(copy_button)
        
        button_layout.addStretch()
        
        # Botón editar (según permisos)
        if self.user_info:
            from ..data.seed import get_auth_service
            auth_service = get_auth_service()
            if auth_service.has_permission('update', self.user_info['role']):
                edit_button = QPushButton("Editar")
                edit_button.clicked.connect(self.request_edit)
                edit_button.setStyleSheet("""
                    QPushButton {
                        background-color: #e74c3c;
                        color: white;
                        border: 2px solid #c0392b;
                        border-radius: 8px;
                        padding: 10px 20px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #c0392b;
                        border-color: #e74c3c;
                        transform: translateY(-1px);
                    }
                    QPushButton:pressed {
                        background-color: #a93226;
                    }
                """)
                button_layout.addWidget(edit_button)
        
        # Botón cerrar
        close_button = QPushButton("Cerrar")
        close_button.clicked.connect(self.accept)
        close_button.setDefault(True)
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)
    
    def setup_styles(self):
        """Configura estilos CSS."""
        self.setStyleSheet("""
            QDialog {
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
                padding: 6px;
                color: #e0e0e0;
                background-color: transparent;
            }
            
            QTextEdit {
                border: 2px solid #34495e;
                border-radius: 8px;
                background-color: #2c3e50;
                color: #ecf0f1;
                padding: 12px;
                selection-background-color: #74b9ff;
            }
            
            QPushButton {
                padding: 12px 20px;
                border: 2px solid #34495e;
                border-radius: 8px;
                font-weight: bold;
                min-width: 100px;
                background-color: #34495e;
                color: #ecf0f1;
            }
            
            QPushButton:hover {
                background-color: #4a6741;
                border-color: #74b9ff;
                color: #ffffff;
            }
            
            QPushButton:pressed {
                background-color: #2c3e50;
                border-color: #5dade2;
            }
            
            QPushButton[default="true"] {
                background-color: #2980b9;
                border-color: #3498db;
                color: white;
            }
            
            QPushButton[default="true"]:hover {
                background-color: #3498db;
                border-color: #74b9ff;
            }
            
            QTabWidget::pane {
                border: 2px solid #34495e;
                border-radius: 8px;
                background-color: #2c3e50;
            }
            
            QTabBar::tab {
                background-color: #34495e;
                color: #bdc3c7;
                padding: 12px 20px;
                border: 2px solid #2c3e50;
                border-bottom: none;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                margin-right: 4px;
                font-weight: bold;
            }
            
            QTabBar::tab:selected {
                background-color: #2980b9;
                color: #ffffff;
                border-color: #3498db;
            }
            
            QTabBar::tab:hover:!selected {
                background-color: #4a6741;
                color: #ecf0f1;
                border-color: #74b9ff;
            }
            
            QScrollArea {
                border: 2px solid #34495e;
                border-radius: 8px;
                background-color: #2c3e50;
            }
            
            QScrollArea > QWidget > QWidget {
                background-color: #2c3e50;
            }
        """)
    
    def load_data(self):
        """Carga los datos de la homologación en la interfaz."""
        if not self.homologation_data:
            return
        
        data = self.homologation_data
        
        # Header
        self.title_label.setText(data.get('real_name', 'Sin nombre'))
        
        info_parts = []
        if data.get('logical_name'):
            info_parts.append(f"Lógico: {data['logical_name']}")
        if data.get('repository_location'):
            info_parts.append(f"Repositorio: {data['repository_location']}")
        if data.get('homologation_date'):
            info_parts.append(f"Homologado: {data['homologation_date']}")
        
        self.info_label.setText(" | ".join(cast(List[str], info_parts)))
        
        # Información básica
        self.real_name_label.setText(data.get('real_name', 'N/A'))
        self.logical_name_label.setText(data.get('logical_name', 'No especificado'))
        
        # URL con enlace
        kb_url = data.get('kb_url', '')
        if kb_url:
            self.kb_url_label.setText(f'<a href="{kb_url}">{kb_url}</a>')
        else:
            self.kb_url_label.setText('No especificada')
        
        # KB SYNC
        kb_sync = data.get('kb_sync', False)
        self.kb_sync_label.setText('Activado' if kb_sync else 'Desactivado')
        
        # Información técnica
        self.homologation_date_label.setText(
            self.format_date(data.get('homologation_date')) or 'No especificada'
        )
        self.repository_label.setText(data.get('repository_location', 'No especificado'))
        
        has_versions = data.get('has_previous_versions', False)
        self.versions_label.setText('Sí' if has_versions else 'No')
        
        # Detalles
        details = data.get('details', '')
        if details:
            self.details_display.setPlainText(details)
        else:
            self.details_display.setPlainText('Sin detalles adicionales')
        
        # Metadatos
        creator = data.get('created_by_full_name') or data.get('created_by_username', 'Desconocido')
        self.created_by_label.setText(creator)
        
        self.created_at_label.setText(
            self.format_datetime(data.get('created_at')) or 'No disponible'
        )
        self.updated_at_label.setText(
            self.format_datetime(data.get('updated_at')) or 'No disponible'
        )
        self.id_label.setText(str(data.get('id', 'N/A')))
    
    def format_date(self, date_str: Optional[str]) -> str:
        """Formatea una fecha para mostrar."""
        if not date_str:
            return ''
        
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            return date_obj.strftime('%d/%m/%Y')
        except:
            return date_str
    
    def format_datetime(self, datetime_str: Optional[str]) -> str:
        """Formatea una fecha y hora para mostrar."""
        if not datetime_str:
            return ''
        
        try:
            # Manejar diferentes formatos
            if 'T' in datetime_str:
                dt = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
            else:
                dt = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
            
            return dt.strftime('%d/%m/%Y %H:%M:%S')
        except:
            return datetime_str
    
    def load_audit_data(self):
        """Carga el historial de auditoría."""
        if not self.homologation_data or not self.homologation_data.get('id'):
            return
        
        # Cargar en worker thread
        self.audit_worker = AuditLoadWorker(self.homologation_data['id'])
        self.audit_worker.audit_loaded.connect(self.on_audit_loaded)
        self.audit_worker.error_occurred.connect(self.on_audit_error)
        self.audit_worker.start()
    
    @pyqtSlot(list)
    def on_audit_loaded(self, audit_data):
        """Maneja auditoría cargada exitosamente."""
        self.audit_table.load_audit_data(cast(List[Dict[str, Any]], audit_data))
    
    @pyqtSlot(str)
    def on_audit_error(self, error_message):
        """Maneja error de carga de auditoría."""
        logger.warning(f"Error cargando auditoría: {error_message}")
        # No mostrar error al usuario, la auditoría es información adicional
    
    def copy_to_clipboard(self):
        """Copia la información de la homologación al portapapeles."""
        if not self.homologation_data:
            return
        
        data = self.homologation_data
        
        text_info = []
        text_info.append("=== INFORMACIÓN DE HOMOLOGACIÓN ===")
        text_info.append(f"Nombre Real: {data.get('real_name', 'N/A')}")
        text_info.append(f"Nombre Lógico: {data.get('logical_name', 'No especificado')}")
        text_info.append(f"URL Documentación: {data.get('kb_url', 'No especificada')}")
        text_info.append(f"KB SYNC: {'Activado' if data.get('kb_sync') else 'Desactivado'}")
        text_info.append(f"Fecha Homologación: {self.format_date(data.get('homologation_date'))}")
        text_info.append(f"Repositorio: {data.get('repository_location', 'No especificado')}")
        text_info.append(f"Versiones Previas: {'Sí' if data.get('has_previous_versions') else 'No'}")
        
        if data.get('details'):
            text_info.append(f"Detalles: {data['details']}")
        
        text_info.append(f"Creado por: {data.get('created_by_full_name') or data.get('created_by_username', 'Desconocido')}")
        text_info.append(f"Fecha creación: {self.format_datetime(data.get('created_at'))}")
        text_info.append(f"ID: {data.get('id')}")
        
        clipboard_text = "\n".join(cast(List[str], text_info))
        
        # Copiar al portapapeles
        clipboard = QClipboard()
        clipboard.setText(clipboard_text)
        
        QMessageBox.information(self, "Copiado", "Información copiada al portapapeles")
    
    def request_edit(self):
        """Solicita editar la homologación."""
        self.edit_requested.emit(self.homologation_data)
        self.accept()
    
    def closeEvent(self, event):
        """Maneja el cierre del dialog."""
        if self.audit_worker and self.audit_worker.isRunning():
            self.audit_worker.terminate()
            self.audit_worker.wait()
        event.accept()


def show_homologation_details(parent: Optional[QWidget] = None, homologation_data: Optional[Dict[str, Any]] = None, user_info: Optional[Dict[str, Any]] = None):
    """Función utilitaria para mostrar detalles de homologación."""
    dialog = HomologationDetailsDialog(cast(QWidget, parent), homologation_data, user_info)
    return dialog


if __name__ == "__main__":
    # Test de la vista de detalles
    import sys

    from ..core.settings import setup_logging
    from PyQt6.QtWidgets import QApplication
    
    setup_logging()
    
    app = QApplication(sys.argv)
    
    # Mock data
    mock_data = {
        'id': 1,
        'real_name': 'Sistema de Gestión Documental',
        'logical_name': 'DocManager',
        'kb_url': 'https://wiki.empresa.com/docmanager',
        'kb_sync': True,
        'homologation_date': '2024-01-15',
        'has_previous_versions': True,
        'repository_location': 'AESA',
        'details': 'Sistema para gestión de documentos corporativos con integración AD.',
        'created_by_username': 'admin',
        'created_by_full_name': 'Administrador del Sistema',
        'created_at': '2024-01-10T10:30:00',
        'updated_at': '2024-01-15T14:45:00'
    }
    
    user_info = {
        'user_id': 1,
        'username': 'admin',
        'role': 'admin'
    }
    
    dialog = show_homologation_details(homologation_data=cast(Dict[str, Any], mock_data), user_info=cast(Dict[str, Any], user_info))
    dialog.exec()
    
    sys.exit(0)