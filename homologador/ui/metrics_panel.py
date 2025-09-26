"""
Panel de métricas y estadísticas optimizado para el dashboard.
Versión completamente corregida con consultas SQL optimizadas y mejor rendimiento.
"""

import logging
import sqlite3
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from PyQt6.QtCore import Qt, QThread, QTimer, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QColor, QFont, QPalette
from PyQt6.QtWidgets import (QComboBox, QFrame, QGridLayout, QGroupBox,
                             QHBoxLayout, QHeaderView, QLabel, QProgressBar,
                             QPushButton, QScrollArea, QTableWidget,
                             QTableWidgetItem, QVBoxLayout, QWidget)

from homologador.core.storage import get_homologation_repository
from homologador.ui.theme import ThemeType, get_current_theme

logger = logging.getLogger(__name__)


class MetricsDataWorker(QThread):
    """Worker optimizado para calcular métricas sin bloquear la UI."""
    
    metrics_calculated = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, date_range: str = "30"):
        super().__init__()
        self.date_range = int(date_range)
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
        """Calcula métricas optimizadas usando consultas SQL directas."""
        
        # Fechas para los cálculos
        days_back = self.date_range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        prev_start_date = start_date - timedelta(days=days_back)
        
        # Formatear fechas para SQL
        start_date_str = start_date.strftime('%Y-%m-%d %H:%M:%S')
        prev_start_date_str = prev_start_date.strftime('%Y-%m-%d %H:%M:%S')
        
        db = self.repo.db
        
        # 1. Contar totales
        total_query = "SELECT COUNT(*) as total FROM homologations"
        total_result = db.execute_query(total_query)
        total_count = total_result[0]['total'] if total_result else 0
        
        # 2. Contar recientes
        recent_query = """
        SELECT COUNT(*) as recent 
        FROM homologations 
        WHERE created_at >= ?
        """
        recent_result = db.execute_query(recent_query, (start_date_str,))
        recent_count = recent_result[0]['recent'] if recent_result else 0
        
        # 3. Contar período anterior para growth rate
        prev_query = """
        SELECT COUNT(*) as prev_count 
        FROM homologations 
        WHERE created_at >= ? AND created_at < ?
        """
        prev_result = db.execute_query(prev_query, (prev_start_date_str, start_date_str))
        prev_count = prev_result[0]['prev_count'] if prev_result else 0
        
        # Calcular growth rate
        if prev_count > 0:
            growth_rate = ((recent_count - prev_count) / prev_count) * 100
        else:
            growth_rate = 100.0 if recent_count > 0 else 0.0
        
        # 4. Estadísticas de finalización
        status_counts = self._calculate_completion_stats(db)
        
        # 5. Estadísticas de repositorio
        top_repos = self._calculate_repository_stats(db)
        
        # 6. Tendencias diarias
        daily_counts = self._calculate_daily_trends(db, days_back)
        
        return {
            'total_count': total_count,
            'recent_count': recent_count,
            'growth_rate': round(growth_rate, 2),
            'status_counts': status_counts,
            'top_repositories': top_repos,
            'daily_trends': daily_counts,
            'date_range': days_back
        }
    
    def _calculate_completion_stats(self, db) -> Dict[str, int]:
        """Calcula estadísticas de finalización basadas en campos reales."""
        
        stats_query = """
        SELECT 
            SUM(CASE WHEN homologation_date IS NOT NULL AND homologation_date != '' THEN 1 ELSE 0 END) as completed,
            SUM(CASE WHEN kb_sync = 1 THEN 1 ELSE 0 END) as synced,
            SUM(CASE WHEN has_previous_versions = 1 THEN 1 ELSE 0 END) as with_versions,
            SUM(CASE WHEN repository_location IS NOT NULL AND repository_location != '' THEN 1 ELSE 0 END) as with_repo,
            COUNT(*) as total
        FROM homologations
        """
        
        result = db.execute_query(stats_query)
        if result:
            row = result[0]
            return {
                'Completadas': row['completed'],
                'Sincronizadas': row['synced'], 
                'Con Versiones Previas': row['with_versions'],
                'Con Repositorio': row['with_repo'],
                'Pendientes': row['total'] - row['completed']
            }
        
        return {'Sin datos': 0}
    
    def _calculate_repository_stats(self, db) -> List[tuple]:
        """Calcula estadísticas de repositorio usando el campo correcto."""
        
        repo_query = """
        SELECT 
            repository_location,
            COUNT(*) as count
        FROM homologations 
        WHERE repository_location IS NOT NULL 
            AND repository_location != ''
        GROUP BY repository_location
        ORDER BY count DESC
        LIMIT 5
        """
        
        result = db.execute_query(repo_query)
        repo_stats = []
        
        for row in result:
            repo_name = row['repository_location']
            # Extraer nombre limpio
            if '/' in repo_name:
                repo_name = repo_name.split('/')[-1]
            elif '\\' in repo_name:
                repo_name = repo_name.split('\\')[-1]
            
            repo_name = repo_name.replace('.git', '').strip()
            if repo_name:
                repo_stats.append((repo_name, row['count']))
        
        return repo_stats
    
    def _calculate_daily_trends(self, db, days: int) -> Dict[str, int]:
        """Calcula tendencias diarias."""
        
        trends = {}
        
        # Limitar a 30 días máximo para rendimiento
        max_days = min(days, 30)
        
        for i in range(max_days):
            day = datetime.now() - timedelta(days=i)
            day_key = day.strftime('%Y-%m-%d')
            trends[day_key] = 0
        
        trends_query = """
        SELECT 
            DATE(created_at) as day,
            COUNT(*) as count
        FROM homologations 
        WHERE created_at >= DATE('now', '-{} days')
        GROUP BY DATE(created_at)
        ORDER BY day DESC
        """.format(max_days)
        
        result = db.execute_query(trends_query)
        
        for row in result:
            day_key = row['day']
            if day_key in trends:
                trends[day_key] = row['count']
        
        return trends


