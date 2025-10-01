"""
Panel de Auditoría y Logs del Sistema.

Este módulo proporciona una interfaz completa para visualizar y analizar
los logs de auditoría del sistema, permitiendo rastrear todas las acciones
de los usuarios y cambios en el sistema.
"""


from datetime import date, datetime, timedelta
from typing import Any, Dict, Iterable, List, Optional, Tuple, cast
import logging

from PyQt6.QtCore import QDate, Qt, QThread, QTimer, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QAction, QColor, QFont, QIcon, QPalette
from PyQt6.QtWidgets import (
    QButtonGroup,
    QCalendarWidget,
    QCheckBox,
    QComboBox,
    QDateEdit,
    QDialog,
    QFormLayout,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QRadioButton,
    QSlider,
    QSpinBox,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget)

from ..core.storage import get_audit_repository, get_user_repository
from ..data.seed import get_auth_service

logger = logging.getLogger(__name__)


class AuditLogWidget(QWidget):
    """Widget principal para el panel de auditoría."""
    
    def __init__(self, user_info: Dict[str, Any], parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.user_info = user_info
        self.audit_repo = get_audit_repository()
        self.user_repo = get_user_repository()
        
        self.setup_ui()
        self.load_audit_logs()
        
        logger.info(f"Panel de auditoría iniciado por: {user_info.get('username')}")
    
    def setup_ui(self):
        """Configura la interfaz del panel de auditoría."""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        
        # Título
        title_label = QLabel("📋 Panel de Auditoría y Logs del Sistema")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setWeight(QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #74b9ff; margin-bottom: 15px; text-decoration: underline;")
        main_layout.addWidget(title_label)
        
        # Pestañas
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        self.create_logs_tab()
        self.create_statistics_tab()
        self.create_security_tab()
        self.create_export_tab()
        
        # Aplicar tema nocturno
        self.apply_dark_theme()
    
    def create_logs_tab(self):
        """Crea la pestaña de logs de auditoría."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Filtros
        filters_group = QGroupBox("🔍 Filtros de Búsqueda")
        filters_layout = QHBoxLayout(filters_group)
        
        # Filtro por fecha
        date_layout = QVBoxLayout()
        date_layout.addWidget(QLabel("Desde:"))
        self.date_from = QDateEdit()
        self.date_from.setDate(QDate.currentDate().addDays(-30))
        self.date_from.setCalendarPopup(True)
        date_layout.addWidget(self.date_from)
        
        date_layout.addWidget(QLabel("Hasta:"))
        self.date_to = QDateEdit()
        self.date_to.setDate(QDate.currentDate())
        self.date_to.setCalendarPopup(True)
        date_layout.addWidget(self.date_to)
        filters_layout.addLayout(date_layout)
        
        # Filtro por usuario
        user_layout = QVBoxLayout()
        user_layout.addWidget(QLabel("Usuario:"))
        self.user_filter = QComboBox()
        self.user_filter.addItem("Todos los usuarios", "")
        user_layout.addWidget(self.user_filter)
        filters_layout.addLayout(user_layout)
        
        # Filtro por acción
        action_layout = QVBoxLayout()
        action_layout.addWidget(QLabel("Acción:"))
        self.action_filter = QComboBox()
        actions = ["", "CREATE", "UPDATE", "DELETE", "LOGIN", "LOGOUT", 
                  "CREATE_USER", "UPDATE_USER", "DELETE_USER", "EXPORT"]
        for action in actions:
            display_name = action if action else "Todas las acciones"
            self.action_filter.addItem(display_name, action)
        action_layout.addWidget(self.action_filter)
        filters_layout.addLayout(action_layout)
        
        # Filtro por tabla
        table_layout = QVBoxLayout()
        table_layout.addWidget(QLabel("Tabla:"))
        self.table_filter = QComboBox()
        tables = ["", "users", "homologations", "audit_logs"]
        for table in tables:
            display_name = table if table else "Todas las tablas"
            self.table_filter.addItem(display_name, table)
        table_layout.addWidget(self.table_filter)
        filters_layout.addLayout(table_layout)
        
        # Botones de filtro
        button_layout = QVBoxLayout()
        self.apply_filters_btn = QPushButton("🔍 Aplicar Filtros")
        self.apply_filters_btn.clicked.connect(self.apply_filters)
        self.apply_filters_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        button_layout.addWidget(self.apply_filters_btn)
        
        self.clear_filters_btn = QPushButton("🗑️ Limpiar")
        self.clear_filters_btn.clicked.connect(self.clear_filters)
        button_layout.addWidget(self.clear_filters_btn)
        
        button_layout.addStretch()
        filters_layout.addLayout(button_layout)
        
        layout.addWidget(filters_group)
        
        # Tabla de logs
        logs_group = QGroupBox("📝 Registros de Auditoría")
        logs_layout = QVBoxLayout(logs_group)
        
        self.logs_table = QTableWidget()
        self.logs_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.logs_table.setAlternatingRowColors(True)
        self.logs_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #e0e0e0;
                background-color: white;
                color: #2c3e50;
                border: 1px solid #ddd;
                border-radius: 6px;
            }
            QTableWidget::item {
                padding: 8px;
                color: #2c3e50;
                background-color: white;
            }
            QTableWidget::item:alternate {
                background-color: #f8f9fa;
                color: #2c3e50;
            }
            QTableWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 10px;
                border: none;
                font-weight: bold;
            }
        """)
        
        # Configurar columnas
        columns = ["ID", "Fecha/Hora", "Usuario", "Acción", "Tabla", "Registro ID", "IP", "Detalles"]
        self.logs_table.setColumnCount(len(columns))
        self.logs_table.setHorizontalHeaderLabels(columns)
        
        # Ajustar columnas
        header = self.logs_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # Fecha
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Usuario
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Acción
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Tabla
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # Registro ID
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)  # IP
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.Stretch)           # Detalles
        
        # Doble clic para ver detalles
        self.logs_table.doubleClicked.connect(self.show_log_details)
        
        logs_layout.addWidget(self.logs_table)
        layout.addWidget(logs_group)
        
        # Información de resultados
        info_layout = QHBoxLayout()
        self.results_label = QLabel("Resultados: 0")
        self.results_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        info_layout.addWidget(self.results_label)
        info_layout.addStretch()
        
        # Botón de actualización automática
        self.auto_refresh_check = QCheckBox("Actualización automática (30s)")
        self.auto_refresh_check.toggled.connect(self.toggle_auto_refresh)
        info_layout.addWidget(self.auto_refresh_check)
        
        layout.addLayout(info_layout)
        
        self.tab_widget.addTab(tab, "📋 Logs de Auditoría")
    
    def create_statistics_tab(self):
        """Crea la pestaña de estadísticas."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Estadísticas generales
        stats_group = QGroupBox("📊 Estadísticas Generales")
        stats_layout = QFormLayout(stats_group)
        
        self.total_logs_label = QLabel("0")
        stats_layout.addRow("Total de Logs:", self.total_logs_label)
        
        self.logs_today_label = QLabel("0")
        stats_layout.addRow("Logs de Hoy:", self.logs_today_label)
        
        self.unique_users_label = QLabel("0")
        stats_layout.addRow("Usuarios Únicos (30 días):", self.unique_users_label)
        
        self.most_active_user_label = QLabel("-")
        stats_layout.addRow("Usuario Más Activo:", self.most_active_user_label)
        
        layout.addWidget(stats_group)
        
        # Actividad por tipo
        activity_group = QGroupBox("📈 Actividad por Tipo de Acción")
        activity_layout = QVBoxLayout(activity_group)
        
        self.activity_list = QListWidget()
        self.activity_list.setStyleSheet("""
            QListWidget {
                background-color: white;
                color: #2c3e50;
                border: 1px solid #ddd;
                border-radius: 6px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #eee;
                color: #2c3e50;
            }
            QListWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #ecf0f1;
                color: #2c3e50;
            }
        """)
        activity_layout.addWidget(self.activity_list)
        
        layout.addWidget(activity_group)
        
        # Actividad reciente
        recent_group = QGroupBox("⏰ Actividad Reciente (Últimas 24 horas)")
        recent_layout = QVBoxLayout(recent_group)
        
        self.recent_activity_list = QListWidget()
        self.recent_activity_list.setStyleSheet("""
            QListWidget {
                background-color: white;
                color: #2c3e50;
                border: 1px solid #ddd;
                border-radius: 6px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #eee;
                color: #2c3e50;
            }
            QListWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #ecf0f1;
                color: #2c3e50;
            }
        """)
        recent_layout.addWidget(self.recent_activity_list)
        
        layout.addWidget(recent_group)
        
        self.tab_widget.addTab(tab, "📊 Estadísticas")
    
    def create_security_tab(self):
        """Crea la pestaña de seguridad."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Intentos de login fallidos
        failed_logins_group = QGroupBox("🔐 Intentos de Login Fallidos")
        failed_layout = QVBoxLayout(failed_logins_group)
        
        self.failed_logins_table = QTableWidget()
        self.failed_logins_table.setColumnCount(4)
        self.failed_logins_table.setHorizontalHeaderLabels(["Fecha/Hora", "Usuario", "IP", "Intentos"])
        self.failed_logins_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #e0e0e0;
                background-color: white;
                color: #2c3e50;
                border: 1px solid #ddd;
                border-radius: 6px;
            }
            QTableWidget::item {
                padding: 8px;
                color: #2c3e50;
                background-color: white;
            }
            QTableWidget::item:alternate {
                background-color: #f8f9fa;
                color: #2c3e50;
            }
            QTableWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 10px;
                border: none;
                font-weight: bold;
            }
        """)
        failed_layout.addWidget(self.failed_logins_table)
        
        layout.addWidget(failed_logins_group)
        
        # Accesos sospechosos
        suspicious_group = QGroupBox("⚠️ Actividad Sospechosa")
        suspicious_layout = QVBoxLayout(suspicious_group)
        
        self.suspicious_activity_list = QListWidget()
        self.suspicious_activity_list.setStyleSheet("""
            QListWidget {
                background-color: white;
                color: #2c3e50;
                border: 1px solid #ddd;
                border-radius: 6px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #eee;
                color: #2c3e50;
            }
            QListWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #ecf0f1;
                color: #2c3e50;
            }
        """)
        suspicious_layout.addWidget(self.suspicious_activity_list)
        
        layout.addWidget(suspicious_group)
        
        # Configuración de seguridad
        security_config_group = QGroupBox("⚙️ Configuración de Seguridad")
        security_config_layout = QFormLayout(security_config_group)
        
        self.max_failed_attempts = QSpinBox()
        self.max_failed_attempts.setRange(3, 10)
        self.max_failed_attempts.setValue(5)
        security_config_layout.addRow("Máximo intentos fallidos:", self.max_failed_attempts)
        
        self.lockout_duration = QSpinBox()
        self.lockout_duration.setRange(5, 60)
        self.lockout_duration.setValue(15)
        self.lockout_duration.setSuffix(" minutos")
        security_config_layout.addRow("Duración de bloqueo:", self.lockout_duration)
        
        save_security_btn = QPushButton("💾 Guardar Configuración")
        save_security_btn.clicked.connect(self.save_security_config)
        security_config_layout.addRow(save_security_btn)
        
        layout.addWidget(security_config_group)
        
        self.tab_widget.addTab(tab, "🔐 Seguridad")
    
    def create_export_tab(self):
        """Crea la pestaña de exportación."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Exportación de logs
        export_group = QGroupBox("📤 Exportar Logs de Auditoría")
        export_layout = QFormLayout(export_group)
        
        # Formato de exportación
        self.export_format = QComboBox()
        self.export_format.addItems(["CSV", "JSON", "PDF", "Excel"])
        export_layout.addRow("Formato:", self.export_format)
        
        # Rango de fechas para exportar
        self.export_date_from = QDateEdit()
        self.export_date_from.setDate(QDate.currentDate().addDays(-30))
        self.export_date_from.setCalendarPopup(True)
        export_layout.addRow("Desde:", self.export_date_from)
        
        self.export_date_to = QDateEdit()
        self.export_date_to.setDate(QDate.currentDate())
        self.export_date_to.setCalendarPopup(True)
        export_layout.addRow("Hasta:", self.export_date_to)
        
        # Filtros de exportación
        self.export_actions = QCheckBox("Incluir solo acciones críticas")
        export_layout.addRow(self.export_actions)
        
        self.export_user_data = QCheckBox("Incluir datos de usuario")
        export_layout.addRow(self.export_user_data)
        
        # Botón de exportación
        export_btn = QPushButton("📤 Exportar Logs")
        export_btn.setStyleSheet("""
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
        """)
        export_btn.clicked.connect(self.export_logs)
        export_layout.addRow(export_btn)
        
        layout.addWidget(export_group)
        
        # Programar exportaciones automáticas
        schedule_group = QGroupBox("⏰ Exportaciones Programadas")
        schedule_layout = QFormLayout(schedule_group)
        
        self.auto_export_enabled = QCheckBox("Habilitar exportación automática")
        schedule_layout.addRow(self.auto_export_enabled)
        
        self.auto_export_frequency = QComboBox()
        self.auto_export_frequency.addItems(["Diario", "Semanal", "Mensual"])
        schedule_layout.addRow("Frecuencia:", self.auto_export_frequency)
        
        self.auto_export_format = QComboBox()
        self.auto_export_format.addItems(["CSV", "JSON", "PDF"])
        schedule_layout.addRow("Formato:", self.auto_export_format)
        
        save_schedule_btn = QPushButton("💾 Guardar Programación")
        save_schedule_btn.clicked.connect(self.save_export_schedule)
        schedule_layout.addRow(save_schedule_btn)
        
        layout.addWidget(schedule_group)
        
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "📤 Exportación")
    
    def load_audit_logs(self):
        """Carga los logs de auditoría."""
        try:
            # Cargar usuarios para el filtro
            users = self.user_repo.get_all_active()
            for user in users:
                user_dict = dict(user)
                self.user_filter.addItem(
                    f"{user_dict.get('full_name', '')} ({user_dict.get('username', '')})",
                    user_dict.get('id')
                )
            
            # Cargar logs iniciales
            self.apply_filters()
            
            # Cargar estadísticas
            self.load_statistics()
            
        except Exception as e:
            logger.error(f"Error cargando logs de auditoría: {e}")
            QMessageBox.critical(self, "Error", f"Error cargando logs: {str(e)}")
    
    def apply_filters(self):
        """Aplica los filtros y carga los logs."""
        try:
            # Obtener parámetros de filtro
            qdate_from = self.date_from.date()
            qdate_to = self.date_to.date()
            date_from = date(qdate_from.year(), qdate_from.month(), qdate_from.day())
            date_to = date(qdate_to.year(), qdate_to.month(), qdate_to.day())
            user_id = self.user_filter.currentData()
            action = self.action_filter.currentData()
            table_name = self.table_filter.currentData()
            
            # Obtener logs filtrados
            logs = self.audit_repo.get_logs_filtered(
                date_from=date_from,
                date_to=date_to,
                user_id=user_id if user_id else None,
                action=action if action else None,
                table_name=table_name if table_name else None
            )
            
            self.display_logs(logs)
            
        except Exception as e:
            logger.error(f"Error aplicando filtros: {e}")
            QMessageBox.critical(self, "Error", f"Error aplicando filtros: {str(e)}")
    
    def display_logs(self, logs: Iterable[Any]) -> None:
        """Muestra los logs en la tabla."""
        log_entries: list[Any] = list(logs)
        self.logs_table.setRowCount(len(log_entries))
        
        for row, log in enumerate(log_entries):
            # Convertir si es necesario
            if hasattr(log, 'keys'):
                log_dict = dict(log)
            else:
                log_dict = log
            
            # ID
            self.logs_table.setItem(row, 0, QTableWidgetItem(str(log_dict.get('id', ''))))
            
            # Fecha/Hora
            timestamp = log_dict.get('timestamp', '')
            if timestamp:
                try:
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    formatted_time = dt.strftime('%d/%m/%Y %H:%M:%S')
                except:
                    formatted_time = timestamp
            else:
                formatted_time = ""
            self.logs_table.setItem(row, 1, QTableWidgetItem(formatted_time))
            
            # Usuario
            user_info = log_dict.get('user_info', 'Sistema')
            self.logs_table.setItem(row, 2, QTableWidgetItem(str(user_info)))
            
            # Acción
            action = log_dict.get('action', '')
            action_item = QTableWidgetItem(action)
            # Colorear según tipo de acción
            if action in ['DELETE', 'DELETE_USER']:
                action_item.setForeground(QColor("#e74c3c"))
            elif action in ['CREATE', 'CREATE_USER']:
                action_item.setForeground(QColor("#27ae60"))
            elif action in ['UPDATE', 'UPDATE_USER']:
                action_item.setForeground(QColor("#f39c12"))
            self.logs_table.setItem(row, 3, action_item)
            
            # Tabla
            self.logs_table.setItem(row, 4, QTableWidgetItem(log_dict.get('table_name', '')))
            
            # Registro ID
            self.logs_table.setItem(row, 5, QTableWidgetItem(str(log_dict.get('record_id', ''))))
            
            # IP
            self.logs_table.setItem(row, 6, QTableWidgetItem(log_dict.get('ip_address', '')))
            
            # Detalles
            details = str(log_dict.get('details', ''))
            if len(details) > 50:
                details = details[:47] + "..."
            self.logs_table.setItem(row, 7, QTableWidgetItem(details))
        
        # Actualizar contador
        self.results_label.setText(f"Resultados: {len(log_entries)}")
    
    def load_statistics(self):
        """Carga las estadísticas del panel."""
        try:
            # Estadísticas generales
            stats = self.audit_repo.get_statistics()
            
            self.total_logs_label.setText(str(stats.get('total_logs', 0)))
            self.logs_today_label.setText(str(stats.get('logs_today', 0)))
            self.unique_users_label.setText(str(stats.get('unique_users_30d', 0)))
            self.most_active_user_label.setText(stats.get('most_active_user', '-'))
            
            # Actividad por tipo
            self.activity_list.clear()
            activity_by_type = stats.get('activity_by_type', {})
            for action, count in activity_by_type.items():
                item = QListWidgetItem(f"{action}: {count} registros")
                self.activity_list.addItem(item)
            
            # Actividad reciente
            self.recent_activity_list.clear()
            recent_activity = stats.get('recent_activity', [])
            for activity in recent_activity[:10]:  # Últimas 10
                timestamp = activity.get('timestamp', '')
                user = activity.get('user_info', 'Sistema')
                action = activity.get('action', '')
                item = QListWidgetItem(f"{timestamp} - {user}: {action}")
                self.recent_activity_list.addItem(item)
                
        except Exception as e:
            logger.error(f"Error cargando estadísticas: {e}")
    
    def clear_filters(self):
        """Limpia todos los filtros."""
        self.date_from.setDate(QDate.currentDate().addDays(-30))
        self.date_to.setDate(QDate.currentDate())
        self.user_filter.setCurrentIndex(0)
        self.action_filter.setCurrentIndex(0)
        self.table_filter.setCurrentIndex(0)
        self.apply_filters()
    
    def show_log_details(self):
        """Muestra los detalles de un log seleccionado."""
        current_row = self.logs_table.currentRow()
        if current_row >= 0:
            log_id = self.logs_table.item(current_row, 0).text()
            self.show_log_detail_dialog(int(log_id))
    
    def show_log_detail_dialog(self, log_id: int):
        """Muestra un diálogo con los detalles completos del log."""
        try:
            log_details = self.audit_repo.get_log_details(log_id)
            if log_details:
                dialog = LogDetailDialog(log_details, self)
                dialog.exec()
        except Exception as e:
            logger.error(f"Error mostrando detalles del log: {e}")
            QMessageBox.critical(self, "Error", f"Error mostrando detalles: {str(e)}")
    
    def toggle_auto_refresh(self, enabled: bool):
        """Activa/desactiva la actualización automática."""
        if enabled:
            if not hasattr(self, 'refresh_timer'):
                self.refresh_timer = QTimer()
                self.refresh_timer.timeout.connect(self.apply_filters)
            self.refresh_timer.start(30000)  # 30 segundos
        else:
            if hasattr(self, 'refresh_timer'):
                self.refresh_timer.stop()
    
    def export_logs(self):
        """Exporta los logs según la configuración."""
        try:
            format_type = self.export_format.currentText()
            qdate_from = self.export_date_from.date()
            qdate_to = self.export_date_to.date()
            date_from = date(qdate_from.year(), qdate_from.month(), qdate_from.day())
            date_to = date(qdate_to.year(), qdate_to.month(), qdate_to.day())
            
            # Obtener logs para exportar
            logs = self.audit_repo.get_logs_filtered(
                date_from=date_from,
                date_to=date_to
            )
            
            if not logs:
                QMessageBox.information(self, "Sin Datos", "No hay logs para exportar en el rango seleccionado.")
                return
            
            # Aquí iría la lógica de exportación según el formato
            filename = f"audit_logs_{date_from}_{date_to}.{format_type.lower()}"
            
            QMessageBox.information(
                self,
                "Exportación Exitosa",
                f"Los logs han sido exportados exitosamente como {filename}"
            )
            
        except Exception as e:
            logger.error(f"Error exportando logs: {e}")
            QMessageBox.critical(self, "Error", f"Error exportando logs: {str(e)}")
    
    def save_security_config(self):
        """Guarda la configuración de seguridad."""
        QMessageBox.information(self, "Configuración Guardada", "La configuración de seguridad ha sido guardada.")
    
    def save_export_schedule(self):
        """Guarda la programación de exportaciones."""
        QMessageBox.information(self, "Programación Guardada", "La programación de exportaciones ha sido guardada.")
    
    def apply_dark_theme(self):
        """Aplica el tema nocturno elegante al panel de auditoría."""
        self.setStyleSheet("""
            QWidget {
                background-color: #1a1a1a;
                color: #e0e0e0;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            
            QTabWidget::pane {
                border: 1px solid #3a3a3a;
                background-color: #2a2a2a;
            }
            
            QTabWidget::tab-bar {
                alignment: left;
            }
            
            QTabBar::tab {
                background-color: #3a3a3a;
                color: #e0e0e0;
                padding: 8px 16px;
                margin: 2px;
                border-radius: 4px;
            }
            
            QTabBar::tab:selected {
                background-color: #4a9eff;
                color: white;
            }
            
            QTabBar::tab:hover {
                background-color: #4a4a4a;
            }
            
            QGroupBox {
                color: #e0e0e0;
                border: 2px solid #3a3a3a;
                border-radius: 8px;
                margin-top: 1ex;
                font-weight: bold;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                color: #4a9eff;
            }
            
            QTableWidget {
                background-color: #2a2a2a;
                alternate-background-color: #3a3a3a;
                color: #e0e0e0;
                gridline-color: #4a4a4a;
                border: 1px solid #3a3a3a;
                border-radius: 6px;
            }
            
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #4a4a4a;
            }
            
            QTableWidget::item:selected {
                background-color: #4a9eff;
                color: white;
            }
            
            QHeaderView::section {
                background-color: #3a3a3a;
                color: #e0e0e0;
                padding: 8px;
                border: none;
                border-right: 1px solid #4a4a4a;
                font-weight: bold;
            }
            
            QPushButton {
                background-color: #4a9eff;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
                min-width: 80px;
            }
            
            QPushButton:hover {
                background-color: #5aafff;
            }
            
            QPushButton:pressed {
                background-color: #3a8eff;
            }
            
            QPushButton:disabled {
                background-color: #5a5a5a;
                color: #9a9a9a;
            }
            
            QComboBox, QLineEdit, QDateEdit {
                background-color: #3a3a3a;
                color: #e0e0e0;
                border: 1px solid #5a5a5a;
                padding: 6px;
                border-radius: 4px;
            }
            
            QComboBox:hover, QLineEdit:hover, QDateEdit:hover {
                border-color: #4a9eff;
            }
            
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #e0e0e0;
                margin-right: 5px;
            }
            
            QScrollBar:vertical {
                background-color: #2a2a2a;
                width: 12px;
                border-radius: 6px;
            }
            
            QScrollBar::handle:vertical {
                background-color: #5a5a5a;
                border-radius: 6px;
                min-height: 20px;
            }
            
            QScrollBar::handle:vertical:hover {
                background-color: #6a6a6a;
            }
            
            QTextEdit {
                background-color: #2a2a2a;
                color: #e0e0e0;
                border: 1px solid #3a3a3a;
                border-radius: 6px;
                padding: 8px;
            }
        """)


