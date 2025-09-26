"""
Script de prueba para integrar notificaciones con el sistema principal.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt, QTimer
from datetime import datetime

from homologador.ui.notification_system import (
    NotificationPanel, notification_manager, NotificationBadge,
    send_info, send_success, send_warning, send_error, send_system
)

class IntegratedTestWindow(QMainWindow):
    """Ventana de prueba que simula la integración con el sistema principal."""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.start_demo()
        
    def setup_ui(self):
        """Configura la interfaz de prueba."""
        self.setWindowTitle("🔔 Sistema de Notificaciones - Prueba de Integración")
        self.setGeometry(100, 100, 1400, 900)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QHBoxLayout(central_widget)
        
        # Panel izquierdo - Simulación de acciones del sistema
        left_panel = QWidget()
        left_panel.setMaximumWidth(300)
        left_layout = QVBoxLayout(left_panel)
        
        # Título
        title_label = QLabel("🎮 Simulador de Sistema")
        title_label.setStyleSheet("font-weight: bold; font-size: 16px; margin-bottom: 15px;")
        left_layout.addWidget(title_label)
        
        # Badge de notificaciones
        badge_layout = QHBoxLayout()
        badge_label = QLabel("Notificaciones pendientes:")
        self.notification_badge = NotificationBadge(notification_manager)
        badge_layout.addWidget(badge_label)
        badge_layout.addWidget(self.notification_badge)
        badge_layout.addStretch()
        left_layout.addLayout(badge_layout)
        
        left_layout.addWidget(QLabel())  # Espaciador
        
        # Simulaciones de acciones del sistema
        sim_label = QLabel("🔄 Simulaciones Automáticas:")
        sim_label.setStyleSheet("font-weight: bold; margin-top: 20px;")
        left_layout.addWidget(sim_label)
        
        self.auto_demo_btn = QPushButton("▶️ Iniciar Demo Automático")
        self.auto_demo_btn.clicked.connect(self.toggle_auto_demo)
        left_layout.addWidget(self.auto_demo_btn)
        
        user_actions_label = QLabel("👤 Acciones de Usuario:")
        user_actions_label.setStyleSheet("font-weight: bold; margin-top: 20px;")
        left_layout.addWidget(user_actions_label)
        
        # Botones de simulación
        login_btn = QPushButton("🔐 Simular Login")
        login_btn.clicked.connect(self.simulate_login)
        left_layout.addWidget(login_btn)
        
        save_btn = QPushButton("💾 Simular Guardado")
        save_btn.clicked.connect(self.simulate_save)
        left_layout.addWidget(save_btn)
        
        error_btn = QPushButton("❌ Simular Error")
        error_btn.clicked.connect(self.simulate_error)
        left_layout.addWidget(error_btn)
        
        backup_btn = QPushButton("🗄️ Simular Backup")
        backup_btn.clicked.connect(self.simulate_backup)
        left_layout.addWidget(backup_btn)
        
        system_btn = QPushButton("⚙️ Mantenimiento Sistema")
        system_btn.clicked.connect(self.simulate_maintenance)
        left_layout.addWidget(system_btn)
        
        left_layout.addStretch()
        
        # Estadísticas
        stats_label = QLabel("📊 Estadísticas:")
        stats_label.setStyleSheet("font-weight: bold; margin-top: 20px;")
        left_layout.addWidget(stats_label)
        
        self.stats_label = QLabel("Total notificaciones: 0\\nNo leídas: 0")
        self.stats_label.setStyleSheet("margin-left: 10px; color: #666;")
        left_layout.addWidget(self.stats_label)
        
        # Panel derecho - Centro de notificaciones
        self.notification_panel = NotificationPanel(notification_manager)
        
        layout.addWidget(left_panel)
        layout.addWidget(self.notification_panel)
        
        # Timer para demo automático
        self.auto_timer = QTimer()
        self.auto_timer.timeout.connect(self.auto_demo_step)
        self.demo_step = 0
        self.auto_demo_running = False
        
        # Timer para actualizar estadísticas
        self.stats_timer = QTimer()
        self.stats_timer.timeout.connect(self.update_stats)
        self.stats_timer.start(1000)  # Actualizar cada segundo
        
    def start_demo(self):
        """Inicia la demostración con notificaciones de bienvenida."""
        send_success(
            "Sistema Iniciado",
            "¡Bienvenido al sistema de notificaciones integrado! Todas las funciones están operativas.",
            "sistema_inicio"
        )
        
        send_info(
            "Demo Interactiva",
            "Utiliza los botones de la izquierda para simular diferentes acciones del sistema y ver cómo se generan las notificaciones.",
            "demo_inicio"
        )
        
    def toggle_auto_demo(self):
        """Activa/desactiva la demostración automática."""
        if self.auto_demo_running:
            self.auto_timer.stop()
            self.auto_demo_running = False
            self.auto_demo_btn.setText("▶️ Iniciar Demo Automático")
            send_system("Demo Automático Detenido", "La demostración automática se ha detenido.", "demo_control")
        else:
            self.auto_timer.start(3000)  # Cada 3 segundos
            self.auto_demo_running = True
            self.auto_demo_btn.setText("⏸️ Detener Demo Automático")
            send_system("Demo Automático Iniciado", "La demostración automática está ejecutándose. Se generarán notificaciones cada 3 segundos.", "demo_control")
            
    def auto_demo_step(self):
        """Ejecuta un paso de la demostración automática."""
        demo_actions = [
            self.simulate_login,
            self.simulate_save,
            self.simulate_backup,
            self.simulate_maintenance,
            self.simulate_warning,
            self.simulate_user_activity
        ]
        
        action = demo_actions[self.demo_step % len(demo_actions)]
        action()
        self.demo_step += 1
        
    def simulate_login(self):
        """Simula un evento de login."""
        send_success(
            "Usuario Conectado",
            f"El usuario 'admin' se ha conectado exitosamente al sistema a las {datetime.now().strftime('%H:%M:%S')}.",
            "auth_system"
        )
        
    def simulate_save(self):
        """Simula un guardado de datos."""
        send_success(
            "Datos Guardados",
            f"Los datos se han guardado correctamente en la base de datos. Operación completada a las {datetime.now().strftime('%H:%M:%S')}.",
            "data_management"
        )
        
    def simulate_error(self):
        """Simula un error del sistema."""
        send_error(
            "Error de Conexión",
            f"Se perdió la conexión con el servidor de base de datos. Error detectado a las {datetime.now().strftime('%H:%M:%S')}. Reintentando automáticamente...",
            "database_system"
        )
        
    def simulate_backup(self):
        """Simula un proceso de backup."""
        send_info(
            "Backup Programado",
            f"Iniciando backup automático del sistema. Proceso comenzado a las {datetime.now().strftime('%H:%M:%S')}. Tiempo estimado: 5 minutos.",
            "backup_system"
        )
        
    def simulate_maintenance(self):
        """Simula mantenimiento del sistema."""
        send_system(
            "Mantenimiento Programado",
            f"El sistema realizará mantenimiento automático a las {datetime.now().strftime('%H:%M:%S')}. No se interrumpirán las operaciones normales.",
            "maintenance_system"
        )
        
    def simulate_warning(self):
        """Simula una advertencia del sistema."""
        send_warning(
            "Espacio en Disco Bajo",
            f"El espacio disponible en disco está por debajo del 15%. Se recomienda liberar espacio o expandir el almacenamiento. Verificado a las {datetime.now().strftime('%H:%M:%S')}.",
            "storage_monitor"
        )
        
    def simulate_user_activity(self):
        """Simula actividad de usuarios."""
        activities = [
            ("Nueva Homologación", "Se ha creado una nueva homologación en el sistema.", "homolog_system"),
            ("Reporte Generado", "El reporte mensual se ha generado automáticamente.", "report_system"),
            ("Usuario Registrado", "Un nuevo usuario se ha registrado en el sistema.", "user_management"),
            ("Actualización Disponible", "Hay una nueva actualización disponible para el sistema.", "update_system")
        ]
        
        import random
        title, message, source = random.choice(activities)
        
        timestamp = datetime.now().strftime('%H:%M:%S')
        full_message = f"{message} Timestamp: {timestamp}"
        
        send_info(title, full_message, source)
        
    def update_stats(self):
        """Actualiza las estadísticas de notificaciones."""
        total = len(notification_manager.notifications)
        unread = notification_manager.get_unread_count()
        
        self.stats_label.setText(f"Total notificaciones: {total}\\nNo leídas: {unread}")

def main():
    """Función principal para ejecutar la prueba."""
    app = QApplication(sys.argv)
    
    # Configurar estilo básico
    app.setStyle('Fusion')
    
    # Crear y mostrar ventana principal
    window = IntegratedTestWindow()
    window.show()
    
    # Ejecutar aplicación
    sys.exit(app.exec())

if __name__ == "__main__":
    main()