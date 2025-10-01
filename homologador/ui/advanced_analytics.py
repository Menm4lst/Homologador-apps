"""
Sistema de Analytics Avanzado para EL OMO LOGADOR 🥵.

Proporciona gráficos interactivos, métricas en tiempo real y analytics
para dashboard administrativo con visualizaciones hermosas.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
import logging
import sqlite3

from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QSize
from PyQt6.QtGui import QColor, QFont, QPainter, QPen, QBrush, QLinearGradient, QMouseEvent
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QGridLayout, QScrollArea, QGroupBox, QProgressBar, QDialog
)

from ..core.storage import get_database_manager

logger = logging.getLogger(__name__)


class AnalyticsData:
    """Clase para manejar datos de analytics."""
    
    def __init__(self):
        self.db_manager = get_database_manager()
    
    def get_homologations_by_month(self, months: int = 12) -> List[Tuple[str, int]]:
        """Obtiene homologaciones por mes para los últimos N meses."""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                # Calcular fecha de inicio
                start_date = datetime.now() - timedelta(days=months * 30)
                
                cursor.execute("""
                    SELECT 
                        strftime('%Y-%m', homologation_date) as month,
                        COUNT(*) as count
                    FROM homologations 
                    WHERE homologation_date >= ?
                    GROUP BY strftime('%Y-%m', homologation_date)
                    ORDER BY month
                """, (start_date.strftime('%Y-%m-%d'),))
                
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error obteniendo homologaciones por mes: {e}")
            return []
    
    def get_top_applications(self, limit: int = 10) -> List[Tuple[str, int]]:
        """Obtiene las aplicaciones más homologadas."""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT real_name, COUNT(*) as count
                    FROM homologations 
                    GROUP BY real_name
                    ORDER BY count DESC
                    LIMIT ?
                """, (limit,))
                
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error obteniendo top aplicaciones: {e}")
            return []
    
    def get_user_activity(self) -> List[Tuple[str, int]]:
        """Obtiene actividad por usuario."""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT 
                        u.username,
                        COUNT(h.id) as homologations_count
                    FROM users u
                    LEFT JOIN homologations h ON u.id = h.created_by
                    WHERE u.is_active = 1
                    GROUP BY u.username
                    ORDER BY homologations_count DESC
                """)
                
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error obteniendo actividad de usuarios: {e}")
            return []
    
    def get_repository_stats(self) -> List[Tuple[str, int]]:
        """Obtiene estadísticas por repositorio."""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT 
                        COALESCE(repository, 'Sin repositorio') as repo,
                        COUNT(*) as count
                    FROM homologations 
                    GROUP BY repository
                    ORDER BY count DESC
                """)
                
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error obteniendo stats de repositorio: {e}")
            return []
    
    def get_weekly_activity(self) -> List[Tuple[str, int]]:
        """Obtiene actividad de los últimos 7 días."""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                # Últimos 7 días
                start_date = datetime.now() - timedelta(days=7)
                
                cursor.execute("""
                    SELECT 
                        strftime('%Y-%m-%d', homologation_date) as day,
                        COUNT(*) as count
                    FROM homologations 
                    WHERE homologation_date >= ?
                    GROUP BY strftime('%Y-%m-%d', homologation_date)
                    ORDER BY day
                """, (start_date.strftime('%Y-%m-%d'),))
                
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error obteniendo actividad semanal: {e}")
            return []


