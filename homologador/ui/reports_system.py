"""
Sistema Avanzado de Reportes y Análisis.

Este módulo proporciona un sistema completo de reportes con gráficos,
estadísticas detalladas, análisis de tendencias y exportación automática
en múltiples formatos.
"""

import csv
import json
import logging
import os
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, cast

from PyQt6.QtCore import (QDate, QSize, Qt, QThread, QTimer, pyqtSignal,
                          pyqtSlot)
from PyQt6.QtGui import (QAction, QBrush, QColor, QFont, QIcon, QPainter,
                         QPalette, QPen)
from PyQt6.QtWidgets import (QButtonGroup, QCheckBox, QComboBox, QDateEdit,
                             QDialog, QFileDialog, QFormLayout, QFrame,
                             QGridLayout, QGroupBox, QHBoxLayout, QHeaderView,
                             QLabel, QLineEdit, QListWidget, QListWidgetItem,
                             QMessageBox, QProgressBar, QPushButton,
                             QRadioButton, QScrollArea, QSizePolicy, QSlider,
                             QSpacerItem, QSpinBox, QSplitter, QTableWidget,
                             QTableWidgetItem, QTabWidget, QTextBrowser,
                             QTextEdit, QVBoxLayout, QWidget)

# Intentar importar matplotlib para gráficos
try:
    import matplotlib.dates as mdates
    import matplotlib.pyplot as plt
    import numpy as np
    from matplotlib.backends.backend_qt5agg import \
        FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

from ..core.storage import (get_audit_repository, get_homologation_repository,
                          get_user_repository)

logger = logging.getLogger(__name__)