class MetricCard(QFrame):
    """Tarjeta mejorada para mostrar una métrica."""
    
    def __init__(self, title: str, value: str, description: str = "", 
                 trend: Optional[float] = None, color: str = "#3498db"):
        super().__init__()
        self.setup_ui(title, value, description, trend, color)
    
    def setup_ui(self, title: str, value: str, description: str, 
                 trend: Optional[float], color: str):
        """Configura la UI de la tarjeta."""
        
        self.setFrameStyle(QFrame.Shape.Box)
        self.setStyleSheet(f"""
            QFrame {{
                border: 2px solid {color};
                border-radius: 8px;
                background-color: rgba(255, 255, 255, 0.1);
                padding: 15px;
                margin: 5px;
            }}
            QLabel {{
                border: none;
                background-color: transparent;
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # Título
        title_label = QLabel(title)
        title_font = QFont()
        title_font.setPointSize(11)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet(f"color: {color};")
        layout.addWidget(title_label)
        
        # Valor principal
        value_label = QLabel(str(value))
        value_font = QFont()
        value_font.setPointSize(28)
        value_font.setBold(True)
        value_label.setFont(value_font)
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(value_label)
        
        # Descripción y tendencia
        if description or trend is not None:
            desc_layout = QHBoxLayout()
            
            if description:
                desc_label = QLabel(description)
                desc_label.setStyleSheet("color: #666666; font-size: 10px;")
                desc_layout.addWidget(desc_label)
            
            if trend is not None:
                trend_text = f"{'↗' if trend >= 0 else '↘'} {abs(trend):.1f}%"
                trend_color = "#27ae60" if trend >= 0 else "#e74c3c"
                trend_label = QLabel(trend_text)
                trend_label.setStyleSheet(f"color: {trend_color}; font-weight: bold; font-size: 10px;")
                desc_layout.addWidget(trend_label)
            
            desc_layout.addStretch()
            layout.addLayout(desc_layout)
        
        layout.addStretch()


class StatusChart(QWidget):
    """Widget simple para mostrar distribución de estados."""
    
    def __init__(self, status_data: Dict[str, int]):
        super().__init__()
        self.status_data = status_data
        self.setup_ui()
    
    def setup_ui(self):
        """Configura la UI del gráfico de estados."""
        layout = QVBoxLayout(self)
        
        # Título
        title = QLabel("📊 Estado de Homologaciones")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Lista de estados
        for status, count in self.status_data.items():
            status_layout = QHBoxLayout()
            
            status_label = QLabel(f"{status}:")
            status_label.setMinimumWidth(150)
            status_layout.addWidget(status_label)
            
            count_label = QLabel(str(count))
            count_label.setStyleSheet("font-weight: bold; color: #3498db;")
            status_layout.addWidget(count_label)
            
            # Barra visual simple
            progress = QProgressBar()
            progress.setMaximum(max(self.status_data.values()) if self.status_data.values() else 1)
            progress.setValue(count)
            progress.setTextVisible(False)
            progress.setMaximumHeight(10)
            status_layout.addWidget(progress)
            
            layout.addLayout(status_layout)


class TopRepositoriesWidget(QWidget):
    """Widget para mostrar los repositorios más utilizados."""
    
    def __init__(self, repo_data: List[tuple]):
        super().__init__()
        self.repo_data = repo_data
        self.setup_ui()
    
    def setup_ui(self):
        """Configura la UI de repositorios."""
        layout = QVBoxLayout(self)
        
        # Título
        title = QLabel("🗂️ Top Repositorios")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        if not self.repo_data:
            no_data = QLabel("No hay datos de repositorio disponibles")
            no_data.setStyleSheet("color: #666666; font-style: italic;")
            layout.addWidget(no_data)
            return
        
        # Tabla de repositorios
        table = QTableWidget(len(self.repo_data), 2)
        table.setHorizontalHeaderLabels(["Repositorio", "Uso"])
        table.horizontalHeader().setStretchLastSection(True)
        table.verticalHeader().setVisible(False)
        table.setMaximumHeight(150)
        
        for i, (repo_name, count) in enumerate(self.repo_data):
            table.setItem(i, 0, QTableWidgetItem(str(repo_name)))
            table.setItem(i, 1, QTableWidgetItem(str(count)))
        
        layout.addWidget(table)


class MetricsPanel(QWidget):
    """Panel principal de métricas optimizado."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.metrics_worker = None
        self.setup_ui()
        self.load_metrics()
        
        # Timer para actualización automática (cada 5 minutos)
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.load_metrics)
        self.refresh_timer.start(300000)
    
    def setup_ui(self):
        """Configura la interfaz del panel de métricas."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(20)
        
        # Header con controles
        header_layout = QHBoxLayout()
        
        title = QLabel("📊 Panel de Métricas Optimizado")
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
        refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
        """)
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
        
        loading_label = QLabel("⏳ Calculando métricas...")
        loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        loading_label.setStyleSheet("font-size: 14px; color: #666666; margin: 40px;")
        
        self.metrics_layout.addWidget(loading_label)
    
    def clear_metrics(self):
        """Limpia las métricas actuales."""
        while self.metrics_layout.count():
            child = self.metrics_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
    
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
            "Todas las homologaciones",
            color="#3498db"
        )
        cards_layout.addWidget(total_card, 0, 0)
        
        # Homologaciones recientes
        recent_card = MetricCard(
            f"Últimos {metrics['date_range']} días",
            str(metrics['recent_count']),
            "Homologaciones recientes",
            metrics.get('growth_rate', 0),
            color="#27ae60"
        )
        cards_layout.addWidget(recent_card, 0, 1)
        
        # Promedio diario
        avg_daily = metrics['recent_count'] / metrics['date_range'] if metrics['date_range'] > 0 else 0
        avg_card = MetricCard(
            "Promedio Diario",
            f"{avg_daily:.1f}",
            f"Últimos {metrics['date_range']} días",
            color="#f39c12"
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
        if charts_layout.count() > 0:
            charts_widget = QWidget()
            charts_widget.setLayout(charts_layout)
            self.metrics_layout.addWidget(charts_widget)
        
        # Información de actualización
        info_label = QLabel(f"📊 Métricas actualizadas • {datetime.now().strftime('%H:%M:%S')}")
        info_label.setStyleSheet("color: #666666; font-size: 10px; margin: 10px;")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.metrics_layout.addWidget(info_label)
        
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
                QTableWidget {
                    background-color: #2d2d2d;
                    gridline-color: #444444;
                    color: #ffffff;
                }
                QHeaderView::section {
                    background-color: #404040;
                    color: #ffffff;
                    border: 1px solid #555555;
                }
            """)
        else:
            self.setStyleSheet("""
                MetricsPanel {
                    background-color: #ffffff;
                    color: #333333;
                }
                QTableWidget {
                    background-color: #ffffff;
                    gridline-color: #e0e0e0;
                }
                QHeaderView::section {
                    background-color: #f5f5f5;
                    border: 1px solid #cccccc;
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
