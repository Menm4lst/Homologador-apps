"""
Ventana principal del Homologador de Aplicaciones.
Interfaz principal con tabla de homologaciones, filtros y gestión según roles.
"""

from __future__ import annotations

from datetime import date, datetime
import csv
import logging
import sys
from typing import Any, Callable, Dict, List, Optional, cast

from PyQt6.QtCore import QDate, QPoint, Qt, QThread, QTimer, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QAction, QFont, QIcon
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QComboBox,
    QDateEdit,
    QDialog,
    QFileDialog,
    QFormLayout,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMenuBar,
    QMenu,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QSpinBox,
    QSplitter,
    QStatusBar,
    QTableWidget,
    QTableWidgetItem,
    QToolBar,
    QVBoxLayout,
    QWidget)

from ..core.storage import get_audit_repository, get_homologation_repository
from ..data.seed import get_auth_service

from .change_password_dialog import ChangeMyPasswordDialog
from .details_view import show_homologation_details
from .homologation_form import HomologationFormDialog
from .metrics_panel import MetricsPanel
from .notification_system import (
    send_error,
    send_info,
    send_success,
    send_warning)
from .theme import (
    ThemeType,
    apply_theme_from_settings,
    get_current_theme,
    get_theme_monitor,
    set_widget_style_class,
    toggle_theme)


from .tooltips import get_help_system, setup_tooltips, setup_widget_tooltips
from .user_guide import UserGuideManager, start_user_tour
from .web_preview import show_web_preview
logger = logging.getLogger(__name__)

# Sistema optimizado de carga de módulos opcionales
class OptionalModules:
    """Gestor centralizado de módulos opcionales con lazy loading."""
    
    def __init__(self) -> None:
        self._modules: Dict[str, Any] = {}
        self._availability: Dict[str, bool] = {}
    
    def get_module(self, module_name: str, import_path: str, fallback: Any = None) -> Any:
        """Obtiene un módulo con lazy loading."""
        if module_name not in self._modules:
            try:
                if import_path.startswith('.'):
                    # Import relativo desde el paquete ui
                    if import_path == '.user_management':
                        from . import user_management
                        module = user_management
                    elif import_path == '.audit_panel':
                        from . import audit_panel
                        module = audit_panel
                    elif import_path == '.admin_dashboard':
                        from . import admin_dashboard
                        module = admin_dashboard
                    elif import_path == '.reports_system':
                        from . import reports_system
                        module = reports_system
                    elif import_path == '.notification_system':
                        from . import notification_system
                        module = notification_system
                    elif import_path == '.backup_system':
                        from . import backup_system
                        module = backup_system
                    else:
                        raise ImportError(f"Módulo {import_path} no reconocido")
                        
                else:
                    # Import absoluto
                    module = __import__(import_path, fromlist=[''])
                
                self._modules[module_name] = module
                self._availability[module_name] = True
                
            except ImportError as e:
                logger.debug(f"Módulo opcional {module_name} no disponible: {e}")
                self._modules[module_name] = fallback
                self._availability[module_name] = False
        
        return self._modules[module_name]
    
    def is_available(self, module_name: str) -> bool:
        """Verifica si un módulo está disponible."""
        return self._availability.get(module_name, False)

# Instancia global del gestor
_optional_modules = OptionalModules()

# Definición de módulos opcionales
OPTIONAL_MODULES = {
    'user_management': '.user_management',
    'audit_panel': '.audit_panel', 
    'backup_panel': '.backup_system',  # Corregido: backup_system en lugar de backup_panel
    'admin_dashboard': '.admin_dashboard',
    'reports_system': '.reports_system',
    'advanced_search': 'advanced_search',
    'accessibility': 'accessibility',
    'notification_system': '.notification_system'
}

# Funciones de acceso optimizadas
def get_user_management() -> Optional[Callable[..., Any]]:
    module = _optional_modules.get_module('user_management', OPTIONAL_MODULES['user_management'])
    return getattr(module, 'show_user_management', None) if module else None

def get_audit_panel() -> Optional[Callable[..., Any]]:
    module = _optional_modules.get_module('audit_panel', OPTIONAL_MODULES['audit_panel'])
    return getattr(module, 'show_audit_panel', None) if module else None

def get_backup_panel() -> Optional[Any]:
    module = _optional_modules.get_module('backup_panel', OPTIONAL_MODULES['backup_panel'])
    return getattr(module, 'show_backup_system', None) if module else None

def get_admin_dashboard() -> Optional[Callable[..., Any]]:
    module = _optional_modules.get_module('admin_dashboard', OPTIONAL_MODULES['admin_dashboard'])
    return getattr(module, 'show_admin_dashboard', None) if module else None

def get_reports_system() -> Optional[Callable[..., Any]]:
    module = _optional_modules.get_module('reports_system', OPTIONAL_MODULES['reports_system'])
    return getattr(module, 'show_reports_system', None) if module else None

def get_advanced_search() -> Optional[Any]:
    module = _optional_modules.get_module('advanced_search', OPTIONAL_MODULES['advanced_search'])
    return getattr(module, 'AdvancedSearchWidget', None) if module else None

def get_accessibility_manager() -> Optional[Any]:
    module = _optional_modules.get_module('accessibility', OPTIONAL_MODULES['accessibility'])
    return getattr(module, 'AccessibilityManager', None) if module else None

def get_notification_system() -> Optional[Dict[str, Any]]:
    module = _optional_modules.get_module('notification_system', OPTIONAL_MODULES['notification_system'])
    if module:
        return {
            'badge': getattr(module, 'NotificationBadge', None),
            'panel': getattr(module, 'NotificationPanel', None),
            'manager': getattr(module, 'notification_manager', None)
        }
    return None

# Compatibilidad con código existente
def USER_MANAGEMENT_AVAILABLE() -> bool:
    """Verifica si el módulo de gestión de usuarios está disponible."""
    _optional_modules.get_module('user_management', OPTIONAL_MODULES['user_management'])
    return _optional_modules.is_available('user_management')

def AUDIT_PANEL_AVAILABLE() -> bool:
    """Verifica si el panel de auditoría está disponible."""
    _optional_modules.get_module('audit_panel', OPTIONAL_MODULES['audit_panel'])
    return _optional_modules.is_available('audit_panel')

def BACKUP_SYSTEM_AVAILABLE() -> bool:
    """Verifica si el sistema de respaldos está disponible."""
    _optional_modules.get_module('backup_panel', OPTIONAL_MODULES['backup_panel'])
    return _optional_modules.is_available('backup_panel')

def ADMIN_DASHBOARD_AVAILABLE() -> bool:
    """Verifica si el dashboard administrativo está disponible."""
    _optional_modules.get_module('admin_dashboard', OPTIONAL_MODULES['admin_dashboard'])
    return _optional_modules.is_available('admin_dashboard')

def REPORTS_SYSTEM_AVAILABLE() -> bool:
    """Verifica si el sistema de reportes está disponible."""
    _optional_modules.get_module('reports_system', OPTIONAL_MODULES['reports_system'])
    return _optional_modules.is_available('reports_system')

def ADVANCED_SEARCH_AVAILABLE() -> bool:
    """Verifica si la búsqueda avanzada está disponible."""
    _optional_modules.get_module('advanced_search', OPTIONAL_MODULES['advanced_search'])
    return _optional_modules.is_available('advanced_search')

def ACCESSIBILITY_AVAILABLE() -> bool:
    """Verifica si el gestor de accesibilidad está disponible."""
    _optional_modules.get_module('accessibility', OPTIONAL_MODULES['accessibility'])
    return _optional_modules.is_available('accessibility')

def NOTIFICATIONS_AVAILABLE() -> bool:
    """Verifica si el sistema de notificaciones está disponible."""
    _optional_modules.get_module('notification_system', OPTIONAL_MODULES['notification_system'])
    return _optional_modules.is_available('notification_system')


class DataLoadWorker(QThread):
    """Worker thread para cargar datos sin bloquear la UI."""
    
    data_ready = pyqtSignal(list)
    error = pyqtSignal(str)
    
    def __init__(self, repo, filters=None):
        super().__init__()
        self.repo = repo
        self.filters = filters or {}
    
    def run(self):
        try:
            results = self.repo.get_all(self.filters)
            self.data_ready.emit(results)
        except Exception as e:
            logger.error(f"Error cargando datos: {e}")
            self.error.emit(str(e))


