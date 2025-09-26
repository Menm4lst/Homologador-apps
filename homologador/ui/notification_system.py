"""
Sistema de Notificaciones Interno.

Este módulo proporciona un sistema de notificaciones simple y elegante
que funciona únicamente dentro de la aplicación, sin envío de emails.
"""

import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from PyQt6.QtCore import (QEasingCurve, QParallelAnimationGroup,
                          QPropertyAnimation, QRect, QSize, Qt, QThread,
                          QTimer, pyqtSignal)
from PyQt6.QtGui import QColor, QFont, QIcon, QPainter, QPalette, QPixmap
from PyQt6.QtWidgets import (QCheckBox, QComboBox, QDialog, QDialogButtonBox,
                             QFormLayout, QFrame, QGroupBox, QHBoxLayout,
                             QHeaderView, QLabel, QLineEdit, QListWidget,
                             QListWidgetItem, QMessageBox, QPushButton,
                             QScrollArea, QSizePolicy, QSplitter, QTableWidget,
                             QTableWidgetItem, QTabWidget, QTextEdit,
                             QVBoxLayout, QWidget)

# Configurar logging
logger = logging.getLogger(__name__)

class NotificationType(Enum):
    """Tipos de notificación disponibles."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"
    SYSTEM = "system"

class NotificationPriority(Enum):
    """Prioridades de notificación."""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class Notification:
    """Clase de datos para una notificación."""
    id: str
    title: str
    message: str
    type: NotificationType
    priority: NotificationPriority
    timestamp: datetime
    read: bool = False
    dismissed: bool = False
    source: str = "system"
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class NotificationToast(QWidget):
    """Widget de notificación emergente (toast)."""
    
    def __init__(self, notification: Notification, parent=None):
        super().__init__(parent)
        self.notification = notification
        self.setup_ui()
        self.setup_animations()
        
    def setup_ui(self):
        """Configura la interfaz del toast."""
        self.setFixedSize(350, 100)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Layout principal
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Frame principal
        self.main_frame = QFrame()
        self.main_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {self._get_color_for_type()};
                border-radius: 8px;
                border: 2px solid {self._get_border_color_for_type()};
            }}
        """)
        
        frame_layout = QHBoxLayout(self.main_frame)
        
        # Icono
        icon_label = QLabel()
        icon_label.setText(self._get_icon_for_type())
        icon_label.setStyleSheet("font-size: 24px; color: white; font-weight: bold;")
        icon_label.setFixedSize(40, 40)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Contenido
        content_layout = QVBoxLayout()
        
        title_label = QLabel(self.notification.title)
        title_label.setStyleSheet("color: white; font-weight: bold; font-size: 12px;")
        title_label.setWordWrap(True)
        
        message_text = self.notification.message
        if len(message_text) > 100:
            message_text = message_text[:100] + "..."
            
        message_label = QLabel(message_text)
        message_label.setStyleSheet("color: white; font-size: 10px;")
        message_label.setWordWrap(True)
        
        content_layout.addWidget(title_label)
        content_layout.addWidget(message_label)
        
        # Botón cerrar
        close_btn = QPushButton("×")
        close_btn.setFixedSize(25, 25)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: white;
                border: none;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.2);
                border-radius: 12px;
            }
        """)
        close_btn.clicked.connect(self.close_toast)
        
        frame_layout.addWidget(icon_label)
        frame_layout.addLayout(content_layout)
        frame_layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignTop)
        
        layout.addWidget(self.main_frame)
        
    def setup_animations(self):
        """Configura las animaciones del toast."""
        self.slide_animation = QPropertyAnimation(self, b"geometry")
        self.slide_animation.setDuration(300)
        self.slide_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        self.fade_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_animation.setDuration(200)
        
    def show_toast(self):
        """Muestra el toast con animación."""
        # Posicionar fuera de la pantalla
        screen = self.screen().availableGeometry()
        start_pos = QRect(screen.width(), screen.height() - 120, self.width(), self.height())
        end_pos = QRect(screen.width() - self.width() - 20, screen.height() - 120, self.width(), self.height())
        
        self.setGeometry(start_pos)
        self.show()
        
        # Animar entrada
        self.slide_animation.setStartValue(start_pos)
        self.slide_animation.setEndValue(end_pos)
        self.slide_animation.start()
        
        # Auto-cerrar después de 5 segundos
        QTimer.singleShot(5000, self.close_toast)
        
    def close_toast(self):
        """Cierra el toast con animación."""
        self.fade_animation.setStartValue(1.0)
        self.fade_animation.setEndValue(0.0)
        self.fade_animation.finished.connect(self.close)
        self.fade_animation.start()
        
    def _get_color_for_type(self):
        """Obtiene el color de fondo según el tipo."""
        colors = {
            NotificationType.INFO: "#3498db",
            NotificationType.SUCCESS: "#27ae60",
            NotificationType.WARNING: "#f39c12",
            NotificationType.ERROR: "#e74c3c",
            NotificationType.SYSTEM: "#34495e"
        }
        return colors.get(self.notification.type, "#3498db")
        
    def _get_border_color_for_type(self):
        """Obtiene el color del borde según el tipo."""
        colors = {
            NotificationType.INFO: "#2980b9",
            NotificationType.SUCCESS: "#229954",
            NotificationType.WARNING: "#d68910",
            NotificationType.ERROR: "#c0392b",
            NotificationType.SYSTEM: "#2c3e50"
        }
        return colors.get(self.notification.type, "#2980b9")
        
    def _get_icon_for_type(self):
        """Obtiene el icono según el tipo."""
        icons = {
            NotificationType.INFO: "ℹ",
            NotificationType.SUCCESS: "✓",
            NotificationType.WARNING: "⚠",
            NotificationType.ERROR: "✗",
            NotificationType.SYSTEM: "⚙"
        }
        return icons.get(self.notification.type, "ℹ")

class NotificationManager:
    """Gestor central del sistema de notificaciones."""
    
    def __init__(self):
        self.notifications: List[Notification] = []
        self.notification_callbacks: List[Callable] = []
        self.max_notifications = 100  # Límite de notificaciones en memoria
        
    def add_notification(self, notification: Notification):
        """Añade una nueva notificación."""
        # Generar ID único si no se proporciona
        if not notification.id:
            notification.id = f"notif_{len(self.notifications)}_{int(datetime.now().timestamp())}"
            
        self.notifications.append(notification)
        
        # Limitar número de notificaciones
        if len(self.notifications) > self.max_notifications:
            # Mantener solo las más recientes
            self.notifications = self.notifications[-self.max_notifications:]
        
        # Notificar a los callbacks registrados
        for callback in self.notification_callbacks:
            try:
                callback(notification)
            except Exception as e:
                logger.error(f"Error en callback de notificación: {e}")
                
    def get_notifications(self, unread_only: bool = False) -> List[Notification]:
        """Obtiene las notificaciones."""
        notifications = self.notifications
        if unread_only:
            notifications = [n for n in notifications if not n.read]
        return sorted(notifications, key=lambda x: x.timestamp, reverse=True)
        
    def mark_as_read(self, notification_id: str):
        """Marca una notificación como leída."""
        for notification in self.notifications:
            if notification.id == notification_id:
                notification.read = True
                break
                
    def dismiss_notification(self, notification_id: str):
        """Descarta una notificación."""
        for notification in self.notifications:
            if notification.id == notification_id:
                notification.dismissed = True
                break
                
    def clear_old_notifications(self, days: int = 7):
        """Limpia notificaciones antiguas."""
        cutoff_date = datetime.now() - timedelta(days=days)
        self.notifications = [
            n for n in self.notifications 
            if n.timestamp > cutoff_date or not n.read
        ]
        
    def add_callback(self, callback: Callable):
        """Añade un callback para nuevas notificaciones."""
        self.notification_callbacks.append(callback)
        
    def remove_callback(self, callback: Callable):
        """Remueve un callback."""
        if callback in self.notification_callbacks:
            self.notification_callbacks.remove(callback)
            
    def get_unread_count(self) -> int:
        """Obtiene el número de notificaciones no leídas."""
        return len([n for n in self.notifications if not n.read and not n.dismissed])

class NotificationBadge(QLabel):
    """Badge que muestra el número de notificaciones no leídas."""
    
    def __init__(self, notification_manager: NotificationManager, parent=None):
        super().__init__(parent)
        self.notification_manager = notification_manager
        self.setup_ui()
        self.update_count()
        
        # Conectar con el manager para actualizaciones
        self.notification_manager.add_callback(self._on_notification_change)
        
    def setup_ui(self):
        """Configura la interfaz del badge."""
        self.setFixedSize(20, 20)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet("""
            QLabel {
                background-color: #e74c3c;
                color: white;
                border-radius: 10px;
                font-size: 10px;
                font-weight: bold;
            }
        """)
        self.hide()  # Inicialmente oculto
        
    def update_count(self):
        """Actualiza el contador de notificaciones."""
        count = self.notification_manager.get_unread_count()
        if count > 0:
            self.setText(str(min(count, 99)))  # Máximo 99
            self.show()
        else:
            self.hide()
            
    def _on_notification_change(self, notification: Notification):
        """Maneja cambios en las notificaciones."""
        self.update_count()

class NotificationPanel(QWidget):
    """Panel principal del sistema de notificaciones."""
    
    def __init__(self, notification_manager: NotificationManager, parent=None):
        super().__init__(parent)
        self.notification_manager = notification_manager
        self.current_toast = None
        self.setup_ui()
        self.load_notifications()
        
        # Registrar callback para nuevas notificaciones
        self.notification_manager.add_callback(self._on_new_notification)
        
    def setup_ui(self):
        """Configura la interfaz del panel."""
        layout = QVBoxLayout(self)
        
        # Header
        header_layout = QHBoxLayout()
        
        title_label = QLabel("Centro de Notificaciones")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        
        # Botones de acción
        clear_btn = QPushButton("Limpiar Leídas")
        clear_btn.clicked.connect(self.clear_read_notifications)
        
        test_btn = QPushButton("Prueba")
        test_btn.clicked.connect(self.send_test_notification)
        
        mark_all_btn = QPushButton("Marcar Todas Leídas")
        mark_all_btn.clicked.connect(self.mark_all_read)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(mark_all_btn)
        header_layout.addWidget(clear_btn)
        header_layout.addWidget(test_btn)
        
        # Filtros
        filter_layout = QHBoxLayout()
        
        self.filter_type = QComboBox()
        self.filter_type.addItem("Todos los tipos", "all")
        for notif_type in NotificationType:
            self.filter_type.addItem(notif_type.value.title(), notif_type.value)
        self.filter_type.currentTextChanged.connect(self.apply_filters)
        
        self.filter_read = QComboBox()
        self.filter_read.addItems(["Todas", "No leídas", "Leídas"])
        self.filter_read.currentTextChanged.connect(self.apply_filters)
        
        filter_layout.addWidget(QLabel("Tipo:"))
        filter_layout.addWidget(self.filter_type)
        filter_layout.addWidget(QLabel("Estado:"))
        filter_layout.addWidget(self.filter_read)
        filter_layout.addStretch()
        
        # Lista de notificaciones
        self.notifications_list = QListWidget()
        self.notifications_list.itemClicked.connect(self.on_notification_clicked)
        
        # Panel de detalles
        self.details_panel = QTextEdit()
        self.details_panel.setMaximumHeight(150)
        self.details_panel.setReadOnly(True)
        
        # Layout principal con splitter
        splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Widget superior
        top_widget = QWidget()
        top_layout = QVBoxLayout(top_widget)
        top_layout.addLayout(header_layout)
        top_layout.addLayout(filter_layout)
        top_layout.addWidget(self.notifications_list)
        
        splitter.addWidget(top_widget)
        splitter.addWidget(self.details_panel)
        splitter.setSizes([400, 150])
        
        layout.addWidget(splitter)
        
    def load_notifications(self):
        """Carga las notificaciones en la lista."""
        self.notifications_list.clear()
        
        # Aplicar filtros
        notifications = self.notification_manager.get_notifications()
        
        # Filtro por tipo
        type_filter = self.filter_type.currentData()
        if type_filter and type_filter != "all":
            notifications = [n for n in notifications if n.type.value == type_filter]
            
        # Filtro por estado de lectura
        read_filter = self.filter_read.currentText()
        if read_filter == "No leídas":
            notifications = [n for n in notifications if not n.read]
        elif read_filter == "Leídas":
            notifications = [n for n in notifications if n.read]
            
        # Filtrar no descartadas
        notifications = [n for n in notifications if not n.dismissed]
        
        for notification in notifications:
            item = QListWidgetItem()
            
            # Crear widget personalizado para la notificación
            item_widget = self._create_notification_widget(notification)
            item.setSizeHint(item_widget.sizeHint())
            
            self.notifications_list.addItem(item)
            self.notifications_list.setItemWidget(item, item_widget)
            
    def _create_notification_widget(self, notification: Notification) -> QWidget:
        """Crea un widget personalizado para una notificación."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        
        # Indicador de estado
        status_label = QLabel()
        status_label.setFixedSize(10, 10)
        status_label.setStyleSheet(f"""
            background-color: {'#95a5a6' if notification.read else '#e74c3c'};
            border-radius: 5px;
        """)
        
        # Icono del tipo
        icon_label = QLabel(self._get_icon_for_type(notification.type))
        icon_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        icon_label.setFixedSize(25, 25)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Contenido principal
        content_layout = QVBoxLayout()
        
        # Título y timestamp
        title_layout = QHBoxLayout()
        title_label = QLabel(notification.title)
        title_label.setStyleSheet(f"""
            font-weight: {'normal' if notification.read else 'bold'};
            color: {'#7f8c8d' if notification.read else '#2c3e50'};
        """)
        
        time_label = QLabel(notification.timestamp.strftime("%d/%m %H:%M"))
        time_label.setStyleSheet("color: #95a5a6; font-size: 10px;")
        
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        title_layout.addWidget(time_label)
        
        # Mensaje (truncado)
        message_text = notification.message
        if len(message_text) > 80:
            message_text = message_text[:80] + "..."
            
        message_label = QLabel(message_text)
        message_label.setStyleSheet("color: #7f8c8d; font-size: 11px;")
        message_label.setWordWrap(True)
        
        content_layout.addLayout(title_layout)
        content_layout.addWidget(message_label)
        
        # Botones de acción
        actions_layout = QHBoxLayout()
        
        if not notification.read:
            mark_read_btn = QPushButton("Marcar leída")
            mark_read_btn.setMaximumHeight(25)
            mark_read_btn.clicked.connect(lambda: self._mark_as_read(notification.id))
            actions_layout.addWidget(mark_read_btn)
            
        dismiss_btn = QPushButton("Descartar")
        dismiss_btn.setMaximumHeight(25)
        dismiss_btn.clicked.connect(lambda: self._dismiss_notification(notification.id))
        actions_layout.addWidget(dismiss_btn)
        
        actions_layout.addStretch()
        
        layout.addWidget(status_label, alignment=Qt.AlignmentFlag.AlignTop)
        layout.addWidget(icon_label, alignment=Qt.AlignmentFlag.AlignTop)
        layout.addLayout(content_layout)
        layout.addLayout(actions_layout)
        
        return widget
        
    def _get_icon_for_type(self, notif_type: NotificationType) -> str:
        """Obtiene el icono para un tipo de notificación."""
        icons = {
            NotificationType.INFO: "ℹ",
            NotificationType.SUCCESS: "✓",
            NotificationType.WARNING: "⚠",
            NotificationType.ERROR: "✗",
            NotificationType.SYSTEM: "⚙"
        }
        return icons.get(notif_type, "ℹ")
        
    def _mark_as_read(self, notification_id: str):
        """Marca una notificación como leída."""
        self.notification_manager.mark_as_read(notification_id)
        self.load_notifications()
        
    def _dismiss_notification(self, notification_id: str):
        """Descarta una notificación."""
        self.notification_manager.dismiss_notification(notification_id)
        self.load_notifications()
        
    def mark_all_read(self):
        """Marca todas las notificaciones como leídas."""
        for notification in self.notification_manager.notifications:
            if not notification.dismissed:
                notification.read = True
        self.load_notifications()
        
    def on_notification_clicked(self, item):
        """Maneja el clic en una notificación."""
        # Encontrar la notificación correspondiente
        row = self.notifications_list.row(item)
        notifications = self.notification_manager.get_notifications()
        
        # Aplicar los mismos filtros para obtener la notificación correcta
        type_filter = self.filter_type.currentData()
        if type_filter and type_filter != "all":
            notifications = [n for n in notifications if n.type.value == type_filter]
            
        read_filter = self.filter_read.currentText()
        if read_filter == "No leídas":
            notifications = [n for n in notifications if not n.read]
        elif read_filter == "Leídas":
            notifications = [n for n in notifications if n.read]
            
        notifications = [n for n in notifications if not n.dismissed]
        
        if row < len(notifications):
            notification = notifications[row]
            
            # Mostrar detalles
            details = f"""
            <h3>{notification.title}</h3>
            <p><strong>Tipo:</strong> {notification.type.value.title()}</p>
            <p><strong>Prioridad:</strong> {notification.priority.name}</p>
            <p><strong>Fecha:</strong> {notification.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p><strong>Origen:</strong> {notification.source}</p>
            <br>
            <p>{notification.message}</p>
            """
            
            self.details_panel.setHtml(details)
            
            # Marcar como leída si no lo está
            if not notification.read:
                self._mark_as_read(notification.id)
                
    def apply_filters(self):
        """Aplica los filtros de visualización."""
        self.load_notifications()
        
    def clear_read_notifications(self):
        """Limpia las notificaciones leídas."""
        self.notification_manager.notifications = [
            n for n in self.notification_manager.notifications 
            if not n.read or not n.dismissed
        ]
        self.load_notifications()
        
    def send_test_notification(self):
        """Envía una notificación de prueba."""
        test_notification = Notification(
            id="test_" + str(int(datetime.now().timestamp())),
            title="Notificación de Prueba",
            message="Esta es una notificación de prueba del sistema. Verifica que todo funcione correctamente.",
            type=NotificationType.INFO,
            priority=NotificationPriority.NORMAL,
            timestamp=datetime.now(),
            source="test_panel"
        )
        
        self.notification_manager.add_notification(test_notification)
        
    def _on_new_notification(self, notification: Notification):
        """Maneja nuevas notificaciones."""
        # Recargar la lista
        self.load_notifications()
        
        # Mostrar toast
        self.show_toast_notification(notification)
            
    def show_toast_notification(self, notification: Notification):
        """Muestra una notificación toast."""
        if self.current_toast:
            self.current_toast.close()
            
        self.current_toast = NotificationToast(notification)
        self.current_toast.show_toast()

