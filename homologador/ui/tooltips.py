"""
Sistema de tooltips informativos para la aplicación.
Proporciona ayuda contextual y información adicional en tiempo real.
"""

import logging
from typing import Any, Dict, Optional

from PyQt6.QtCore import QPoint, Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QPalette
from PyQt6.QtWidgets import QApplication, QLabel, QToolTip, QWidget

from .theme import ThemeType, get_current_theme

logger = logging.getLogger(__name__)


class TooltipManager:
    """Gestor centralizado de tooltips para la aplicación."""
    
    def __init__(self):
        self.tooltips_data = self._load_tooltips_data()
        self.setup_tooltip_styles()
    
    def _load_tooltips_data(self) -> Dict[str, str]:
        """Carga los datos de tooltips para diferentes elementos."""
        return {
            # Tooltips para formularios
            'real_name': 'Nombre oficial de la aplicación tal como aparece en el sistema.',
            'logical_name': 'Nombre técnico o identificador interno de la aplicación.',
            'kb_url': 'URL de la documentación oficial en la base de conocimiento.',
            'kb_sync': 'Indica si esta homologación está sincronizada con la KB externa.',
            'homologation_date': 'Fecha en que se realizó la homologación de la aplicación.',
            'has_previous_versions': 'Marca si existen versiones anteriores de esta aplicación.',
            'repository_location': 'Ubicación del repositorio de código fuente (Git, SVN, etc.).',
            'details': 'Información detallada sobre la homologación, configuración especial, etc.',
            
            # Tooltips para tabla
            'table_id': 'Identificador único de la homologación en el sistema.',
            'table_name': 'Haga doble clic para ver detalles completos.',
            'table_repository': 'Ubicación del código fuente. Clic para copiar URL.',
            'table_date': 'Fecha de homologación. Ordenable por columna.',
            'table_creator': 'Usuario que creó esta homologación.',
            'table_updated': 'Última fecha de modificación.',
            
            # Tooltips para filtros
            'filter_name': 'Buscar por nombre exacto o parcial (no sensible a mayúsculas).',
            'filter_repo': 'Filtrar por repositorio específico.',
            'filter_date_from': 'Fecha mínima de homologación (inclusive).',
            'filter_date_to': 'Fecha máxima de homologación (inclusive).',
            'filter_creator': 'Filtrar por usuario que creó la homologación.',
            'filter_kb_sync': 'Filtrar por estado de sincronización con KB.',
            
            # Tooltips para botones
            'btn_new': 'Crear una nueva homologación (Ctrl+N).',
            'btn_edit': 'Editar la homologación seleccionada.',
            'btn_delete': 'Eliminar permanentemente la homologación seleccionada.',
            'btn_details': 'Ver información completa y historial.',
            'btn_refresh': 'Actualizar datos desde la base de datos (F5).',
            'btn_export': 'Exportar datos a CSV, Excel, PDF o JSON (Ctrl+E).',
            'btn_metrics': 'Abrir panel de métricas y estadísticas (Ctrl+M).',
            
            # Tooltips para métricas
            'metrics_total': 'Número total de homologaciones en el sistema.',
            'metrics_recent': 'Homologaciones creadas en el período seleccionado.',
            'metrics_growth': 'Porcentaje de crecimiento respecto al período anterior.',
            'metrics_avg_daily': 'Promedio de homologaciones creadas por día.',
            'metrics_status_chart': 'Distribución de homologaciones por estado.',
            'metrics_top_repos': 'Repositorios más utilizados en homologaciones.',
            
            # Tooltips para paginación
            'pagination_page': 'Número de página actual. Use las flechas o escriba directamente.',
            'pagination_size': 'Cantidad de registros mostrados por página.',
            'pagination_info': 'Rango de registros mostrados del total disponible.',
            
            # Tooltips para tema
            'theme_toggle': 'Alternar entre tema claro y oscuro (Ctrl+T).',
            'theme_system': 'Seguir automáticamente el tema del sistema operativo.',
            'theme_dark': 'Cambiar a tema oscuro manualmente.',
            'theme_light': 'Cambiar a tema claro manualmente.',
            
            # Tooltips para exportación
            'export_format': 'Seleccione el formato de salida para los datos.',
            'export_fields': 'Elija qué campos incluir en la exportación.',
            'export_file': 'Ubicación donde se guardará el archivo exportado.',
            'export_options': 'Configuraciones adicionales para la exportación.'
        }
    
    def setup_tooltip_styles(self):
        """Configura los estilos de tooltips según el tema."""
        current_theme = get_current_theme()
        
        if current_theme == ThemeType.DARK:
            QToolTip.setFont(QFont('Segoe UI', 9))
            # Los estilos de QToolTip se aplicarán globalmente
            tooltip_style = """
                QToolTip {
                    background-color: #333333;
                    color: #ffffff;
                    border: 1px solid #555555;
                    border-radius: 4px;
                    padding: 8px;
                    font-size: 9pt;
                    max-width: 300px;
                }
            """
        else:
            QToolTip.setFont(QFont('Segoe UI', 9))
            tooltip_style = """
                QToolTip {
                    background-color: #f8f8f8;
                    color: #333333;
                    border: 1px solid #cccccc;
                    border-radius: 4px;
                    padding: 8px;
                    font-size: 9pt;
                    max-width: 300px;
                }
            """
        
        # Aplicar estilo globalmente
        app = QApplication.instance()
        if app and isinstance(app, QApplication):
            current_style = app.styleSheet()
            app.setStyleSheet(current_style + tooltip_style)
    
    def set_tooltip(self, widget: QWidget, tooltip_key: str, custom_text: Optional[str] = None):
        """Establece un tooltip en un widget usando la clave o texto personalizado."""
        if custom_text:
            tooltip_text = custom_text
        else:
            tooltip_text = self.tooltips_data.get(tooltip_key, tooltip_key)
        
        widget.setToolTip(tooltip_text)
        
        # Habilitar tracking del mouse para tooltips más responsivos
        widget.setMouseTracking(True)
    
    def get_tooltip_text(self, tooltip_key: str) -> str:
        """Obtiene el texto de un tooltip por su clave."""
        return self.tooltips_data.get(tooltip_key, "")
    
    def update_tooltip_styles(self):
        """Actualiza los estilos de tooltips cuando cambia el tema."""
        self.setup_tooltip_styles()
    
    def add_dynamic_tooltip(self, widget: QWidget, tooltip_key: str, **format_kwargs):
        """Agrega un tooltip dinámico que puede incluir variables."""
        base_text = self.tooltips_data.get(tooltip_key, tooltip_key)
        
        if format_kwargs:
            try:
                tooltip_text = base_text.format(**format_kwargs)
            except KeyError:
                tooltip_text = base_text
        else:
            tooltip_text = base_text
        
        widget.setToolTip(tooltip_text)