class ChartWidget(QWidget):
    """Widget base para mostrar gráficos."""
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Configura la interfaz básica del widget."""
        layout = QVBoxLayout(self)
        
        if MATPLOTLIB_AVAILABLE:
            # Crear figura de matplotlib
            self.figure = Figure(figsize=(10, 6), dpi=100)
            self.canvas = FigureCanvas(self.figure)
            layout.addWidget(self.canvas)
        else:
            # Fallback sin matplotlib
            no_chart_label = QLabel("📊 Gráficos no disponibles\\n\\nInstale matplotlib para ver gráficos:\\npip install matplotlib")
            no_chart_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            no_chart_label.setStyleSheet("""
                QLabel {
                    background-color: #f8f9fa;
                    border: 2px dashed #dee2e6;
                    border-radius: 8px;
                    padding: 40px;
                    color: #6c757d;
                    font-size: 14px;
                }
            """)
            layout.addWidget(no_chart_label)
    
    def plot_line_chart(self, x_data: List, y_data: List, title: str = "", xlabel: str = "", ylabel: str = ""):
        """Dibuja un gráfico de líneas."""
        if not MATPLOTLIB_AVAILABLE:
            return
        
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        ax.plot(x_data, y_data, marker='o', linewidth=2, markersize=6)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.grid(True, alpha=0.3)
        
        # Rotar etiquetas del eje x si son fechas
        if x_data and isinstance(x_data[0], (date, datetime)):
            ax.tick_params(axis='x', rotation=45)
        
        self.figure.tight_layout()
        self.canvas.draw()
    
    def plot_bar_chart(self, labels: List[str], values: List[float], title: str = "", ylabel: str = ""):
        """Dibuja un gráfico de barras."""
        if not MATPLOTLIB_AVAILABLE:
            return
        
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        bars = ax.bar(labels, values, color=['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6'][:len(labels)])
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_ylabel(ylabel)
        
        # Agregar valores en las barras
        for bar, value in zip(bars, values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + max(values)*0.01,
                   f'{value:.0f}', ha='center', va='bottom', fontweight='bold')
        
        ax.tick_params(axis='x', rotation=45)
        self.figure.tight_layout()
        self.canvas.draw()
    
    def plot_pie_chart(self, labels: List[str], values: List[float], title: str = ""):
        """Dibuja un gráfico de torta."""
        if not MATPLOTLIB_AVAILABLE:
            return
        
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        colors = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c', '#34495e']
        wedges, texts, autotexts = ax.pie(values, labels=labels, autopct='%1.1f%%', 
                                         colors=colors[:len(labels)], startangle=90)
        
        ax.set_title(title, fontsize=14, fontweight='bold')
        
        # Mejorar la apariencia del texto
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        self.figure.tight_layout()
        self.canvas.draw()


class ReportGeneratorWorker(QThread):
    """Worker thread para generar reportes en segundo plano."""
    
    progress_updated = pyqtSignal(int)
    status_updated = pyqtSignal(str)
    finished = pyqtSignal(bool, str, dict)  # success, message, data
    
    def __init__(self, report_config: Dict[str, Any]):
        super().__init__()
        self.report_config = report_config
        
    def run(self):
        """Ejecuta la generación del reporte."""
        try:
            self.status_updated.emit("Iniciando generación de reporte...")
            self.progress_updated.emit(10)
            
            report_type = self.report_config.get('type', 'general')
            date_from = self.report_config.get('date_from')
            date_to = self.report_config.get('date_to')
            
            # Obtener repositorios
            homolog_repo = get_homologation_repository()
            user_repo = get_user_repository()
            audit_repo = get_audit_repository()
            
            report_data = {}
            
            if report_type == 'general':
                report_data = self._generate_general_report(homolog_repo, user_repo, audit_repo, date_from, date_to)
            elif report_type == 'users':
                report_data = self._generate_users_report(user_repo, audit_repo, date_from, date_to)
            elif report_type == 'activity':
                report_data = self._generate_activity_report(audit_repo, date_from, date_to)
            elif report_type == 'homologations':
                report_data = self._generate_homologations_report(homolog_repo, date_from, date_to)
            else:
                raise ValueError(f"Tipo de reporte no válido: {report_type}")
            
            self.progress_updated.emit(100)
            self.status_updated.emit("Reporte generado exitosamente")
            self.finished.emit(True, "Reporte generado exitosamente", report_data)
            
        except Exception as e:
            logger.error(f"Error generando reporte: {e}")
            self.finished.emit(False, f"Error generando reporte: {str(e)}", {})
    
    def _generate_general_report(self, homolog_repo, user_repo, audit_repo, date_from, date_to):
        """Genera un reporte general del sistema."""
        self.status_updated.emit("Recopilando estadísticas generales...")
        self.progress_updated.emit(30)
        
        data = {
            'type': 'general',
            'date_range': f"{date_from} - {date_to}",
            'generated_at': datetime.now().isoformat(),
            'summary': {},
            'charts': {}
        }
        
        # Estadísticas de usuarios
        users = user_repo.get_all_active()
        data['summary']['total_users'] = len(users)
        data['summary']['users_by_role'] = {}
        
        for user in users:
            user_dict = dict(user)
            role = user_dict.get('role', 'unknown')
            data['summary']['users_by_role'][role] = data['summary']['users_by_role'].get(role, 0) + 1
        
        self.progress_updated.emit(50)
        
        # Estadísticas de auditoría
        audit_stats = audit_repo.get_statistics()
        data['summary']['total_logs'] = audit_stats.get('total_logs', 0)
        data['summary']['logs_today'] = audit_stats.get('logs_today', 0)
        data['summary']['activity_by_type'] = audit_stats.get('activity_by_type', {})
        
        self.progress_updated.emit(70)
        
        # Datos para gráficos
        data['charts']['users_by_role'] = {
            'labels': list(data['summary']['users_by_role'].keys()),
            'values': list(data['summary']['users_by_role'].values())
        }
        
        data['charts']['activity_by_type'] = {
            'labels': list(data['summary']['activity_by_type'].keys()),
            'values': list(data['summary']['activity_by_type'].values())
        }
        
        self.progress_updated.emit(90)
        
        return data
    
    def _generate_users_report(self, user_repo, audit_repo, date_from, date_to):
        """Genera un reporte de usuarios."""
        self.status_updated.emit("Analizando actividad de usuarios...")
        self.progress_updated.emit(40)
        
        data = {
            'type': 'users',
            'date_range': f"{date_from} - {date_to}",
            'generated_at': datetime.now().isoformat(),
            'users': [],
            'summary': {},
            'charts': {}
        }
        
        users = user_repo.get_all_active()
        
        for user in users:
            user_dict = dict(user)
            user_info = {
                'id': user_dict.get('id'),
                'username': user_dict.get('username'),
                'full_name': user_dict.get('full_name'),
                'role': user_dict.get('role'),
                'department': user_dict.get('department'),
                'created_at': user_dict.get('created_at'),
                'last_login': user_dict.get('last_login'),
                'is_active': user_dict.get('is_active')
            }
            data['users'].append(user_info)
        
        # Resumen
        data['summary']['total_users'] = len(users)
        data['summary']['active_users'] = len([u for u in data['users'] if u['is_active']])
        
        # Distribución por roles
        role_distribution = {}
        for user in data['users']:
            role = user['role']
            role_distribution[role] = role_distribution.get(role, 0) + 1
        
        data['charts']['role_distribution'] = {
            'labels': list(role_distribution.keys()),
            'values': list(role_distribution.values())
        }
        
        self.progress_updated.emit(80)
        
        return data
    
    def _generate_activity_report(self, audit_repo, date_from, date_to):
        """Genera un reporte de actividad."""
        self.status_updated.emit("Analizando patrones de actividad...")
        self.progress_updated.emit(60)
        
        data = {
            'type': 'activity',
            'date_range': f"{date_from} - {date_to}",
            'generated_at': datetime.now().isoformat(),
            'summary': {},
            'charts': {},
            'trends': {}
        }
        
        # Obtener estadísticas de auditoría
        stats = audit_repo.get_statistics()
        data['summary'] = stats
        
        # Actividad por tipo
        activity_by_type = stats.get('activity_by_type', {})
        data['charts']['activity_by_type'] = {
            'labels': list(activity_by_type.keys()),
            'values': list(activity_by_type.values())
        }
        
        self.progress_updated.emit(85)
        
        return data
    
    def _generate_homologations_report(self, homolog_repo, date_from, date_to):
        """Genera un reporte de homologaciones."""
        self.status_updated.emit("Analizando homologaciones...")
        self.progress_updated.emit(50)
        
        data = {
            'type': 'homologations',
            'date_range': f"{date_from} - {date_to}",
            'generated_at': datetime.now().isoformat(),
            'summary': {},
            'charts': {}
        }
        
        # Aquí se agregarían las estadísticas de homologaciones
        # Por ahora datos de ejemplo
        data['summary'] = {
            'total_homologations': 45,
            'completed': 30,
            'in_progress': 12,
            'pending': 3
        }
        
        data['charts']['status_distribution'] = {
            'labels': ['Completadas', 'En Progreso', 'Pendientes'],
            'values': [30, 12, 3]
        }
        
        self.progress_updated.emit(90)
        
        return data


class ReportViewerWidget(QWidget):
    """Widget para visualizar reportes generados."""
    
    def __init__(self, report_data: Dict[str, Any], parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.report_data = report_data
        self.setup_ui()
        self.display_report()
    
    def setup_ui(self):
        """Configura la interfaz del visor de reportes."""
        layout = QVBoxLayout(self)
        
        # Header del reporte
        header_layout = QHBoxLayout()
        
        title = QLabel(f"📊 Reporte: {self.report_data.get('type', 'General').title()}")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50; margin-bottom: 10px;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Información del reporte
        info_layout = QVBoxLayout()
        
        date_range = QLabel(f"📅 Periodo: {self.report_data.get('date_range', 'N/A')}")
        date_range.setStyleSheet("color: #7f8c8d; font-size: 12px;")
        info_layout.addWidget(date_range)
        
        generated_at = self.report_data.get('generated_at', '')
        if generated_at:
            try:
                dt = datetime.fromisoformat(generated_at)
                formatted_date = dt.strftime('%d/%m/%Y %H:%M')
            except:
                formatted_date = generated_at
        else:
            formatted_date = "N/A"
        
        gen_time = QLabel(f"🕐 Generado: {formatted_date}")
        gen_time.setStyleSheet("color: #7f8c8d; font-size: 12px;")
        info_layout.addWidget(gen_time)
        
        header_layout.addLayout(info_layout)
        layout.addLayout(header_layout)
        
        # Pestañas del reporte
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Botones de acción
        buttons_layout = QHBoxLayout()
        
        export_btn = QPushButton("📤 Exportar Reporte")
        export_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
        """)
        export_btn.clicked.connect(self.export_report)
        buttons_layout.addWidget(export_btn)
        
        print_btn = QPushButton("🖨️ Imprimir")
        print_btn.clicked.connect(self.print_report)
        buttons_layout.addWidget(print_btn)
        
        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)
    
    def display_report(self):
        """Muestra el contenido del reporte."""
        # Pestaña de resumen
        self.create_summary_tab()
        
        # Pestaña de gráficos
        if self.report_data.get('charts'):
            self.create_charts_tab()
        
        # Pestaña de datos detallados
        self.create_details_tab()
    
    def create_summary_tab(self):
        """Crea la pestaña de resumen."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        summary_data = self.report_data.get('summary', {})
        
        # Crear tarjetas de resumen
        cards_layout = QGridLayout()
        row, col = 0, 0
        
        for key, value in summary_data.items():
            if isinstance(value, (int, float, str)) and not key.endswith('_by_') and not key.endswith('_activity'):
                card = self.create_summary_card(key.replace('_', ' ').title(), str(value))
                cards_layout.addWidget(card, row, col)
                
                col += 1
                if col >= 3:
                    col = 0
                    row += 1
        
        layout.addLayout(cards_layout)
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "📊 Resumen")
    
    def create_charts_tab(self):
        """Crea la pestaña de gráficos."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        charts_data = self.report_data.get('charts', {})
        
        for chart_name, chart_info in charts_data.items():
            if isinstance(chart_info, dict) and 'labels' in chart_info and 'values' in chart_info:
                # Crear gráfico
                chart_group = QGroupBox(chart_name.replace('_', ' ').title())
                chart_layout = QVBoxLayout(chart_group)
                
                chart_widget = ChartWidget()
                
                # Determinar tipo de gráfico basado en los datos
                if len(chart_info['labels']) <= 6:
                    chart_widget.plot_pie_chart(
                        chart_info['labels'], 
                        chart_info['values'], 
                        chart_name.replace('_', ' ').title()
                    )
                else:
                    chart_widget.plot_bar_chart(
                        chart_info['labels'], 
                        chart_info['values'], 
                        chart_name.replace('_', ' ').title()
                    )
                
                chart_layout.addWidget(chart_widget)
                scroll_layout.addWidget(chart_group)
        
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)
        
        self.tab_widget.addTab(tab, "📈 Gráficos")
    
    def create_details_tab(self):
        """Crea la pestaña de datos detallados."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Mostrar datos detallados según el tipo de reporte
        if self.report_data.get('type') == 'users' and 'users' in self.report_data:
            self.create_users_table(layout)
        else:
            # Mostrar JSON formateado para otros tipos
            details_text = QTextBrowser()
            details_text.setPlainText(json.dumps(self.report_data, indent=2, ensure_ascii=False))
            layout.addWidget(details_text)
        
        self.tab_widget.addTab(tab, "📋 Datos Detallados")
    
    def create_users_table(self, layout: QVBoxLayout):
        """Crea una tabla de usuarios."""
        users_data = self.report_data.get('users', [])
        
        table = QTableWidget()
        table.setRowCount(len(users_data))
        
        if users_data:
            columns = list(users_data[0].keys())
            table.setColumnCount(len(columns))
            table.setHorizontalHeaderLabels([col.replace('_', ' ').title() for col in columns])
            
            for row, user in enumerate(users_data):
                for col, key in enumerate(columns):
                    value = user.get(key, '')
                    table.setItem(row, col, QTableWidgetItem(str(value)))
            
            # Ajustar columnas
            table.resizeColumnsToContents()
        
        layout.addWidget(table)
    
    def create_summary_card(self, title: str, value: str) -> QFrame:
        """Crea una tarjeta de resumen."""
        card = QFrame()
        card.setFrameStyle(QFrame.Shape.StyledPanel)
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 15px;
                margin: 5px;
            }
        """)
        
        layout = QVBoxLayout(card)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("font-weight: bold; color: #7f8c8d; font-size: 12px;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        value_label = QLabel(value)
        value_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50;")
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(value_label)
        
        return card
    
    def export_report(self):
        """Exporta el reporte."""
        file_path, selected_filter = QFileDialog.getSaveFileName(
            self,
            "Exportar Reporte",
            f"reporte_{self.report_data.get('type', 'general')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "JSON (*.json);;CSV (*.csv);;Texto (*.txt)"
        )
        
        if file_path:
            try:
                if selected_filter.startswith("JSON"):
                    self._export_json(file_path)
                elif selected_filter.startswith("CSV"):
                    self._export_csv(file_path)
                else:
                    self._export_text(file_path)
                
                QMessageBox.information(self, "Exportación Exitosa", f"Reporte exportado a: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error exportando reporte: {str(e)}")
    
    def _export_json(self, file_path: str):
        """Exporta el reporte como JSON."""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.report_data, f, indent=2, ensure_ascii=False)
    
    def _export_csv(self, file_path: str):
        """Exporta el reporte como CSV."""
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Header
            writer.writerow(['Tipo de Reporte', self.report_data.get('type', 'N/A')])
            writer.writerow(['Periodo', self.report_data.get('date_range', 'N/A')])
            writer.writerow(['Generado', self.report_data.get('generated_at', 'N/A')])
            writer.writerow([])
            
            # Resumen
            writer.writerow(['RESUMEN'])
            summary = self.report_data.get('summary', {})
            for key, value in summary.items():
                if isinstance(value, (int, float, str)):
                    writer.writerow([key.replace('_', ' ').title(), value])
            
            writer.writerow([])
            
            # Datos detallados si los hay
            if self.report_data.get('type') == 'users' and 'users' in self.report_data:
                writer.writerow(['USUARIOS'])
                users = self.report_data['users']
                if users:
                    headers = list(users[0].keys())
                    writer.writerow([h.replace('_', ' ').title() for h in headers])
                    for user in users:
                        writer.writerow([user.get(h, '') for h in headers])
    
    def _export_text(self, file_path: str):
        """Exporta el reporte como texto plano."""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"REPORTE DEL SISTEMA\\n")
            f.write("=" * 50 + "\\n\\n")
            f.write(f"Tipo: {self.report_data.get('type', 'N/A')}\\n")
            f.write(f"Periodo: {self.report_data.get('date_range', 'N/A')}\\n")
            f.write(f"Generado: {self.report_data.get('generated_at', 'N/A')}\\n\\n")
            
            f.write("RESUMEN\\n")
            f.write("-" * 20 + "\\n")
            summary = self.report_data.get('summary', {})
            for key, value in summary.items():
                if isinstance(value, (int, float, str)):
                    f.write(f"{key.replace('_', ' ').title()}: {value}\\n")
    
    def print_report(self):
        """Imprime el reporte."""
        QMessageBox.information(self, "Imprimir", "Funcionalidad de impresión en desarrollo.")