# Función auxiliar para crear notificaciones rápidas
def create_notification(title: str, message: str, 
                       notif_type: NotificationType = NotificationType.INFO,
                       priority: NotificationPriority = NotificationPriority.NORMAL,
                       source: str = "system") -> Notification:
    """Crea una notificación con parámetros básicos."""
    return Notification(
        id="",  # Se generará automáticamente
        title=title,
        message=message,
        type=notif_type,
        priority=priority,
        timestamp=datetime.now(),
        source=source
    )

# Instancia global del gestor de notificaciones
notification_manager = NotificationManager()

# Funciones de conveniencia para enviar notificaciones
def send_info(title: str, message: str, source: str = "system"):
    """Envía una notificación de información."""
    notification = create_notification(title, message, NotificationType.INFO, NotificationPriority.NORMAL, source)
    notification_manager.add_notification(notification)

def send_success(title: str, message: str, source: str = "system"):
    """Envía una notificación de éxito."""
    notification = create_notification(title, message, NotificationType.SUCCESS, NotificationPriority.NORMAL, source)
    notification_manager.add_notification(notification)

def send_warning(title: str, message: str, source: str = "system"):
    """Envía una notificación de advertencia."""
    notification = create_notification(title, message, NotificationType.WARNING, NotificationPriority.HIGH, source)
    notification_manager.add_notification(notification)

def send_error(title: str, message: str, source: str = "system"):
    """Envía una notificación de error."""
    notification = create_notification(title, message, NotificationType.ERROR, NotificationPriority.CRITICAL, source)
    notification_manager.add_notification(notification)

def send_system(title: str, message: str, source: str = "system"):
    """Envía una notificación del sistema."""
    notification = create_notification(title, message, NotificationType.SYSTEM, NotificationPriority.NORMAL, source)
    notification_manager.add_notification(notification)