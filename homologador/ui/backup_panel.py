"""
Panel de gestión de respaldos para la aplicación Homologador.
"""


from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional
import os

from PyQt6.QtCore import QDateTime, Qt, QThread, QTimer, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QIcon, QPalette
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDateTimeEdit,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QInputDialog,
    QLabel,
    QLineEdit,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget)



from ..core.backup_system import BackupInfo, BackupManager, get_backup_manager
from .notification_system import (
    send_error,
    send_info,
    send_success,
    send_warning,
)
from .theme import DarkTheme

class BackupWorker(QThread):
    """Worker thread para operaciones de respaldo en background."""
    
    progress_updated = pyqtSignal(int, str)
    backup_completed = pyqtSignal(bool, str, str)  # success, message, filepath
    
    def __init__(self, backup_type: str, description: str):
        super().__init__()
        self.backup_type = backup_type
        self.description = description
        self.backup_manager = get_backup_manager()
    
    def run(self):
        """Ejecuta el respaldo en background."""
        try:
            # Conectar señales
            self.backup_manager.backup_progress.connect(self.progress_updated.emit)
            
            # Crear respaldo
            backup_info = self.backup_manager.create_backup(self.backup_type, self.description)
            
            if backup_info:
                self.backup_completed.emit(True, f"Respaldo creado: {backup_info.filename}", backup_info.filepath)
            else:
                self.backup_completed.emit(False, "Error creando respaldo", "")
                
        except Exception as e:
            self.backup_completed.emit(False, f"Error: {e}", "")


class RestoreWorker(QThread):
    """Worker thread para operaciones de restauración en background."""
    
    progress_updated = pyqtSignal(int, str)
    restore_completed = pyqtSignal(bool, str)
    
    def __init__(self, backup_info: BackupInfo, restore_database: bool, restore_config: bool):
        super().__init__()
        self.backup_info = backup_info
        self.restore_database = restore_database
        self.restore_config = restore_config
        self.backup_manager = get_backup_manager()
    
    def run(self):
        """Ejecuta la restauración en background."""
        try:
            # Conectar señales
            self.backup_manager.backup_progress.connect(self.progress_updated.emit)
            
            # Restaurar respaldo
            success = self.backup_manager.restore_backup(
                self.backup_info, 
                self.restore_database, 
                self.restore_config
            )
            
            if success:
                self.restore_completed.emit(True, f"Respaldo restaurado desde {self.backup_info.filename}")
            else:
                self.restore_completed.emit(False, "Error restaurando respaldo")
                
        except Exception as e:
            self.restore_completed.emit(False, f"Error: {e}")


