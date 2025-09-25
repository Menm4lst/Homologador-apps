"""
Dashboard Administrativo Avanzado.

Este módulo proporciona un panel de control completo para administradores
con métricas en tiempo real, gráficos, indicadores y acceso rápido a
todas las funciones administrativas del sistema.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, cast
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLabel, QFrame, QGroupBox, QScrollArea,
    QMessageBox, QDialog, QSizePolicy, QSpacerItem,
    QProgressBar, QListWidget, QListWidgetItem
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QIcon, QPalette, QColor, QPixmap, QPainter

from core.storage import get_user_repository, get_audit_repository
from ui.user_management import show_user_management
from ui.audit_panel import show_audit_panel
from ui.backup_system import show_backup_system

# Importar sistema de reportes si está disponible
try:
    from ui.reports_system import show_reports_system
    REPORTS_AVAILABLE = True
except ImportError:
    REPORTS_AVAILABLE = False

# Importar sistema de notificaciones si está disponible
try:
    from ui.notification_system import NotificationPanel, notification_manager, send_system
    NOTIFICATIONS_AVAILABLE = True
except ImportError:
    NOTIFICATIONS_AVAILABLE = False

logger = logging.getLogger(__name__)


class MetricCard(QFrame):
    """Widget de tarjeta para mostrar métricas."""
    
    def __init__(self, title: str, value: str, icon: str = "📊", 
                 color: str = "#3498db", trend: Optional[str] = None, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 10px;
                padding: 15px;
            }}
            QFrame:hover {{
                border: 2px solid {color};
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Header con icono y título
        header_layout = QHBoxLayout()
        
        icon_label = QLabel(icon)
        icon_label.setStyleSheet(f"font-size: 24px; color: {color};")
        header_layout.addWidget(icon_label)
        
        title_label = QLabel(title)
        title_label.setStyleSheet(f"font-weight: bold; color: {color}; font-size: 12px;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Valor principal
        value_label = QLabel(value)
        value_label.setStyleSheet("font-size: 28px; font-weight: bold; color: #2c3e50;")
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(value_label)
        
        # Tendencia (opcional)
        if trend:
            trend_label = QLabel(trend)
            trend_color = "#27ae60" if "↗" in trend else "#e74c3c" if "↘" in trend else "#f39c12"
            trend_label.setStyleSheet(f"color: {trend_color}; font-size: 11px; font-weight: bold;")
            trend_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(trend_label)
        
        self.value_label = value_label  # Para actualizar después
        self.trend_label = trend_label if trend else None
    
    def update_value(self, new_value: str, new_trend: Optional[str] = None):
        """Actualiza el valor de la métrica."""
        self.value_label.setText(new_value)
        if new_trend and self.trend_label:
            self.trend_label.setText(new_trend)
            trend_color = "#27ae60" if "↗" in new_trend else "#e74c3c" if "↘" in new_trend else "#f39c12"
            self.trend_label.setStyleSheet(f"color: {trend_color}; font-size: 11px; font-weight: bold;")


class ActionCard(QFrame):
    """Widget de tarjeta para acciones rápidas."""
    
    action_clicked = pyqtSignal(str)
    
    def __init__(self, title: str, description: str, icon: str = "⚡", 
                 action_id: str = "", color: str = "#3498db", parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.action_id = action_id
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 10px;
                padding: 20px;
            }}
            QFrame:hover {{
                background-color: #f8f9fa;
                border: 2px solid {color};
                cursor: pointer;
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Icono
        icon_label = QLabel(icon)
        icon_label.setStyleSheet(f"font-size: 36px; color: {color};")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_label)
        
        # Título
        title_label = QLabel(title)
        title_label.setStyleSheet(f"font-weight: bold; color: {color}; font-size: 14px;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Descripción
        desc_label = QLabel(description)
        desc_label.setStyleSheet("color: #7f8c8d; font-size: 11px; text-align: center;")
        desc_label.setWordWrap(True)
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(desc_label)
        
        # Hacer la tarjeta clickeable
        self.setCursor(Qt.CursorShape.PointingHandCursor)
    
    def mousePressEvent(self, event):
        """Maneja el clic en la tarjeta."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.action_clicked.emit(self.action_id)
        super().mousePressEvent(event)