class SmartTooltip(QLabel):
    """Tooltip personalizado con funcionalidades avanzadas."""
    
    def __init__(self, text: str, parent: Optional[QWidget] = None):
        super().__init__(text, parent)
        self.setWindowFlags(Qt.WindowType.ToolTip)
        self.setStyleSheet(self._get_tooltip_style())
        self.setWordWrap(True)
        self.setMaximumWidth(400)
        self.adjustSize()
        
        # Timer para auto-ocultado
        self.hide_timer = QTimer()
        self.hide_timer.setSingleShot(True)
        self.hide_timer.timeout.connect(self.hide)
    
    def _get_tooltip_style(self) -> str:
        """Obtiene el estilo del tooltip según el tema actual."""
        current_theme = get_current_theme()
        
        if current_theme == ThemeType.DARK:
            return """
                QLabel {
                    background-color: #2d2d2d;
                    color: #ffffff;
                    border: 1px solid #555555;
                    border-radius: 6px;
                    padding: 10px;
                    font-size: 9pt;
                    font-family: 'Segoe UI';
                }
            """
        else:
            return """
                QLabel {
                    background-color: #ffffcc;
                    color: #333333;
                    border: 1px solid #cccccc;
                    border-radius: 6px;
                    padding: 10px;
                    font-size: 9pt;
                    font-family: 'Segoe UI';
                }
            """
    
    def show_at_position(self, position: QPoint, auto_hide_ms: int = 5000):
        """Muestra el tooltip en una posición específica."""
        self.move(position)
        self.show()
        
        if auto_hide_ms > 0:
            self.hide_timer.start(auto_hide_ms)
    
    def show_near_widget(self, widget: QWidget, auto_hide_ms: int = 5000):
        """Muestra el tooltip cerca de un widget específico."""
        # Calcular posición relativa al widget
        widget_rect = widget.geometry()
        global_pos = widget.mapToGlobal(widget_rect.bottomLeft())
        
        # Ajustar posición para que no se salga de la pantalla
        primary_screen = QApplication.primaryScreen()
        if not primary_screen:
            # Fallback: mostrar en posición fija
            self.move(global_pos.x(), global_pos.y() + 5)
            return
            
        screen = primary_screen.geometry()
        
        x = global_pos.x()
        y = global_pos.y() + 5
        
        # Ajustar si se sale por la derecha
        if x + self.width() > screen.right():
            x = screen.right() - self.width() - 10
        
        # Ajustar si se sale por abajo
        if y + self.height() > screen.bottom():
            y = global_pos.y() - self.height() - 5
        
        self.show_at_position(QPoint(x, y), auto_hide_ms)