class BarChartWidget(QWidget):
    """Widget para gráfico de barras personalizado."""
    
    def __init__(self, title: str = "", data: List[Tuple[str, int]] = None):
        super().__init__()
        self.title = title
        self.data = data or []
        self.setMinimumHeight(200)
        self.setMinimumWidth(300)
    
    def set_data(self, data: List[Tuple[str, int]]):
        """Actualiza los datos del gráfico."""
        self.data = data
        self.update()
    
    def paintEvent(self, event):
        """Dibuja el gráfico de barras."""
        if not self.data:
            return
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Configuración
        margin = 40
        chart_width = self.width() - 2 * margin
        chart_height = self.height() - 2 * margin - 30  # Espacio para título
        
        # Título
        painter.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        painter.setPen(QColor("#ffffff"))
        painter.drawText(0, 0, self.width(), 30, Qt.AlignmentFlag.AlignCenter, self.title)
        
        if not self.data:
            return
        
        # Encontrar valor máximo
        max_value = max(value for _, value in self.data) if self.data else 1
        
        # Dibujar barras
        bar_width = chart_width // len(self.data) - 5
        colors = [
            QColor("#ff6b6b"), QColor("#4ecdc4"), QColor("#45b7d1"),
            QColor("#96ceb4"), QColor("#feca57"), QColor("#ff9ff3"),
            QColor("#54a0ff"), QColor("#5f27cd"), QColor("#00d2d3"),
            QColor("#ff9f43")
        ]
        
        for i, (label, value) in enumerate(self.data):
            # Posición y tamaño de la barra
            x = margin + i * (bar_width + 5)
            bar_height = int((value / max_value) * chart_height) if max_value > 0 else 0
            y = margin + 30 + chart_height - bar_height
            
            # Gradiente para la barra
            color = colors[i % len(colors)]
            gradient = QLinearGradient(0, y, 0, y + bar_height)
            gradient.setColorAt(0, color.lighter(150))
            gradient.setColorAt(1, color.darker(110))
            
            # Dibujar barra
            painter.setBrush(QBrush(gradient))
            painter.setPen(QPen(color.darker(130), 2))
            painter.drawRect(x, y, bar_width, bar_height)
            
            # Valor en la parte superior
            painter.setPen(QColor("#ffffff"))
            painter.setFont(QFont("Arial", 9, QFont.Weight.Bold))
            painter.drawText(x, y - 5, bar_width, 15, Qt.AlignmentFlag.AlignCenter, str(value))
            
            # Etiqueta en la parte inferior (rotada si es necesario)
            painter.save()
            painter.translate(x + bar_width // 2, margin + 30 + chart_height + 15)
            if len(label) > 8:
                painter.rotate(-45)
            painter.setFont(QFont("Arial", 8))
            painter.drawText(-50, 0, 100, 15, Qt.AlignmentFlag.AlignCenter, label[:15])
            painter.restore()


class DonutChartWidget(QWidget):
    """Widget para gráfico de dona personalizado."""
    
    def __init__(self, title: str = "", data: List[Tuple[str, int]] = None):
        super().__init__()
        self.title = title
        self.data = data or []
        self.setMinimumHeight(250)
        self.setMinimumWidth(250)
    
    def set_data(self, data: List[Tuple[str, int]]):
        """Actualiza los datos del gráfico."""
        self.data = data
        self.update()
    
    def paintEvent(self, event):
        """Dibuja el gráfico de dona."""
        if not self.data:
            return
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Configuración
        center_x = self.width() // 2
        center_y = self.height() // 2
        outer_radius = min(self.width(), self.height()) // 2 - 50
        inner_radius = outer_radius // 2
        
        # Título
        painter.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        painter.setPen(QColor("#ffffff"))
        painter.drawText(0, 0, self.width(), 30, Qt.AlignmentFlag.AlignCenter, self.title)
        
        if not self.data:
            return
        
        # Calcular total
        total = sum(value for _, value in self.data)
        if total == 0:
            return
        
        # Colores
        colors = [
            QColor("#ff6b6b"), QColor("#4ecdc4"), QColor("#45b7d1"),
            QColor("#96ceb4"), QColor("#feca57"), QColor("#ff9ff3"),
            QColor("#54a0ff"), QColor("#5f27cd")
        ]
        
        # Dibujar segmentos
        start_angle = 0
        for i, (label, value) in enumerate(self.data):
            span_angle = int((value / total) * 360 * 16)  # Qt usa 1/16 de grado
            
            color = colors[i % len(colors)]
            
            # Gradiente radial
            gradient = QLinearGradient(center_x - outer_radius, center_y - outer_radius,
                                     center_x + outer_radius, center_y + outer_radius)
            gradient.setColorAt(0, color.lighter(130))
            gradient.setColorAt(1, color.darker(110))
            
            painter.setBrush(QBrush(gradient))
            painter.setPen(QPen(color.darker(130), 2))
            
            # Dibujar segmento
            painter.drawPie(center_x - outer_radius, center_y - outer_radius,
                          outer_radius * 2, outer_radius * 2, start_angle, span_angle)
            
            start_angle += span_angle
        
        # Círculo interior (hacer dona)
        painter.setBrush(QBrush(QColor("#2c3e50")))
        painter.setPen(QPen(QColor("#34495e"), 2))
        painter.drawEllipse(center_x - inner_radius, center_y - inner_radius,
                          inner_radius * 2, inner_radius * 2)
        
        # Texto central
        painter.setPen(QColor("#ffffff"))
        painter.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        painter.drawText(center_x - 30, center_y - 10, 60, 20,
                        Qt.AlignmentFlag.AlignCenter, str(total))


class LineChartWidget(QWidget):
    """Widget para gráfico de líneas personalizado."""
    
    def __init__(self, title: str = "", data: List[Tuple[str, int]] = None):
        super().__init__()
        self.title = title
        self.data = data or []
        self.setMinimumHeight(200)
        self.setMinimumWidth(300)
    
    def set_data(self, data: List[Tuple[str, int]]):
        """Actualiza los datos del gráfico."""
        self.data = data
        self.update()
    
    def paintEvent(self, event):
        """Dibuja el gráfico de líneas."""
        if not self.data:
            return
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Configuración
        margin = 40
        chart_width = self.width() - 2 * margin
        chart_height = self.height() - 2 * margin - 30
        
        # Título
        painter.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        painter.setPen(QColor("#ffffff"))
        painter.drawText(0, 0, self.width(), 30, Qt.AlignmentFlag.AlignCenter, self.title)
        
        if len(self.data) < 2:
            return
        
        # Encontrar valor máximo y mínimo
        values = [value for _, value in self.data]
        max_value = max(values)
        min_value = min(values)
        value_range = max_value - min_value if max_value != min_value else 1
        
        # Dibujar línea
        painter.setPen(QPen(QColor("#4ecdc4"), 3))
        
        points = []
        for i, (_, value) in enumerate(self.data):
            x = margin + (i / (len(self.data) - 1)) * chart_width
            y = margin + 30 + chart_height - ((value - min_value) / value_range) * chart_height
            points.append((x, y))
        
        # Dibujar líneas conectoras
        for i in range(len(points) - 1):
            painter.drawLine(int(points[i][0]), int(points[i][1]),
                           int(points[i+1][0]), int(points[i+1][1]))
        
        # Dibujar puntos
        painter.setBrush(QBrush(QColor("#ff6b6b")))
        painter.setPen(QPen(QColor("#c0392b"), 2))
        
        for i, ((label, value), (x, y)) in enumerate(zip(self.data, points)):
            # Punto
            painter.drawEllipse(int(x-4), int(y-4), 8, 8)
            
            # Valor
            painter.setPen(QColor("#ffffff"))
            painter.setFont(QFont("Arial", 9, QFont.Weight.Bold))
            painter.drawText(int(x-15), int(y-15), 30, 15, Qt.AlignmentFlag.AlignCenter, str(value))
            
            # Etiqueta
            painter.setFont(QFont("Arial", 8))
            painter.drawText(int(x-30), margin + 30 + chart_height + 5, 60, 15,
                           Qt.AlignmentFlag.AlignCenter, label[-5:])  # Últimos 5 caracteres


class MetricCardAdvanced(QFrame):
    """Tarjeta de métrica avanzada con estilo mejorado."""
    
    clicked = pyqtSignal(str)
    
    def __init__(self, title: str, value: str, subtitle: str = "",
                 color: str = "#3498db", icon: str = "📊"):
        super().__init__()
        self.title = title
        self.metric_color = color
        self.setFrameStyle(QFrame.Shape.Box)
        self.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #2c3e50, stop:1 #34495e);
                border: 2px solid {color};
                border-radius: 15px;
                padding: 10px;
                margin: 5px;
            }}
            QFrame:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #34495e, stop:1 #2c3e50);
                border: 2px solid {color};
                transform: scale(1.02);
            }}
        """)
        
        layout = QVBoxLayout(self)
        
        # Icono y título
        header_layout = QHBoxLayout()
        
        icon_label = QLabel(icon)
        icon_label.setFont(QFont("Arial", 20))
        icon_label.setFixedSize(40, 40)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        title_label.setStyleSheet(f"color: {color}; margin-left: 10px;")
        
        header_layout.addWidget(icon_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        # Valor principal
        value_label = QLabel(value)
        value_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        value_label.setStyleSheet("color: #ffffff; margin: 10px 0;")
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Subtítulo
        if subtitle:
            subtitle_label = QLabel(subtitle)
            subtitle_label.setFont(QFont("Arial", 10))
            subtitle_label.setStyleSheet("color: #bdc3c7;")
            subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addLayout(header_layout)
        layout.addWidget(value_label)
        if subtitle:
            layout.addWidget(subtitle_label)
        
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedSize(200, 120)
    
    def mousePressEvent(self, event: QMouseEvent):
        """Maneja el clic en la tarjeta."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.title)