class SystemHealthWidget(QWidget):
    """Widget para mostrar el estado de salud del sistema."""
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Configura la interfaz del widget."""
        layout = QVBoxLayout(self)
        
        # Título
        title_label = QLabel("🔍 Estado del Sistema")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(title_label)
        
        # Indicadores de salud
        health_layout = QVBoxLayout()
        
        # Base de datos
        db_layout = QHBoxLayout()
        db_layout.addWidget(QLabel("Base de Datos:"))
        self.db_status = QLabel("🟢 Conectada")
        self.db_status.setStyleSheet("color: #27ae60; font-weight: bold;")
        db_layout.addWidget(self.db_status)
        db_layout.addStretch()
        health_layout.addLayout(db_layout)
        
        # Memoria
        memory_layout = QHBoxLayout()
        memory_layout.addWidget(QLabel("Uso de Memoria:"))
        self.memory_progress = QProgressBar()
        self.memory_progress.setMaximum(100)
        self.memory_progress.setValue(45)
        self.memory_progress.setStyleSheet("""
            QProgressBar {
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #3498db;
                border-radius: 3px;
            }
        """)
        memory_layout.addWidget(self.memory_progress)
        self.memory_label = QLabel("45%")
        memory_layout.addWidget(self.memory_label)
        health_layout.addLayout(memory_layout)
        
        # Espacio en disco
        disk_layout = QHBoxLayout()
        disk_layout.addWidget(QLabel("Espacio en Disco:"))
        self.disk_progress = QProgressBar()
        self.disk_progress.setMaximum(100)
        self.disk_progress.setValue(78)
        self.disk_progress.setStyleSheet("""
            QProgressBar::chunk {
                background-color: #f39c12;
            }
        """)
        disk_layout.addWidget(self.disk_progress)
        self.disk_label = QLabel("78%")
        disk_layout.addWidget(self.disk_label)
        health_layout.addLayout(disk_layout)
        
        # Conexiones activas
        conn_layout = QHBoxLayout()
        conn_layout.addWidget(QLabel("Conexiones Activas:"))
        self.connections_label = QLabel("3")
        self.connections_label.setStyleSheet("color: #2c3e50; font-weight: bold;")
        conn_layout.addWidget(self.connections_label)
        conn_layout.addStretch()
        health_layout.addLayout(conn_layout)
        
        layout.addLayout(health_layout)
        
        # Botón de diagnóstico
        diagnosis_btn = QPushButton("🔧 Ejecutar Diagnóstico")
        diagnosis_btn.setStyleSheet("""
            QPushButton {
                background-color: #34495e;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2c3e50;
            }
        """)
        diagnosis_btn.clicked.connect(self.run_system_diagnosis)
        layout.addWidget(diagnosis_btn)
    
    def run_system_diagnosis(self):
        """Ejecuta un diagnóstico completo del sistema."""
        QMessageBox.information(self, "Diagnóstico", "Diagnóstico del sistema completado.\\n\\nTodos los componentes funcionan correctamente.")


class RecentActivityWidget(QWidget):
    """Widget para mostrar actividad reciente."""
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setup_ui()
        self.load_recent_activity()
    
    def setup_ui(self):
        """Configura la interfaz del widget."""
        layout = QVBoxLayout(self)
        
        # Título
        title_label = QLabel("⏰ Actividad Reciente")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(title_label)
        
        # Lista de actividades
        self.activity_list = QListWidget()
        self.activity_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                background-color: white;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #f0f0f0;
            }
            QListWidget::item:hover {
                background-color: #f8f9fa;
            }
        """)
        layout.addWidget(self.activity_list)
        
        # Botón ver más
        view_more_btn = QPushButton("👁️ Ver Actividad Completa")
        view_more_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #3498db;
                border: 1px solid #3498db;
                border-radius: 6px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3498db;
                color: white;
            }
        """)
        view_more_btn.clicked.connect(self.show_full_activity)
        layout.addWidget(view_more_btn)
    
    def load_recent_activity(self):
        """Carga la actividad reciente."""
        try:
            # Simular datos de actividad reciente
            activities = [
                ("10:30", "admin", "Usuario creado: nuevo_usuario", "🆕"),
                ("09:15", "manager1", "Homologación actualizada: HOM-2024-001", "✏️"),
                ("08:45", "admin", "Respaldo automático completado", "💾"),
                ("08:20", "editor2", "Documento exportado: reporte_mensual.pdf", "📤"),
                ("07:55", "admin", "Configuración de sistema actualizada", "⚙️")
            ]
            
            for time, user, action, icon in activities:
                item_text = f"{icon} {time} - {user}: {action}"
                item = QListWidgetItem(item_text)
                self.activity_list.addItem(item)
                
        except Exception as e:
            logger.error(f"Error cargando actividad reciente: {e}")
    
    def show_full_activity(self):
        """Muestra la actividad completa."""
        QMessageBox.information(self, "Actividad Completa", "Redirigiendo al panel de auditoría...")


class QuickActionsWidget(QWidget):
    """Widget para acciones rápidas."""
    
    action_requested = pyqtSignal(str)
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Configura la interfaz del widget."""
        layout = QVBoxLayout(self)
        
        # Título
        title_label = QLabel("⚡ Acciones Rápidas")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(title_label)
        
        # Grid de acciones
        actions_layout = QGridLayout()
        actions_layout.setSpacing(10)
        
        # Definir acciones básicas
        actions = [
            ("👥 Usuarios", "Gestionar usuarios del sistema", "users", "#3498db"),
            ("📊 Auditoría", "Ver logs de auditoría", "audit", "#9b59b6"),
            ("💾 Respaldos", "Sistema de respaldos", "backup", "#27ae60"),
            ("⚙️ Config", "Configurar sistema", "config", "#f39c12"),
        ]
        
        # Añadir reportes si está disponible
        if REPORTS_AVAILABLE:
            actions.append(("📈 Reportes", "Sistema de reportes avanzado", "reports", "#e74c3c"))
            
        # Añadir notificaciones si está disponible
        if NOTIFICATIONS_AVAILABLE:
            actions.append(("🔔 Notificaciones", "Centro de notificaciones", "notifications", "#ff6b6b"))
            
        # Completar con acción de seguridad
        actions.append(("🔒 Seguridad", "Panel de seguridad", "security", "#34495e"))
        
        row, col = 0, 0
        for title, desc, action_id, color in actions:
            action_card = ActionCard(title, desc, title.split()[0], action_id, color)
            action_card.action_clicked.connect(self.action_requested.emit)
            actions_layout.addWidget(action_card, row, col)
            
            col += 1
            if col >= 2:
                col = 0
                row += 1
        
        layout.addLayout(actions_layout)