class HelpSystem:
    """Sistema de ayuda contextual para la aplicación."""
    
    def __init__(self):
        self.tooltip_manager = TooltipManager()
        self.help_texts = self._load_help_texts()
        self.current_tooltip = None
    
    def _load_help_texts(self) -> Dict[str, str]:
        """Carga textos de ayuda más extensos para diferentes secciones."""
        return {
            'main_window': """
                <h3>Ventana Principal</h3>
                <p>Esta es la ventana principal del Homologador de Aplicaciones.</p>
                <ul>
                <li><b>Tabla:</b> Muestra todas las homologaciones registradas</li>
                <li><b>Filtros:</b> Use el panel izquierdo para filtrar resultados</li>
                <li><b>Botones:</b> Acciones disponibles según sus permisos</li>
                <li><b>Métricas:</b> Acceda al panel de estadísticas desde el menú Ver</li>
                </ul>
            """,
            
            'form_help': """
                <h3>Formulario de Homologación</h3>
                <p>Complete todos los campos obligatorios marcados con asterisco (*).</p>
                <ul>
                <li><b>Nombre Real:</b> Nombre oficial de la aplicación</li>
                <li><b>Repositorio:</b> URL del código fuente (Git, SVN, etc.)</li>
                <li><b>Fecha:</b> Cuándo se realizó la homologación</li>
                <li><b>Detalles:</b> Información adicional relevante</li>
                </ul>
                <p><i>Consejo:</i> Los datos se guardan automáticamente como borrador.</p>
            """,
            
            'filters_help': """
                <h3>Sistema de Filtros</h3>
                <p>Use los filtros para encontrar homologaciones específicas.</p>
                <ul>
                <li><b>Texto libre:</b> Busca en nombre y descripción</li>
                <li><b>Repositorio:</b> Filtra por ubicación de código</li>
                <li><b>Fechas:</b> Rango de fechas de homologación</li>
                <li><b>Usuario:</b> Quien creó la homologación</li>
                </ul>
                <p><i>Consejo:</i> Los filtros se aplican automáticamente al escribir.</p>
            """,
            
            'metrics_help': """
                <h3>Panel de Métricas</h3>
                <p>Visualice estadísticas y tendencias de las homologaciones.</p>
                <ul>
                <li><b>Tarjetas superiores:</b> Métricas principales</li>
                <li><b>Gráficos:</b> Distribución por estado y repositorios</li>
                <li><b>Período:</b> Seleccione el rango temporal</li>
                <li><b>Actualización:</b> Los datos se actualizan automáticamente</li>
                </ul>
                <p><i>Consejo:</i> Use diferentes períodos para análisis de tendencias.</p>
            """
        }
    
    def setup_widget_help(self, widget: QWidget, help_key: str):
        """Configura la ayuda contextual para un widget."""
        # Agregar tooltip básico
        tooltip_text = self.tooltip_manager.get_tooltip_text(help_key)
        if tooltip_text:
            self.tooltip_manager.set_tooltip(widget, help_key)
    
    def show_contextual_help(self, help_key: str, parent_widget: Optional[QWidget] = None):
        """Muestra ayuda contextual extendida."""
        help_text = self.help_texts.get(help_key, "Ayuda no disponible para esta sección.")
        
        # Crear tooltip inteligente con el texto de ayuda
        if self.current_tooltip:
            self.current_tooltip.hide()
        
        self.current_tooltip = SmartTooltip(help_text, parent_widget)
        
        if parent_widget:
            self.current_tooltip.show_near_widget(parent_widget, auto_hide_ms=10000)
        else:
            # Mostrar en el centro de la pantalla
            primary_screen = QApplication.primaryScreen()
            if primary_screen:
                screen = primary_screen.geometry()
                center_x = screen.width() // 2 - self.current_tooltip.width() // 2
                center_y = screen.height() // 2 - self.current_tooltip.height() // 2
                self.current_tooltip.show_at_position(QPoint(center_x, center_y), auto_hide_ms=10000)
            else:
                # Fallback: mostrar en posición por defecto
                self.current_tooltip.show_at_position(QPoint(100, 100), auto_hide_ms=10000)
    
    def update_theme(self):
        """Actualiza el sistema de ayuda cuando cambia el tema."""
        self.tooltip_manager.update_tooltip_styles()
        
        if self.current_tooltip:
            self.current_tooltip.setStyleSheet(self.current_tooltip._get_tooltip_style())


# Instancia global del sistema de ayuda
_help_system = None

def get_help_system() -> HelpSystem:
    """Obtiene la instancia global del sistema de ayuda."""
    global _help_system
    if _help_system is None:
        _help_system = HelpSystem()
    return _help_system

def setup_tooltips(parent_widget: QWidget):
    """Configurar tooltips globalmente para un widget padre."""
    help_system = get_help_system()
    # Esta función puede ser expandida para configurar tooltips automáticamente
    # en todos los widgets hijos de parent_widget
    pass

def setup_widget_tooltips(widget: QWidget, tooltip_key: str):
    """Función de conveniencia para configurar tooltips."""
    help_system = get_help_system()
    help_system.setup_widget_help(widget, tooltip_key)

def show_help(help_key: str, parent_widget: Optional[QWidget] = None):
    """Función de conveniencia para mostrar ayuda contextual."""
    help_system = get_help_system()
    help_system.show_contextual_help(help_key, parent_widget)