class BackupPanel(QWidget):
    """Panel principal de gestión de respaldos."""
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.backup_manager: BackupManager = get_backup_manager()
        self.backup_worker: Optional[BackupWorker] = None
        self.restore_worker: Optional[RestoreWorker] = None
        
        self.init_ui()
        self.load_backup_list()
        self.update_statistics()
        
        # Timer para actualizar la lista cada 5 minutos
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.load_backup_list)
        self.refresh_timer.start(300000)  # 5 minutos
    
    def init_ui(self):
        """Inicializa la interfaz de usuario."""
        layout = QVBoxLayout()
        
        # Título
        title = QLabel("💾 Sistema de Respaldos y Restauración")
        title_font = QFont("Arial", 16, QFont.Weight.Bold)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Tabs principales
        self.tab_widget = QTabWidget()
        
        # Tab 1: Gestión de Respaldos
        self.backup_tab = self.create_backup_tab()
        self.tab_widget.addTab(self.backup_tab, "🔄 Respaldos")
        
        # Tab 2: Configuración
        self.config_tab = self.create_config_tab()
        self.tab_widget.addTab(self.config_tab, "⚙️ Configuración")
        
        # Tab 3: Estadísticas
        self.stats_tab = self.create_statistics_tab()
        self.tab_widget.addTab(self.stats_tab, "📊 Estadísticas")
        
        layout.addWidget(self.tab_widget)
        self.setLayout(layout)
        
        # Aplicar tema
        DarkTheme.apply_to_widget(self)
    
    def create_backup_tab(self) -> QWidget:
        """Crea la pestaña de gestión de respaldos."""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Sección de acciones rápidas
        actions_group = QGroupBox("🚀 Acciones Rápidas")
        actions_layout = QHBoxLayout()
        
        self.create_backup_btn = QPushButton("📦 Crear Respaldo Manual")
        self.create_backup_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2d5aa0, stop:1 #1e3f73);
                color: white;
                font-weight: bold;
                padding: 8px 16px;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3d6ab0, stop:1 #2e4f83);
            }
        """)
        self.create_backup_btn.clicked.connect(self.create_manual_backup)
        
        self.refresh_btn = QPushButton("🔄 Actualizar Lista")
        self.refresh_btn.clicked.connect(self.load_backup_list)
        
        self.import_backup_btn = QPushButton("📥 Importar Respaldo")
        self.import_backup_btn.clicked.connect(self.import_backup)
        
        actions_layout.addWidget(self.create_backup_btn)
        actions_layout.addWidget(self.refresh_btn)
        actions_layout.addWidget(self.import_backup_btn)
        actions_layout.addStretch()
        
        actions_group.setLayout(actions_layout)
        layout.addWidget(actions_group)
        
        # Barra de progreso
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_label = QLabel()
        self.progress_label.setVisible(False)
        
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.progress_label)
        
        # Tabla de respaldos
        backup_group = QGroupBox("📋 Lista de Respaldos")
        backup_layout = QVBoxLayout()
        
        self.backup_table = QTableWidget()
        self.setup_backup_table()
        backup_layout.addWidget(self.backup_table)
        
        # Botones de acción para respaldos
        table_actions = QHBoxLayout()
        
        self.restore_btn = QPushButton("🔄 Restaurar Seleccionado")
        self.restore_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0d7377, stop:1 #14a085);
                color: white;
                font-weight: bold;
                padding: 6px 12px;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1d8387, stop:1 #24b095);
            }
        """)
        self.restore_btn.clicked.connect(self.restore_selected_backup)
        self.restore_btn.setEnabled(False)
        
        self.delete_btn = QPushButton("🗑️ Eliminar Seleccionado")
        self.delete_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #dc2626, stop:1 #b91c1c);
                color: white;
                font-weight: bold;
                padding: 6px 12px;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ef4444, stop:1 #dc2626);
            }
        """)
        self.delete_btn.clicked.connect(self.delete_selected_backup)
        self.delete_btn.setEnabled(False)
        
        self.export_btn = QPushButton("💾 Exportar Seleccionado")
        self.export_btn.clicked.connect(self.export_selected_backup)
        self.export_btn.setEnabled(False)
        
        table_actions.addWidget(self.restore_btn)
        table_actions.addWidget(self.delete_btn)
        table_actions.addWidget(self.export_btn)
        table_actions.addStretch()
        
        backup_layout.addLayout(table_actions)
        backup_group.setLayout(backup_layout)
        layout.addWidget(backup_group)
        
        tab.setLayout(layout)
        return tab
    
    def setup_backup_table(self):
        """Configura la tabla de respaldos."""
        headers = ["Archivo", "Fecha/Hora", "Tamaño", "Tipo", "Descripción", "Estado"]
        self.backup_table.setColumnCount(len(headers))
        self.backup_table.setHorizontalHeaderLabels(headers)
        
        # Configurar tamaños de columna
        header = self.backup_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        
        # Configurar selección
        self.backup_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.backup_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.backup_table.itemSelectionChanged.connect(self.on_backup_selection_changed)
    
    def create_config_tab(self) -> QWidget:
        """Crea la pestaña de configuración."""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Configuración de respaldos automáticos
        auto_group = QGroupBox("🤖 Respaldos Automáticos")
        auto_layout = QFormLayout()
        
        self.auto_backup_enabled = QCheckBox("Habilitar respaldos automáticos")
        self.auto_backup_enabled.setChecked(self.backup_manager.auto_backup_enabled)
        self.auto_backup_enabled.stateChanged.connect(self.on_auto_backup_toggled)
        
        self.backup_interval = QSpinBox()
        self.backup_interval.setRange(1, 168)  # 1 hora a 1 semana
        self.backup_interval.setValue(self.backup_manager.backup_interval_hours)
        self.backup_interval.setSuffix(" horas")
        self.backup_interval.valueChanged.connect(self.on_backup_interval_changed)
        
        auto_layout.addRow("Estado:", self.auto_backup_enabled)
        auto_layout.addRow("Intervalo:", self.backup_interval)
        auto_group.setLayout(auto_layout)
        layout.addWidget(auto_group)
        
        # Configuración de retención
        retention_group = QGroupBox("🗂️ Retención de Respaldos")
        retention_layout = QFormLayout()
        
        self.max_backups = QSpinBox()
        self.max_backups.setRange(5, 100)
        self.max_backups.setValue(self.backup_manager.max_backups)
        self.max_backups.valueChanged.connect(self.on_max_backups_changed)
        
        retention_layout.addRow("Máximo de respaldos:", self.max_backups)
        retention_group.setLayout(retention_layout)
        layout.addWidget(retention_group)
        
        # Configuración de directorio
        directory_group = QGroupBox("📁 Directorio de Respaldos")
        directory_layout = QVBoxLayout()
        
        dir_selection_layout = QHBoxLayout()
        self.backup_dir_label = QLabel(str(self.backup_manager.backup_dir))
        self.change_dir_btn = QPushButton("📂 Cambiar Directorio")
        self.change_dir_btn.clicked.connect(self.change_backup_directory)
        
        dir_selection_layout.addWidget(self.backup_dir_label)
        dir_selection_layout.addWidget(self.change_dir_btn)
        
        directory_layout.addLayout(dir_selection_layout)
        directory_group.setLayout(directory_layout)
        layout.addWidget(directory_group)
        
        # Botones de configuración
        config_actions = QHBoxLayout()
        
        self.save_config_btn = QPushButton("💾 Guardar Configuración")
        self.save_config_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #059669, stop:1 #047857);
                color: white;
                font-weight: bold;
                padding: 8px 16px;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #10b981, stop:1 #059669);
            }
        """)
        self.save_config_btn.clicked.connect(self.save_configuration)
        
        config_actions.addWidget(self.save_config_btn)
        config_actions.addStretch()
        
        layout.addLayout(config_actions)
        layout.addStretch()
        
        tab.setLayout(layout)
        return tab
    
    def create_statistics_tab(self) -> QWidget:
        """Crea la pestaña de estadísticas."""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Estadísticas generales
        general_group = QGroupBox("📊 Estadísticas Generales")
        general_layout = QFormLayout()
        
        self.total_backups_label = QLabel("0")
        self.total_size_label = QLabel("0.00 MB")
        self.latest_backup_label = QLabel("Nunca")
        self.auto_backups_label = QLabel("0")
        self.manual_backups_label = QLabel("0")
        
        general_layout.addRow("Total de respaldos:", self.total_backups_label)
        general_layout.addRow("Tamaño total:", self.total_size_label)
        general_layout.addRow("Último respaldo:", self.latest_backup_label)
        general_layout.addRow("Respaldos automáticos:", self.auto_backups_label)
        general_layout.addRow("Respaldos manuales:", self.manual_backups_label)
        
        general_group.setLayout(general_layout)
        layout.addWidget(general_group)
        
        # Estado del sistema
        system_group = QGroupBox("💻 Estado del Sistema")
        system_layout = QFormLayout()
        
        self.backup_status_label = QLabel()
        self.next_backup_label = QLabel()
        self.disk_space_label = QLabel()
        
        system_layout.addRow("Estado de respaldos:", self.backup_status_label)
        system_layout.addRow("Próximo respaldo:", self.next_backup_label)
        system_layout.addRow("Espacio en disco:", self.disk_space_label)
        
        system_group.setLayout(system_layout)
        layout.addWidget(system_group)
        
        layout.addStretch()
        tab.setLayout(layout)
        return tab
    
    def load_backup_list(self):
        """Carga la lista de respaldos en la tabla."""
        try:
            backups = self.backup_manager.list_backups()
            
            self.backup_table.setRowCount(len(backups))
            
            for row, backup in enumerate(backups):
                # Archivo
                self.backup_table.setItem(row, 0, QTableWidgetItem(backup.filename))
                
                # Fecha/Hora
                date_str = backup.timestamp.strftime("%d/%m/%Y %H:%M")
                self.backup_table.setItem(row, 1, QTableWidgetItem(date_str))
                
                # Tamaño
                size_str = f"{backup.size_mb:.2f} MB"
                self.backup_table.setItem(row, 2, QTableWidgetItem(size_str))
                
                # Tipo
                type_display = {
                    'manual': '👤 Manual',
                    'auto': '🤖 Automático',
                    'scheduled': '⏰ Programado',
                    'safety': '🛡️ Seguridad'
                }.get(backup.type, backup.type.title())
                
                self.backup_table.setItem(row, 3, QTableWidgetItem(type_display))
                
                # Descripción
                self.backup_table.setItem(row, 4, QTableWidgetItem(backup.description))
                
                # Estado (basado en la edad del backup)
                if backup.age_days == 0:
                    status = "🟢 Reciente"
                elif backup.age_days <= 7:
                    status = "🟡 1 semana"
                elif backup.age_days <= 30:
                    status = "🟠 1 mes"
                else:
                    status = "🔴 Antiguo"
                
                self.backup_table.setItem(row, 5, QTableWidgetItem(status))
                
                # Guardar backup info como data del item
                self.backup_table.item(row, 0).setData(Qt.ItemDataRole.UserRole, backup)
            
            send_info("Respaldos", f"Lista actualizada: {len(backups)} respaldos encontrados", "backup_system")
            
        except Exception as e:
            send_error("Error", f"Error cargando lista de respaldos: {e}", "backup_system")
    
    def update_statistics(self):
        """Actualiza las estadísticas de respaldos."""
        try:
            stats = self.backup_manager.get_backup_statistics()
            
            # Actualizar estadísticas generales
            self.total_backups_label.setText(str(stats.get('total_backups', 0)))
            self.total_size_label.setText(f"{stats.get('total_size_mb', 0):.2f} MB")
            self.auto_backups_label.setText(str(stats.get('auto_backups', 0)))
            self.manual_backups_label.setText(str(stats.get('manual_backups', 0)))
            
            # Último respaldo
            latest = stats.get('latest_backup')
            if latest:
                latest_str = latest.timestamp.strftime("%d/%m/%Y %H:%M")
                self.latest_backup_label.setText(latest_str)
            else:
                self.latest_backup_label.setText("Nunca")
            
            # Estado del sistema
            if self.backup_manager.auto_backup_enabled:
                self.backup_status_label.setText("🟢 Activo")
                
                # Calcular próximo respaldo
                if latest:
                    next_backup = latest.timestamp + timedelta(hours=self.backup_manager.backup_interval_hours)
                    next_str = next_backup.strftime("%d/%m/%Y %H:%M")
                    self.next_backup_label.setText(next_str)
                else:
                    self.next_backup_label.setText("Próximo")
            else:
                self.backup_status_label.setText("🔴 Inactivo")
                self.next_backup_label.setText("N/A")
            
            # Espacio en disco
            try:
                import shutil
                total, used, free = shutil.disk_usage(self.backup_manager.backup_dir)
                free_mb = free / (1024 * 1024)
                self.disk_space_label.setText(f"{free_mb:.0f} MB disponibles")
            except:
                self.disk_space_label.setText("No disponible")
                
        except Exception as e:
            send_error("Error", f"Error actualizando estadísticas: {e}", "backup_system")
    
    def on_backup_selection_changed(self):
        """Maneja cambios en la selección de respaldos."""
        selected_items = self.backup_table.selectedItems()
        has_selection = len(selected_items) > 0
        
        self.restore_btn.setEnabled(has_selection)
        self.delete_btn.setEnabled(has_selection)
        self.export_btn.setEnabled(has_selection)
    
    def get_selected_backup(self) -> Optional[BackupInfo]:
        """Obtiene el respaldo seleccionado."""
        current_row = self.backup_table.currentRow()
        if current_row >= 0:
            item = self.backup_table.item(current_row, 0)
            if item:
                return item.data(Qt.ItemDataRole.UserRole)
        return None
    
    def create_manual_backup(self):
        """Crea un respaldo manual."""
        try:
            # Diálogo para descripción
            description, ok = QInputDialog.getText(
                self,
                "Respaldo Manual",
                "Descripción del respaldo (opcional):",
                text="Respaldo manual"
            )
            
            if not ok:
                return
            
            # Crear worker thread
            self.backup_worker = BackupWorker("manual", description)
            self.backup_worker.progress_updated.connect(self.update_progress)
            self.backup_worker.backup_completed.connect(self.on_backup_completed)
            
            # Mostrar barra de progreso
            self.show_progress("Creando respaldo manual...")
            
            # Iniciar respaldo
            self.backup_worker.start()
            
            send_info("Respaldos", "Iniciando respaldo manual...", "backup_system")
            
        except Exception as e:
            send_error("Error", f"Error iniciando respaldo: {e}", "backup_system")
    
    def restore_selected_backup(self):
        """Restaura el respaldo seleccionado."""
        backup = self.get_selected_backup()
        if not backup:
            return
        
        try:
            # Diálogo de confirmación con opciones
            dialog = QDialog(self)
            dialog.setWindowTitle("Restaurar Respaldo")
            dialog.setModal(True)
            
            layout = QVBoxLayout()
            
            layout.addWidget(QLabel(f"¿Restaurar respaldo '{backup.filename}'?"))
            layout.addWidget(QLabel(""))
            layout.addWidget(QLabel("⚠️ ADVERTENCIA: Esta acción reemplazará los datos actuales."))
            layout.addWidget(QLabel("Se creará un respaldo de seguridad automáticamente."))
            layout.addWidget(QLabel(""))
            
            # Opciones de restauración
            restore_db = QCheckBox("Restaurar base de datos")
            restore_db.setChecked(True)
            restore_config = QCheckBox("Restaurar configuración")
            restore_config.setChecked(False)
            
            layout.addWidget(restore_db)
            layout.addWidget(restore_config)
            
            buttons = QDialogButtonBox(
                QDialogButtonBox.StandardButton.Yes | QDialogButtonBox.StandardButton.No
            )
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)
            layout.addWidget(buttons)
            
            dialog.setLayout(layout)
            
            if dialog.exec() == QDialog.DialogCode.Accepted:
                # Crear worker thread
                self.restore_worker = RestoreWorker(
                    backup, 
                    restore_db.isChecked(),
                    restore_config.isChecked()
                )
                self.restore_worker.progress_updated.connect(self.update_progress)
                self.restore_worker.restore_completed.connect(self.on_restore_completed)
                
                # Mostrar barra de progreso
                self.show_progress("Restaurando respaldo...")
                
                # Iniciar restauración
                self.restore_worker.start()
                
                send_info("Respaldos", f"Iniciando restauración de {backup.filename}...", "backup_system")
            
        except Exception as e:
            send_error("Error", f"Error iniciando restauración: {e}", "backup_system")
    
    def delete_selected_backup(self):
        """Elimina el respaldo seleccionado."""
        backup = self.get_selected_backup()
        if not backup:
            return
        
        try:
            reply = QMessageBox.question(
                self,
                "Eliminar Respaldo",
                f"¿Está seguro de eliminar el respaldo '{backup.filename}'?\n\n"
                f"Esta acción no se puede deshacer.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                if self.backup_manager.delete_backup(backup):
                    send_success("Respaldos", f"Respaldo {backup.filename} eliminado exitosamente", "backup_system")
                    self.load_backup_list()
                    self.update_statistics()
                else:
                    send_error("Error", f"No se pudo eliminar el respaldo {backup.filename}", "backup_system")
            
        except Exception as e:
            send_error("Error", f"Error eliminando respaldo: {e}", "backup_system")
    
    def export_selected_backup(self):
        """Exporta el respaldo seleccionado."""
        backup = self.get_selected_backup()
        if not backup:
            return
        
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Exportar Respaldo",
                backup.filename,
                "Archivos ZIP (*.zip);;Todos los archivos (*)"
            )
            
            if file_path:
                import shutil
                shutil.copy2(backup.filepath, file_path)
                send_success("Respaldos", f"Respaldo exportado a {file_path}", "backup_system")
            
        except Exception as e:
            send_error("Error", f"Error exportando respaldo: {e}", "backup_system")
    
    def import_backup(self):
        """Importa un respaldo externo."""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Importar Respaldo",
                "",
                "Archivos ZIP (*.zip);;Todos los archivos (*)"
            )
            
            if file_path:

                # Copiar archivo al directorio de respaldos

                import shutil
                filename = Path(file_path).name
                destination = self.backup_manager.backup_dir / filename
                
                shutil.copy2(file_path, destination)
                
                send_success("Respaldos", f"Respaldo {filename} importado exitosamente", "backup_system")
                self.load_backup_list()
                self.update_statistics()
            
        except Exception as e:
            send_error("Error", f"Error importando respaldo: {e}", "backup_system")
    
    def show_progress(self, message: str):
        """Muestra la barra de progreso."""
        self.progress_bar.setVisible(True)
        self.progress_label.setVisible(True)
        self.progress_label.setText(message)
        self.progress_bar.setValue(0)
    
    def hide_progress(self):
        """Oculta la barra de progreso."""
        self.progress_bar.setVisible(False)
        self.progress_label.setVisible(False)
    
    def update_progress(self, value: int, message: str):
        """Actualiza la barra de progreso."""
        self.progress_bar.setValue(value)
        self.progress_label.setText(message)
    
    def on_backup_completed(self, success: bool, message: str, filepath: str):
        """Maneja la finalización de un respaldo."""
        self.hide_progress()
        
        if success:
            send_success("Respaldos", message, "backup_system")
            self.load_backup_list()
            self.update_statistics()
        else:
            send_error("Error", message, "backup_system")
        
        if self.backup_worker:
            self.backup_worker.quit()
            self.backup_worker.wait()
            self.backup_worker = None
    
    def on_restore_completed(self, success: bool, message: str):
        """Maneja la finalización de una restauración."""
        self.hide_progress()
        
        if success:
            send_success("Respaldos", message, "backup_system")
            
            # Mostrar mensaje sobre reinicio
            QMessageBox.information(
                self,
                "Restauración Completada",
                "El respaldo se restauró exitosamente.\n\n"
                "Se recomienda reiniciar la aplicación para asegurar\n"
                "que todos los cambios se apliquen correctamente."
            )
        else:
            send_error("Error", message, "backup_system")
        
        if self.restore_worker:
            self.restore_worker.quit()
            self.restore_worker.wait()
            self.restore_worker = None
    
    def on_auto_backup_toggled(self, state):
        """Maneja el cambio de estado de respaldos automáticos."""
        enabled = state == Qt.CheckState.Checked.value
        self.backup_manager.auto_backup_enabled = enabled
        
        if enabled:
            self.backup_manager.start_auto_backup_schedule()
            send_info("Respaldos", "Respaldos automáticos habilitados", "backup_system")
        else:
            self.backup_manager.stop_auto_backup_schedule()
            send_warning("Respaldos", "Respaldos automáticos deshabilitados", "backup_system")
        
        self.update_statistics()
    
    def on_backup_interval_changed(self, value):
        """Maneja el cambio de intervalo de respaldos."""
        self.backup_manager.backup_interval_hours = value
        
        if self.backup_manager.auto_backup_enabled:
            self.backup_manager.start_auto_backup_schedule()
        
        self.update_statistics()
    
    def on_max_backups_changed(self, value):
        """Maneja el cambio de máximo de respaldos."""
        self.backup_manager.max_backups = value
    
    def change_backup_directory(self):
        """Cambia el directorio de respaldos."""
        try:
            new_dir = QFileDialog.getExistingDirectory(
                self,
                "Seleccionar Directorio de Respaldos",
                str(self.backup_manager.backup_dir)
            )
            
            if new_dir:
                new_path = Path(new_dir)
                self.backup_manager.backup_dir = new_path
                self.backup_dir_label.setText(str(new_path))
                
                send_info("Respaldos", f"Directorio cambiado a {new_path}", "backup_system")
            
        except Exception as e:
            send_error("Error", f"Error cambiando directorio: {e}", "backup_system")
    
    def save_configuration(self):
        """Guarda la configuración actual."""
        try:
            # Actualizar settings
            settings = self.backup_manager.settings
            settings.config['auto_backup'] = self.auto_backup_enabled.isChecked()
            settings.config['backup_interval_hours'] = self.backup_interval.value()
            settings.config['backup_retention_days'] = self.max_backups.value()
            settings.config['backups_dir'] = str(self.backup_manager.backup_dir)
            
            send_success("Configuración", "Configuración de respaldos guardada exitosamente", "backup_system")
            
        except Exception as e:
            send_error("Error", f"Error guardando configuración: {e}", "backup_system")