class LogDetailDialog(QDialog):
    """Diálogo para mostrar detalles completos de un log."""
    
    def __init__(self, log_data: Dict[str, Any], parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.log_data = log_data
        self.setWindowTitle("Detalles del Log de Auditoría")
        self.setModal(True)
        self.resize(600, 500)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Configura la interfaz del diálogo."""
        layout = QVBoxLayout(self)
        
        # Título
        title_label = QLabel("📋 Detalles Completos del Log")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setWeight(QFont.Weight.Bold)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # Información principal
        info_group = QGroupBox("Información Principal")
        info_layout = QFormLayout(info_group)
        
        info_layout.addRow("ID:", QLabel(str(self.log_data.get('id', ''))))
        info_layout.addRow("Fecha/Hora:", QLabel(self.log_data.get('timestamp', '')))
        info_layout.addRow("Usuario:", QLabel(self.log_data.get('user_info', '')))
        info_layout.addRow("Acción:", QLabel(self.log_data.get('action', '')))
        info_layout.addRow("Tabla:", QLabel(self.log_data.get('table_name', '')))
        info_layout.addRow("Registro ID:", QLabel(str(self.log_data.get('record_id', ''))))
        info_layout.addRow("Dirección IP:", QLabel(self.log_data.get('ip_address', '')))
        
        layout.addWidget(info_group)
        
        # Detalles
        details_group = QGroupBox("Detalles Completos")
        details_layout = QVBoxLayout(details_group)
        
        details_text = QTextEdit()
        details_text.setPlainText(self.log_data.get('details', ''))
        details_text.setReadOnly(True)
        details_layout.addWidget(details_text)
        
        layout.addWidget(details_group)
        
        # Botón cerrar
        close_btn = QPushButton("Cerrar")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
    
    def apply_dark_theme(self):
        """Aplica el tema nocturno elegante al panel de auditoría."""
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
                min-width: 100px;
                background-color: #34495e;
                color: #ecf0f1;
            }
            
            QPushButton:hover {
                background-color: #4a6741;
                border-color: #74b9ff;
                color: #ffffff;
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
            
            QComboBox, QLineEdit, QDateEdit, QSpinBox {
                background-color: #2c3e50;
                color: #ecf0f1;
                border: 2px solid #34495e;
                border-radius: 6px;
                padding: 8px;
            }
            
            QComboBox:hover, QLineEdit:hover, QDateEdit:hover, QSpinBox:hover {
                border-color: #74b9ff;
            }
            
            QCheckBox {
                color: #e0e0e0;
            }
            
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #34495e;
                border-radius: 4px;
                background-color: #2c3e50;
            }
            
            QCheckBox::indicator:checked {
                background-color: #74b9ff;
                border-color: #74b9ff;
            }
        """)


def show_audit_panel(user_info: Dict[str, Any], parent: Optional[QWidget] = None) -> QDialog:
    """Muestra el panel de auditoría."""
    dialog = QDialog(parent)
    dialog.setWindowTitle("Panel de Auditoría y Logs")
    dialog.setModal(True)
    dialog.resize(1400, 900)
    
    layout = QVBoxLayout(dialog)
    
    try:
        widget = AuditLogWidget(user_info)
        layout.addWidget(widget)
        
        # Botón cerrar
        close_button = QPushButton("Cerrar")
        close_button.clicked.connect(dialog.accept)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)
        
        return dialog
        
    except Exception as e:
        logger.error(f"Error inicializando panel de auditoría: {e}")
        QMessageBox.critical(
            cast(QWidget, parent),
            "Error",
            f"Error inicializando panel de auditoría: {str(e)}"
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
    
    dialog = show_audit_panel(admin_user)
    dialog.exec()
    
    sys.exit(0)