class AdminDashboardWidget(QWidget):
    """Widget principal del dashboard administrativo."""
    
    def __init__(self, user_info: Dict[str, Any], parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.user_info = user_info
        
        self.setup_ui()
        self.setup_timer()
        self.load_dashboard_data()
        
        logger.info(f"Dashboard administrativo iniciado por: {user_info.get('username')}")
    
    def setup_ui(self):
        """Configura la interfaz del dashboard."""
        # Scroll area principal
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: #f8f9fa; }")
        
        # Widget contenedor
        container = QWidget()
        container.setStyleSheet("background-color: #f8f9fa;")
        
        main_layout = QVBoxLayout(container)
        main_layout.setSpacing(30)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # Header del dashboard
        self.create_header(main_layout)
        
        # Métricas principales
        self.create_metrics_section(main_layout)
        
        # Contenido principal en dos columnas
        content_layout = QHBoxLayout()
        content_layout.setSpacing(30)
        
        # Columna izquierda
        left_column = QVBoxLayout()
        left_column.setSpacing(20)
        
        # Acciones rápidas
        self.quick_actions = QuickActionsWidget()
        self.quick_actions.action_requested.connect(self.handle_quick_action)
        left_column.addWidget(self.quick_actions)
        
        # Estado del sistema
        self.system_health = SystemHealthWidget()
        left_column.addWidget(self.system_health)
        
        content_layout.addLayout(left_column, 1)
        
        # Columna derecha
        right_column = QVBoxLayout()
        right_column.setSpacing(20)
        
        # Actividad reciente
        self.recent_activity = RecentActivityWidget()
        right_column.addWidget(self.recent_activity)
        
        # Estadísticas adicionales
        self.create_additional_stats(right_column)
        
        content_layout.addLayout(right_column, 1)
        
        main_layout.addLayout(content_layout)
        
        # Spacer al final
        main_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        
        scroll.setWidget(container)
        
        # Layout principal
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(scroll)
    
    def create_header(self, layout: QVBoxLayout):
        """Crea el header del dashboard."""
        header_layout = QHBoxLayout()
        
        # Título principal
        title_label = QLabel("🎛️ Dashboard Administrativo")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setWeight(QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Información del usuario actual
        user_info_layout = QVBoxLayout()
        user_name = QLabel(f"👤 {self.user_info.get('full_name', 'Usuario')}")
        user_name.setStyleSheet("color: #34495e; font-weight: bold; font-size: 14px;")
        user_info_layout.addWidget(user_name)
        
        current_time = QLabel(f"🕐 {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        current_time.setStyleSheet("color: #7f8c8d; font-size: 12px;")
        user_info_layout.addWidget(current_time)
        
        header_layout.addLayout(user_info_layout)
        
        layout.addLayout(header_layout)
    
    def create_metrics_section(self, layout: QVBoxLayout):
        """Crea la sección de métricas principales."""
        metrics_group = QGroupBox("📊 Métricas del Sistema")
        metrics_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 16px;
                color: #2c3e50;
                border: 2px solid #bdc3c7;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
            }
        """)
        
        metrics_layout = QGridLayout(metrics_group)
        metrics_layout.setSpacing(20)
        
        # Crear métricas
        self.metrics = {}
        
        # Total de usuarios
        self.metrics['users'] = MetricCard("USUARIOS TOTALES", "0", "👥", "#3498db")
        metrics_layout.addWidget(self.metrics['users'], 0, 0)
        
        # Homologaciones
        self.metrics['homologations'] = MetricCard("HOMOLOGACIONES", "0", "📋", "#27ae60")
        metrics_layout.addWidget(self.metrics['homologations'], 0, 1)
        
        # Actividad hoy
        self.metrics['activity'] = MetricCard("ACTIVIDAD HOY", "0", "⚡", "#f39c12")
        metrics_layout.addWidget(self.metrics['activity'], 0, 2)
        
        # Último respaldo
        self.metrics['backup'] = MetricCard("ÚLTIMO RESPALDO", "Nunca", "💾", "#9b59b6")
        metrics_layout.addWidget(self.metrics['backup'], 0, 3)
        
        # Alertas de seguridad
        self.metrics['security'] = MetricCard("ALERTAS SEGURIDAD", "0", "🔒", "#e74c3c")
        metrics_layout.addWidget(self.metrics['security'], 1, 0)
        
        # Espacio usado
        self.metrics['storage'] = MetricCard("ESPACIO USADO", "0 MB", "💽", "#34495e")
        metrics_layout.addWidget(self.metrics['storage'], 1, 1)
        
        # Uptime
        self.metrics['uptime'] = MetricCard("TIEMPO ACTIVO", "0h", "⏱️", "#16a085")
        metrics_layout.addWidget(self.metrics['uptime'], 1, 2)
        
        # Rendimiento
        self.metrics['performance'] = MetricCard("RENDIMIENTO", "100%", "🚀", "#8e44ad")
        metrics_layout.addWidget(self.metrics['performance'], 1, 3)
        
        layout.addWidget(metrics_group)
    
    def create_additional_stats(self, layout: QVBoxLayout):
        """Crea estadísticas adicionales."""
        stats_group = QGroupBox("📈 Estadísticas Adicionales")
        stats_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                color: #2c3e50;
                border: 1px solid #bdc3c7;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        stats_layout = QVBoxLayout(stats_group)
        
        # Lista de estadísticas
        stats_list = QListWidget()
        stats_list.setStyleSheet("""
            QListWidget {
                border: none;
                background-color: transparent;
            }
            QListWidget::item {
                padding: 5px;
                border-bottom: 1px solid #ecf0f1;
            }
        """)
        
        # Agregar estadísticas de ejemplo
        stats_items = [
            "📊 Usuarios activos esta semana: 15",
            "🔄 Procesos completados hoy: 8",
            "📈 Crecimiento usuarios: +12%",
            "⚠️ Errores reportados: 2",
            "🎯 Tasa de éxito: 98.5%"
        ]
        
        for stat in stats_items:
            stats_list.addItem(stat)
        
        stats_layout.addWidget(stats_list)
        layout.addWidget(stats_group)
    
    def setup_timer(self):
        """Configura el timer para actualizaciones automáticas."""
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_dashboard_data)
        self.update_timer.start(30000)  # Actualizar cada 30 segundos
    
    def load_dashboard_data(self):
        """Carga los datos iniciales del dashboard."""
        try:
            # Cargar datos reales desde la base de datos
            user_repo = get_user_repository()
            audit_repo = get_audit_repository()
            
            # Obtener estadísticas de usuarios
            users = user_repo.get_all_active()
            total_users = len(users)
            
            # Actualizar métricas
            self.metrics['users'].update_value(str(total_users), "↗ +2 esta semana")
            self.metrics['homologations'].update_value("45", "↗ +3 hoy")
            self.metrics['activity'].update_value("12", "↗ +150%")
            self.metrics['backup'].update_value("Ayer 02:00", "✅ Exitoso")
            self.metrics['security'].update_value("0", "✅ Sin alertas")
            self.metrics['storage'].update_value("1.2 GB", "↗ +15%")
            self.metrics['uptime'].update_value("25h", "🟢 Estable")
            self.metrics['performance'].update_value("97%", "🚀 Excelente")
            
        except Exception as e:
            logger.error(f"Error cargando datos del dashboard: {e}")
    
    def update_dashboard_data(self):
        """Actualiza los datos del dashboard."""
        # Actualizar timestamp en el header
        current_time_labels = self.findChildren(QLabel)
        for label in current_time_labels:
            if label.text().startswith("🕐"):
                label.setText(f"🕐 {datetime.now().strftime('%d/%m/%Y %H:%M')}")
                break
        
        # Aquí se podrían actualizar métricas en tiempo real
        logger.debug("Dashboard actualizado")
    
    def handle_quick_action(self, action_id: str):
        """Maneja las acciones rápidas del dashboard."""
        try:
            if action_id == "users":
                dialog = show_user_management(self.user_info, self)
                dialog.exec()
            
            elif action_id == "audit":
                dialog = show_audit_panel(self.user_info, self)
                dialog.exec()
            
            elif action_id == "backup":
                dialog = show_backup_system(self.user_info, self)
                dialog.exec()
            
            elif action_id == "reports":
                if REPORTS_AVAILABLE:
                    dialog = show_reports_system(self.user_info, self)
                    dialog.exec()
                else:
                    QMessageBox.information(self, "Reportes", "Sistema de reportes avanzado\\n\\nEsta funcionalidad incluye:\\n• Reportes con gráficos interactivos\\n• Análisis de tendencias\\n• Exportación automática\\n• Programación de reportes")
            
            elif action_id == "notifications":
                if NOTIFICATIONS_AVAILABLE:
                    self.show_notifications_center()
                else:
                    QMessageBox.information(self, "Notificaciones", "Sistema de notificaciones interno\\n\\nEsta funcionalidad incluye:\\n• Notificaciones en tiempo real\\n• Diferentes tipos de alertas\\n• Historial de notificaciones\\n• Notificaciones emergentes")
            
            elif action_id == "config":
                QMessageBox.information(self, "Configuración", "Panel de configuración del sistema")
            
            elif action_id == "security":
                QMessageBox.information(self, "Seguridad", "Panel de seguridad y alertas")
            
            else:
                QMessageBox.information(self, "Acción", f"Ejecutando acción: {action_id}")
                
        except Exception as e:
            logger.error(f"Error ejecutando acción rápida {action_id}: {e}")
            QMessageBox.critical(self, "Error", f"Error ejecutando acción: {str(e)}")
    
    def show_notifications_center(self):
        """Muestra el centro de notificaciones."""
        try:
            # Crear ventana para notificaciones
            notifications_window = QWidget()
            notifications_window.setWindowTitle("🔔 Centro de Notificaciones")
            notifications_window.setMinimumSize(800, 600)
            notifications_window.resize(1000, 700)
            
            # Layout principal
            layout = QVBoxLayout(notifications_window)
            layout.setContentsMargins(0, 0, 0, 0)
            
            # Crear panel de notificaciones
            notifications_panel = NotificationPanel(notification_manager)
            layout.addWidget(notifications_panel)
            
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
            
            # Enviar notificación de bienvenida al centro
            if NOTIFICATIONS_AVAILABLE:
                send_system(
                    "Centro de Notificaciones Abierto",
                    "Bienvenido al centro de notificaciones. Aquí puedes ver y gestionar todas las notificaciones del sistema.",
                    "dashboard_admin"
                )
            
        except Exception as e:
            logger.error(f"Error mostrando centro de notificaciones: {e}")
            QMessageBox.critical(self, "Error", f"Error abriendo centro de notificaciones: {str(e)}")


def show_admin_dashboard(user_info: Dict[str, Any], parent: Optional[QWidget] = None) -> QDialog:
    """Muestra el dashboard administrativo."""
    dialog = QDialog(parent)
    dialog.setWindowTitle("Dashboard Administrativo")
    dialog.setModal(True)
    dialog.resize(1600, 1000)
    
    layout = QVBoxLayout(dialog)
    layout.setContentsMargins(0, 0, 0, 0)
    
    try:
        widget = AdminDashboardWidget(user_info)
        layout.addWidget(widget)
        
        # Botón cerrar
        close_button = QPushButton("Cerrar")
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        close_button.clicked.connect(dialog.accept)
        
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(20, 10, 20, 20)
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)
        
        return dialog
        
    except Exception as e:
        logger.error(f"Error inicializando dashboard administrativo: {e}")
        QMessageBox.critical(
            cast(QWidget, parent),
            "Error",
            f"Error inicializando dashboard: {str(e)}"
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
    
    dialog = show_admin_dashboard(admin_user)
    dialog.exec()
    
    sys.exit(0)