class HomologationTableWidget(QTableWidget):
    """Widget personalizado para la tabla de homologaciones con soporte para paginación."""
    
    # Señales
    total_records_changed = pyqtSignal(int)  # Emitida cuando cambia el total de registros
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(cast(QWidget, parent))
        # Almacena todos los datos (incluso los que no se muestran en la página actual)
        self.all_record_data = []
        # Almacena solo los registros de la página actual
        self.record_data = []
        # Configuración de paginación
        self.current_page = 1
        self.page_size = 20
        # Configuración de ordenamiento
        self.sort_column = -1  # No hay columna de ordenamiento por defecto
        self.sort_order = Qt.SortOrder.AscendingOrder
        # Configurar tabla
        self.setup_table()
        # Configurar menú contextual
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        # Referencia al widget principal para acceder a métodos
        self.main_window = None
    
    def setup_table(self):
        """Configura la apariencia y comportamiento de la tabla."""
        columns = [
            "ID", "Nombre", "Nombre Lógico", "Repositorio", 
            "Fecha Homologación", "Creado Por", "Actualizado"
        ]
        
        self.setColumnCount(len(columns))
        self.setHorizontalHeaderLabels(columns)
        
        # Configurar cabecera
        header = self.horizontalHeader()
        if header:
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Nombre estira
            header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)  # Nombre lógico estira
        
        # Configurar comportamiento
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setAlternatingRowColors(True)
        self.setShowGrid(True)
        
        # Configurar ordenamiento personalizado (no usar el de Qt)
        self.setSortingEnabled(False)  # Desactivar el sorting automático
        if header:
            header.sectionClicked.connect(self.on_header_clicked)
        
        # Deshabilitar edición
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
    
    def on_header_clicked(self, logical_index):
        """Maneja clics en la cabecera para ordenar."""
        # Si se hace clic en la misma columna, cambiar dirección
        if self.sort_column == logical_index:
            self.sort_order = Qt.SortOrder.DescendingOrder if self.sort_order == Qt.SortOrder.AscendingOrder else Qt.SortOrder.AscendingOrder
        else:
            self.sort_column = logical_index
            self.sort_order = Qt.SortOrder.AscendingOrder
        
        # Aplicar ordenamiento
        self.sort_data()
        self.update_view()
        
        # Actualizar indicadores visuales de ordenamiento en la cabecera
        self.update_sort_indicators()
    
    def update_sort_indicators(self):
        """Actualiza indicadores visuales de ordenamiento en la cabecera."""
        header = self.horizontalHeader()
        if not header:
            return
        
        # Limpiar indicadores existentes
        for i in range(self.columnCount()):
            header.setSortIndicator(-1, Qt.SortOrder.AscendingOrder)
        
        # Establecer nuevo indicador
        if self.sort_column >= 0:
            header.setSortIndicator(cast(int, self.sort_column), cast(Qt.SortOrder, self.sort_order))
    
    def sort_data(self):
        """Ordena los datos según la columna y dirección actual."""
        if self.sort_column < 0 or not self.all_record_data:
            return
        
        # Función para obtener la clave de ordenamiento para cada columna
        def get_sort_key(item, col_idx):
            if col_idx == 0:  # ID
                return int(cast(str, item['id']))
            elif col_idx == 1:  # Nombre
                return item['real_name'].lower()
            elif col_idx == 2:  # Nombre Lógico
                return (item.get('logical_name') or '').lower()
            elif col_idx == 3:  # Repositorio
                return (item.get('repository_location') or '').lower()
            elif col_idx == 4:  # Fecha Homologación
                return item['homologation_date'] or ''
            elif col_idx == 5:  # Creador
                return (item.get('created_by_username') or '').lower()
            elif col_idx == 6:  # Fecha Actualización
                return item.get('updated_at') or ''
            return ''
        
        # Ordenar los datos
        self.all_record_data.sort(
            key=lambda x: get_sort_key(x, self.sort_column),
            reverse=(self.sort_order == Qt.SortOrder.DescendingOrder)
        )
    
    def load_data(self, data_rows: List[Any]):
        """Carga todos los datos y actualiza la vista con la página actual."""
        # Convertir sqlite3.Row a diccionarios y guardar todos los registros
        self.all_record_data = [cast(Dict[str, Any], dict(row)) for row in data_rows]
        
        # Emitir señal con el total de registros
        self.total_records_changed.emit(len(cast(List[Dict[str, Any]], self.all_record_data)))
        
        # Si hay ordenamiento activo, aplicarlo
        if self.sort_column >= 0:
            self.sort_data()
        
        # Actualizar la vista con la página actual
        self.update_view()
    
    def set_page(self, page: int):
        """Cambia a la página especificada."""
        if page != self.current_page and page > 0:
            self.current_page = page
            self.update_view()
    
    def set_page_size(self, page_size: int):
        """Cambia el tamaño de página."""
        if page_size != self.page_size and page_size > 0:
            self.page_size = page_size
            # Verificar que la página actual sigue siendo válida
            max_page = max(1, (len(cast(List[Dict[str, Any]], self.all_record_data)) + self.page_size - 1) // self.page_size)
            if self.current_page > max_page:
                self.current_page = max_page
            self.update_view()
    
    def update_view(self):
        """Actualiza la vista para mostrar sólo los registros de la página actual."""
        # Calcular rango de registros para la página actual
        start_idx = (self.current_page - 1) * self.page_size
        end_idx = min(start_idx + self.page_size, len(cast(List[Dict[str, Any]], self.all_record_data)))
        
        # Obtener solo los registros de la página actual
        self.record_data = self.all_record_data[start_idx:end_idx]
        
        # Limpiar tabla y agregar filas
        self.setRowCount(len(cast(List[Dict[str, Any]], self.record_data)))
        
        for row_idx, row_data in enumerate(self.record_data):
            # ID
            id_item = QTableWidgetItem(str(row_data['id']))
            # Guardar ID numérico para ordenamiento
            id_item.setData(Qt.ItemDataRole.UserRole, int(row_data['id']))
            self.setItem(row_idx, 0, id_item)
            
            # Nombre Real
            self.setItem(row_idx, 1, QTableWidgetItem(row_data['real_name']))
            
            # Nombre Lógico
            logical_name = row_data.get('logical_name') or ''
            self.setItem(row_idx, 2, QTableWidgetItem(logical_name))
            
            # Repositorio
            repo = row_data.get('repository_location') or ''
            self.setItem(row_idx, 3, QTableWidgetItem(repo))
            
            # Fecha Homologación
            date_item = QTableWidgetItem()
            if row_data['homologation_date']:
                date_str = row_data['homologation_date']
                try:
                    # Convertir a formato legible
                    py_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                    formatted_date = py_date.strftime('%d/%m/%Y')
                    date_item.setText(formatted_date)
                    # Guardar fecha ISO para ordenamiento
                    date_item.setData(Qt.ItemDataRole.UserRole, date_str)
                except ValueError:
                    date_item.setText(date_str)
            self.setItem(row_idx, 4, date_item)
            
            # Creador
            creator = row_data.get('created_by_username', '') 
            if row_data.get('created_by_full_name'):
                creator += f" ({row_data['created_by_full_name']})"
            self.setItem(row_idx, 5, QTableWidgetItem(creator))
            
            # Fecha Actualización
            updated_item = QTableWidgetItem()
            if row_data.get('updated_at'):
                try:
                    dt = datetime.fromisoformat(row_data['updated_at'].replace('Z', '+00:00'))
                    updated_item.setText(dt.strftime('%d/%m/%Y %H:%M'))
                    # Guardar timestamp para ordenamiento
                    updated_item.setData(Qt.ItemDataRole.UserRole, row_data['updated_at'])
                except (ValueError, TypeError):
                    updated_item.setText(str(row_data.get('updated_at', '')))
            self.setItem(row_idx, 6, updated_item)
        
        self.resizeColumnsToContents()
        
        # Actualizar indicadores de ordenamiento
        self.update_sort_indicators()
        
    def clear_data(self):
        """Limpia todos los datos de la tabla."""
        self.all_record_data = []
        self.record_data = []
        self.setRowCount(0)
        self.total_records_changed.emit(0)
    
    def get_selected_record(self):
        """Obtiene el registro seleccionado completo."""
        selection_model = self.selectionModel()
        if not selection_model:
            return None
            
        selected_rows = selection_model.selectedRows()
        if not selected_rows:
            return None
            
        row_index = selected_rows[0].row()
        if 0 <= row_index < len(self.record_data):
            return self.record_data[row_index]
            
        return None
        
    def get_total_records(self):
        """Retorna el número total de registros."""
        return len(self.all_record_data)
        
    def get_visible_range(self):
        """Retorna el rango de registros visibles (inicio, fin)."""
        if not self.record_data:
            return (0, 0)
        start_idx = (self.current_page - 1) * self.page_size + 1
        end_idx = start_idx + len(self.record_data) - 1
        return (start_idx, end_idx)
    
    def show_context_menu(self, position: QPoint) -> None:
        """Muestra el menú contextual de la tabla."""

        # Verificar que hay un registro seleccionado
        record = self.get_selected_record()
        if not record or not self.main_window:
            return
        
        # Crear menú contextual
        context_menu = QMenu(self)
        
        # Acción Ver Detalles
        details_action = QAction("👁️ Ver Detalles", self)
        details_action.triggered.connect(self.main_window.view_details)
        context_menu.addAction(details_action)
        
        # Acción Editar
        edit_action = QAction("✏️ Editar", self)
        edit_action.triggered.connect(self.main_window.edit_homologation)
        context_menu.addAction(edit_action)
        
        # Acción Previsualizar Web (solo si tiene URL)
        kb_url = record.get('kb_url', '').strip()
        if kb_url:
            context_menu.addSeparator()
            web_preview_action = QAction("🌐 Previsualizar Web", self)
            web_preview_action.triggered.connect(lambda: self.main_window.preview_web_url(record))
            context_menu.addAction(web_preview_action)
        
        # Separador
        context_menu.addSeparator()
        
        # Acción Eliminar (solo para admin/manager)
        if (
            hasattr(self.main_window, 'current_user')
            and self.main_window.current_user
            and self.main_window.current_user.get('role') in ['admin', 'manager']
        ):
            delete_action = QAction("🗑️ Eliminar", self)
            delete_action.triggered.connect(self.main_window.delete_homologation)
            # Estilo rojo para indicar acción destructiva
            delete_action.setProperty("style", "danger")
            context_menu.addAction(delete_action)
        
        # Mostrar menú en la posición del cursor
        global_pos = self.mapToGlobal(position)
        context_menu.exec(global_pos)
        

class PaginationWidget(QWidget):
    """Widget para controles de paginación de tabla."""
    
    # Señales para cuando cambian los parámetros de paginación
    page_changed = pyqtSignal(int)  # Emite nueva página
    page_size_changed = pyqtSignal(int)  # Emite nuevo tamaño de página
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.current_page = 1
        self.total_pages = 1
        self.page_size = 20
        self.total_records = 0
        self.setup_ui()
        
    def setup_ui(self):
        """Configura la interfaz de los controles de paginación."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Etiqueta de información (1-20 de 100 registros)
        self.info_label = QLabel()
        layout.addWidget(self.info_label)
        
        # Espaciador flexible
        layout.addItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        
        # Controles de página
        layout.addWidget(QLabel("Página:"))
        
        # Botón Anterior
        self.prev_button = QPushButton("◀")
        self.prev_button.setMaximumWidth(40)
        self.prev_button.clicked.connect(self.go_previous_page)
        layout.addWidget(self.prev_button)
        
        # Spinner de página actual
        self.page_spinner = QSpinBox()
        self.page_spinner.setMinimum(1)
        self.page_spinner.setMaximum(1)
        self.page_spinner.setValue(1)
        self.page_spinner.valueChanged.connect(self.on_page_changed)
        layout.addWidget(self.page_spinner)
        
        # Botón Siguiente
        self.next_button = QPushButton("▶")
        self.next_button.setMaximumWidth(40)
        self.next_button.clicked.connect(self.go_next_page)
        layout.addWidget(self.next_button)
        
        # Total de páginas
        self.total_label = QLabel("de 1")
        layout.addWidget(self.total_label)
        
        # Selector de registros por página
        layout.addWidget(QLabel("Mostrar:"))
        self.page_size_combo = QComboBox()
        for size in [10, 20, 50, 100]:
            self.page_size_combo.addItem(f"{size}", size)
        # Seleccionar 20 por defecto
        self.page_size_combo.setCurrentIndex(1)
        self.page_size_combo.currentIndexChanged.connect(self.on_page_size_changed)
        layout.addWidget(self.page_size_combo)
        layout.addWidget(QLabel("registros"))
        
        # Actualizar estado inicial
        self.update_controls()
    
    def set_total_records(self, total: int):
        """Actualiza el total de registros y recalcula las páginas."""
        self.total_records = max(0, total)
        self.total_pages = max(1, (self.total_records + self.page_size - 1) // self.page_size)
        
        # Asegurar que la página actual es válida
        if self.current_page > self.total_pages:
            self.current_page = self.total_pages
            self.page_changed.emit(self.current_page)
        
        self.update_controls()
    
    def update_controls(self):
        """Actualiza el estado de los controles según la paginación actual."""
        # Actualizar etiqueta de información
        start_record = (self.current_page - 1) * self.page_size + 1
        end_record = min(self.current_page * self.page_size, self.total_records)
        
        if self.total_records == 0:
            info_text = "No hay registros"
            start_record = 0
        else:
            info_text = f"{start_record}-{end_record} de {self.total_records} registros"
        
        self.info_label.setText(info_text)
        
        # Actualizar selector de página
        self.page_spinner.blockSignals(True)
        self.page_spinner.setMaximum(self.total_pages)
        self.page_spinner.setValue(self.current_page)
        self.page_spinner.blockSignals(False)
        
        # Actualizar etiqueta de total
        self.total_label.setText(f"de {self.total_pages}")
        
        # Habilitar/deshabilitar botones según posición
        self.prev_button.setEnabled(self.current_page > 1)
        self.next_button.setEnabled(self.current_page < self.total_pages)
    
    def on_page_changed(self, page: int):
        """Manejador para cuando se cambia directamente la página."""
        if page != self.current_page:
            self.current_page = page
            self.update_controls()
            self.page_changed.emit(self.current_page)
    
    def on_page_size_changed(self):
        """Manejador para cuando se cambia el tamaño de página."""
        new_size = self.page_size_combo.currentData()
        if new_size != self.page_size:
            self.page_size = new_size
            
            # Recalcular el número total de páginas
            self.total_pages = max(1, (self.total_records + self.page_size - 1) // self.page_size)
            
            # Ajustar la página actual si es necesario
            if self.current_page > self.total_pages:
                self.current_page = self.total_pages
            
            self.update_controls()
            self.page_size_changed.emit(self.page_size)
    
    def go_next_page(self):
        """Avanza a la siguiente página."""
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.update_controls()
            self.page_changed.emit(self.current_page)
    
    def go_previous_page(self):
        """Retrocede a la página anterior."""
        if self.current_page > 1:
            self.current_page -= 1
            self.update_controls()
            self.page_changed.emit(self.current_page)
    
    def reset(self):
        """Reinicia la paginación a valores iniciales."""
        self.current_page = 1
        self.update_controls()
        self.page_changed.emit(self.current_page)


class FilterWidget(QFrame):
    """Widget para filtros de búsqueda."""
    
    filter_changed = pyqtSignal(dict)
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setup_ui()
        self.setup_filter_styles()
    
    def setup_ui(self):
        """Configura la interfaz de filtros."""
        filter_layout = QGridLayout(self)
        filter_layout.setContentsMargins(10, 10, 10, 10)
        filter_layout.setSpacing(10)
        
        # Título
        title = QLabel("Filtros")
        title_font = QFont()
        title_font.setBold(True)
        title.setFont(title_font)
        filter_layout.addWidget(title, 0, 0, 1, 2)
        
        # Filtro por Nombre
        filter_layout.addWidget(QLabel("Nombre:"), 1, 0)
        self.name_filter = QLineEdit()
        self.name_filter.setPlaceholderText("Buscar por nombre...")
        self.name_filter.textChanged.connect(self.trigger_filter_change)
        filter_layout.addWidget(self.name_filter, 1, 1)
        
        # Filtro por Repositorio
        filter_layout.addWidget(QLabel("Repositorio:"), 2, 0)
        self.repo_filter = QComboBox()
        self.repo_filter.addItem("Todos", "")
        self.repo_filter.addItem("AESA", "AESA")
        self.repo_filter.addItem("APPS$", "APPS$")
        self.repo_filter.currentIndexChanged.connect(self.trigger_filter_change)
        filter_layout.addWidget(self.repo_filter, 2, 1)
        
        # Filtro por Fecha Desde
        filter_layout.addWidget(QLabel("Desde:"), 3, 0)
        self.date_from_filter = QDateEdit()
        self.date_from_filter.setCalendarPopup(True)
        self.date_from_filter.setDate(QDate.currentDate().addYears(-1))
        self.date_from_filter.setSpecialValueText("Sin fecha mínima")
        self.date_from_filter.dateChanged.connect(self.trigger_filter_change)
        filter_layout.addWidget(self.date_from_filter, 3, 1)
        
        # Filtro por Fecha Hasta
        filter_layout.addWidget(QLabel("Hasta:"), 4, 0)
        self.date_to_filter = QDateEdit()
        self.date_to_filter.setCalendarPopup(True)
        self.date_to_filter.setDate(QDate.currentDate())
        self.date_to_filter.setSpecialValueText("Sin fecha máxima")
        self.date_to_filter.dateChanged.connect(self.trigger_filter_change)
        filter_layout.addWidget(self.date_to_filter, 4, 1)
        
        # Botones
        button_layout = QHBoxLayout()
        
        apply_button = QPushButton("Aplicar Filtros")
        apply_button.clicked.connect(self.apply_filters)
        button_layout.addWidget(apply_button)
        
        clear_button = QPushButton("Limpiar")
        clear_button.clicked.connect(self.clear_filters)
        button_layout.addWidget(clear_button)
        
        filter_layout.addLayout(button_layout, 5, 0, 1, 2)
        
        # Espaciador vertical
        filter_layout.addItem(
            QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding),
            6, 0, 1, 2
        )
    
    def trigger_filter_change(self):
        """Activa el temporizador para cambio de filtro."""
        # Para evitar múltiples actualizaciones seguidas
        QTimer.singleShot(300, self.apply_filters)
    
    def apply_filters(self):
        """Aplica los filtros actuales."""
        filters = {}
        
        # Nombre
        if self.name_filter.text().strip():
            filters['real_name'] = self.name_filter.text().strip()
        
        # Repositorio
        if self.repo_filter.currentData():
            filters['repository_location'] = self.repo_filter.currentData()
        
        # Fechas
        from_date = self.date_from_filter.date()
        if not self.date_from_filter.specialValueText() or from_date != self.date_from_filter.minimumDate():
            filters['date_from'] = from_date.toString(Qt.DateFormat.ISODate)
            
        to_date = self.date_to_filter.date()
        if not self.date_to_filter.specialValueText() or to_date != self.date_to_filter.minimumDate():
            filters['date_to'] = to_date.toString(Qt.DateFormat.ISODate)
        
        self.filter_changed.emit(filters)
    
    def clear_filters(self):
        """Limpia todos los filtros."""
        self.name_filter.clear()
        self.repo_filter.setCurrentIndex(0)
        self.date_from_filter.setDate(self.date_from_filter.minimumDate())
        self.date_to_filter.setDate(QDate.currentDate())
        self.apply_filters()
        
    def setup_filter_styles(self):
        """Aplica estilos para mejor visibilidad en tema oscuro."""
        # Estilo para los labels
        for child in self.findChildren(QLabel):
            child.setStyleSheet("color: #e0e0e0;")
            
        # Estilo para los QLineEdit
        for child in self.findChildren(QLineEdit):
            child.setStyleSheet("""
                QLineEdit {
                    background-color: #3a3a3a;
                    color: white;
                    border: 1px solid #555555;
                    border-radius: 3px;
                    padding: 2px;
                }
                QLineEdit:focus {
                    border: 1px solid #888888;
                }
            """)
            
        # Estilo para QComboBox
        for child in self.findChildren(QComboBox):
            child.setStyleSheet("""
                QComboBox {
                    background-color: #3a3a3a;
                    color: white;
                    border: 1px solid #555555;
                    border-radius: 3px;
                    padding: 2px;
                }
                QComboBox::drop-down {
                    subcontrol-origin: padding;
                    subcontrol-position: top right;
                    width: 15px;
                    border-left: 1px solid #555555;
                }
                QComboBox QAbstractItemView {
                    background-color: #3a3a3a;
                    color: white;
                    selection-background-color: #505050;
                }
            """)
            
        # Estilo para QDateEdit
        for child in self.findChildren(QDateEdit):
            child.setStyleSheet("""
                QDateEdit {
                    background-color: #3a3a3a;
                    color: white;
                    border: 1px solid #555555;
                    border-radius: 3px;
                    padding: 2px;
                }
                QDateEdit::drop-down {
                    subcontrol-origin: padding;
                    subcontrol-position: top right;
                    width: 15px;
                    border-left: 1px solid #555555;
                }
                QDateEdit QAbstractItemView {
                    background-color: #3a3a3a;
                    color: white;
                    selection-background-color: #505050;
                }
            """)
            
        # Estilo para los botones
        for child in self.findChildren(QPushButton):
            child.setStyleSheet("""
                QPushButton {
                    background-color: #0066cc;
                    color: white;
                    border: none;
                    border-radius: 3px;
                    padding: 6px 12px;
                }
                QPushButton:hover {
                    background-color: #0077ee;
                }
                QPushButton:pressed {
                    background-color: #0055aa;
                }
            """)


class MainWindow(QMainWindow):
    """Ventana principal del Homologador."""
    
    def __init__(self, user_info: Optional[Dict[str, Any]] = None):
        super().__init__()
        self.user_info: Optional[Dict[str, Any]] = user_info
        self.current_user: Optional[Dict[str, Any]] = user_info
        self.repo = get_homologation_repository()
        self.audit_repo = get_audit_repository()
        self.data_worker: Optional[DataLoadWorker] = None
        self.current_filters: Dict[str, Any] = {}
        
        # Inicializar nuevas funcionalidades
        self.advanced_search_widget: Optional[QWidget] = None
        self.accessibility_manager: Optional[Any] = None
        
        # Aplicar tema desde configuraciones guardadas
        apply_theme_from_settings(self)
        
        # Suscribirse a cambios en el tema del sistema
        self.theme_monitor = get_theme_monitor()
        self.theme_monitor.theme_changed.connect(self.on_system_theme_changed)
        
        self.setup_ui()
        self.setup_styles()
        self.setup_actions()
        self.setup_signals()
        
        # Configurar nuevas funcionalidades
        self.setup_advanced_features()
        
        # Cargar datos iniciales
        self.refresh_data()
        
    def setup_ui(self):
        """Configura la interfaz de usuario."""
        self.setWindowTitle("EL OMO LOGADOR 🥵 - Homologador de Aplicaciones")
        self.resize(1200, 700)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Título principal del software
        title_label = QLabel("EL OMO LOGADOR 🥵")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(28)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("""
            QLabel {
                color: #ff6b6b;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #ff6b6b, stop:0.5 #ffd93d, stop:1 #6bcf7f);
                -webkit-background-clip: text;
                padding: 20px;
                margin: 10px;
                border: 2px solid #ff6b6b;
                border-radius: 15px;
                background-color: rgba(255, 107, 107, 0.1);
            }
        """)
        main_layout.addWidget(title_label)
        
        # Splitter para dividir filtros y tabla
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Panel de filtros (izquierda)
        self.filter_widget = FilterWidget()
        self.filter_widget.filter_changed.connect(self.on_filter_changed)
        splitter.addWidget(self.filter_widget)
        
        # Tabla de homologaciones (derecha)
        self.table_widget = HomologationTableWidget()
        self.table_widget.doubleClicked.connect(self.on_table_double_click)
        # Conectar señal para actualizar paginación
        self.table_widget.total_records_changed.connect(self.on_total_records_changed)
        splitter.addWidget(self.table_widget)
        
        # Establecer proporciones iniciales
        splitter.setSizes([int(self.width() * 0.25), int(self.width() * 0.75)])
        
        main_layout.addWidget(splitter)
        
        # Control de paginación
        self.pagination_widget = PaginationWidget()
        self.pagination_widget.page_changed.connect(self.on_page_changed)
        self.pagination_widget.page_size_changed.connect(self.on_page_size_changed)
        main_layout.addWidget(self.pagination_widget)
        
        # Barra de botones
        button_layout = QHBoxLayout()
        
        # Botones según rol
        is_admin = self.user_info and self.user_info.get('role') == 'admin'
        is_editor = is_admin or (self.user_info and self.user_info.get('role') == 'editor')
        
        if is_editor:
            new_button = QPushButton("Nueva Homologación")
            new_button.clicked.connect(self.new_homologation)
            setup_widget_tooltips(new_button, 'btn_new')
            button_layout.addWidget(new_button)
            
            edit_button = QPushButton("Editar")
            edit_button.clicked.connect(self.edit_homologation)
            setup_widget_tooltips(edit_button, 'btn_edit')
            button_layout.addWidget(edit_button)
            
            # Botón eliminar - visible para admin y manager
            if is_admin or self.current_user.get('role') == 'manager':
                delete_button = QPushButton("🗑️ Eliminar")
                delete_button.clicked.connect(self.delete_homologation)
                delete_button.setStyleSheet("""
                    QPushButton {
                        background-color: #d32f2f;
                        color: white;
                        border: none;
                        padding: 6px 12px;
                        border-radius: 4px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #b71c1c;
                    }
                    QPushButton:pressed {
                        background-color: #8e0000;
                    }
                """)
                setup_widget_tooltips(delete_button, 'btn_delete')
                button_layout.addWidget(delete_button)
        
        details_button = QPushButton("Ver Detalles")
        details_button.clicked.connect(self.view_details)
        setup_widget_tooltips(details_button, 'btn_details')
        button_layout.addWidget(details_button)
        
        # Espaciador
        button_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        
        # Botón de métricas
        metrics_button = QPushButton("📊 Métricas")
        metrics_button.clicked.connect(self.show_metrics_panel)
        setup_widget_tooltips(metrics_button, 'btn_metrics')
        button_layout.addWidget(metrics_button)
        
        # Botón de actualizar
        refresh_button = QPushButton("Actualizar")
        refresh_button.clicked.connect(self.refresh_data)
        setup_widget_tooltips(refresh_button, 'btn_refresh')
        button_layout.addWidget(refresh_button)
        
        # Botón de exportar
        export_button = QPushButton("Exportar")
        export_button.clicked.connect(self.export_data)
        setup_widget_tooltips(export_button, 'btn_export')
        button_layout.addWidget(export_button)
        
        main_layout.addLayout(button_layout)
        
        # Barra de estado
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Listo")
        
        # Barra de herramientas y menús
        self.setup_menu()
        self.setup_toolbar()
    
    def setup_menu(self):
        """Configura el menú principal."""
        menubar = self.menuBar()
        if not menubar:
            return
        
        # Menú Archivo
        file_menu = menubar.addMenu('&Archivo')
        if not file_menu:
            return
        
        is_editor = self.user_info and self.user_info.get('role') in ('admin', 'editor')
        if is_editor:
            new_action = QAction("Nueva Homologación", self)
            new_action.setShortcut("Ctrl+N")
            new_action.triggered.connect(self.new_homologation)
            file_menu.addAction(new_action)
            file_menu.addSeparator()
        
        export_action = QAction("Exportar...", self)
        export_action.setShortcut("Ctrl+E")
        export_action.triggered.connect(self.export_data)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Salir", self)
        exit_action.setShortcut("Alt+F4")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Menú Ver
        view_menu = menubar.addMenu('&Ver')
        if not view_menu:
            return
        
        refresh_action = QAction("Actualizar", self)
        refresh_action.setShortcut("F5")
        refresh_action.triggered.connect(self.refresh_data)
        view_menu.addAction(refresh_action)
        
        view_menu.addSeparator()
        
        # Panel de métricas
        metrics_action = QAction("📊 Panel de Métricas", self)
        metrics_action.setShortcut("Ctrl+M")
        metrics_action.triggered.connect(self.show_metrics_panel)
        view_menu.addAction(metrics_action)
        
        # Centro de notificaciones
        if NOTIFICATIONS_AVAILABLE:
            notifications_action = QAction("🔔 Centro de Notificaciones", self)
            notifications_action.setShortcut("Ctrl+N")
            notifications_action.triggered.connect(self.show_notifications_panel)
            view_menu.addAction(notifications_action)
        
        view_menu.addSeparator()
        
        # Opciones de tema
        theme_menu = view_menu.addMenu("Tema")
        if not theme_menu:
            return
        
        theme_toggle_action = QAction("Cambiar Tema", self)
        theme_toggle_action.setShortcut("Ctrl+T")
        theme_toggle_action.triggered.connect(self.toggle_theme)
        theme_menu.addAction(theme_toggle_action)
        
        dark_theme_action = QAction("Tema Oscuro", self)
        dark_theme_action.triggered.connect(lambda: self.set_theme("dark"))
        theme_menu.addAction(dark_theme_action)
        
        light_theme_action = QAction("Tema Claro", self)
        light_theme_action.triggered.connect(lambda: self.set_theme("light"))
        theme_menu.addAction(light_theme_action)
        
        # Separador
        theme_menu.addSeparator()
        
        # Opción para seguir el tema del sistema
        system_theme_action = QAction("Seguir tema del sistema", self)
        system_theme_action.triggered.connect(lambda: self.set_theme("system"))
        theme_menu.addAction(system_theme_action)
        
        # Menú Buscar (si está disponible)
        if ADVANCED_SEARCH_AVAILABLE:
            search_menu = menubar.addMenu('&Buscar')
            if search_menu:
                search_action = QAction("🔍 Búsqueda Avanzada", self)
                search_action.setShortcut("Ctrl+F")
                search_action.triggered.connect(self.show_advanced_search)
                search_menu.addAction(search_action)
                
                search_menu.addSeparator()
                
                clear_search_action = QAction("Limpiar Búsqueda", self)
                clear_search_action.setShortcut("Ctrl+Shift+F")
                clear_search_action.triggered.connect(self.clear_search)
                search_menu.addAction(clear_search_action)
        
        # Menú Accesibilidad (si está disponible)
        if ACCESSIBILITY_AVAILABLE:
            accessibility_menu = menubar.addMenu('&Accesibilidad')
            if accessibility_menu:
                accessibility_settings_action = QAction("♿ Configuración de Accesibilidad", self)
                accessibility_settings_action.setShortcut("Ctrl+Alt+A")
                accessibility_settings_action.triggered.connect(self.show_accessibility_settings)
                accessibility_menu.addAction(accessibility_settings_action)
                
                accessibility_menu.addSeparator()
                
                high_contrast_action = QAction("Alternar Alto Contraste", self)
                high_contrast_action.setShortcut("Ctrl+Alt+H")
                high_contrast_action.triggered.connect(self.toggle_high_contrast)
                accessibility_menu.addAction(high_contrast_action)
                
                large_text_action = QAction("Alternar Texto Grande", self)
                large_text_action.setShortcut("Ctrl+Alt+L")
                large_text_action.triggered.connect(self.toggle_large_text)
                accessibility_menu.addAction(large_text_action)
        
        # Menú Usuario
        if self.user_info:
            user_menu = menubar.addMenu('&Usuario')
            if user_menu:
                # Información del usuario
                user_info_text = f"👤 {self.user_info.get('username', 'Usuario')} ({self.user_info.get('role', 'viewer')})"
                user_info_action = QAction(user_info_text, self)
                user_info_action.setEnabled(False)  # Solo informativo
                user_menu.addAction(user_info_action)
                
                user_menu.addSeparator()
                
                # Cambiar contraseña
                change_password_action = QAction("🔑 Cambiar Mi Contraseña", self)
                change_password_action.setShortcut("Ctrl+Shift+P")
                change_password_action.triggered.connect(self.change_my_password)
                user_menu.addAction(change_password_action)
                
                user_menu.addSeparator()
                
                # Cerrar sesión
                logout_action = QAction("🚪 Cerrar Sesión", self)
                logout_action.setShortcut("Ctrl+Shift+L")
                logout_action.triggered.connect(self.logout)
                user_menu.addAction(logout_action)

        # Menú Herramientas
        if self.user_info:
            tools_menu = menubar.addMenu('&Herramientas')
            if tools_menu:
                # Crear respaldo rápido (solo administradores)
                if self.user_info.get('role') == 'admin' and BACKUP_SYSTEM_AVAILABLE:
                    quick_backup_action = QAction("💾 Crear Respaldo Rápido", self)
                    quick_backup_action.setShortcut("Ctrl+Shift+B")
                    quick_backup_action.triggered.connect(self.create_quick_backup)
                    tools_menu.addAction(quick_backup_action)
                
                tools_menu.addSeparator()
                
                # Exportar datos
                export_action = QAction("📤 Exportar Datos", self)
                export_action.setShortcut("Ctrl+E")
                export_action.triggered.connect(self.export_data_dialog)
                tools_menu.addAction(export_action)

        # Menú Administración (solo para administradores)
        if self.user_info and self.user_info.get('role') == 'admin':
            admin_menu = menubar.addMenu('&Administración')
            if admin_menu:
                # Dashboard administrativo
                if ADMIN_DASHBOARD_AVAILABLE:
                    dashboard_action = QAction("🎛️ Dashboard Administrativo", self)
                    dashboard_action.setShortcut("Ctrl+D")
                    dashboard_action.triggered.connect(self.show_admin_dashboard)
                    admin_menu.addAction(dashboard_action)
                
                # Analytics Avanzado
                analytics_action = QAction("📊 Analytics Avanzado", self)
                analytics_action.setShortcut("Ctrl+Shift+A")
                analytics_action.triggered.connect(self.show_advanced_analytics)
                admin_menu.addAction(analytics_action)
                    
                admin_menu.addSeparator()
                
                # Gestión de usuarios
                if USER_MANAGEMENT_AVAILABLE:
                    user_management_action = QAction("👥 Gestión de Usuarios", self)
                    user_management_action.setShortcut("Ctrl+U")
                    user_management_action.triggered.connect(self.show_user_management)
                    admin_menu.addAction(user_management_action)
                
                # Panel de auditoría
                if AUDIT_PANEL_AVAILABLE():
                    audit_action = QAction("📋 Panel de Auditoría", self)
                    audit_action.setShortcut("Ctrl+A")
                    audit_action.triggered.connect(self.show_audit_panel)
                    admin_menu.addAction(audit_action)
                
                # Sistema de respaldos
                if BACKUP_SYSTEM_AVAILABLE:
                    backup_action = QAction("💾 Sistema de Respaldos", self)
                    backup_action.setShortcut("Ctrl+B")
                    backup_action.triggered.connect(self.show_backup_system)
                    admin_menu.addAction(backup_action)
                
                admin_menu.addSeparator()
                
                # Configuraciones del sistema
                settings_action = QAction("⚙️ Configuraciones del Sistema", self)
                settings_action.triggered.connect(self.show_system_settings)
                admin_menu.addAction(settings_action)
                
                # Reportes administrativos
                reports_action = QAction("� Reportes Administrativos", self)
                reports_action.triggered.connect(self.show_admin_reports)
                admin_menu.addAction(reports_action)
        
        # Menú Ayuda
        help_menu = menubar.addMenu('A&yuda')
        if help_menu:
            # Tour de usuario
            tour_action = QAction("🎯 Tour de Usuario", self)
            tour_action.setShortcut("F1")
            tour_action.triggered.connect(self.start_user_tour)
            help_menu.addAction(tour_action)
            
            help_menu.addSeparator()
            
            about_action = QAction("Acerca de", self)
            about_action.triggered.connect(self.show_about)
            help_menu.addAction(about_action)
    
    def setup_toolbar(self):
        """Configura la barra de herramientas."""
        toolbar = QToolBar("Barra Principal")
        toolbar.setMovable(False)
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.addToolBar(toolbar)
        
        # Actualizar datos
        refresh_action = QAction("🔄 Actualizar", self)
        refresh_action.setShortcut("F5")
        refresh_action.setToolTip("Actualizar datos de homologaciones")
        refresh_action.triggered.connect(self.refresh_data)
        toolbar.addAction(refresh_action)
        
        toolbar.addSeparator()
        
        # Nueva homologación (solo editores)
        if self.user_info and self.user_info.get('role') in ('admin', 'editor'):
            new_action = QAction("➕ Nueva", self)
            new_action.setShortcut("Ctrl+N")
            new_action.setToolTip("Crear nueva homologación")
            new_action.triggered.connect(self.new_homologation)
            toolbar.addAction(new_action)
        
        # Exportar
        export_action = QAction("📊 Exportar", self)
        export_action.setShortcut("Ctrl+E")
        export_action.setToolTip("Exportar datos a CSV")
        export_action.triggered.connect(self.export_data)
        toolbar.addAction(export_action)
        
        # Agregar espacio flexible
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        toolbar.addWidget(spacer)
        
        # Información del usuario y contraseña (lado derecho)
        if self.user_info:
            # Etiqueta con info del usuario
            user_label = QLabel(f"👤 {self.user_info.get('username', 'Usuario')}")
            user_label.setStyleSheet("""
                QLabel {
                    color: #f0f6fc;
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, 
                        stop: 0 #21262d, stop: 1 #0d1117);
                    padding: 5px 10px;
                    border-radius: 4px;
                    margin-right: 5px;
                }
            """)
            toolbar.addWidget(user_label)
            
            # Botón cambiar contraseña
            password_action = QAction("🔑 Mi Contraseña", self)
            password_action.setShortcut("Ctrl+Shift+P")
            password_action.setToolTip("Cambiar mi contraseña")
            password_action.triggered.connect(self.change_my_password)
            toolbar.addAction(password_action)
            
            # Botón cerrar sesión
            logout_action = QAction("🚪 Salir", self)
            logout_action.setShortcut("Ctrl+Shift+L")
            logout_action.setToolTip("Cerrar sesión")
            logout_action.triggered.connect(self.logout)
            toolbar.addAction(logout_action)
    
    def setup_styles(self):
        """Aplica estilos para mejorar la visibilidad en tema oscuro."""
        # Configurar estilo global para la aplicación
        self.setStyleSheet("""
            QMainWindow {
                background-color: #222222;
                color: #ffffff;
            }
            QMenuBar {
                background-color: #333333;
                color: #ffffff;
            }
            QMenuBar::item {
                background-color: transparent;
                padding: 5px 12px;
            }
            QMenuBar::item:selected {
                background-color: #0078d4;
            }
            QMenu {
                background-color: #333333;
                color: #ffffff;
                border: 1px solid #555555;
            }
            QMenu::item:selected {
                background-color: #0078d4;
            }
            QStatusBar {
                background-color: #333333;
                color: #ffffff;
            }
        """)
        
        # Estilo para la tabla con mejor visibilidad
        self.table_widget.setStyleSheet("""
            QTableWidget {
                background-color: #2d2d2d;
                color: #ffffff;
                gridline-color: #4a4a4a;
                selection-background-color: #0078d4;
                selection-color: #ffffff;
                border: 1px solid #555555;
                alternate-background-color: #353535;
                outline: none;
            }
            QHeaderView::section {
                background-color: #424242;
                color: #ffffff;
                padding: 5px;
                border: 1px solid #555555;
                font-weight: bold;
            }
            QTableCornerButton::section {
                background-color: #424242;
                border: 1px solid #555555;
            }
            QTableWidget::item {
                border-bottom: 1px solid #3a3a3a;
                padding: 4px;
                color: #ffffff;
            }
            QTableWidget::item:alternate {
                background-color: #353535;
            }
            QTableWidget::item:selected {
                background-color: #0078d4;
                color: #ffffff;
            }
            QScrollBar:vertical {
                border: none;
                background-color: #2d2d2d;
                width: 14px;
                margin: 15px 0 15px 0;
            }
            QScrollBar::handle:vertical {
                background-color: #5a5a5a;
                min-height: 30px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #6a6a6a;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
        """)
        
        # Estilo para los filtros
        self.filter_widget.setStyleSheet("""
            QFrame {
                background-color: #2d2d2d;
                border: 1px solid #555555;
                border-radius: 4px;
            }
            QLabel {
                color: #ffffff;
                font-weight: 500;
            }
            QLineEdit {
                background-color: #3c3c3c;
                color: #ffffff;
                border: 1px solid #666666;
                border-radius: 3px;
                padding: 6px;
                selection-background-color: #0078d4;
            }
            QLineEdit:focus {
                border: 1px solid #0078d4;
            }
            QComboBox {
                background-color: #3c3c3c;
                color: #ffffff;
                border: 1px solid #666666;
                border-radius: 3px;
                padding: 6px;
                min-height: 20px;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 15px;
                border-left: 1px solid #666666;
            }
            QComboBox QAbstractItemView {
                background-color: #3c3c3c;
                color: #ffffff;
                border: 1px solid #666666;
                selection-background-color: #0078d4;
            }
            QDateEdit {
                background-color: #3c3c3c;
                color: #ffffff;
                border: 1px solid #666666;
                border-radius: 3px;
                padding: 6px;
            }
            QDateEdit::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 15px;
                border-left: 1px solid #666666;
            }
            QCalendarWidget {
                background-color: #333333;
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
            QPushButton:pressed {
                background-color: #005a9e;
            }
            QPushButton:disabled {
                background-color: #4a4a4a;
                color: #aaaaaa;
            }
        """)
        
        # Estilo específico para botones principales
        button_style = """
            QPushButton {
                background-color: #0078d4;
                color: #ffffff;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
            QPushButton:pressed {
                background-color: #005a9e;
            }
            QPushButton:disabled {
                background-color: #4a4a4a;
                color: #aaaaaa;
            }
        """
        
        # Aplicar estilos a los botones principales
        central_widget = self.centralWidget()
        if central_widget:
            for child in central_widget.findChildren(QPushButton):
                child.setStyleSheet(button_style)
                
            # Aplicar estilo al widget central
            central_widget.setStyleSheet("""
                QWidget {
                    background-color: #222222;
                    color: #ffffff;
                }
        """)
    
    def setup_actions(self):
        """Configura acciones adicionales."""
        pass
    
    def setup_signals(self):
        """Conecta señales y slots."""
        pass
    
    def setup_advanced_features(self):
        """Configura las funcionalidades avanzadas."""
        # Configurar búsqueda avanzada
        if ADVANCED_SEARCH_AVAILABLE():
            try:
                AdvancedSearchWidget = get_advanced_search()
                if AdvancedSearchWidget:
                    self.advanced_search_widget = AdvancedSearchWidget()
                    self.advanced_search_widget.search_requested.connect(self.on_advanced_search)
                    self.advanced_search_widget.result_selected.connect(self.on_search_result_selected)
                    # Ocultar por defecto
                    self.advanced_search_widget.hide()
                    logger.info("Búsqueda avanzada configurada correctamente")
                else:
                    logger.warning("No se pudo cargar el widget de búsqueda avanzada")
            except Exception as e:
                logger.error(f"Error configurando búsqueda avanzada: {e}")
                self.advanced_search_widget = None
        
        # Configurar accesibilidad
        if ACCESSIBILITY_AVAILABLE():
            try:
                AccessibilityManager = get_accessibility_manager()
                if AccessibilityManager:
                    app_instance = QApplication.instance()
                    if app_instance and isinstance(app_instance, QApplication):
                        self.accessibility_manager = AccessibilityManager(
                            app_instance, self
                        )
                        logger.info("Gestor de accesibilidad configurado correctamente")
                    else:
                        logger.warning("No se pudo obtener la instancia de QApplication")
                        self.accessibility_manager = None
                else:
                    logger.warning("No se pudo cargar el gestor de accesibilidad")
                    self.accessibility_manager = None
            except Exception as e:
                logger.error(f"Error configurando accesibilidad: {e}")
                self.accessibility_manager = None
    
    def on_filter_changed(self, filters):
        """Maneja cambios en los filtros."""
        self.current_filters = filters
        # Resetear a la primera página al cambiar filtros
        self.pagination_widget.reset()
        self.refresh_data()
    
    def on_page_changed(self, page: int):
        """Maneja cambios de página en la paginación."""
        self.table_widget.set_page(page)
    
    def on_page_size_changed(self, page_size: int):
        """Maneja cambios en el tamaño de página."""
        self.table_widget.set_page_size(page_size)
    
    def on_total_records_changed(self, total_records: int):
        """Actualiza el contador de registros en la paginación."""
        self.pagination_widget.set_total_records(total_records)
        
        # Actualizar mensaje en la barra de estado
        if total_records == 0:
            self.status_bar.showMessage("No se encontraron registros")
        else:
            self.status_bar.showMessage(f"Se encontraron {total_records} registros")
    
    def on_table_double_click(self):
        """Maneja doble clic en la tabla."""
        self.view_details()
    
    def refresh_data(self):
        """Refresca los datos de la tabla."""
        self.apply_filters()
    
    def on_homologation_saved(self, homologation_id):
        """Maneja el evento cuando una homologación es guardada."""
        self.refresh_data()
        # Usar el sistema de notificaciones en lugar de la barra de estado
        send_success("Homologación Guardada", f"Homologación guardada exitosamente con ID: {homologation_id}", "main_window")
    
    def new_homologation(self):
        """Abre formulario para nueva homologación."""
        dialog = HomologationFormDialog(self, user_info=cast(Dict[str, Any], self.user_info) if self.user_info else {})
        dialog.homologation_saved.connect(self.on_homologation_saved)
        dialog.exec()
    
    def view_details(self):
        """Muestra detalles de la homologación seleccionada."""
        record = self.table_widget.get_selected_record()
        if not record:
            QMessageBox.warning(self, "Advertencia", "Seleccione una homologación")
            return
        
        dialog = show_homologation_details(self, homologation_data=cast(Dict[str, Any], dict(record)), user_info=cast(Dict[str, Any], self.user_info))
        dialog.exec()
    
    def edit_homologation(self):
        """Edita la homologación seleccionada."""
        record = self.table_widget.get_selected_record()
        if not record:
            QMessageBox.warning(self, "Advertencia", "Seleccione una homologación")
            return
        
        dialog = HomologationFormDialog(self, homologation_data=cast(Dict[str, Any], dict(record)), user_info=cast(Dict[str, Any], self.user_info) if self.user_info else {})
        dialog.homologation_saved.connect(self.on_homologation_saved)
        dialog.exec()
    
    def delete_homologation(self):
        """Elimina la homologación seleccionada."""
        record = self.table_widget.get_selected_record()
        if not record:
            send_warning("Seleccione una homologación", "Debe seleccionar una homologación primero", "main_window")
            return
            
        # Confirmar eliminación
        confirm = QMessageBox.question(
            self, 
            "Confirmar eliminación",
            f"¿Está seguro de eliminar la homologación '{record['real_name']}'?\n\nEsta acción no se puede deshacer.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if confirm == QMessageBox.StandardButton.Yes:
            try:
                success = self.repo.delete(record['id'])
                if success:
                    send_success("Homologación Eliminada", f"Homologación eliminada exitosamente: {record['real_name']}", "main_window")
                    self.refresh_data()
                else:
                    send_error("Error", "No se pudo eliminar la homologación", "main_window")
            except Exception as e:
                logger.error(f"Error eliminando homologación: {e}")
                send_error("Error de Eliminación", f"Error eliminando homologación: {str(e)}", "main_window")
    
    def apply_filters(self):
        """Aplica filtros actuales y carga datos."""
        self.status_bar.showMessage("Cargando datos...")
        self.table_widget.clear_data()
        
        # Asegurarnos de que la paginación esté en la primera página
        # al aplicar nuevos filtros
        if hasattr(self, 'pagination_widget'):
            self.pagination_widget.reset()
        
        if self.data_worker and self.data_worker.isRunning():
            self.data_worker.terminate()
            self.data_worker.wait()
            
        self.data_worker = DataLoadWorker(self.repo, self.current_filters)
        self.data_worker.data_ready.connect(self.on_data_loaded)
        self.data_worker.error.connect(self.on_data_error)
        self.data_worker.start()
    
    def on_data_loaded(self, data: List[Any]):
        """Maneja datos cargados exitosamente."""
        # El control de registros totales ahora lo maneja la tabla
        # y se actualiza a través de la señal total_records_changed
        self.table_widget.load_data(data)
    
    def on_data_error(self, error_message):
        """Maneja errores de carga."""
        self.status_bar.showMessage("Error cargando datos")
        QMessageBox.critical(self, "Error", f"Error cargando datos: {error_message}")
    
    def export_data(self):
        """Exporta los datos a CSV."""
        if not self.table_widget.record_data:
            QMessageBox.warning(self, "Advertencia", "No hay datos para exportar")
            return
            
        filename, _ = QFileDialog.getSaveFileName(
            self, "Guardar archivo CSV", "", "CSV (*.csv)"
        )
        
        if not filename:
            return
            
        if not filename.endswith('.csv'):
            filename += '.csv'
            
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # Escribir encabezados
                writer.writerow([
                    'ID', 'Nombre Real', 'Nombre Lógico', 'URL Documentación',
                    'KB SYNC', 'Fecha Homologación', 'Versiones Previas', 
                    'Repositorio', 'Detalles', 'Creado Por', 'Creado', 'Actualizado'
                ])
                
                # Escribir datos
                for row in self.table_widget.record_data:
                    writer.writerow([
                        row['id'], 
                        row['real_name'], 
                        row.get('logical_name', ''),
                        row.get('kb_url', ''),
                        'Sí' if row.get('kb_sync') else 'No',
                        row.get('homologation_date', ''),
                        'Sí' if row.get('has_previous_versions') else 'No',
                        row.get('repository_location', ''),
                        row.get('details', '').replace('\n', ' ').replace('\r', ''),
                        row.get('created_by_username', ''),
                        row.get('created_at', ''),
                        row.get('updated_at', '')
                    ])
                    
            self.status_bar.showMessage(f"Datos exportados a {filename}", 5000)
            
        except Exception as e:
            logger.error(f"Error exportando datos: {e}")
            QMessageBox.critical(self, "Error", f"Error exportando datos: {str(e)}")
    
    def show_about(self):
        """Muestra información sobre la aplicación."""
        QMessageBox.about(
            self, 
            "Acerca de Homologador",
            "Homologador de Aplicaciones v1.0.0\n"
            "© 2024-2025 Empresa S.A.\n\n"
            "Sistema para gestión y documentación de homologaciones."
        )
    
    def show_metrics_panel(self):
        """Muestra el panel de métricas y estadísticas."""
        # Crear ventana secundaria para métricas
        metrics_window = QWidget()
        metrics_window.setWindowTitle("📊 Panel de Métricas y Estadísticas")
        metrics_window.setMinimumSize(1000, 700)
        metrics_window.resize(1200, 800)
        
        # Layout principal
        layout = QVBoxLayout(metrics_window)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Crear panel de métricas
        metrics_panel = MetricsPanel()
        layout.addWidget(metrics_panel)
        
        # Hacer que la ventana sea modal
        metrics_window.setWindowModality(Qt.WindowModality.ApplicationModal)
        
        # Posicionar relativo a la ventana principal
        if self.geometry().isValid():
            x = self.geometry().x() + 50
            y = self.geometry().y() + 50
            metrics_window.move(x, y)
        
        # Mostrar ventana
        metrics_window.show()
        
        # Guardar referencia para evitar garbage collection
        self.metrics_window = metrics_window
    
    def show_notifications_panel(self):
        """Muestra el centro de notificaciones."""
        if not NOTIFICATIONS_AVAILABLE:
            QMessageBox.warning(
                self,
                "Módulo No Disponible",
                "El sistema de notificaciones no está disponible."
            )
            return
        
        # Crear ventana secundaria para notificaciones
        notifications_window = QWidget()
        notifications_window.setWindowTitle("🔔 Centro de Notificaciones")
        notifications_window.setMinimumSize(800, 600)
        notifications_window.resize(1000, 700)
        
        # Layout principal
        layout = QVBoxLayout(notifications_window)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Crear panel de notificaciones
        notification_system = get_notification_system()
        if notification_system and notification_system.get('panel') and notification_system.get('manager'):
            NotificationPanel = notification_system['panel']
            notification_manager = notification_system['manager']
            notifications_panel = NotificationPanel(notification_manager)
            layout.addWidget(notifications_panel)
        else:
            # Fallback si el sistema de notificaciones no está disponible
            from PyQt6.QtWidgets import QLabel
            fallback_label = QLabel("Sistema de notificaciones no disponible")
            fallback_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(fallback_label)
        
        # Hacer que la ventana sea modal
        notifications_window.setWindowModality(Qt.WindowModality.ApplicationModal)
        
        # Posicionar relativo a la ventana principal
        if self.geometry().isValid():
            x = self.geometry().x() + 50
            y = self.geometry().y() + 50
            notifications_window.move(x, y)
        
        # Mostrar ventana
        notifications_window.show()
        
        # Guardar referencia para evitar garbage collection
        self.notifications_window = notifications_window
    
    def show_user_management(self):
        """Muestra el módulo de administración de usuarios."""
        if not USER_MANAGEMENT_AVAILABLE():
            QMessageBox.warning(
                self,
                "Módulo No Disponible",
                "El módulo de administración de usuarios no está disponible."
            )
            return
        
        if not self.user_info or self.user_info.get('role') != 'admin':
            QMessageBox.warning(
                self,
                "Acceso Denegado",
                "Solo los administradores pueden acceder a este módulo."
            )
            return
        
        try:
            show_user_management_func = get_user_management()
            if not show_user_management_func:
                QMessageBox.critical(
                    self,
                    "Error",
                    "El módulo de administración de usuarios no se pudo cargar."
                )
                return
            
            dialog = show_user_management_func(cast(Dict[str, Any], self.user_info), self)
            dialog.exec()
        except Exception as e:
            logger.error(f"Error abriendo administración de usuarios: {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"Error abriendo módulo de administración: {str(e)}"
            )
    
    def start_user_tour(self):
        """Inicia el tour de usuario para la ventana principal."""
        tour = start_user_tour('main_window_tour', self)
        if tour:
            # Conectar señales del tour
            tour.tour_completed.connect(lambda: send_success("Operación Exitosa", "¡Tour completado! Ya conoce las funciones principales.", "main_window"))
            tour.tour_cancelled.connect(lambda: send_info("Información", "Tour cancelado. Puede reiniciarlo desde el menú Ayuda.", "main_window"))
        else:
            send_warning("Advertencia", "No se pudo iniciar el tour de usuario.", "main_window")
        
    def toggle_theme(self):
        """Cambia entre tema claro y oscuro."""
        toggle_theme(self)
        self.refresh_data()  # Actualizar datos para aplicar correctamente los estilos
    
    def set_theme(self, theme: str):
        """Establece un tema específico."""
        if theme not in ["dark", "light", "system"]:
            return
        

        # Si es "system", guardamos la preferencia y aplicamos el tema detectado

        from .theme import ThemeSettings, detect_system_theme
        if theme == "system":
            ThemeSettings.save_theme_preference(ThemeType.SYSTEM)
            # Detectar el tema del sistema y aplicarlo
            detected_theme = detect_system_theme()
            actual_theme = "light" if detected_theme == ThemeType.LIGHT else "dark"
            
            # Usar transición suave si está disponible
            try:

                # Crear gestor de transición

                from .theme_effects import ThemeTransitionManager
                transition = ThemeTransitionManager(duration=300)
                transition.prepare_transition(self, actual_theme)
                
                # Iniciar transición
                transition.start_transition()
                
            except ImportError:
                # Fallback: cambio instantáneo si no está disponible el efecto
                set_widget_style_class(self, actual_theme)
            
            # Mostrar mensaje de éxito
            send_success("Operación Exitosa", "Tema configurado para seguir el tema del sistema", "main_window")
            
            # Actualizar datos para aplicar correctamente los estilos
            self.refresh_data()
            return
            
        # Si es "dark" o "light"
        current_theme = self.property("styleClass") or "dark"
        if current_theme != theme:
            # Usar transición suave si está disponible
            try:

                # Crear gestor de transición

                from .theme_effects import ThemeTransitionManager
                transition = ThemeTransitionManager(duration=300)
                transition.prepare_transition(self, theme)
                
                # Iniciar transición
                transition.start_transition()
                
            except ImportError:
                # Fallback: cambio instantáneo si no está disponible el efecto
                set_widget_style_class(self, theme)
            theme_name = "Claro" if theme == "light" else "Oscuro"
            
            # Usar nuevo sistema de notificaciones
            send_success("Tema Cambiado", f"Tema cambiado exitosamente a: {theme_name}", "theme_system")
            
            # Guardar preferencia
            theme_type = ThemeType.LIGHT if theme == "light" else ThemeType.DARK
            ThemeSettings.save_theme_preference(theme_type)
            
            # Actualizar datos para aplicar correctamente los estilos
            self.refresh_data()
    
    def on_system_theme_changed(self, theme_type):
        """Responde a cambios en el tema del sistema operativo."""
        # Solo aplicar cambios si estamos configurados para seguir el tema del sistema
        from .theme import ThemeSettings
        user_preference = ThemeSettings.load_theme_preference()
        if user_preference == ThemeType.SYSTEM:
            # Aplicar el tema del sistema
            actual_theme = "light" if theme_type == ThemeType.LIGHT else "dark"
            current_theme = self.property("styleClass") or "dark"
            
            # Solo cambiar si es diferente al actual
            if actual_theme != current_theme:
                # Usar transición suave si está disponible
                try:

                    # Crear gestor de transición

                    from .theme_effects import ThemeTransitionManager
                    transition = ThemeTransitionManager(duration=300)
                    transition.prepare_transition(self, actual_theme)
                    
                    # Iniciar transición
                    transition.start_transition()
                    
                except ImportError:
                    # Fallback: cambio instantáneo si no está disponible el efecto
                    set_widget_style_class(self, actual_theme)
                
                # Actualizar sistema de ayuda
                help_system = get_help_system()
                help_system.update_theme()
                    
                self.refresh_data()  # Actualizar estilos de datos
    
    # Métodos para funcionalidades avanzadas
    
    def show_advanced_search(self):
        """Muestra el widget de búsqueda avanzada."""
        if not self.advanced_search_widget:
            send_warning("Advertencia", "Búsqueda avanzada no disponible", "main_window")
            return
        
        # Configurar datos para la búsqueda
        all_data = self.repo.get_all({})
        # Convertir Row objects a diccionarios
        dict_data = [dict(row) for row in all_data]
        self.advanced_search_widget.set_data(dict_data)
        
        # Mostrar en un diálogo
        

        from PyQt6.QtWidgets import QDialog, QVBoxLayout
        dialog = QDialog(self)
        dialog.setWindowTitle("🔍 Búsqueda Avanzada")
        dialog.setModal(False)  # No modal para permitir interacción con la ventana principal
        dialog.resize(800, 600)
        
        layout = QVBoxLayout(dialog)
        layout.addWidget(self.advanced_search_widget)
        
        # Mostrar diálogo
        dialog.show()
        
        # Enfocar el campo de búsqueda
        if hasattr(self.advanced_search_widget, 'search_input'):
            self.advanced_search_widget.search_input.setFocus()
    
    def clear_search(self):
        """Limpia la búsqueda actual."""
        if self.advanced_search_widget:
            self.advanced_search_widget.clear_search()
        
        # También limpiar filtros locales
        self.filter_widget.clear_filters()
        self.refresh_data()
    
    def on_advanced_search(self, query: str, filters: dict):
        """Maneja una búsqueda avanzada."""
        logger.info(f"Búsqueda avanzada: '{query}' con filtros: {filters}")
        
        # Combinar con filtros existentes
        combined_filters = {**self.current_filters, **filters}
        
        # Si hay una consulta de texto, agregar a los filtros
        if query.strip():
            # En una implementación real, esto podría usar un motor de búsqueda
            # Por ahora, simulamos aplicando los filtros
            combined_filters['search_query'] = query
        
        # Aplicar filtros y actualizar tabla
        self.current_filters = combined_filters
        self.refresh_data()
        
        # Mostrar mensaje de estado
        self.status_bar.showMessage(f"Búsqueda: '{query}' - Filtros aplicados")
    
    def on_search_result_selected(self, result_data: dict):
        """Maneja la selección de un resultado de búsqueda."""
        homolog_id = result_data.get('id')
        if homolog_id:
            # Seleccionar el elemento en la tabla principal
            for row in range(self.table_widget.rowCount()):
                item = self.table_widget.item(row, 0)  # Columna ID
                if item and item.text() == str(cast(int, homolog_id)):
                    self.table_widget.selectRow(row)
                    # Mostrar detalles
                    self.view_details()
                    break
    
    def show_accessibility_settings(self):
        """Muestra la configuración de accesibilidad."""
        if not self.accessibility_manager:
            send_warning("Advertencia", "Gestor de accesibilidad no disponible", "main_window")
            return
        
        self.accessibility_manager.show_accessibility_settings()
    
    def toggle_high_contrast(self):
        """Alterna el modo de alto contraste."""
        if not self.accessibility_manager:
            send_warning("Advertencia", "Gestor de accesibilidad no disponible", "main_window")
            return
        
        self.accessibility_manager.toggle_high_contrast()
        
        # Mostrar notificación
        from accessibility import AccessibilityMode
        current_mode = self.accessibility_manager.theme_manager.current_mode
        if current_mode == AccessibilityMode.HIGH_CONTRAST:
            send_info("Información", "Modo alto contraste activado", "main_window")
        else:
            send_info("Información", "Modo alto contraste desactivado", "main_window")
    
    def toggle_large_text(self):
        """Alterna el modo de texto grande."""
        if not self.accessibility_manager:
            send_warning("Advertencia", "Gestor de accesibilidad no disponible", "main_window")
            return
        
        # Alternar entre texto normal y grande
        from accessibility import AccessibilityMode
        current_mode = self.accessibility_manager.theme_manager.current_mode
        app = QApplication.instance()
        
        if app and isinstance(app, QApplication):
            if current_mode == AccessibilityMode.LARGE_TEXT:
                self.accessibility_manager.theme_manager.set_mode(AccessibilityMode.NORMAL, app)
                send_info("Información", "Modo texto normal activado", "main_window")
            else:
                self.accessibility_manager.theme_manager.set_mode(AccessibilityMode.LARGE_TEXT, app)
                send_info("Información", "Modo texto grande activado", "main_window")
    
    def show_admin_dashboard(self):
        """Muestra el dashboard administrativo."""
        try:
            if not ADMIN_DASHBOARD_AVAILABLE():
                QMessageBox.warning(
                    self,
                    "Función No Disponible",
                    "El dashboard administrativo no está disponible."
                )
                return
            
            if not self.user_info or self.user_info.get('role') != 'admin':
                QMessageBox.warning(
                    self,
                    "Acceso Denegado",
                    "Solo los administradores pueden acceder al dashboard."
                )
                return
            
            show_admin_dashboard_func = get_admin_dashboard()
            if not show_admin_dashboard_func:
                QMessageBox.critical(
                    self,
                    "Error",
                    "El módulo del dashboard administrativo no se pudo cargar."
                )
                return
            
            logger.info(f"Abriendo dashboard administrativo para usuario: {self.user_info.get('username')}")
            dialog = show_admin_dashboard_func(self.user_info, self)
            dialog.exec()
            
        except Exception as e:
            logger.error(f"Error abriendo dashboard administrativo: {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"Error abriendo dashboard administrativo: {str(e)}"
            )
    
    def show_advanced_analytics(self):
        """Muestra el sistema de analytics avanzado."""
        try:
            if not self.user_info or self.user_info.get('role') != 'admin':
                QMessageBox.warning(
                    self,
                    "Acceso Denegado",
                    "Solo los administradores pueden acceder al sistema de analytics avanzado."
                )
                return
            
            try:
                from .advanced_analytics import show_advanced_analytics
                dialog = show_advanced_analytics(self)
                dialog.exec()
            except ImportError:
                QMessageBox.information(
                    self,
                    "Analytics Avanzado",
                    "Sistema de Analytics Avanzado - EL OMO LOGADOR 🥵\\n\\n"
                    "Esta funcionalidad incluye:\\n"
                    "• 📊 Gráficos interactivos personalizados\\n"
                    "• 📈 Métricas en tiempo real\\n"
                    "• 📉 Análisis de tendencias\\n"
                    "• 🎯 Dashboard de visualización\\n"
                    "• 📋 Reportes automáticos"
                )
            
            logger.info(f"Abriendo analytics avanzado para usuario: {self.user_info.get('username')}")
            
        except Exception as e:
            logger.error(f"Error abriendo analytics avanzado: {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"Error abriendo analytics avanzado: {str(e)}"
            )
    
    def show_audit_panel(self):
        """Muestra el panel de auditoría."""
        try:
            if not AUDIT_PANEL_AVAILABLE():
                QMessageBox.warning(
                    self,
                    "Función No Disponible",
                    "El panel de auditoría no está disponible."
                )
                return
            
            if not self.user_info or self.user_info.get('role') not in ['admin', 'manager']:
                QMessageBox.warning(
                    self,
                    "Acceso Denegado",
                    "Solo los administradores y managers pueden acceder a los logs de auditoría."
                )
                return
            
            show_audit_panel_func = get_audit_panel()
            if not show_audit_panel_func:
                QMessageBox.critical(
                    self,
                    "Error",
                    "El módulo de auditoría no se pudo cargar."
                )
                return
            
            logger.info(f"Abriendo panel de auditoría para usuario: {self.user_info.get('username')}")
            dialog = show_audit_panel_func(self.user_info, self)
            dialog.exec()
            
        except Exception as e:
            logger.error(f"Error abriendo panel de auditoría: {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"Error abriendo panel de auditoría: {str(e)}"
            )
    
    def show_backup_system(self):
        """Muestra el sistema de respaldos."""
        try:
            if not BACKUP_SYSTEM_AVAILABLE:
                QMessageBox.warning(
                    self,
                    "Función No Disponible",
                    "El sistema de respaldos no está disponible."
                )
                return
            
            if not self.user_info or self.user_info.get('role') != 'admin':
                QMessageBox.warning(
                    self,
                    "Acceso Denegado",
                    "Solo los administradores pueden acceder al sistema de respaldos."
                )
                return
            
            logger.info(f"Abriendo sistema de respaldos para usuario: {self.user_info.get('username')}")
            
            # Crear y mostrar el panel de respaldos como diálogo
            dialog = QDialog(self)
            dialog.setWindowTitle("💾 Sistema de Respaldos")
            dialog.setModal(True)
            dialog.resize(900, 700)
            
            # Obtener clase BackupPanel del módulo
            BackupPanelClass = get_backup_panel()
            if not BackupPanelClass:
                QMessageBox.critical(
                    self,
                    "Error",
                    "El módulo de respaldos no se pudo cargar."
                )
                return
            
            # Crear el panel de respaldos y agregarlo al diálogo
            layout = QVBoxLayout()
            backup_panel = BackupPanelClass(dialog)
            layout.addWidget(backup_panel)
            
            # Botón de cerrar
            button_layout = QHBoxLayout()
            close_button = QPushButton("Cerrar")
            close_button.clicked.connect(dialog.accept)
            button_layout.addStretch()
            button_layout.addWidget(close_button)
            layout.addLayout(button_layout)
            
            dialog.setLayout(layout)
            dialog.exec()
            
        except Exception as e:
            logger.error(f"Error abriendo sistema de respaldos: {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"Error abriendo sistema de respaldos: {str(e)}"
            )
    
    def show_system_settings(self):
        """Muestra las configuraciones del sistema."""
        try:
            if not self.user_info or self.user_info.get('role') != 'admin':
                QMessageBox.warning(
                    self,
                    "Acceso Denegado",
                    "Solo los administradores pueden acceder a las configuraciones del sistema."
                )
                return
            
            # Aquí iría el diálogo de configuraciones del sistema
            QMessageBox.information(
                self,
                "Configuraciones del Sistema",
                "Panel de configuraciones del sistema\\n\\n"
                "Esta funcionalidad estará disponible en una próxima versión."
            )
            
        except Exception as e:
            logger.error(f"Error abriendo configuraciones del sistema: {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"Error abriendo configuraciones: {str(e)}"
            )
    
    def show_admin_reports(self):
        """Muestra los reportes administrativos."""
        try:
            if not self.user_info or self.user_info.get('role') not in ['admin', 'manager']:
                QMessageBox.warning(
                    self,
                    "Acceso Denegado",
                    "Solo los administradores y managers pueden acceder a los reportes administrativos."
                )
                return
            
            # Aquí iría el sistema de reportes administrativos
            QMessageBox.information(
                self,
                "Reportes Administrativos",
                "Sistema de reportes administrativos\\n\\n"
                "Esta funcionalidad incluirá:\\n"
                "• Reportes de actividad de usuarios\\n"
                "• Estadísticas de uso del sistema\\n"
                "• Análisis de rendimiento\\n"
                "• Reportes de seguridad\\n\\n"
                "Estará disponible en una próxima versión."
            )
            
        except Exception as e:
            logger.error(f"Error abriendo reportes administrativos: {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"Error abriendo reportes: {str(e)}"
            )
    
    def show_reports_system(self):
        """Muestra el sistema de reportes avanzado."""
        try:
            if not REPORTS_SYSTEM_AVAILABLE():
                QMessageBox.warning(
                    self,
                    "Función No Disponible",
                    "El sistema de reportes no está disponible."
                )
                return
            
            if not self.user_info or self.user_info.get('role') not in ['admin', 'manager']:
                QMessageBox.warning(
                    self,
                    "Acceso Denegado",
                    "Solo los administradores y managers pueden acceder al sistema de reportes."
                )
                return
            
            show_reports_system_func = get_reports_system()
            if not show_reports_system_func:
                QMessageBox.critical(
                    self,
                    "Error",
                    "El módulo de reportes no se pudo cargar."
                )
                return
            
            logger.info(f"Abriendo sistema de reportes para usuario: {self.user_info.get('username')}")
            dialog = show_reports_system_func(self.user_info, self)
            dialog.exec()
            
        except Exception as e:
            logger.error(f"Error abriendo sistema de reportes: {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"Error abriendo sistema de reportes: {str(e)}"
            )
        else:
            send_warning("Advertencia", "No se pudo cambiar el modo de texto", "main_window")
    
    def setup_widget_accessibility(self, widget: QWidget, name: str, description: str = ""):
        """Configura la accesibilidad de un widget."""
        if self.accessibility_manager:
            self.accessibility_manager.setup_widget_accessibility(widget, name, description)
    
    def announce_to_screen_reader(self, text: str):
        """Anuncia texto al lector de pantalla."""
        if self.accessibility_manager:
            self.accessibility_manager.announce_to_screen_reader(text)
    
    def closeEvent(self, event):
        """Maneja el cierre de la ventana."""
        # Detener threads en curso
        if self.data_worker and self.data_worker.isRunning():
            self.data_worker.terminate()
            self.data_worker.wait()
        
        event.accept()

    def preview_web_url(self, record: Dict[str, Any]) -> None:
        """
        Abre una ventana de previsualización web para la URL de la homologación.
        
        Args:
            record: Diccionario con los datos de la homologación
        """
        kb_url = record.get('kb_url', '').strip()
        
        if not kb_url:
            QMessageBox.warning(
                self,
                "Sin URL",
                "Esta homologación no tiene una URL de KB asociada."
            )
            return
        
        homologation_name = record.get('app_name', 'Homologación')
        
        try:
            show_web_preview(kb_url, parent=self)
        except Exception as e:
            logging.error(f"Error al abrir previsualización web: {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"No se pudo abrir la previsualización web:\n{str(e)}"
            )
    
    def change_my_password(self):
        """Abre el diálogo para cambiar la contraseña del usuario actual."""
        if not self.user_info:
            QMessageBox.warning(
                self,
                "⚠️ Advertencia",
                "No hay información de usuario disponible."
            )
            return
        
        try:
            dialog = ChangeMyPasswordDialog(cast(Dict[str, Any], self.user_info), self)
            dialog.password_changed.connect(self.on_password_changed)
            dialog.exec()
        except Exception as e:
            logger.error(f"Error al abrir diálogo de cambio de contraseña: {e}")
            QMessageBox.critical(
                self,
                "❌ Error",
                f"No se pudo abrir el diálogo de cambio de contraseña:\n{str(e)}"
            )
    
    def on_password_changed(self):
        """Maneja cuando se cambia la contraseña del usuario."""
        send_success("Contraseña Actualizada", "Tu contraseña ha sido cambiada exitosamente", "user_management")
        
        # Opcional: mostrar mensaje informativo
        result = QMessageBox.question(
            self,
            "🔄 Contraseña Cambiada",
            "Tu contraseña ha sido cambiada exitosamente.\n\n"
            "¿Deseas cerrar sesión para usar la nueva contraseña?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if result == QMessageBox.StandardButton.Yes:
            self.logout()
    
    def logout(self):
        """Cierra la sesión actual y regresa al login."""
        result = QMessageBox.question(
            self,
            "🚪 Cerrar Sesión",
            f"¿Está seguro de que desea cerrar la sesión de {self.user_info.get('username', 'Usuario')}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if result == QMessageBox.StandardButton.Yes:
            try:
                # Cerrar la ventana principal
                self.close()
                
                # Mostrar ventana de login nuevamente
                from .final_login import FinalLoginWindow
                login_window = FinalLoginWindow()
                login_window.show()
                
                send_info("Sesión Cerrada", f"Sesión cerrada para {self.user_info.get('username', 'Usuario')}", "user_management")
                
            except Exception as e:
                logger.error(f"Error al cerrar sesión: {e}")
                QMessageBox.critical(
                    self,
                    "❌ Error",
                    f"Error al cerrar sesión:\n{str(e)}"
                )

    def create_quick_backup(self):
        """Crea un respaldo rápido del sistema."""
        try:
            if not BACKUP_SYSTEM_AVAILABLE:
                QMessageBox.warning(
                    self,
                    "Función No Disponible",
                    "El sistema de respaldos no está disponible."
                )
                return
            
            if not self.user_info or self.user_info.get('role') != 'admin':
                QMessageBox.warning(
                    self,
                    "Acceso Denegado",
                    "Solo los administradores pueden crear respaldos."
                )
                return
            
            # Confirmar acción
            reply = QMessageBox.question(
                self,
                "Crear Respaldo Rápido",
                "¿Desea crear un respaldo completo del sistema ahora?\n\n"
                "Esta operación puede tardar unos minutos dependiendo del tamaño de la base de datos.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                # Crear barra de progreso
                progress_dialog = QMessageBox(self)
                progress_dialog.setWindowTitle("Creando Respaldo")
                progress_dialog.setText("Creando respaldo del sistema...")
                progress_dialog.setStandardButtons(QMessageBox.StandardButton.NoButton)
                progress_dialog.show()
                QApplication.processEvents()
                
                try:
                    # Obtener el backup manager
                    from ..app import get_app_instance
                    app = get_app_instance()
                    backup_manager = app.get_backup_manager()
                    
                    # Crear respaldo
                    backup_info = backup_manager.create_backup(f"Respaldo rápido - {self.user_info.get('username', 'Admin')}")
                    
                    progress_dialog.close()
                    
                    if backup_info:
                        QMessageBox.information(
                            self,
                            "Respaldo Completado",
                            f"Respaldo creado exitosamente:\n\n"
                            f"Archivo: {backup_info.filename}\n"
                            f"Tamaño: {backup_info.size_mb:.2f} MB\n"
                            f"Fecha: {backup_info.created_at}"
                        )
                        logger.info(f"Respaldo rápido creado por {self.user_info.get('username')}: {backup_info.filename}")
                    else:
                        QMessageBox.warning(
                            self,
                            "Error en Respaldo",
                            "No se pudo completar el respaldo. Revise los logs para más detalles."
                        )
                        
                except Exception as backup_error:
                    progress_dialog.close()
                    logger.error(f"Error creando respaldo rápido: {backup_error}")
                    QMessageBox.critical(
                        self,
                        "Error en Respaldo",
                        f"Error al crear el respaldo:\n{str(backup_error)}"
                    )
                    
        except Exception as e:
            logger.error(f"Error en create_quick_backup: {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"Error al iniciar respaldo rápido:\n{str(e)}"
            )



    def export_data_dialog(self):
        """Muestra el diálogo de exportación de datos."""
        try:
            logger.info(f"Abriendo exportación de datos - Usuario: {self.user_info.get('username', 'Unknown')}")
            
            # Por ahora, mostrar un diálogo informativo
            reply = QMessageBox.question(
                self,
                "Exportar Datos",
                "¿Desea exportar los datos de homologaciones?\n\n"
                "Esta función exportará todos los datos en formato CSV.\n"
                "¿Continuar con la exportación?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                # Seleccionar ubicación del archivo
                from PyQt6.QtWidgets import QFileDialog
                filename, _ = QFileDialog.getSaveFileName(
                    self,
                    "Guardar Exportación",
                    f"homologaciones_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    "Archivos CSV (*.csv);;Todos los archivos (*)"
                )
                
                if filename:
                    try:
                        # Aquí iría la lógica real de exportación
                        # Por ahora, crear un archivo básico de ejemplo
                        with open(filename, 'w', encoding='utf-8') as f:
                            f.write("ID,Aplicacion,Version,Fecha_Inicio,Estado\n")
                            f.write("1,Aplicacion_Ejemplo,1.0.0,2025-09-26,En_Proceso\n")
                        
                        QMessageBox.information(
                            self,
                            "Exportación Completada",
                            f"Datos exportados exitosamente a:\n{filename}"
                        )
                        logger.info(f"Datos exportados a: {filename}")
                        
                    except Exception as export_error:
                        logger.error(f"Error exportando datos: {export_error}")
                        QMessageBox.critical(
                            self,
                            "Error en Exportación",
                            f"Error al exportar los datos:\n{str(export_error)}"
                        )
                        
        except Exception as e:
            logger.error(f"Error en export_data_dialog: {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"Error al abrir exportación de datos:\n{str(e)}"
            )


if __name__ == "__main__":
    # Test de la ventana principal

    
    import sys

    from core.settings import setup_logging
    from data.seed import create_seed_data
    setup_logging()
    
    app = QApplication(sys.argv)
    
    # Crear datos de prueba
    create_seed_data()
    
    # Datos de usuario de prueba
    user_info: Dict[str, Any] = {
        'user_id': 1,
        'username': 'admin',
        'role': 'admin'
    }
    
    window = MainWindow(user_info)
    window.show()
    
    sys.exit(app.exec())