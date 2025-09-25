#!/usr/bin/env python
"""
Sistema optimizado de métricas para el dashboard
Corrige todos los errores identificados y mejora el rendimiento
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from functools import lru_cache
import sqlite3

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, 
    QFrame, QScrollArea, QGroupBox, QPushButton, QComboBox,
    QProgressBar, QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread, pyqtSlot
from PyQt6.QtGui import QFont, QPalette, QColor

from homologador.core.storage import get_homologation_repository
from homologador.ui.theme import get_current_theme, ThemeType

logger = logging.getLogger(__name__)

@dataclass
class MetricsData:
    """Estructura optimizada para datos de métricas."""
    total_count: int
    recent_count: int
    growth_rate: float
    completion_stats: Dict[str, int]
    repository_stats: Dict[str, int]
    daily_trends: Dict[str, int]
    avg_days_to_complete: Optional[float]
    date_range: int

class OptimizedMetricsWorker(QThread):
    """Worker optimizado para cálculo de métricas con consultas SQL eficientes."""
    
    metrics_calculated = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, date_range: str = "30"):
        super().__init__()
        self.date_range = int(date_range)
        self.repo = get_homologation_repository()
    
    def run(self):
        """Calcula métricas usando consultas SQL optimizadas."""
        try:
            metrics_data = self.calculate_optimized_metrics()
            self.metrics_calculated.emit(metrics_data.__dict__)
        except Exception as e:
            logger.error(f"Error calculando métricas optimizadas: {e}")
            self.error_occurred.emit(str(e))
    
    def calculate_optimized_metrics(self) -> MetricsData:
        """Calcula métricas usando consultas SQL directas para mejor rendimiento."""
        
        # Fechas para los cálculos
        end_date = datetime.now()
        start_date = end_date - timedelta(days=self.date_range)
        prev_start_date = start_date - timedelta(days=self.date_range)
        
        # Formatear fechas para SQL
        end_date_str = end_date.strftime('%Y-%m-%d %H:%M:%S')
        start_date_str = start_date.strftime('%Y-%m-%d %H:%M:%S')
        prev_start_date_str = prev_start_date.strftime('%Y-%m-%d %H:%M:%S')
        
        db = self.repo.db
        
        # 1. Contar totales con una sola consulta
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
        
        # 4. Estadísticas de estado basadas en campos reales
        completion_stats = self._calculate_completion_stats(db)
        
        # 5. Estadísticas de repositorio optimizadas
        repository_stats = self._calculate_repository_stats(db)
        
        # 6. Tendencias diarias optimizadas
        daily_trends = self._calculate_daily_trends(db, self.date_range)
        
        # 7. Promedio de días para completar (basado en fechas)
        avg_completion = self._calculate_avg_completion_days(db)
        
        return MetricsData(
            total_count=total_count,
            recent_count=recent_count,
            growth_rate=round(growth_rate, 2),
            completion_stats=completion_stats,
            repository_stats=repository_stats,
            daily_trends=daily_trends,
            avg_days_to_complete=avg_completion,
            date_range=self.date_range
        )
    
    def _calculate_completion_stats(self, db) -> Dict[str, int]:
        """Calcula estadísticas de finalización basadas en campos reales."""
        
        # Usar campos que realmente existen
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
    
    def _calculate_repository_stats(self, db) -> Dict[str, int]:
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
        LIMIT 10
        """
        
        result = db.execute_query(repo_query)
        repo_stats = {}
        
        for row in result:
            repo_name = row['repository_location']
            # Extraer nombre limpio del repositorio
            if '/' in repo_name:
                repo_name = repo_name.split('/')[-1]
            elif '\\' in repo_name:
                repo_name = repo_name.split('\\')[-1]
            
            # Limpiar y normalizar
            repo_name = repo_name.replace('.git', '').strip()
            if repo_name:
                repo_stats[repo_name] = row['count']
        
        return repo_stats
    
    def _calculate_daily_trends(self, db, days: int) -> Dict[str, int]:
        """Calcula tendencias diarias para el período especificado."""
        
        trends = {}
        
        # Inicializar todos los días con 0
        for i in range(days):
            day = datetime.now() - timedelta(days=i)
            day_key = day.strftime('%Y-%m-%d')
            trends[day_key] = 0
        
        # Consulta optimizada para contar por día
        trends_query = """
        SELECT 
            DATE(created_at) as day,
            COUNT(*) as count
        FROM homologations 
        WHERE created_at >= DATE('now', '-{} days')
        GROUP BY DATE(created_at)
        ORDER BY day DESC
        """.format(days)
        
        result = db.execute_query(trends_query)
        
        for row in result:
            day_key = row['day']
            if day_key in trends:
                trends[day_key] = row['count']
        
        return trends
    
    def _calculate_avg_completion_days(self, db) -> Optional[float]:
        """Calcula el promedio de días para completar homologaciones."""
        
        completion_query = """
        SELECT 
            AVG(
                CAST(
                    (julianday(COALESCE(homologation_date, updated_at)) - julianday(created_at))
                    AS REAL
                )
            ) as avg_days
        FROM homologations 
        WHERE homologation_date IS NOT NULL 
            AND homologation_date != ''
            AND created_at IS NOT NULL
        """
        
        result = db.execute_query(completion_query)
        if result and result[0]['avg_days']:
            return round(result[0]['avg_days'], 1)
        
        return None

