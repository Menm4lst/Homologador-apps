"""
Sistema de guía de usuario integrada para la aplicación.
Proporciona tutoriales paso a paso y tour de funcionalidades.
"""

import logging
from typing import List, Dict, Any, Optional, Callable
from PyQt6.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QFrame, QApplication, QDialog
)
from PyQt6.QtCore import Qt, QTimer, QPoint, QRect, pyqtSignal, QEasingCurve, QPropertyAnimation
from PyQt6.QtGui import QFont, QPainter, QPen, QBrush, QColor

from .theme import get_current_theme, ThemeType

logger = logging.getLogger(__name__)


class TourStep:
    """Representa un paso individual en el tour de la aplicación."""
    
    def __init__(self, 
                 target_widget: QWidget, 
                 title: str, 
                 description: str,
                 position: str = "bottom",
                 action: Optional[Callable] = None,
                 highlight: bool = True):
        self.target_widget = target_widget
        self.title = title
        self.description = description
        self.position = position  # "top", "bottom", "left", "right"
        self.action = action  # Acción opcional a ejecutar en este paso
        self.highlight = highlight


class TourGuide(QDialog):
    """Dialog overlay para guiar al usuario a través de la aplicación."""
    
    tour_completed = pyqtSignal()
    tour_cancelled = pyqtSignal()
    
    def __init__(self, parent: QWidget, tour_steps: List[TourStep]):
        super().__init__(parent)
        self.tour_steps = tour_steps
        self.current_step = 0
        self.parent_widget = parent
        self.previous_highlighted_widgets = []  # Para rastrear widgets destacados anteriormente
        
        # Configurar como overlay
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setModal(True)
        
        # Cubrir toda la ventana padre
        if parent:
            self.setGeometry(parent.geometry())
        
        self.setup_ui()
        self.setup_animations()
    
    def setup_ui(self):
        """Configura la interfaz del tour."""
        # Layout principal (invisible)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Crear widget de instrucciones
        self.instruction_widget = TourInstructionWidget()
        self.instruction_widget.next_clicked.connect(self.next_step)
        self.instruction_widget.previous_clicked.connect(self.previous_step)
        self.instruction_widget.skip_clicked.connect(self.skip_tour)
        self.instruction_widget.close_clicked.connect(self.close_tour)
        
        # El widget de instrucciones se posicionará dinámicamente
        self.instruction_widget.setParent(self)
        self.instruction_widget.hide()
    
    def setup_animations(self):
        """Configura las animaciones para el tour."""
        self.fade_animation = QPropertyAnimation(self.instruction_widget, b"windowOpacity")
        self.fade_animation.setDuration(300)
        self.fade_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
    
    def start_tour(self):
        """Inicia el tour desde el primer paso."""
        if not self.tour_steps:
            return
        
        self.current_step = 0
        self.previous_highlighted_widgets.clear()  # Limpiar lista de widgets anteriores
        self.show()
        self.show_current_step()
    
    def show_current_step(self):
        """Muestra el paso actual del tour."""
        if self.current_step >= len(self.tour_steps):
            self.complete_tour()
            return
        
        step = self.tour_steps[self.current_step]
        
        # Agregar el widget del paso anterior a la lista de widgets ocultos
        if self.current_step > 0:
            previous_step = self.tour_steps[self.current_step - 1]
            if (previous_step.target_widget and 
                previous_step.highlight and 
                previous_step.target_widget not in self.previous_highlighted_widgets):
                self.previous_highlighted_widgets.append(previous_step.target_widget)
        
        # Ejecutar acción del paso si existe
        if step.action:
            try:
                step.action()
            except Exception as e:
                logger.error(f"Error ejecutando acción del tour: {e}")
        
        # Actualizar widget de instrucciones
        self.instruction_widget.update_content(
            step.title,
            step.description,
            self.current_step + 1,
            len(self.tour_steps)
        )
        
        # Posicionar widget de instrucciones
        self.position_instruction_widget(step)
        
        # Mostrar con animación
        if not self.instruction_widget.isVisible():
            self.instruction_widget.show()
            self.fade_animation.setStartValue(0.0)
            self.fade_animation.setEndValue(1.0)
            self.fade_animation.start()
        else:
            # Si ya está visible, solo hacer una pequeña animación de "bounce"
            current_pos = self.instruction_widget.pos()
            self.instruction_widget.move(current_pos.x(), current_pos.y() - 10)
            bounce_animation = QPropertyAnimation(self.instruction_widget, b"pos")
            bounce_animation.setDuration(200)
            bounce_animation.setStartValue(self.instruction_widget.pos())
            bounce_animation.setEndValue(current_pos)
            bounce_animation.setEasingCurve(QEasingCurve.Type.OutBounce)
            bounce_animation.start()
        
        # Forzar repintado para mostrar highlight
        self.update()
    
    def position_instruction_widget(self, step: TourStep):
        """Posiciona el widget de instrucciones relativo al target."""
        if not step.target_widget or not step.target_widget.isVisible():
            # Centrar si no hay target válido
            self.center_instruction_widget()
            return
        
        # Obtener geometría del target en coordenadas del overlay
        target_global = step.target_widget.mapToGlobal(QPoint(0, 0))
        overlay_local = self.mapFromGlobal(target_global)
        target_rect = QRect(overlay_local, step.target_widget.size())
        
        instruction_size = self.instruction_widget.sizeHint()
        overlay_rect = self.rect()
        
        # Margen para separación del elemento
        margin = 25
        
        # Lista de posiciones a probar en orden de preferencia
        positions_to_try = []
        
        # Agregar posición preferida primero
        if step.position == "bottom":
            positions_to_try.append(("bottom", target_rect.center().x() - instruction_size.width() // 2, 
                                   target_rect.bottom() + margin))
        elif step.position == "top":
            positions_to_try.append(("top", target_rect.center().x() - instruction_size.width() // 2, 
                                   target_rect.top() - instruction_size.height() - margin))
        elif step.position == "right":
            positions_to_try.append(("right", target_rect.right() + margin, 
                                   target_rect.center().y() - instruction_size.height() // 2))
        elif step.position == "left":
            positions_to_try.append(("left", target_rect.left() - instruction_size.width() - margin, 
                                   target_rect.center().y() - instruction_size.height() // 2))
        
        # Agregar posiciones alternativas
        positions_to_try.extend([
            ("bottom", target_rect.center().x() - instruction_size.width() // 2, 
             target_rect.bottom() + margin),
            ("top", target_rect.center().x() - instruction_size.width() // 2, 
             target_rect.top() - instruction_size.height() - margin),
            ("right", target_rect.right() + margin, 
             target_rect.center().y() - instruction_size.height() // 2),
            ("left", target_rect.left() - instruction_size.width() - margin, 
             target_rect.center().y() - instruction_size.height() // 2),
            ("center", overlay_rect.center().x() - instruction_size.width() // 2,
             overlay_rect.center().y() - instruction_size.height() // 2)
        ])
        
        # Buscar la primera posición que funcione
        final_x, final_y = None, None
        
        for pos_name, x, y in positions_to_try:
            # Verificar si la posición está dentro del overlay
            if (10 <= x <= overlay_rect.width() - instruction_size.width() - 10 and
                10 <= y <= overlay_rect.height() - instruction_size.height() - 10):
                
                # Verificar si no se superpone con el target (excepto para center)
                instruction_rect = QRect(x, y, instruction_size.width(), instruction_size.height())
                target_with_margin = target_rect.adjusted(-margin//2, -margin//2, margin//2, margin//2)
                
                if pos_name == "center" or not instruction_rect.intersects(target_with_margin):
                    final_x, final_y = x, y
                    break
        
        # Si no se encontró una posición válida, usar el centro
        if final_x is None or final_y is None:
            final_x = overlay_rect.center().x() - instruction_size.width() // 2
            final_y = overlay_rect.center().y() - instruction_size.height() // 2
        
        # Aplicar límites finales
        final_x = max(10, min(final_x, overlay_rect.width() - instruction_size.width() - 10))
        final_y = max(10, min(final_y, overlay_rect.height() - instruction_size.height() - 10))
        
        self.instruction_widget.move(final_x, final_y)
        self.instruction_widget.resize(instruction_size)
    
    def center_instruction_widget(self):
        """Centra el widget de instrucciones."""
        instruction_size = self.instruction_widget.sizeHint()
        x = self.width() // 2 - instruction_size.width() // 2
        y = self.height() // 2 - instruction_size.height() // 2
        self.instruction_widget.move(x, y)
        self.instruction_widget.resize(instruction_size)
    
    def next_step(self):
        """Avanza al siguiente paso."""
        self.current_step += 1
        self.show_current_step()
    
    def previous_step(self):
        """Retrocede al paso anterior."""
        if self.current_step > 0:
            # Si retrocedemos, quitar el widget actual de la lista de anteriores
            if self.current_step < len(self.tour_steps):
                current_widget = self.tour_steps[self.current_step].target_widget
                if current_widget in self.previous_highlighted_widgets:
                    self.previous_highlighted_widgets.remove(current_widget)
            
            self.current_step -= 1
            self.show_current_step()
    
    def skip_tour(self):
        """Omite el tour completo."""
        self.tour_cancelled.emit()
        self.close()
    
    def close_tour(self):
        """Cierra el tour."""
        self.tour_cancelled.emit()
        self.close()
    
    def complete_tour(self):
        """Completa el tour exitosamente."""
        self.tour_completed.emit()
        self.close()
    
    def paintEvent(self, event):
        """Pinta el overlay con highlight del elemento actual."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Fondo semi-transparente más sutil
        overlay_color = QColor(0, 0, 0, 60)  # Reducir opacidad de 120 a 60
        painter.fillRect(self.rect(), overlay_color)
        
        # Highlight del elemento actual
        if (self.current_step < len(self.tour_steps) and 
            self.tour_steps[self.current_step].highlight and
            self.tour_steps[self.current_step].target_widget and
            self.tour_steps[self.current_step].target_widget.isVisible()):
            
            step = self.tour_steps[self.current_step]
            target_widget = step.target_widget
            
            # Solo resaltar si no está en la lista de widgets anteriores
            if target_widget not in self.previous_highlighted_widgets:
                # Obtener geometría del target
                target_global = target_widget.mapToGlobal(QPoint(0, 0))
                target_local = self.mapFromGlobal(target_global)
                target_rect = QRect(target_local, target_widget.size())
                
                # Expandir un poco el área highlight
                margin = 12  # Aumentar margen para mejor visibilidad
                highlight_rect = target_rect.adjusted(-margin, -margin, margin, margin)
                
                # Crear recorte para "perforar" el overlay
                painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
                painter.fillRect(highlight_rect, Qt.GlobalColor.transparent)
                
                # Dibujar borde de highlight con glow effect
                painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
                
                # Dibujar sombra exterior para efecto glow
                glow_rect = highlight_rect.adjusted(-4, -4, 4, 4)
                glow_pen = QPen(QColor(0, 120, 215, 100), 8)
                painter.setPen(glow_pen)
                painter.drawRoundedRect(glow_rect, 8, 8)
                
                # Dibujar borde principal más brillante
                highlight_pen = QPen(QColor(0, 160, 255), 4)
                painter.setPen(highlight_pen)
                painter.drawRoundedRect(highlight_rect, 6, 6)
                
                # Dibujar borde interior para mejor definición
                inner_pen = QPen(QColor(255, 255, 255, 180), 2)
                painter.setPen(inner_pen)
                painter.drawRoundedRect(highlight_rect.adjusted(2, 2, -2, -2), 4, 4)


class TourInstructionWidget(QFrame):
    """Widget que muestra las instrucciones de cada paso del tour."""
    
    next_clicked = pyqtSignal()
    previous_clicked = pyqtSignal()
    skip_clicked = pyqtSignal()
    close_clicked = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.apply_theme_styles()
    
    def setup_ui(self):
        """Configura la interfaz del widget de instrucciones."""
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        self.setMaximumWidth(420)  # Aumentado de 350 a 420
        self.setMinimumWidth(380)  # Aumentado de 300 a 380
        self.setMinimumHeight(180)  # Nuevo: altura mínima
        self.setMaximumHeight(300)  # Nuevo: altura máxima
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)  # Aumentado padding de 15 a 18
        layout.setSpacing(12)  # Aumentado espacio de 10 a 12
        
        # Título
        self.title_label = QLabel()
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(14)  # Aumentado de 12 a 14
        self.title_label.setFont(title_font)
        self.title_label.setWordWrap(True)
        layout.addWidget(self.title_label)
        
        # Descripción
        self.description_label = QLabel()
        desc_font = QFont()
        desc_font.setPointSize(11)  # Nuevo: tamaño específico para descripción
        self.description_label.setFont(desc_font)
        self.description_label.setWordWrap(True)
        self.description_label.setMinimumHeight(60)  # Nuevo: altura mínima para descripción
        layout.addWidget(self.description_label)
        
        # Espaciador flexible para empujar el contador y botones hacia abajo
        layout.addStretch()
        
        # Contador de pasos
        self.step_counter = QLabel()
        step_font = QFont()
        step_font.setPointSize(10)  # Aumentado de 9 a 10
        self.step_counter.setFont(step_font)
        self.step_counter.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.step_counter)
        
        # Botones
        button_layout = QHBoxLayout()
        
        self.close_button = QPushButton("✕")
        self.close_button.setMaximumWidth(40)  # Aumentado de 30 a 40
        self.close_button.setMaximumHeight(40)  # Nuevo
        self.close_button.setMinimumWidth(40)   # Nuevo
        self.close_button.setMinimumHeight(40)  # Nuevo
        self.close_button.setToolTip("Cerrar tour")
        self.close_button.clicked.connect(self.close_clicked.emit)
        button_layout.addWidget(self.close_button)
        
        self.skip_button = QPushButton("Omitir")
        self.skip_button.clicked.connect(self.skip_clicked.emit)
        button_layout.addWidget(self.skip_button)
        
        button_layout.addStretch()
        
        self.previous_button = QPushButton("◀ Anterior")
        self.previous_button.clicked.connect(self.previous_clicked.emit)
        button_layout.addWidget(self.previous_button)
        
        self.next_button = QPushButton("Siguiente ▶")
        self.next_button.clicked.connect(self.next_clicked.emit)
        button_layout.addWidget(self.next_button)
        
        layout.addLayout(button_layout)
    
    def update_content(self, title: str, description: str, current_step: int, total_steps: int):
        """Actualiza el contenido del widget."""
        self.title_label.setText(title)
        self.description_label.setText(description)
        self.step_counter.setText(f"Paso {current_step} de {total_steps}")
        
        # Actualizar estado de botones
        self.previous_button.setEnabled(current_step > 1)
        
        if current_step == total_steps:
            self.next_button.setText("Finalizar ✓")
        else:
            self.next_button.setText("Siguiente ▶")
    
    def apply_theme_styles(self):
        """Aplica estilos según el tema actual."""
        current_theme = get_current_theme()
        
        if current_theme == ThemeType.DARK:
            self.setStyleSheet("""
                TourInstructionWidget {
                    background-color: rgba(45, 45, 45, 240);
                    border: 3px solid #0078d4;
                    border-radius: 12px;
                    color: #ffffff;
                    box-shadow: 0px 8px 20px rgba(0, 0, 0, 0.3);
                }
                QLabel {
                    color: #ffffff;
                    background-color: transparent;
                    border: none;
                }
                QLabel[objectName="title_label"] {
                    color: #4fc3f7;
                    font-weight: bold;
                }
                QLabel[objectName="step_counter"] {
                    color: #81c784;
                    font-style: italic;
                    padding: 6px;
                    background-color: rgba(129, 199, 132, 0.1);
                    border-radius: 6px;
                    margin: 4px 0px;
                }
                QPushButton {
                    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #0078d4, stop:1 #005a9e);
                    color: #ffffff;
                    border: 1px solid #0066cc;
                    border-radius: 8px;
                    padding: 10px 20px;
                    font-weight: bold;
                    font-size: 11px;
                    min-width: 80px;
                    min-height: 36px;
                }
                QPushButton:hover {
                    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #106ebe, stop:1 #0066cc);
                    border-color: #0078d4;
                }
                QPushButton:pressed {
                    background-color: #005a9e;
                }
                QPushButton:disabled {
                    background-color: #555555;
                    color: #aaaaaa;
                    border-color: #666666;
                }
                QPushButton[objectName="close_button"] {
                    background-color: #e74c3c;
                    border-color: #c0392b;
                    max-width: 35px;
                    min-width: 35px;
                    border-radius: 17px;
                    font-size: 12px;
                    font-weight: bold;
                }
                QPushButton[objectName="close_button"]:hover {
                    background-color: #c0392b;
                }
                QPushButton[objectName="skip_button"] {
                    background-color: transparent;
                    color: #bdc3c7;
                    border: 1px solid #7f8c8d;
                }
                QPushButton[objectName="skip_button"]:hover {
                    background-color: rgba(127, 140, 141, 0.2);
                    color: #ecf0f1;
                }
            """)
        else:
            self.setStyleSheet("""
                TourInstructionWidget {
                    background-color: rgba(255, 255, 255, 250);
                    border: 3px solid #0078d4;
                    border-radius: 12px;
                    color: #333333;
                    box-shadow: 0px 8px 20px rgba(0, 0, 0, 0.15);
                }
                QLabel {
                    color: #333333;
                    background-color: transparent;
                    border: none;
                }
                QLabel[objectName="title_label"] {
                    color: #0066cc;
                    font-weight: bold;
                }
                QLabel[objectName="step_counter"] {
                    color: #2e7d32;
                    font-style: italic;
                    padding: 4px;
                    background-color: rgba(46, 125, 50, 0.1);
                    border-radius: 4px;
                }
                QPushButton {
                    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #0078d4, stop:1 #005a9e);
                    color: #ffffff;
                    border: 1px solid #0066cc;
                    border-radius: 8px;
                    padding: 10px 20px;
                    font-weight: bold;
                    font-size: 11px;
                    min-width: 80px;
                    min-height: 36px;
                }
                QPushButton:hover {
                    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #106ebe, stop:1 #0066cc);
                    border-color: #0078d4;
                }
                QPushButton:pressed {
                    background-color: #005a9e;
                }
                QPushButton:disabled {
                    background-color: #e0e0e0;
                    color: #999999;
                    border-color: #cccccc;
                }
                QPushButton[objectName="close_button"] {
                    background-color: #e74c3c;
                    border-color: #c0392b;
                    max-width: 40px;
                    min-width: 40px;
                    max-height: 40px;
                    min-height: 40px;
                    border-radius: 20px;
                    font-size: 14px;
                    font-weight: bold;
                    padding: 0px;
                }
                QPushButton[objectName="close_button"]:hover {
                    background-color: #c0392b;
                }
                QPushButton[objectName="skip_button"] {
                    background-color: transparent;
                    color: #7f8c8d;
                    border: 1px solid #bdc3c7;
                }
                QPushButton[objectName="skip_button"]:hover {
                    background-color: rgba(189, 195, 199, 0.2);
                    color: #34495e;
                }
            """)
        
        # Establecer objectName para los estilos específicos
        self.title_label.setObjectName("title_label")
        self.step_counter.setObjectName("step_counter")
        self.close_button.setObjectName("close_button")
        self.skip_button.setObjectName("skip_button")


class UserGuideManager:
    """Gestor principal del sistema de guía de usuario."""
    
    def __init__(self):
        self.available_tours = self._create_tours()
    
    def _create_tours(self) -> Dict[str, List[TourStep]]:
        """Crea los tours disponibles en la aplicación."""
        return {
            'main_window_tour': [],  # Se configurará dinámicamente
            'form_tour': [],         # Se configurará dinámicamente
            'metrics_tour': []       # Se configurará dinámicamente
        }
    
    def create_main_window_tour(self, main_window) -> List[TourStep]:
        """Crea el tour para la ventana principal."""
        steps = []
        
        # Encontrar widgets de la ventana principal
        table_widget = getattr(main_window, 'table_widget', None)
        filter_widget = getattr(main_window, 'filter_widget', None)
        
        if filter_widget:
            steps.append(TourStep(
                target_widget=filter_widget,
                title="Panel de Filtros",
                description="Use este panel para buscar y filtrar homologaciones específicas. Los filtros se aplican automáticamente mientras escribe.",
                position="right"
            ))
        
        if table_widget:
            steps.append(TourStep(
                target_widget=table_widget,
                title="Tabla de Homologaciones",
                description="Aquí se muestran todas las homologaciones. Haga doble clic en una fila para ver detalles completos.",
                position="top"
            ))
        
        # Buscar botones de acción
        central_widget = main_window.centralWidget()
        if central_widget:
            buttons = central_widget.findChildren(QPushButton)
            
            for button in buttons:
                if "Nueva" in button.text():
                    steps.append(TourStep(
                        target_widget=button,
                        title="Crear Nueva Homologación",
                        description="Use este botón para crear una nueva homologación. Se abrirá un formulario completo.",
                        position="top"
                    ))
                    break
            
            for button in buttons:
                if "Métricas" in button.text():
                    steps.append(TourStep(
                        target_widget=button,
                        title="Panel de Métricas",
                        description="Acceda a estadísticas y gráficos de las homologaciones desde aquí.",
                        position="top"
                    ))
                    break
        
        return steps
    
    def create_form_tour(self, form_dialog) -> List[TourStep]:
        """Crea el tour para el formulario de homologación."""
        steps = []
        
        # Buscar campos principales del formulario
        form_fields = [
            ('real_name', 'Nombre Real', 'Este es el nombre oficial de la aplicación como aparece en el sistema.'),
            ('repository_location', 'Repositorio', 'URL del repositorio de código fuente (Git, SVN, etc.).'),
            ('homologation_date', 'Fecha de Homologación', 'Seleccione la fecha en que se realizó la homologación.'),
            ('details', 'Detalles', 'Agregue información adicional relevante sobre la homologación.')
        ]
        
        for field_name, title, description in form_fields:
            field_widget = getattr(form_dialog, field_name, None)
            if field_widget:
                steps.append(TourStep(
                    target_widget=field_widget,
                    title=title,
                    description=description,
                    position="right"
                ))
        
        return steps
    
    def start_tour(self, tour_name: str, parent_widget: QWidget) -> Optional[TourGuide]:
        """Inicia un tour específico."""
        if tour_name == 'main_window_tour':
            tour_steps = self.create_main_window_tour(parent_widget)
        elif tour_name == 'form_tour':
            tour_steps = self.create_form_tour(parent_widget)
        else:
            tour_steps = self.available_tours.get(tour_name, [])
        
        if not tour_steps:
            logger.warning(f"No se encontraron pasos para el tour: {tour_name}")
            return None
        
        tour_guide = TourGuide(parent_widget, tour_steps)
        tour_guide.start_tour()
        
        return tour_guide


# Instancia global del gestor de guías
_guide_manager = None

def get_guide_manager() -> UserGuideManager:
    """Obtiene la instancia global del gestor de guías."""
    global _guide_manager
    if _guide_manager is None:
        _guide_manager = UserGuideManager()
    return _guide_manager

def start_user_tour(tour_name: str, parent_widget: QWidget) -> Optional[TourGuide]:
    """Función de conveniencia para iniciar un tour."""
    guide_manager = get_guide_manager()
    return guide_manager.start_tour(tour_name, parent_widget)