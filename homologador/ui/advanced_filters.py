"""
Filtros avanzados para la tabla de homologaciones.
Proporciona filtros más específicos y opciones de búsqueda mejoradas.
"""

import logging
from datetime import datetime, date
from typing import Dict, List, Any, Optional

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QFormLayout,
    QLabel, QLineEdit, QComboBox, QDateEdit, QPushButton, QCheckBox,
    QFrame, QGroupBox, QButtonGroup, QRadioButton, QSpinBox,
    QSlider, QProgressBar, QTabWidget, QScrollArea
)
from PyQt6.QtCore import Qt, QDate, pyqtSignal, QTimer
from PyQt6.QtGui import QFont

from core.storage import get_homologation_repository
from .theme import get_current_theme, ThemeType

logger = logging.getLogger(__name__)


class AdvancedFilterWidget(QFrame):
    """Widget avanzado para filtros de búsqueda con múltiples criterios."""
    
    filter_changed = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.repo = get_homologation_repository()
        self.filter_timer = QTimer()
        self.filter_timer.setSingleShot(True)
        self.filter_timer.timeout.connect(self.apply_filters)
        
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setup_ui()
        self.load_filter_options()
        self.apply_theme_styles()
    
    def setup_ui(self):
        """Configura la interfaz de filtros avanzados."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        
        # Título principal
        title = QLabel("🔍 Filtros Avanzados")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(12)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Área scrollable para filtros
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Widget contenedor
        container_widget = QWidget()
        container_layout = QVBoxLayout(container_widget)
        container_layout.setSpacing(15)
        
        # Pestañas para organizar filtros
        tab_widget = QTabWidget()
        
        # Pestaña básica
        self.setup_basic_filters_tab(tab_widget)
        
        # Pestaña avanzada
        self.setup_advanced_filters_tab(tab_widget)
        
        # Pestaña de fechas
        self.setup_date_filters_tab(tab_widget)
        
        container_layout.addWidget(tab_widget)
        
        # Botones de acción
        self.setup_action_buttons(container_layout)
        
        scroll_area.setWidget(container_widget)
        layout.addWidget(scroll_area)
    
    def setup_basic_filters_tab(self, tab_widget):
        """Configura la pestaña de filtros básicos."""
        basic_tab = QWidget()
        layout = QFormLayout(basic_tab)
        layout.setSpacing(10)
        
        # Búsqueda por texto
        self.text_search = QLineEdit()
        self.text_search.setPlaceholderText("Buscar en nombre, descripción, repositorio...")
        self.text_search.textChanged.connect(self.trigger_filter_change)
        layout.addRow("Búsqueda general:", self.text_search)
        
        # Filtro por nombre específico
        self.name_filter = QLineEdit()
        self.name_filter.setPlaceholderText("Nombre exacto de aplicación")
        self.name_filter.textChanged.connect(self.trigger_filter_change)
        layout.addRow("Nombre aplicación:", self.name_filter)
        
        # Filtro por repositorio
        self.repo_filter = QComboBox()
        self.repo_filter.addItem("Todos los repositorios", "")
        self.repo_filter.currentIndexChanged.connect(self.trigger_filter_change)
        layout.addRow("Repositorio:", self.repo_filter)
        
        # Filtro por creador
        self.creator_filter = QComboBox()
        self.creator_filter.addItem("Todos los usuarios", "")
        self.creator_filter.currentIndexChanged.connect(self.trigger_filter_change)
        layout.addRow("Creado por:", self.creator_filter)
        
        # Estado KB Sync
        self.kb_sync_group = QButtonGroup()
        kb_layout = QHBoxLayout()
        
        self.kb_all = QRadioButton("Todos")
        self.kb_all.setChecked(True)
        self.kb_sync_group.addButton(self.kb_all, 0)
        kb_layout.addWidget(self.kb_all)
        
        self.kb_yes = QRadioButton("Con KB Sync")
        self.kb_sync_group.addButton(self.kb_yes, 1)
        kb_layout.addWidget(self.kb_yes)
        
        self.kb_no = QRadioButton("Sin KB Sync")
        self.kb_sync_group.addButton(self.kb_no, 2)
        kb_layout.addWidget(self.kb_no)
        
        self.kb_sync_group.buttonClicked.connect(self.trigger_filter_change)
        layout.addRow("KB Sync:", kb_layout)
        
        tab_widget.addTab(basic_tab, "🔍 Básico")
    
    def setup_advanced_filters_tab(self, tab_widget):
        """Configura la pestaña de filtros avanzados."""
        advanced_tab = QWidget()
        layout = QFormLayout(advanced_tab)
        layout.setSpacing(10)
        
        # Filtro por URL de documentación
        self.doc_url_filter = QLineEdit()
        self.doc_url_filter.setPlaceholderText("URL de documentación...")
        self.doc_url_filter.textChanged.connect(self.trigger_filter_change)
        layout.addRow("URL Documentación:", self.doc_url_filter)
        
        # Filtro por versiones previas
        self.prev_versions_group = QButtonGroup()
        pv_layout = QHBoxLayout()
        
        self.pv_all = QRadioButton("Todas")
        self.pv_all.setChecked(True)
        self.prev_versions_group.addButton(self.pv_all, 0)
        pv_layout.addWidget(self.pv_all)
        
        self.pv_yes = QRadioButton("Con versiones previas")
        self.prev_versions_group.addButton(self.pv_yes, 1)
        pv_layout.addWidget(self.pv_yes)
        
        self.pv_no = QRadioButton("Primera versión")
        self.prev_versions_group.addButton(self.pv_no, 2)
        pv_layout.addWidget(self.pv_no)
        
        self.prev_versions_group.buttonClicked.connect(self.trigger_filter_change)
        layout.addRow("Versiones previas:", pv_layout)
        
        # Filtro por longitud de detalles
        details_layout = QHBoxLayout()
        
        self.details_min = QSpinBox()
        self.details_min.setRange(0, 10000)
        self.details_min.setSuffix(" chars")
        self.details_min.valueChanged.connect(self.trigger_filter_change)
        details_layout.addWidget(QLabel("Mín:"))
        details_layout.addWidget(self.details_min)
        
        self.details_max = QSpinBox()
        self.details_max.setRange(0, 10000)
        self.details_max.setValue(10000)
        self.details_max.setSuffix(" chars")
        self.details_max.valueChanged.connect(self.trigger_filter_change)
        details_layout.addWidget(QLabel("Máx:"))
        details_layout.addWidget(self.details_max)
        
        layout.addRow("Longitud detalles:", details_layout)
        
        # Filtro por presencia de campos
        presence_group = QGroupBox("Campos presentes")
        presence_layout = QVBoxLayout(presence_group)
        
        self.has_logical_name = QCheckBox("Tiene nombre lógico")
        self.has_logical_name.stateChanged.connect(self.trigger_filter_change)
        presence_layout.addWidget(self.has_logical_name)
        
        self.has_doc_url = QCheckBox("Tiene URL de documentación")
        self.has_doc_url.stateChanged.connect(self.trigger_filter_change)
        presence_layout.addWidget(self.has_doc_url)
        
        self.has_repository = QCheckBox("Tiene repositorio")
        self.has_repository.stateChanged.connect(self.trigger_filter_change)
        presence_layout.addWidget(self.has_repository)
        
        self.has_details = QCheckBox("Tiene detalles")
        self.has_details.stateChanged.connect(self.trigger_filter_change)
        presence_layout.addWidget(self.has_details)
        
        layout.addRow(presence_group)
        
        tab_widget.addTab(advanced_tab, "⚙️ Avanzado")
    
    def setup_date_filters_tab(self, tab_widget):
        """Configura la pestaña de filtros de fecha."""
        date_tab = QWidget()
        layout = QFormLayout(date_tab)
        layout.setSpacing(10)
        
        # Filtros de fecha de homologación
        homol_group = QGroupBox("Fecha de Homologación")
        homol_layout = QFormLayout(homol_group)
        
        self.homol_date_from = QDateEdit()
        self.homol_date_from.setCalendarPopup(True)
        self.homol_date_from.setDate(QDate.currentDate().addYears(-2))
        self.homol_date_from.setSpecialValueText("Sin fecha mínima")
        self.homol_date_from.dateChanged.connect(self.trigger_filter_change)
        homol_layout.addRow("Desde:", self.homol_date_from)
        
        self.homol_date_to = QDateEdit()
        self.homol_date_to.setCalendarPopup(True)
        self.homol_date_to.setDate(QDate.currentDate())
        self.homol_date_to.setSpecialValueText("Sin fecha máxima")
        self.homol_date_to.dateChanged.connect(self.trigger_filter_change)
        homol_layout.addRow("Hasta:", self.homol_date_to)
        
        layout.addRow(homol_group)
        
        # Filtros de fecha de creación
        created_group = QGroupBox("Fecha de Creación")
        created_layout = QFormLayout(created_group)
        
        self.created_date_from = QDateEdit()
        self.created_date_from.setCalendarPopup(True)
        self.created_date_from.setDate(QDate.currentDate().addMonths(-6))
        self.created_date_from.setSpecialValueText("Sin fecha mínima")
        self.created_date_from.dateChanged.connect(self.trigger_filter_change)
        created_layout.addRow("Desde:", self.created_date_from)
        
        self.created_date_to = QDateEdit()
        self.created_date_to.setCalendarPopup(True)
        self.created_date_to.setDate(QDate.currentDate())
        self.created_date_to.setSpecialValueText("Sin fecha máxima")
        self.created_date_to.dateChanged.connect(self.trigger_filter_change)
        created_layout.addRow("Hasta:", self.created_date_to)
        
        layout.addRow(created_group)
        
        # Filtros de fecha de actualización
        updated_group = QGroupBox("Fecha de Actualización")
        updated_layout = QFormLayout(updated_group)
        
        self.updated_date_from = QDateEdit()
        self.updated_date_from.setCalendarPopup(True)
        self.updated_date_from.setDate(QDate.currentDate().addMonths(-3))
        self.updated_date_from.setSpecialValueText("Sin fecha mínima")
        self.updated_date_from.dateChanged.connect(self.trigger_filter_change)
        updated_layout.addRow("Desde:", self.updated_date_from)
        
        self.updated_date_to = QDateEdit()
        self.updated_date_to.setCalendarPopup(True)
        self.updated_date_to.setDate(QDate.currentDate())
        self.updated_date_to.setSpecialValueText("Sin fecha máxima")
        self.updated_date_to.dateChanged.connect(self.trigger_filter_change)
        updated_layout.addRow("Hasta:", self.updated_date_to)
        
        layout.addRow(updated_group)
        
        tab_widget.addTab(date_tab, "📅 Fechas")
    
    def setup_action_buttons(self, layout):
        """Configura los botones de acción."""
        button_layout = QHBoxLayout()
        
        # Botón aplicar
        apply_button = QPushButton("🔍 Aplicar Filtros")
        apply_button.clicked.connect(self.apply_filters)
        button_layout.addWidget(apply_button)
        
        # Botón limpiar
        clear_button = QPushButton("🗑️ Limpiar Todo")
        clear_button.clicked.connect(self.clear_all_filters)
        button_layout.addWidget(clear_button)
        
        # Botón guardar configuración
        save_button = QPushButton("💾 Guardar Config")
        save_button.clicked.connect(self.save_filter_configuration)
        button_layout.addWidget(save_button)
        
        # Botón cargar configuración
        load_button = QPushButton("📂 Cargar Config")
        load_button.clicked.connect(self.load_filter_configuration)
        button_layout.addWidget(load_button)
        
        layout.addLayout(button_layout)
    
    def load_filter_options(self):
        """Carga opciones dinámicas para los filtros."""
        try:
            # Cargar repositorios únicos
            homologations_raw = self.repo.get_all()
            homologations = [dict(h) for h in homologations_raw]
            
            repositories = set()
            creators = set()
            
            for h in homologations:
                if h.get('repository_location'):
                    repo_name = h['repository_location'].split('/')[-1] if '/' in h['repository_location'] else h['repository_location']
                    repositories.add(repo_name)
                
                if h.get('created_by_username'):
                    creators.add(h['created_by_username'])
            
            # Llenar comboboxes
            for repo in sorted(repositories):
                self.repo_filter.addItem(repo, repo)
            
            for creator in sorted(creators):
                self.creator_filter.addItem(creator, creator)
                
        except Exception as e:
            logger.error(f"Error cargando opciones de filtro: {e}")
    
    def trigger_filter_change(self):
        """Activa el temporizador para cambio de filtro."""
        self.filter_timer.stop()
        self.filter_timer.start(500)  # 500ms de delay
    
    def apply_filters(self):
        """Aplica todos los filtros actuales."""
        filters = {}
        
        # Filtros básicos
        if self.text_search.text().strip():
            filters['text_search'] = self.text_search.text().strip()
        
        if self.name_filter.text().strip():
            filters['real_name'] = self.name_filter.text().strip()
        
        if self.repo_filter.currentData():
            filters['repository_location'] = self.repo_filter.currentData()
        
        if self.creator_filter.currentData():
            filters['created_by_username'] = self.creator_filter.currentData()
        
        # KB Sync
        kb_sync_id = self.kb_sync_group.checkedId()
        if kb_sync_id == 1:
            filters['kb_sync'] = True
        elif kb_sync_id == 2:
            filters['kb_sync'] = False
        
        # Filtros avanzados
        if self.doc_url_filter.text().strip():
            filters['kb_url'] = self.doc_url_filter.text().strip()
        
        # Versiones previas
        pv_id = self.prev_versions_group.checkedId()
        if pv_id == 1:
            filters['has_previous_versions'] = True
        elif pv_id == 2:
            filters['has_previous_versions'] = False
        
        # Longitud de detalles
        if self.details_min.value() > 0:
            filters['details_min_length'] = self.details_min.value()
        if self.details_max.value() < 10000:
            filters['details_max_length'] = self.details_max.value()
        
        # Presencia de campos
        if self.has_logical_name.isChecked():
            filters['has_logical_name'] = True
        if self.has_doc_url.isChecked():
            filters['has_doc_url'] = True
        if self.has_repository.isChecked():
            filters['has_repository'] = True
        if self.has_details.isChecked():
            filters['has_details'] = True
        
        # Filtros de fecha
        # Fecha de homologación
        homol_from = self.homol_date_from.date()
        if homol_from != self.homol_date_from.minimumDate():
            filters['homol_date_from'] = homol_from.toString(Qt.DateFormat.ISODate)
        
        homol_to = self.homol_date_to.date()
        if homol_to != self.homol_date_to.minimumDate():
            filters['homol_date_to'] = homol_to.toString(Qt.DateFormat.ISODate)
        
        # Fecha de creación
        created_from = self.created_date_from.date()
        if created_from != self.created_date_from.minimumDate():
            filters['created_date_from'] = created_from.toString(Qt.DateFormat.ISODate)
        
        created_to = self.created_date_to.date()
        if created_to != self.created_date_to.minimumDate():
            filters['created_date_to'] = created_to.toString(Qt.DateFormat.ISODate)
        
        # Fecha de actualización
        updated_from = self.updated_date_from.date()
        if updated_from != self.updated_date_from.minimumDate():
            filters['updated_date_from'] = updated_from.toString(Qt.DateFormat.ISODate)
        
        updated_to = self.updated_date_to.date()
        if updated_to != self.updated_date_to.minimumDate():
            filters['updated_date_to'] = updated_to.toString(Qt.DateFormat.ISODate)
        
        self.filter_changed.emit(filters)
    
    def clear_all_filters(self):
        """Limpia todos los filtros."""
        # Filtros básicos
        self.text_search.clear()
        self.name_filter.clear()
        self.repo_filter.setCurrentIndex(0)
        self.creator_filter.setCurrentIndex(0)
        self.kb_all.setChecked(True)
        
        # Filtros avanzados
        self.doc_url_filter.clear()
        self.pv_all.setChecked(True)
        self.details_min.setValue(0)
        self.details_max.setValue(10000)
        
        # Checkboxes de presencia
        self.has_logical_name.setChecked(False)
        self.has_doc_url.setChecked(False)
        self.has_repository.setChecked(False)
        self.has_details.setChecked(False)
        
        # Fechas - restablecer a valores por defecto
        self.homol_date_from.setDate(self.homol_date_from.minimumDate())
        self.homol_date_to.setDate(QDate.currentDate())
        self.created_date_from.setDate(self.created_date_from.minimumDate())
        self.created_date_to.setDate(QDate.currentDate())
        self.updated_date_from.setDate(self.updated_date_from.minimumDate())
        self.updated_date_to.setDate(QDate.currentDate())
        
        # Aplicar filtros limpios
        self.apply_filters()
    
    def save_filter_configuration(self):
        """Guarda la configuración actual de filtros."""
        # TODO: Implementar guardado de configuración
        from .notifications import show_info
        show_info(self, "Funcionalidad de guardado de configuración próximamente disponible")
    
    def load_filter_configuration(self):
        """Carga una configuración guardada de filtros."""
        # TODO: Implementar carga de configuración
        from .notifications import show_info
        show_info(self, "Funcionalidad de carga de configuración próximamente disponible")
    
    def apply_theme_styles(self):
        """Aplica estilos según el tema actual."""
        current_theme = get_current_theme()
        
        if current_theme == ThemeType.DARK:
            self.setStyleSheet("""
                AdvancedFilterWidget {
                    background-color: #1a1a1a;
                    color: #ffffff;
                    border: 1px solid #444444;
                    border-radius: 8px;
                }
                QLabel {
                    color: #ffffff;
                    background-color: transparent;
                }
                QLineEdit {
                    background-color: #2d2d2d;
                    border: 1px solid #555555;
                    border-radius: 4px;
                    padding: 6px;
                    color: #ffffff;
                }
                QLineEdit:focus {
                    border: 2px solid #0078d4;
                }
                QComboBox {
                    background-color: #2d2d2d;
                    border: 1px solid #555555;
                    border-radius: 4px;
                    padding: 4px;
                    color: #ffffff;
                }
                QDateEdit {
                    background-color: #2d2d2d;
                    border: 1px solid #555555;
                    border-radius: 4px;
                    padding: 4px;
                    color: #ffffff;
                }
                QPushButton {
                    background-color: #0078d4;
                    color: #ffffff;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #106ebe;
                }
                QGroupBox {
                    font-weight: bold;
                    border: 1px solid #555555;
                    border-radius: 4px;
                    margin-top: 10px;
                    padding-top: 10px;
                    color: #ffffff;
                }
                QTabWidget::pane {
                    border: 1px solid #555555;
                    background-color: #2d2d2d;
                }
                QTabBar::tab {
                    background-color: #3d3d3d;
                    color: #ffffff;
                    padding: 8px 16px;
                    border: 1px solid #555555;
                }
                QTabBar::tab:selected {
                    background-color: #0078d4;
                }
            """)
        else:
            self.setStyleSheet("""
                AdvancedFilterWidget {
                    background-color: #ffffff;
                    color: #333333;
                    border: 1px solid #d0d0d0;
                    border-radius: 8px;
                }
                QLabel {
                    color: #333333;
                    background-color: transparent;
                }
                QLineEdit {
                    background-color: #ffffff;
                    border: 1px solid #d0d0d0;
                    border-radius: 4px;
                    padding: 6px;
                    color: #333333;
                }
                QLineEdit:focus {
                    border: 2px solid #0078d4;
                }
                QComboBox {
                    background-color: #ffffff;
                    border: 1px solid #d0d0d0;
                    border-radius: 4px;
                    padding: 4px;
                    color: #333333;
                }
                QDateEdit {
                    background-color: #ffffff;
                    border: 1px solid #d0d0d0;
                    border-radius: 4px;
                    padding: 4px;
                    color: #333333;
                }
                QPushButton {
                    background-color: #0078d4;
                    color: #ffffff;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #106ebe;
                }
                QGroupBox {
                    font-weight: bold;
                    border: 1px solid #d0d0d0;
                    border-radius: 4px;
                    margin-top: 10px;
                    padding-top: 10px;
                    color: #333333;
                }
                QTabWidget::pane {
                    border: 1px solid #d0d0d0;
                    background-color: #ffffff;
                }
                QTabBar::tab {
                    background-color: #f8f8f8;
                    color: #333333;
                    padding: 8px 16px;
                    border: 1px solid #d0d0d0;
                }
                QTabBar::tab:selected {
                    background-color: #0078d4;
                    color: #ffffff;
                }
            """)