class OptimizedMetricCard(QFrame):
    """Tarjeta optimizada para mostrar métricas con mejor diseño."""
    
    def __init__(self, title: str, value: str, description: str = "", 
                 trend: Optional[float] = None, color: str = "#3498db"):
        super().__init__()
        self.setup_ui(title, value, description, trend, color)
    
    def setup_ui(self, title: str, value: str, description: str, 
                 trend: Optional[float], color: str):
        """Configura la UI de la tarjeta optimizada."""
        
        self.setFrameStyle(QFrame.Shape.Box)
        self.setStyleSheet(f"""
            QFrame {{
                border: 2px solid {color};
                border-radius: 8px;
                background-color: rgba({self._hex_to_rgb(color)}, 0.1);
                padding: 12px;
                margin: 4px;
            }}
            QLabel {{
                border: none;
                background-color: transparent;
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)
        
        # Título
        title_label = QLabel(title)
        title_font = QFont()
        title_font.setPointSize(10)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet(f"color: {color};")
        layout.addWidget(title_label)
        
        # Valor principal
        value_label = QLabel(str(value))
        value_font = QFont()
        value_font.setPointSize(24)
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
    
    def _hex_to_rgb(self, hex_color: str) -> str:
        """Convierte color hex a RGB."""
        hex_color = hex_color.lstrip('#')
        return ','.join(str(int(hex_color[i:i+2], 16)) for i in (0, 2, 4))

class OptimizedMetricsPanel(QWidget):
    """Panel de métricas completamente optimizado."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.metrics_worker = None
        self.cache_timer = QTimer()
        self.cached_metrics = None
        self.cache_expiry = None
        
        self.setup_ui()
        self.load_metrics()
        
        # Cache de 2 minutos para evitar cálculos innecesarios
        self.cache_timer.timeout.connect(self._clear_cache)
        self.cache_timer.start(120000)  # 2 minutos
    
    def setup_ui(self):
        """Configura la interfaz optimizada."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(20)
        
        # Header mejorado
        header_layout = QHBoxLayout()
        
        title = QLabel("📊 Dashboard de Métricas Optimizado")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Controles mejorados
        period_label = QLabel("Período:")
        period_label.setStyleSheet("font-weight: bold;")
        header_layout.addWidget(period_label)
        
        self.period_combo = QComboBox()
        self.period_combo.addItems(["7 días", "30 días", "90 días", "180 días", "1 año"])
        self.period_combo.setCurrentText("30 días")
        self.period_combo.currentTextChanged.connect(self.on_period_changed)
        header_layout.addWidget(self.period_combo)
        
        refresh_button = QPushButton("🔄 Actualizar")
        refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
        """)
        refresh_button.clicked.connect(self.force_refresh)
        header_layout.addWidget(refresh_button)
        
        layout.addLayout(header_layout)
        
        # Área de contenido con scroll
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.metrics_widget = QWidget()
        self.metrics_layout = QVBoxLayout(self.metrics_widget)
        self.metrics_layout.setSpacing(25)
        
        scroll_area.setWidget(self.metrics_widget)
        layout.addWidget(scroll_area)
        
        self.show_loading_message()
        self.apply_theme_styles()
    
    def show_loading_message(self):
        """Muestra mensaje de carga mejorado."""
        self.clear_metrics()
        
        loading_widget = QWidget()
        loading_layout = QVBoxLayout(loading_widget)
        loading_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        loading_label = QLabel("⏳ Calculando métricas optimizadas...")
        loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        loading_label.setStyleSheet("font-size: 16px; color: #666666; margin: 40px;")
        loading_layout.addWidget(loading_label)
        
        progress = QProgressBar()
        progress.setRange(0, 0)  # Indeterminate
        progress.setStyleSheet("""
            QProgressBar {
                border: 2px solid #cccccc;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #0078d4;
                border-radius: 3px;
            }
        """)
        loading_layout.addWidget(progress)
        
        self.metrics_layout.addWidget(loading_widget)
    
    def clear_metrics(self):
        """Limpia métricas actuales de forma eficiente."""
        while self.metrics_layout.count():
            child = self.metrics_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
    
    def on_period_changed(self):
        """Maneja cambios de período con cache."""
        self._clear_cache()
        self.load_metrics()
    
    def force_refresh(self):
        """Fuerza actualización limpiando cache."""
        self._clear_cache()
        self.load_metrics()
    
    def _clear_cache(self):
        """Limpia el cache de métricas."""
        self.cached_metrics = None
        self.cache_expiry = None
    
    def load_metrics(self):
        """Carga métricas con cache inteligente."""
        
        # Verificar cache
        now = datetime.now()
        if (self.cached_metrics and self.cache_expiry and 
            now < self.cache_expiry):
            self.display_metrics(self.cached_metrics)
            return
        
        self.show_loading_message()
        
        # Obtener período
        period_map = {
            "7 días": "7",
            "30 días": "30", 
            "90 días": "90",
            "180 días": "180",
            "1 año": "365"
        }
        days = period_map.get(self.period_combo.currentText(), "30")
        
        # Iniciar worker optimizado
        if self.metrics_worker and self.metrics_worker.isRunning():
            self.metrics_worker.terminate()
            self.metrics_worker.wait()
        
        self.metrics_worker = OptimizedMetricsWorker(days)
        self.metrics_worker.metrics_calculated.connect(self.display_metrics)
        self.metrics_worker.error_occurred.connect(self.show_error)
        self.metrics_worker.start()
    
    @pyqtSlot(dict)
    def display_metrics(self, metrics: Dict[str, Any]):
        """Muestra métricas optimizadas."""
        
        # Guardar en cache
        self.cached_metrics = metrics
        self.cache_expiry = datetime.now() + timedelta(minutes=2)
        
        self.clear_metrics()
        
        # Tarjetas principales optimizadas
        cards_layout = QGridLayout()
        
        # Tarjeta de total
        total_card = OptimizedMetricCard(
            "Total de Homologaciones",
            str(metrics['total_count']),
            "Todas las homologaciones en el sistema",
            color="#3498db"
        )
        cards_layout.addWidget(total_card, 0, 0)
        
        # Tarjeta de recientes
        recent_card = OptimizedMetricCard(
            f"Últimos {metrics['date_range']} días",
            str(metrics['recent_count']),
            "Homologaciones recientes",
            metrics.get('growth_rate', 0),
            color="#27ae60"
        )
        cards_layout.addWidget(recent_card, 0, 1)
        
        # Promedio mejorado
        avg_daily = metrics['recent_count'] / metrics['date_range'] if metrics['date_range'] > 0 else 0
        avg_card = OptimizedMetricCard(
            "Promedio Diario",
            f"{avg_daily:.1f}",
            f"Últimos {metrics['date_range']} días",
            color="#f39c12"
        )
        cards_layout.addWidget(avg_card, 0, 2)
        
        # Tiempo promedio de finalización
        if metrics.get('avg_days_to_complete'):
            completion_card = OptimizedMetricCard(
                "Tiempo Promedio",
                f"{metrics['avg_days_to_complete']:.1f}",
                "días para completar",
                color="#9b59b6"
            )
            cards_layout.addWidget(completion_card, 0, 3)
        
        cards_widget = QWidget()
        cards_widget.setLayout(cards_layout)
        self.metrics_layout.addWidget(cards_widget)
        
        # Estadísticas de finalización
        if metrics.get('completion_stats'):
            completion_group = self._create_completion_stats_widget(metrics['completion_stats'])
            self.metrics_layout.addWidget(completion_group)
        
        # Estadísticas de repositorio  
        if metrics.get('repository_stats'):
            repo_group = self._create_repository_stats_widget(metrics['repository_stats'])
            self.metrics_layout.addWidget(repo_group)
        
        # Información adicional
        info_label = QLabel(f"📊 Métricas calculadas para los últimos {metrics['date_range']} días • "
                           f"Cache válido por 2 minutos • Última actualización: {datetime.now().strftime('%H:%M:%S')}")
        info_label.setStyleSheet("color: #666666; font-size: 10px; margin: 10px;")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.metrics_layout.addWidget(info_label)
        
        self.metrics_layout.addStretch()
    
    def _create_completion_stats_widget(self, stats: Dict[str, int]) -> QGroupBox:
        """Crea widget de estadísticas de finalización."""
        
        group = QGroupBox("📋 Estado de Homologaciones")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        layout = QGridLayout(group)
        
        colors = {
            'Completadas': '#27ae60',
            'Sincronizadas': '#3498db', 
            'Con Versiones Previas': '#f39c12',
            'Con Repositorio': '#9b59b6',
            'Pendientes': '#e74c3c'
        }
        
        row = 0
        col = 0
        for status, count in stats.items():
            color = colors.get(status, '#95a5a6')
            
            stat_frame = QFrame()
            stat_frame.setStyleSheet(f"""
                QFrame {{
                    border-left: 4px solid {color};
                    background-color: rgba({OptimizedMetricCard()._hex_to_rgb(color)}, 0.1);
                    padding: 8px;
                    border-radius: 4px;
                }}
            """)
            
            stat_layout = QHBoxLayout(stat_frame)
            
            status_label = QLabel(status)
            status_label.setStyleSheet("font-weight: bold;")
            stat_layout.addWidget(status_label)
            
            stat_layout.addStretch()
            
            count_label = QLabel(str(count))
            count_label.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 16px;")
            stat_layout.addWidget(count_label)
            
            layout.addWidget(stat_frame, row, col)
            
            col += 1
            if col > 1:  # 2 columnas
                col = 0
                row += 1
        
        return group
    
    def _create_repository_stats_widget(self, repo_stats: Dict[str, int]) -> QGroupBox:
        """Crea widget de estadísticas de repositorio."""
        
        group = QGroupBox("🗂️ Repositorios Más Utilizados")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        if not repo_stats:
            layout = QVBoxLayout(group)
            no_data_label = QLabel("📝 No hay datos de repositorio disponibles")
            no_data_label.setStyleSheet("color: #666666; font-style: italic; padding: 20px;")
            no_data_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(no_data_label)
            return group
        
        table = QTableWidget()
        table.setColumnCount(2)
        table.setHorizontalHeaderLabels(["Repositorio", "Homologaciones"])
        table.setRowCount(len(repo_stats))
        
        # Configurar tabla
        table.horizontalHeader().setStretchLastSection(True)
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        table.verticalHeader().setVisible(False)
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        # Llenar datos
        for row, (repo_name, count) in enumerate(repo_stats.items()):
            repo_item = QTableWidgetItem(str(repo_name))
            count_item = QTableWidgetItem(str(count))
            count_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            table.setItem(row, 0, repo_item)
            table.setItem(row, 1, count_item)
        
        table.setMaximumHeight(200)
        
        layout = QVBoxLayout(group)
        layout.addWidget(table)
        
        return group
    
    @pyqtSlot(str)
    def show_error(self, error_message: str):
        """Muestra error con opción de reintentar."""
        self.clear_metrics()
        
        error_widget = QWidget()
        error_layout = QVBoxLayout(error_widget)
        error_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        error_label = QLabel(f"❌ Error calculando métricas:\n{error_message}")
        error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        error_label.setStyleSheet("color: #dc3545; font-size: 14px; margin: 20px;")
        error_layout.addWidget(error_label)
        
        retry_button = QPushButton("🔄 Reintentar")
        retry_button.clicked.connect(self.force_refresh)
        retry_button.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        error_layout.addWidget(retry_button)
        error_layout.setAlignment(retry_button, Qt.AlignmentFlag.AlignCenter)
        
        self.metrics_layout.addWidget(error_widget)
    
    def apply_theme_styles(self):
        """Aplica estilos de tema optimizados."""
        current_theme = get_current_theme()
        
        if current_theme == ThemeType.DARK:
            self.setStyleSheet("""
                OptimizedMetricsPanel {
                    background-color: #1a1a1a;
                    color: #ffffff;
                }
                QLabel {
                    color: #ffffff;
                }
                QGroupBox {
                    color: #ffffff;
                    border: 2px solid #444444;
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
                    padding: 6px;
                }
            """)
        else:
            self.setStyleSheet("""
                OptimizedMetricsPanel {
                    background-color: #ffffff;
                    color: #333333;
                }
                QGroupBox {
                    border: 2px solid #cccccc;
                }
                QTableWidget {
                    background-color: #ffffff;
                    gridline-color: #e0e0e0;
                }
                QHeaderView::section {
                    background-color: #f5f5f5;
                    border: 1px solid #cccccc;
                    padding: 6px;
                }
            """)
    
    def closeEvent(self, event):
        """Limpia recursos al cerrar."""
        if self.cache_timer:
            self.cache_timer.stop()
        
        if self.metrics_worker and self.metrics_worker.isRunning():
            self.metrics_worker.terminate()
            self.metrics_worker.wait()
        
        event.accept()