class ReportsSystemWidget(QWidget):
    """Widget principal del sistema de reportes."""
    
    def __init__(self, user_info: Dict[str, Any], parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.user_info = user_info
        self.current_report_data = None
        
        self.setup_ui()
        self.apply_dark_theme()
        logger.info(f"Sistema de reportes iniciado por: {user_info.get('username')}")
    
    def setup_ui(self):
        """Configura la interfaz del sistema de reportes."""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        
        # Título
        title_label = QLabel("📊 Sistema de Reportes y Análisis")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setWeight(QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        main_layout.addWidget(title_label)
        
        # Layout principal dividido
        content_layout = QHBoxLayout()
        
        # Panel izquierdo - Configuración
        config_panel = self.create_config_panel()
        content_layout.addWidget(config_panel, 1)
        
        # Panel derecho - Visualización
        self.viewer_panel = QFrame()
        self.viewer_panel.setFrameStyle(QFrame.Shape.StyledPanel)
        self.viewer_panel.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 8px;
            }
        """)
        
        viewer_layout = QVBoxLayout(self.viewer_panel)
        
        # Placeholder inicial
        self.placeholder_label = QLabel("📊 Genere un reporte para ver los resultados aquí")
        self.placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.placeholder_label.setStyleSheet("""
            QLabel {
                color: #6c757d;
                font-size: 16px;
                padding: 60px;
            }
        """)
        viewer_layout.addWidget(self.placeholder_label)
        
        content_layout.addWidget(self.viewer_panel, 2)
        
        main_layout.addLayout(content_layout)
    
    def create_config_panel(self) -> QWidget:
        """Crea el panel de configuración de reportes."""
        panel = QFrame()
        panel.setFrameStyle(QFrame.Shape.StyledPanel)
        panel.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 20px;
            }
        """)
        
        layout = QVBoxLayout(panel)
        
        # Configuración del reporte
        config_group = QGroupBox("⚙️ Configuración del Reporte")
        config_layout = QFormLayout(config_group)
        
        # Tipo de reporte
        self.report_type = QComboBox()
        self.report_type.addItem("📊 Reporte General", "general")
        self.report_type.addItem("👥 Reporte de Usuarios", "users")
        self.report_type.addItem("⚡ Reporte de Actividad", "activity")
        self.report_type.addItem("📋 Reporte de Homologaciones", "homologations")
        config_layout.addRow("Tipo de reporte:", self.report_type)
        
        # Rango de fechas
        self.date_from = QDateEdit()
        self.date_from.setDate(QDate.currentDate().addDays(-30))
        self.date_from.setCalendarPopup(True)
        config_layout.addRow("Fecha desde:", self.date_from)
        
        self.date_to = QDateEdit()
        self.date_to.setDate(QDate.currentDate())
        self.date_to.setCalendarPopup(True)
        config_layout.addRow("Fecha hasta:", self.date_to)
        
        # Opciones adicionales
        self.include_charts = QCheckBox("Incluir gráficos")
        self.include_charts.setChecked(True)
        config_layout.addRow(self.include_charts)
        
        self.include_details = QCheckBox("Incluir datos detallados")
        self.include_details.setChecked(True)
        config_layout.addRow(self.include_details)
        
        layout.addWidget(config_group)
        
        # Botón generar
        self.generate_btn = QPushButton("📊 Generar Reporte")
        self.generate_btn.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 15px 30px;
                font-weight: bold;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:disabled {
                background-color: #6c757d;
            }
        """)
        self.generate_btn.clicked.connect(self.generate_report)
        layout.addWidget(self.generate_btn)
        
        # Progreso
        progress_group = QGroupBox("📈 Progreso")
        progress_layout = QVBoxLayout(progress_group)
        
        self.progress_bar = QProgressBar()
        progress_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("Listo para generar reporte")
        progress_layout.addWidget(self.status_label)
        
        layout.addWidget(progress_group)
        
        # Reportes programados
        scheduled_group = QGroupBox("⏰ Reportes Programados")
        scheduled_layout = QVBoxLayout(scheduled_group)
        
        self.scheduled_list = QListWidget()
        scheduled_layout.addWidget(self.scheduled_list)
        
        schedule_buttons = QHBoxLayout()
        
        add_schedule_btn = QPushButton("➕ Programar")
        add_schedule_btn.clicked.connect(self.add_scheduled_report)
        schedule_buttons.addWidget(add_schedule_btn)
        
        edit_schedule_btn = QPushButton("✏️ Editar")
        schedule_buttons.addWidget(edit_schedule_btn)
        
        delete_schedule_btn = QPushButton("🗑️ Eliminar")
        schedule_buttons.addWidget(delete_schedule_btn)
        
        scheduled_layout.addLayout(schedule_buttons)
        
        layout.addWidget(scheduled_group)
        
        layout.addStretch()
        
        return panel
    
    def generate_report(self):
        """Genera un reporte según la configuración."""
        try:
            # Configuración del reporte
            report_config = {
                'type': self.report_type.currentData(),
                'date_from': self.date_from.date().toPython(),
                'date_to': self.date_to.date().toPython(),
                'include_charts': self.include_charts.isChecked(),
                'include_details': self.include_details.isChecked()
            }
            
            # Deshabilitar botón durante generación
            self.generate_btn.setEnabled(False)
            self.generate_btn.setText("⏳ Generando...")
            
            # Crear worker thread
            self.report_worker = ReportGeneratorWorker(report_config)
            self.report_worker.progress_updated.connect(self.progress_bar.setValue)
            self.report_worker.status_updated.connect(self.status_label.setText)
            self.report_worker.finished.connect(self.on_report_finished)
            
            # Iniciar generación
            self.report_worker.start()
            
        except Exception as e:
            logger.error(f"Error iniciando generación de reporte: {e}")
            QMessageBox.critical(self, "Error", f"Error iniciando generación: {str(e)}")
            self._reset_generate_button()
    
    def on_report_finished(self, success: bool, message: str, data: Dict[str, Any]):
        """Maneja la finalización de la generación del reporte."""
        self._reset_generate_button()
        
        if success:
            self.current_report_data = data
            self.display_report(data)
            QMessageBox.information(self, "Reporte Generado", message)
        else:
            QMessageBox.critical(self, "Error", message)
        
        self.progress_bar.setValue(0)
        self.status_label.setText("Listo para generar reporte")
    
    def _reset_generate_button(self):
        """Resetea el botón de generar."""
        self.generate_btn.setEnabled(True)
        self.generate_btn.setText("📊 Generar Reporte")
    
    def display_report(self, report_data: Dict[str, Any]):
        """Muestra el reporte generado."""
        # Limpiar panel viewer
        for i in reversed(range(self.viewer_panel.layout().count())):
            child = self.viewer_panel.layout().itemAt(i).widget()
            if child:
                child.deleteLater()
        
        # Crear y agregar viewer del reporte
        report_viewer = ReportViewerWidget(report_data)
        self.viewer_panel.layout().addWidget(report_viewer)
    
    def add_scheduled_report(self):
        """Agrega un reporte programado."""
        QMessageBox.information(
            self,
            "Reportes Programados",
            "Funcionalidad de reportes programados\\n\\n"
            "Esta característica permitirá:\\n"
            "• Programar reportes automáticos diarios/semanales/mensuales\\n"
            "• Envío automático por email\\n"
            "• Almacenamiento automático en ubicaciones específicas\\n\\n"
            "Estará disponible en una próxima versión."
        )
    
    def apply_dark_theme(self):
        """Aplica el tema nocturno elegante al sistema de reportes."""
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
                min-width: 120px;
                background-color: #34495e;
                color: #ecf0f1;
            }
            
            QPushButton:hover {
                background-color: #4a6741;
                border-color: #74b9ff;
                color: #ffffff;
            }
            
            QPushButton[default="true"] {
                background-color: #2980b9;
                border-color: #3498db;
            }
            
            QComboBox, QDateEdit {
                background-color: #2c3e50;
                color: #ecf0f1;
                border: 2px solid #34495e;
                border-radius: 6px;
                padding: 8px;
            }
            
            QComboBox:hover, QDateEdit:hover {
                border-color: #74b9ff;
            }
            
            QTextEdit {
                background-color: #2c3e50;
                color: #ecf0f1;
                border: 2px solid #34495e;
                border-radius: 8px;
                padding: 12px;
            }
        """)


def show_reports_system(user_info: Dict[str, Any], parent: Optional[QWidget] = None) -> QDialog:
    """Muestra el sistema de reportes."""
    dialog = QDialog(parent)
    dialog.setWindowTitle("Sistema de Reportes y Análisis")
    dialog.setModal(True)
    dialog.resize(1600, 1000)
    
    layout = QVBoxLayout(dialog)
    layout.setContentsMargins(0, 0, 0, 0)
    
    try:
        widget = ReportsSystemWidget(user_info)
        layout.addWidget(widget)
        
        # Botón cerrar
        close_button = QPushButton("Cerrar")
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5a6268;
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
        logger.error(f"Error inicializando sistema de reportes: {e}")
        QMessageBox.critical(
            cast(QWidget, parent),
            "Error",
            f"Error inicializando sistema de reportes: {str(e)}"
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
    
    dialog = show_reports_system(admin_user)
    dialog.exec()
    
    sys.exit(0)