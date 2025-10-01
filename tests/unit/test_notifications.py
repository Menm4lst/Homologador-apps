"""
Script de prueba para el sistema de notificaciones interno.
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from datetime import datetime

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QHBoxLayout

from homologador.ui.notification_system import (
    NotificationPanel, notification_manager, NotificationBadge,
    send_info, send_success, send_warning, send_error, send_system,
    NotificationType, NotificationPriority
)

class TestMainWindow(QMainWindow):
    """Ventana principal de prueba para el sistema de notificaciones."""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
        # Enviar algunas notificaciones de prueba al inicio
        QTimer.singleShot(1000, self.send_initial_notifications)
        
    def setup_ui(self):
        """Configura la interfaz de prueba."""
        self.setWindowTitle("Prueba del Sistema de Notificaciones")
        self.setGeometry(100, 100, 1200, 800)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QHBoxLayout(central_widget)
        
        # Panel de botones de prueba
        buttons_widget = QWidget()
        buttons_widget.setMaximumWidth(250)
        buttons_layout = QVBoxLayout(buttons_widget)
        
        # Título
        title_label = QPushButton("🔔 Controles de Prueba")
        title_label.setEnabled(False)
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        buttons_layout.addWidget(title_label)
        
        # Badge de notificaciones
        badge_layout = QHBoxLayout()
        badge_label = QPushButton("Notificaciones:")
        badge_label.setEnabled(False)
        self.notification_badge = NotificationBadge(notification_manager)
        badge_layout.addWidget(badge_label)
        badge_layout.addWidget(self.notification_badge)
        badge_layout.addStretch()
        buttons_layout.addLayout(badge_layout)
        
        buttons_layout.addWidget(QPushButton())  # Espaciador
        
        # Botones para enviar diferentes tipos de notificaciones
        info_btn = QPushButton("📘 Enviar Info")
        info_btn.clicked.connect(self.send_info_notification)
        buttons_layout.addWidget(info_btn)
        
        success_btn = QPushButton("✅ Enviar Éxito")
        success_btn.clicked.connect(self.send_success_notification)
        buttons_layout.addWidget(success_btn)
        
        warning_btn = QPushButton("⚠️ Enviar Advertencia")
        warning_btn.clicked.connect(self.send_warning_notification)
        buttons_layout.addWidget(warning_btn)
        
        error_btn = QPushButton("❌ Enviar Error")
        error_btn.clicked.connect(self.send_error_notification)
        buttons_layout.addWidget(error_btn)
        
        system_btn = QPushButton("⚙️ Enviar Sistema")
        system_btn.clicked.connect(self.send_system_notification)
        buttons_layout.addWidget(system_btn)
        
        buttons_layout.addWidget(QPushButton())  # Espaciador
        
        # Botones de control
        bulk_btn = QPushButton("📦 Enviar Múltiples")
        bulk_btn.clicked.connect(self.send_bulk_notifications)
        buttons_layout.addWidget(bulk_btn)
        
        clear_btn = QPushButton("🗑️ Limpiar Todo")
        clear_btn.clicked.connect(self.clear_all_notifications)
        buttons_layout.addWidget(clear_btn)
        
        buttons_layout.addStretch()
        
        # Panel de notificaciones
        self.notification_panel = NotificationPanel(notification_manager)
        
        layout.addWidget(buttons_widget)
        layout.addWidget(self.notification_panel)
        
    def send_initial_notifications(self):
        """Envía notificaciones iniciales de bienvenida."""
        send_success(
            "Sistema Iniciado", 
            "El sistema de notificaciones se ha iniciado correctamente. ¡Bienvenido!",
            "sistema_inicio"
        )
        
        send_info(
            "Centro de Pruebas",
            "Utiliza los botones de la izquierda para probar diferentes tipos de notificaciones.",
            "centro_pruebas"
        )
        
    def send_info_notification(self):
        """Envía una notificación de información."""
        send_info(
            "Información de Prueba",
            f"Esta es una notificación informativa enviada a las {datetime.now().strftime('%H:%M:%S')}. "
            "Las notificaciones de información son útiles para comunicar datos generales al usuario.",
            "prueba_manual"
        )
        
    def send_success_notification(self):
        """Envía una notificación de éxito."""
        send_success(
            "Operación Exitosa",
            f"¡Excelente! La operación se completó exitosamente a las {datetime.now().strftime('%H:%M:%S')}. "
            "Este tipo de notificación confirma que una acción se realizó correctamente.",
            "prueba_manual"
        )
        
    def send_warning_notification(self):
        """Envía una notificación de advertencia."""
        send_warning(
            "Advertencia Importante",
            f"Atención: Se detectó una situación que requiere tu atención a las {datetime.now().strftime('%H:%M:%S')}. "
            "Las advertencias te alertan sobre posibles problemas que debes revisar.",
            "prueba_manual"
        )
        
    def send_error_notification(self):
        """Envía una notificación de error."""
        send_error(
            "Error del Sistema",
            f"Error crítico detectado a las {datetime.now().strftime('%H:%M:%S')}. "
            "Los errores indican problemas serios que requieren atención inmediata. "
            "Por favor, revisa los logs del sistema para más detalles.",
            "prueba_manual"
        )
        
    def send_system_notification(self):
        """Envía una notificación del sistema."""
        send_system(
            "Notificación del Sistema",
            f"El sistema ha generado una notificación automática a las {datetime.now().strftime('%H:%M:%S')}. "
            "Este tipo de notificaciones provienen de procesos internos del sistema.",
            "prueba_manual"
        )
        
    def send_bulk_notifications(self):
        """Envía múltiples notificaciones para probar el rendimiento."""
        notifications_data = [
            ("Info", "Primera notificación de prueba masiva", NotificationType.INFO),
            ("Éxito", "Segunda notificación - operación completada", NotificationType.SUCCESS),
            ("Advertencia", "Tercera notificación - revisa la configuración", NotificationType.WARNING),
            ("Sistema", "Cuarta notificación - actualización automática", NotificationType.SYSTEM),
            ("Info", "Quinta notificación - proceso en segundo plano", NotificationType.INFO),
            ("Error", "Sexta notificación - error de conexión temporal", NotificationType.ERROR),
            ("Éxito", "Séptima notificación - backup completado", NotificationType.SUCCESS),
            ("Sistema", "Octava notificación - mantenimiento programado", NotificationType.SYSTEM),
        ]
        
        for i, (title, message, notif_type) in enumerate(notifications_data, 1):
            QTimer.singleShot(i * 500, lambda t=title, m=message, nt=notif_type: self._send_delayed_notification(t, m, nt))
            
    def _send_delayed_notification(self, title, message, notif_type):
        """Envía una notificación con delay."""
        timestamp = datetime.now().strftime('%H:%M:%S')
        full_message = f"{message} (enviada a las {timestamp})"
        
        if notif_type == NotificationType.INFO:
            send_info(title, full_message, "prueba_masiva")
        elif notif_type == NotificationType.SUCCESS:
            send_success(title, full_message, "prueba_masiva")
        elif notif_type == NotificationType.WARNING:
            send_warning(title, full_message, "prueba_masiva")
        elif notif_type == NotificationType.ERROR:
            send_error(title, full_message, "prueba_masiva")
        elif notif_type == NotificationType.SYSTEM:
            send_system(title, full_message, "prueba_masiva")
            
    def clear_all_notifications(self):
        """Limpia todas las notificaciones."""
        notification_manager.notifications.clear()
        self.notification_panel.load_notifications()
        self.notification_badge.update_count()
        
        send_info(
            "Notificaciones Limpiadas",
            "Todas las notificaciones anteriores han sido eliminadas del sistema.",
            "limpieza_manual"
        )

def main():
    """Función principal para ejecutar la prueba."""
    app = QApplication(sys.argv)
    
    # Configurar estilo básico
    app.setStyle('Fusion')
    
    # Crear y mostrar ventana principal
    window = TestMainWindow()
    window.show()
    
    # Ejecutar aplicación
    sys.exit(app.exec())

if __name__ == "__main__":
    main()