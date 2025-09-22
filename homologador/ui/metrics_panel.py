"""
Panel de métricas y estadísticas para el dashboard.
Muestra gráficos y estadísticas de homologaciones con indicadores visuales.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import sqlite3

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, 
    QFrame, QScrollArea, QGroupBox, QPushButton, QComboBox,
    QProgressBar, QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread, pyqtSlot
from PyQt6.QtGui import QFont, QPalette, QColor

from core.storage import get_homologation_repository
from .theme import get_current_theme, ThemeType

logger = logging.getLogger(__name__)


class MetricsDataWorker(QThread):
    """Worker thread para calcular métricas sin bloquear la UI."""
    
    metrics_calculated = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, date_range: str = "30"):
        super().__init__()
        self.date_range = date_range
        self.repo = get_homologation_repository()
    
    def run(self):
        """Calcula métricas en segundo plano."""
        try:
            metrics = self.calculate_metrics()
            self.metrics_calculated.emit(metrics)
        except Exception as e:
            logger.error(f"Error calculando métricas: {e}")
            self.error_occurred.emit(str(e))
    
    def calculate_metrics(self) -> Dict[str, Any]:
        """Calcula todas las métricas necesarias."""
        # Calcular fecha límite
        days_back = int(self.date_range)
        date_limit = datetime.now() - timedelta(days=days_back)
        
        # Obtener datos básicos
        all_homologations_raw = self.repo.get_all()
        all_homologations = [dict(h) for h in all_homologations_raw]
        recent_homologations = [
            h for h in all_homologations 
            if datetime.fromisoformat(h.get('created_at', '2000-01-01')) >= date_limit
        ]
        
        # Métricas básicas
        total_count = len(all_homologations)
        recent_count = len(recent_homologations)
        
        # Calcular métricas de estado
        status_counts = {}
        for h in all_homologations:
            status = h.get('status', 'unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Métricas de repositorio
        repo_counts = {}
        for h in all_homologations:
            repo = h.get('repository_url', 'Sin repositorio')
            if repo and repo.strip():
                # Extraer nombre del repositorio
                repo_name = repo.split('/')[-1] if '/' in repo else repo
                repo_counts[repo_name] = repo_counts.get(repo_name, 0) + 1
        
        # Top 5 repositorios
        top_repos = sorted(repo_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Tendencias por día (últimos 7 días)
        daily_counts = {}
        for i in range(7):
            day = datetime.now() - timedelta(days=i)
            day_str = day.strftime('%Y-%m-%d')
            daily_counts[day_str] = 0
        
        for h in recent_homologations:
            created_date = datetime.fromisoformat(h.get('created_at', '2000-01-01'))
            day_str = created_date.strftime('%Y-%m-%d')
            if day_str in daily_counts:
                daily_counts[day_str] += 1
        
        # Calcular tasa de crecimiento
        if len(all_homologations) > 0:
            # Comparar con período anterior
            prev_date_limit = date_limit - timedelta(days=days_back)
            prev_homologations = [
                h for h in all_homologations 
                if prev_date_limit <= datetime.fromisoformat(h.get('created_at', '2000-01-01')) < date_limit
            ]
            prev_count = len(prev_homologations)
            
            if prev_count > 0:
                growth_rate = ((recent_count - prev_count) / prev_count) * 100
            else:
                growth_rate = 100.0 if recent_count > 0 else 0.0
        else:
            growth_rate = 0.0
        
        return {
            'total_count': total_count,
            'recent_count': recent_count,
            'growth_rate': growth_rate,
            'status_counts': status_counts,
            'top_repositories': top_repos,
            'daily_trends': daily_counts,
            'date_range': days_back
        }


class MetricCard(QFrame):
    """Tarjeta individual para mostrar una métrica."""
    
    def __init__(self, title: str, value: str, subtitle: str = "", trend: Optional[float] = None):
        super().__init__()
        self.setup_ui(title, value, subtitle, trend)
    
    def setup_ui(self, title: str, value: str, subtitle: str, trend: Optional[float]):
        """Configura la interfaz de la tarjeta de métrica."""
        self.setFrameStyle(QFrame.Shape.Box)
        self.setLineWidth(1)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(5)
        
        # Título
        title_label = QLabel(title)
        title_font = QFont()
        title_font.setPointSize(9)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Valor principal
        value_label = QLabel(value)
        value_font = QFont()
        value_font.setPointSize(24)
        value_font.setBold(True)
        value_label.setFont(value_font)
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(value_label)
        
        # Subtítulo
        if subtitle:
            subtitle_label = QLabel(subtitle)
            subtitle_font = QFont()
            subtitle_font.setPointSize(8)
            subtitle_label.setFont(subtitle_font)
            subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(subtitle_label)
        
        # Indicador de tendencia
        if trend is not None:
            trend_label = QLabel(f"{trend:+.1f}%")
            trend_font = QFont()
            trend_font.setPointSize(10)
            trend_font.setBold(True)
            trend_label.setFont(trend_font)
            trend_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # Color según tendencia
            if trend > 0:
                trend_label.setStyleSheet("color: #28a745;")  # Verde
            elif trend < 0:
                trend_label.setStyleSheet("color: #dc3545;")  # Rojo
            else:
                trend_label.setStyleSheet("color: #6c757d;")  # Gris
            
            layout.addWidget(trend_label)
        
        self.apply_theme_styles()
    
    def apply_theme_styles(self):
        """Aplica estilos según el tema actual."""
        current_theme = get_current_theme()
        
        if current_theme == ThemeType.DARK:
            self.setStyleSheet("""
                MetricCard {
                    background-color: #2d2d2d;
                    border: 1px solid #555555;
                    border-radius: 8px;
                    color: #ffffff;
                }
                QLabel {
                    color: #ffffff;
                    background-color: transparent;
                }
            """)
        else:
            self.setStyleSheet("""
                MetricCard {
                    background-color: #ffffff;
                    border: 1px solid #e0e0e0;
                    border-radius: 8px;
                    color: #333333;
                }
                QLabel {
                    color: #333333;
                    background-color: transparent;
                }
            """)


class StatusChart(QWidget):
    """Widget simple para mostrar distribución de estados."""
    
    def __init__(self, status_data: Dict[str, int]):
        super().__init__()
        self.status_data = status_data
        self.setup_ui()
    
    def setup_ui(self):
        """Configura la interfaz del gráfico de estados."""
        layout = QVBoxLayout(self)
        
        # Título
        title = QLabel("Distribución por Estado")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(12)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Lista de estados con barras de progreso
        total = sum(self.status_data.values()) if self.status_data else 1
        
        for status, count in self.status_data.items():
            row_layout = QHBoxLayout()
            
            # Etiqueta del estado
            status_label = QLabel(f"{status}:")
            status_label.setMinimumWidth(80)
            row_layout.addWidget(status_label)
            
            # Barra de progreso
            progress = QProgressBar()
            progress.setMaximum(total)
            progress.setValue(count)
            progress.setFormat(f"{count} ({count/total*100:.1f}%)")
            row_layout.addWidget(progress)
            
            layout.addLayout(row_layout)
        
        self.apply_theme_styles()
    
    def apply_theme_styles(self):
        """Aplica estilos según el tema actual."""
        current_theme = get_current_theme()
        
        if current_theme == ThemeType.DARK:
            self.setStyleSheet("""
                QLabel {
                    color: #ffffff;
                    background-color: transparent;
                }
                QProgressBar {
                    border: 1px solid #555555;
                    border-radius: 4px;
                    background-color: #2d2d2d;
                    color: #ffffff;
                }
                QProgressBar::chunk {
                    background-color: #0078d4;
                    border-radius: 3px;
                }
            """)
        else:
            self.setStyleSheet("""
                QLabel {
                    color: #333333;
                    background-color: transparent;
                }
                QProgressBar {
                    border: 1px solid #d0d0d0;
                    border-radius: 4px;
                    background-color: #f8f8f8;
                    color: #333333;
                }
                QProgressBar::chunk {
                    background-color: #0078d4;
                    border-radius: 3px;
                }
            """)


class TopRepositoriesWidget(QWidget):
    """Widget para mostrar los repositorios más utilizados."""
    
    def __init__(self, repo_data: List[tuple]):
        super().__init__()
        self.repo_data = repo_data
        self.setup_ui()
    
    def setup_ui(self):
        """Configura la interfaz del widget de repositorios."""
        layout = QVBoxLayout(self)
        
        # Título
        title = QLabel("Top 5 Repositorios")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(12)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Tabla simple
        table = QTableWidget(len(self.repo_data), 2)
        table.setHorizontalHeaderLabels(["Repositorio", "Cantidad"])
        
        # Configurar headers si existen
        h_header = table.horizontalHeader()
        if h_header:
            h_header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
            h_header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        
        v_header = table.verticalHeader()
        if v_header:
            v_header.setVisible(False)
            
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        # Llenar datos
        for i, (repo_name, count) in enumerate(self.repo_data):
            table.setItem(i, 0, QTableWidgetItem(repo_name))
            table.setItem(i, 1, QTableWidgetItem(str(count)))
        
        table.setMaximumHeight(200)
        layout.addWidget(table)
        
        self.apply_theme_styles()
    
    def apply_theme_styles(self):
        """Aplica estilos según el tema actual."""
        current_theme = get_current_theme()
        
        if current_theme == ThemeType.DARK:
            self.setStyleSheet("""
                QLabel {
                    color: #ffffff;
                    background-color: transparent;
                }
                QTableWidget {
                    background-color: #2d2d2d;
                    border: 1px solid #555555;
                    color: #ffffff;
                    gridline-color: #555555;
                }
                QHeaderView::section {
                    background-color: #3d3d3d;
                    color: #ffffff;
                    border: 1px solid #555555;
                    padding: 4px;
                }
            """)
        else:
            self.setStyleSheet("""
                QLabel {
                    color: #333333;
                    background-color: transparent;
                }
                QTableWidget {
                    background-color: #ffffff;
                    border: 1px solid #d0d0d0;
                    color: #333333;
                    gridline-color: #d0d0d0;
                }
                QHeaderView::section {
                    background-color: #f8f8f8;
                    color: #333333;
                    border: 1px solid #d0d0d0;
                    padding: 4px;
                }
            """)


class MetricsPanel(QWidget):
    """Panel principal de métricas y estadísticas."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.metrics_worker = None
        self.setup_ui()
        self.load_metrics()
        
        # Timer para actualización automática (cada 5 minutos)
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.load_metrics)
        self.refresh_timer.start(300000)  # 5 minutos en milisegundos
    
    def setup_ui(self):
        """Configura la interfaz del panel de métricas."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        
        # Header con controles
        header_layout = QHBoxLayout()
        
        title = QLabel("📊 Panel de Métricas")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Selector de período
        period_label = QLabel("Período:")
        header_layout.addWidget(period_label)
        
        self.period_combo = QComboBox()
        self.period_combo.addItems(["7 días", "30 días", "90 días", "1 año"])
        self.period_combo.setCurrentText("30 días")
        self.period_combo.currentTextChanged.connect(self.on_period_changed)
        header_layout.addWidget(self.period_combo)
        
        # Botón de actualizar
        refresh_button = QPushButton("🔄 Actualizar")
        refresh_button.clicked.connect(self.load_metrics)
        header_layout.addWidget(refresh_button)
        
        layout.addLayout(header_layout)
        
        # Área scrollable para métricas
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Widget contenedor para métricas
        self.metrics_widget = QWidget()
        self.metrics_layout = QVBoxLayout(self.metrics_widget)
        self.metrics_layout.setSpacing(20)
        
        scroll_area.setWidget(self.metrics_widget)
        layout.addWidget(scroll_area)
        
        # Placeholder inicial
        self.show_loading_message()
        
        self.apply_theme_styles()
    
    def show_loading_message(self):
        """Muestra mensaje de carga."""
        self.clear_metrics()
        
        loading_label = QLabel("🔄 Cargando métricas...")
        loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        loading_font = QFont()
        loading_font.setPointSize(14)
        loading_label.setFont(loading_font)
        
        self.metrics_layout.addWidget(loading_label)
    
    def clear_metrics(self):
        """Limpia las métricas actuales."""
        while self.metrics_layout.count():
            child = self.metrics_layout.takeAt(0)
            if child and child.widget():
                widget = child.widget()
                if widget:
                    widget.deleteLater()
    
    def on_period_changed(self):
        """Maneja cambios en el período seleccionado."""
        self.load_metrics()
    
    def load_metrics(self):
        """Carga métricas en segundo plano."""
        self.show_loading_message()
        
        # Obtener días del período seleccionado
        period_text = self.period_combo.currentText()
        period_map = {
            "7 días": "7",
            "30 días": "30",
            "90 días": "90",
            "1 año": "365"
        }
        days = period_map.get(period_text, "30")
        
        # Iniciar worker
        if self.metrics_worker and self.metrics_worker.isRunning():
            self.metrics_worker.terminate()
            self.metrics_worker.wait()
        
        self.metrics_worker = MetricsDataWorker(days)
        self.metrics_worker.metrics_calculated.connect(self.display_metrics)
        self.metrics_worker.error_occurred.connect(self.show_error)
        self.metrics_worker.start()
    
    @pyqtSlot(dict)
    def display_metrics(self, metrics: Dict[str, Any]):
        """Muestra las métricas calculadas."""
        self.clear_metrics()
        
        # Tarjetas de métricas principales
        cards_layout = QGridLayout()
        
        # Total de homologaciones
        total_card = MetricCard(
            "Total de Homologaciones",
            str(metrics['total_count']),
            "Todas las homologaciones"
        )
        cards_layout.addWidget(total_card, 0, 0)
        
        # Homologaciones recientes
        recent_card = MetricCard(
            f"Últimos {metrics['date_range']} días",
            str(metrics['recent_count']),
            "Homologaciones recientes",
            metrics.get('growth_rate', 0)
        )
        cards_layout.addWidget(recent_card, 0, 1)
        
        # Promedio diario
        avg_daily = metrics['recent_count'] / metrics['date_range'] if metrics['date_range'] > 0 else 0
        avg_card = MetricCard(
            "Promedio Diario",
            f"{avg_daily:.1f}",
            f"Últimos {metrics['date_range']} días"
        )
        cards_layout.addWidget(avg_card, 0, 2)
        
        # Widget contenedor para las tarjetas
        cards_widget = QWidget()
        cards_widget.setLayout(cards_layout)
        self.metrics_layout.addWidget(cards_widget)
        
        # Gráficos y tablas
        charts_layout = QHBoxLayout()
        
        # Distribución por estado
        if metrics['status_counts']:
            status_chart = StatusChart(metrics['status_counts'])
            charts_layout.addWidget(status_chart)
        
        # Top repositorios
        if metrics['top_repositories']:
            repos_widget = TopRepositoriesWidget(metrics['top_repositories'])
            charts_layout.addWidget(repos_widget)
        
        # Widget contenedor para gráficos
        charts_widget = QWidget()
        charts_widget.setLayout(charts_layout)
        self.metrics_layout.addWidget(charts_widget)
        
        # Espacio flexible
        self.metrics_layout.addStretch()
    
    @pyqtSlot(str)
    def show_error(self, error_message: str):
        """Muestra mensaje de error."""
        self.clear_metrics()
        
        error_label = QLabel(f"❌ Error cargando métricas:\n{error_message}")
        error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        error_label.setStyleSheet("color: #dc3545; font-size: 12pt;")
        
        self.metrics_layout.addWidget(error_label)
        
        # Botón para reintentar
        retry_button = QPushButton("Reintentar")
        retry_button.clicked.connect(self.load_metrics)
        self.metrics_layout.addWidget(retry_button)
        self.metrics_layout.setAlignment(retry_button, Qt.AlignmentFlag.AlignCenter)
    
    def apply_theme_styles(self):
        """Aplica estilos según el tema actual."""
        current_theme = get_current_theme()
        
        if current_theme == ThemeType.DARK:
            self.setStyleSheet("""
                MetricsPanel {
                    background-color: #1a1a1a;
                    color: #ffffff;
                }
                QLabel {
                    color: #ffffff;
                    background-color: transparent;
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
                QComboBox {
                    background-color: #2d2d2d;
                    border: 1px solid #555555;
                    border-radius: 4px;
                    padding: 4px;
                    color: #ffffff;
                }
            """)
        else:
            self.setStyleSheet("""
                MetricsPanel {
                    background-color: #f8f8f8;
                    color: #333333;
                }
                QLabel {
                    color: #333333;
                    background-color: transparent;
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
                QComboBox {
                    background-color: #ffffff;
                    border: 1px solid #d0d0d0;
                    border-radius: 4px;
                    padding: 4px;
                    color: #333333;
                }
            """)
    
    def closeEvent(self, event):
        """Limpia recursos al cerrar."""
        if self.refresh_timer:
            self.refresh_timer.stop()
        
        if self.metrics_worker and self.metrics_worker.isRunning():
            self.metrics_worker.terminate()
            self.metrics_worker.wait()
        
        event.accept()