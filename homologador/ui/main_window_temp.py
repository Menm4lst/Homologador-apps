"""
Ventana principal del Homologador de Aplicaciones.
Interfaz principal con tabla de homologaciones, filtros y gestión según roles.
"""

import csv
import logging
import sys
from datetime import date, datetime
from typing import Any, Dict, List, Optional

from ..core.storage import get_audit_repository, get_homologation_repository
from ..data.seed import get_auth_service
from PyQt6.QtCore import QDate, Qt, QThread, QTimer, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QAction, QFont, QIcon
from PyQt6.QtWidgets import (QAbstractItemView, QApplication, QComboBox,
                             QDateEdit, QFileDialog, QFormLayout, QFrame,
                             QGridLayout, QGroupBox, QHBoxLayout, QHeaderView,
                             QLabel, QLineEdit, QMainWindow, QMenuBar,
                             QMessageBox, QProgressBar, QPushButton,
                             QSizePolicy, QSpacerItem, QSplitter, QStatusBar,
                             QTableWidget, QTableWidgetItem, QToolBar,
                             QVBoxLayout, QWidget)

from .details_view import show_homologation_details
from .homologation_form import HomologationFormDialog
from .theme import set_widget_style_class

logger = logging.getLogger(__name__)


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
    """Widget personalizado para la tabla de homologaciones."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.record_data = []  # Almacena datos completos de cada registro
        self.setup_table()
    
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
        self.setSortingEnabled(True)
        
        # Deshabilitar edición
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
    
    def load_data(self, data_rows):
        """Carga datos en la tabla."""
        self.record_data = list(data_rows)  # Guardar copia de datos completos
        self.setRowCount(len(data_rows))
        
        for row_idx, row_data in enumerate(data_rows):
            # ID
            self.setItem(row_idx, 0, QTableWidgetItem(str(row_data['id'])))
            
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
                    updated_item.setData(Qt.ItemDataRole.UserRole, row_data['updated_at'])
                except (ValueError, TypeError):
                    updated_item.setText(str(row_data.get('updated_at', '')))
            self.setItem(row_idx, 6, updated_item)
        
        self.resizeColumnsToContents()
        
    def clear_data(self):
        """Limpia los datos de la tabla."""
        self.record_data = []
        self.setRowCount(0)
    
    def get_selected_record(self):
        """Obtiene el registro seleccionado completo."""
        selected_rows = []
        selection_model = self.selectionModel()
        if selection_model:
            selected_rows = selection_model.selectedRows()
        if not selected_rows:
            return None
            
        row_index = selected_rows[0].row()
        if 0 <= row_index < len(self.record_data):
            return self.record_data[row_index]
            
        return None
        

class FilterWidget(QFrame):
    """Widget para filtros de búsqueda."""
    
    filter_changed = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setup_ui()
    
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


class MainWindow(QMainWindow):
    """Ventana principal del Homologador."""
    
    def __init__(self, user_info=None):
        super().__init__()
        self.user_info = user_info
        self.repo = get_homologation_repository()
        self.audit_repo = get_audit_repository()
        self.data_worker = None
        self.current_filters = {}
        
        self.setup_ui()
        self.setup_actions()
        self.setup_signals()
        
        # Cargar datos iniciales
        self.refresh_data()
        
    def setup_ui(self):
        """Configura la interfaz de usuario."""
        self.setWindowTitle("Homologador de Aplicaciones")
        self.resize(1200, 700)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Splitter para dividir filtros y tabla
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Panel de filtros (izquierda)
        self.filter_widget = FilterWidget()
        self.filter_widget.filter_changed.connect(self.on_filter_changed)
        splitter.addWidget(self.filter_widget)
        
        # Tabla de homologaciones (derecha)
        self.table_widget = HomologationTableWidget()
        self.table_widget.doubleClicked.connect(self.on_table_double_click)
        splitter.addWidget(self.table_widget)
        
        # Establecer proporciones iniciales
        splitter.setSizes([int(self.width() * 0.25), int(self.width() * 0.75)])
        
        main_layout.addWidget(splitter)
        
        # Barra de botones
        button_layout = QHBoxLayout()
        
        # Botones según rol
        is_admin = self.user_info and self.user_info.get('role') == 'admin'
        is_editor = is_admin or (self.user_info and self.user_info.get('role') == 'editor')
        
        if is_editor:
            new_button = QPushButton("Nueva Homologación")
            new_button.clicked.connect(self.new_homologation)
            button_layout.addWidget(new_button)
            
            edit_button = QPushButton("Editar")
            edit_button.clicked.connect(self.edit_homologation)
            button_layout.addWidget(edit_button)
            
            if is_admin:
                delete_button = QPushButton("Eliminar")
                delete_button.clicked.connect(self.delete_homologation)
                button_layout.addWidget(delete_button)
        
        details_button = QPushButton("Ver Detalles")
        details_button.clicked.connect(self.view_details)
        button_layout.addWidget(details_button)
        
        # Espaciador
        button_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        
        # Botón de actualizar
        refresh_button = QPushButton("Actualizar")
        refresh_button.clicked.connect(self.refresh_data)
        button_layout.addWidget(refresh_button)
        
        # Botón de exportar
        export_button = QPushButton("Exportar")
        export_button.clicked.connect(self.export_data)
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
        
        # Menú Archivo
        file_menu = menubar.addMenu('&Archivo')
        
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
        
        refresh_action = QAction("Actualizar", self)
        refresh_action.setShortcut("F5")
        refresh_action.triggered.connect(self.refresh_data)
        view_menu.addAction(refresh_action)
        
        # Menú Ayuda
        help_menu = menubar.addMenu('A&yuda')
        
        about_action = QAction("Acerca de", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def setup_toolbar(self):
        """Configura la barra de herramientas."""
        toolbar = QToolBar("Barra Principal")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        
        # TODO: Agregar iconos y acciones a la barra
    
    def setup_actions(self):
        """Configura acciones adicionales."""
        pass
    
    def setup_signals(self):
        """Conecta señales y slots."""
        pass
    
    def on_filter_changed(self, filters):
        """Maneja cambios en los filtros."""
        self.current_filters = filters
        self.refresh_data()
    
    def on_table_double_click(self):
        """Maneja doble clic en la tabla."""
        self.view_details()
    
    def refresh_data(self):
        """Refresca los datos de la tabla."""
        self.apply_filters()
    
    def on_homologation_saved(self, homologation_id):
        """Maneja el evento cuando una homologación es guardada."""
        self.refresh_data()
        self.status_bar.showMessage(f"Homologación guardada con ID: {homologation_id}", 5000)
    
    def new_homologation(self):
        """Abre formulario para nueva homologación."""
        dialog = HomologationFormDialog(self, user_info=self.user_info)
        dialog.homologation_saved.connect(self.on_homologation_saved)
        dialog.exec()
    
    def view_details(self):
        """Muestra detalles de la homologación seleccionada."""
        record = self.table_widget.get_selected_record()
        if not record:
            QMessageBox.warning(self, "Advertencia", "Seleccione una homologación")
            return
        
        dialog = show_homologation_details(self, homologation_data=dict(record), user_info=self.user_info)
        dialog.exec()
    
    def edit_homologation(self):
        """Edita la homologación seleccionada."""
        record = self.table_widget.get_selected_record()
        if not record:
            QMessageBox.warning(self, "Advertencia", "Seleccione una homologación")
            return
        
        dialog = HomologationFormDialog(self, homologation_data=dict(record), user_info=self.user_info)
        dialog.homologation_saved.connect(self.on_homologation_saved)
        dialog.exec()
    
    def delete_homologation(self):
        """Elimina la homologación seleccionada."""
        record = self.table_widget.get_selected_record()
        if not record:
            QMessageBox.warning(self, "Advertencia", "Seleccione una homologación")
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
                    self.status_bar.showMessage(f"Homologación eliminada: {record['real_name']}", 5000)
                    self.refresh_data()
                else:
                    QMessageBox.critical(self, "Error", "No se pudo eliminar la homologación")
            except Exception as e:
                logger.error(f"Error eliminando homologación: {e}")
                QMessageBox.critical(self, "Error", f"Error eliminando homologación: {str(e)}")
    
    def apply_filters(self):
        """Aplica filtros actuales y carga datos."""
        self.status_bar.showMessage("Cargando datos...")
        self.table_widget.clear_data()
        
        if self.data_worker and self.data_worker.isRunning():
            self.data_worker.terminate()
            self.data_worker.wait()
            
        self.data_worker = DataLoadWorker(self.repo, self.current_filters)
        self.data_worker.data_ready.connect(self.on_data_loaded)
        self.data_worker.error.connect(self.on_data_error)
        self.data_worker.start()
    
    def on_data_loaded(self, data):
        """Maneja datos cargados exitosamente."""
        self.table_widget.load_data(data)
        count = len(data)
        plural = "s" if count != 1 else ""
        self.status_bar.showMessage(f"{count} homologación{plural} encontrada{plural}")
    
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
    
    def closeEvent(self, event):
        """Maneja el cierre de la ventana."""
        # Detener threads en curso
        if self.data_worker and self.data_worker.isRunning():
            self.data_worker.terminate()
            self.data_worker.wait()
        
        event.accept()


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
    user_info = {
        'user_id': 1,
        'username': 'admin',
        'role': 'admin'
    }
    
    window = MainWindow(user_info)
    window.show()
    
    sys.exit(app.exec())