class AdvancedAnalyticsWidget(QWidget):
    """Widget principal de analytics avanzado."""
    
    def __init__(self):
        super().__init__()
        self.analytics_data = AnalyticsData()
        self.setup_ui()
        self.setup_timer()
    
    def setup_ui(self):
        """Configura la interfaz de usuario."""
        layout = QVBoxLayout(self)
        
        # Título principal
        title_label = QLabel("📊 ANALYTICS AVANZADO - EL OMO LOGADOR 🥵")
        title_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                color: #ff6b6b;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2c3e50, stop:1 #34495e);
                border: 2px solid #ff6b6b;
                border-radius: 10px;
                padding: 15px;
                margin: 10px;
            }
        """)
        layout.addWidget(title_label)
        
        # Área de desplazamiento
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # Métricas principales
        self.create_metrics_section(scroll_layout)
        
        # Gráficos
        self.create_charts_section(scroll_layout)
        
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)
    
    def create_metrics_section(self, layout: QVBoxLayout):
        """Crea la sección de métricas principales."""
        metrics_group = QGroupBox("🎯 Métricas Principales")
        metrics_group.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        metrics_group.setStyleSheet("""
            QGroupBox {
                color: #ffffff;
                border: 2px solid #3498db;
                border-radius: 10px;
                margin: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        metrics_layout = QGridLayout(metrics_group)
        
        # Tarjetas de métricas
        self.total_card = MetricCardAdvanced("Total Homologaciones", "0", "En el sistema", "#e74c3c", "📋")
        self.monthly_card = MetricCardAdvanced("Este Mes", "0", "Nuevas homologaciones", "#27ae60", "📅")
        self.users_card = MetricCardAdvanced("Usuarios Activos", "0", "En el sistema", "#3498db", "👥")
        self.repos_card = MetricCardAdvanced("Repositorios", "0", "Diferentes repos", "#9b59b6", "🗂️")
        
        metrics_layout.addWidget(self.total_card, 0, 0)
        metrics_layout.addWidget(self.monthly_card, 0, 1)
        metrics_layout.addWidget(self.users_card, 0, 2)
        metrics_layout.addWidget(self.repos_card, 0, 3)
        
        layout.addWidget(metrics_group)
    
    def create_charts_section(self, layout: QVBoxLayout):
        """Crea la sección de gráficos."""
        charts_group = QGroupBox("📈 Gráficos y Tendencias")
        charts_group.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        charts_group.setStyleSheet("""
            QGroupBox {
                color: #ffffff;
                border: 2px solid #e67e22;
                border-radius: 10px;
                margin: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        charts_layout = QGridLayout(charts_group)
        
        # Gráficos
        self.monthly_chart = BarChartWidget("Homologaciones por Mes")
        self.monthly_chart.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #2c3e50, stop:1 #34495e);
                border: 1px solid #34495e;
                border-radius: 10px;
                margin: 5px;
            }
        """)
        
        self.apps_chart = DonutChartWidget("Top Aplicaciones")
        self.apps_chart.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #2c3e50, stop:1 #34495e);
                border: 1px solid #34495e;
                border-radius: 10px;
                margin: 5px;
            }
        """)
        
        self.weekly_chart = LineChartWidget("Actividad Semanal")
        self.weekly_chart.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #2c3e50, stop:1 #34495e);
                border: 1px solid #34495e;
                border-radius: 10px;
                margin: 5px;
            }
        """)
        
        charts_layout.addWidget(self.monthly_chart, 0, 0)
        charts_layout.addWidget(self.apps_chart, 0, 1)
        charts_layout.addWidget(self.weekly_chart, 1, 0, 1, 2)
        
        layout.addWidget(charts_group)
    
    def setup_timer(self):
        """Configura el timer para actualización automática."""
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_analytics)
        self.update_timer.start(30000)  # Actualizar cada 30 segundos
        
        # Actualización inicial
        self.update_analytics()
    
    def update_analytics(self):
        """Actualiza todos los datos de analytics."""
        try:
            # Actualizar métricas principales
            self.update_main_metrics()
            
            # Actualizar gráficos
            self.update_charts()
            
        except Exception as e:
            logger.error(f"Error actualizando analytics: {e}")
    
    def update_main_metrics(self):
        """Actualiza las métricas principales."""
        try:
            # Total de homologaciones
            monthly_data = self.analytics_data.get_homologations_by_month(12)
            total_homologations = sum(count for _, count in monthly_data)
            
            # Este mes
            current_month = datetime.now().strftime('%Y-%m')
            this_month = next((count for month, count in monthly_data if month == current_month), 0)
            
            # Usuarios activos
            user_activity = self.analytics_data.get_user_activity()
            active_users = len([user for user, count in user_activity if count > 0])
            
            # Repositorios
            repo_stats = self.analytics_data.get_repository_stats()
            total_repos = len(repo_stats)
            
            # Actualizar tarjetas
            self.total_card.findChild(QLabel).setText(str(total_homologations))
            self.monthly_card.findChild(QLabel).setText(str(this_month))
            self.users_card.findChild(QLabel).setText(str(active_users))
            self.repos_card.findChild(QLabel).setText(str(total_repos))
            
        except Exception as e:
            logger.error(f"Error actualizando métricas principales: {e}")
    
    def update_charts(self):
        """Actualiza los gráficos."""
        try:
            # Gráfico mensual
            monthly_data = self.analytics_data.get_homologations_by_month(6)
            formatted_monthly = [(month.split('-')[1], count) for month, count in monthly_data]
            self.monthly_chart.set_data(formatted_monthly)
            
            # Gráfico de aplicaciones top
            top_apps = self.analytics_data.get_top_applications(5)
            self.apps_chart.set_data(top_apps)
            
            # Gráfico semanal
            weekly_data = self.analytics_data.get_weekly_activity()
            formatted_weekly = [(day.split('-')[2], count) for day, count in weekly_data]
            self.weekly_chart.set_data(formatted_weekly)
            
        except Exception as e:
            logger.error(f"Error actualizando gráficos: {e}")


def show_advanced_analytics(parent=None) -> QDialog:
    """Muestra el diálogo de analytics avanzado."""
    dialog = QDialog(parent)
    dialog.setWindowTitle("📊 Analytics Avanzado - EL OMO LOGADOR 🥵")
    dialog.setModal(True)
    dialog.resize(1000, 700)
    
    layout = QVBoxLayout(dialog)
    analytics_widget = AdvancedAnalyticsWidget()
    layout.addWidget(analytics_widget)
    
    return dialog