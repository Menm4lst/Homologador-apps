"""
Configuraciones adicionales de tema y personalización visual.
Permite ajustes finos del dark theme y efectos especiales.
"""

from __future__ import annotations

from typing import Optional, Dict, Any, List

from PyQt6.QtCore import (
    QEasingCurve,
    QParallelAnimationGroup,
    QPropertyAnimation,
    QRect,
    QTimer)
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QGraphicsDropShadowEffect,
    QGraphicsOpacityEffect,
    QMainWindow,
    QWidget)


class ThemeEffects:
    """Efectos visuales adicionales para mejorar la experiencia del usuario."""
    
    @staticmethod
    def add_shadow_effect(widget: QWidget, blur_radius: int = 10, offset_x: int = 0, offset_y: int = 2) -> None:
        """Agrega efecto de sombra a un widget."""
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(blur_radius)
        shadow.setXOffset(offset_x)
        shadow.setYOffset(offset_y)
        shadow.setColor(QColor(0, 0, 0, 80))  # Sombra semi-transparente
        widget.setGraphicsEffect(shadow)
    
    @staticmethod
    def add_glow_effect(widget: QWidget, color: str = "#0078d4", blur_radius: int = 15) -> None:
        """Agrega efecto de resplandor a un widget."""
        glow = QGraphicsDropShadowEffect()
        glow.setBlurRadius(blur_radius)
        glow.setXOffset(0)
        glow.setYOffset(0)
        glow.setColor(QColor(color))
        widget.setGraphicsEffect(glow)
    
    @staticmethod
    def create_fade_animation(widget: QWidget, duration: int = 250) -> QPropertyAnimation:
        """Crea animación de fade in/out."""
        opacity_effect = QGraphicsOpacityEffect()
        widget.setGraphicsEffect(opacity_effect)
        
        animation = QPropertyAnimation(opacity_effect, b"opacity")
        animation.setDuration(duration)
        animation.setStartValue(0.0)
        animation.setEndValue(1.0)
        animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        
        return animation

class DarkThemeCustomizer:
    """Personalizador avanzado del tema oscuro."""
    
    # Variaciones de color para diferentes estados
    ACCENT_COLORS = {
        "blue": "#0078d4",      # Azul Microsoft (default)
        "purple": "#8b5cf6",    # Púrpura
        "green": "#16a085",     # Verde esmeralda
        "orange": "#f39c12",    # Naranja
        "red": "#e74c3c",       # Rojo
        "teal": "#00b894"       # Verde azulado
    }
    
    @staticmethod
    def get_custom_stylesheet(accent_color: str = "blue"):
        """Retorna stylesheet personalizado con color de acento."""
        color = DarkThemeCustomizer.ACCENT_COLORS.get(accent_color, "#0078d4")
        
        return f"""
        /* Personalización adicional con color de acento */
        QPushButton:default {{
            background-color: {color};
            border: 2px solid {color};
        }}
        
        QPushButton:default:hover {{
            background-color: {DarkThemeCustomizer._lighten_color(color, 10)};
        }}
        
        QLineEdit:focus, QTextEdit:focus {{
            border: 2px solid {color};
        }}
        
        QTableWidget::item:selected {{
            background-color: {color};
        }}
        
        QTabBar::tab:selected {{
            border-bottom: 2px solid {color};
        }}
        
        QProgressBar::chunk {{
            background-color: {color};
        }}
        
        /* Efectos de hover mejorados */
        QPushButton {{
            transition: all 0.2s ease;
        }}
        
        QTableWidget::item {{
            transition: background-color 0.15s ease;
        }}
        
        /* Scrollbars personalizadas */
        QScrollBar::handle:vertical:hover, QScrollBar::handle:horizontal:hover {{
            background-color: {color};
        }}
        
        /* Efectos especiales para botones importantes */
        QPushButton[styleClass="primary"] {{
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 {color}, stop: 1 {DarkThemeCustomizer._darken_color(color, 15)});
            border: none;
            font-weight: bold;
        }}
        
        QPushButton[styleClass="primary"]:hover {{
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 {DarkThemeCustomizer._lighten_color(color, 10)}, 
                                      stop: 1 {color});
        }}
        """
    
    @staticmethod
    def _lighten_color(color: str, percent: int) -> str:
        """Aclara un color en un porcentaje dado."""
        # Implementación simple - en producción usar librería de colores
        if color.startswith('#'):
            color = color[1:]
        
        r = int(color[0:2], 16)
        g = int(color[2:4], 16)
        b = int(color[4:6], 16)
        
        r = min(255, r + int(255 * percent / 100))
        g = min(255, g + int(255 * percent / 100))
        b = min(255, b + int(255 * percent / 100))
        
        return f"#{r:02x}{g:02x}{b:02x}"
    
    @staticmethod
    def _darken_color(color: str, percent: int) -> str:
        """Oscurece un color en un porcentaje dado."""
        if color.startswith('#'):
            color = color[1:]
        
        r = int(color[0:2], 16)
        g = int(color[2:4], 16)
        b = int(color[4:6], 16)
        
        r = max(0, r - int(255 * percent / 100))
        g = max(0, g - int(255 * percent / 100))
        b = max(0, b - int(255 * percent / 100))
        
        return f"#{r:02x}{g:02x}{b:02x}"

class WindowCustomizer:
    """Personalización específica para ventanas."""
    
    @staticmethod
    def setup_login_window_effects(window: QWidget) -> None:
        """Configura efectos especiales para la ventana de login."""
        # Sombra para la ventana
        ThemeEffects.add_shadow_effect(window, blur_radius=20, offset_y=5)
        
        # Animación de aparición
        fade_animation = ThemeEffects.create_fade_animation(window, duration=300)
        fade_animation.start()
    
    @staticmethod
    def setup_main_window_effects(window: QWidget) -> None:
        """Configura efectos para la ventana principal."""
        # Efecto de sombra sutil
        ThemeEffects.add_shadow_effect(window, blur_radius=15, offset_y=3)
    
    @staticmethod
    def setup_dialog_effects(dialog: QDialog) -> None:
        """Configura efectos para diálogos."""
        # Sombra más pronunciada para diálogos
        ThemeEffects.add_shadow_effect(dialog, blur_radius=25, offset_y=8)
        
        # Animación de entrada
        fade_animation = ThemeEffects.create_fade_animation(dialog, duration=200)
        fade_animation.start()

# Configuración de tema por defecto
DEFAULT_THEME_CONFIG = {
    "accent_color": "blue",
    "enable_animations": True,
    "enable_shadows": True,
    "enable_hover_effects": True,
    "table_alternating_rows": True,
    "button_gradients": False  # Por ahora deshabilitado para mejor rendimiento
}

class ThemeTransitionManager:
    """Gestiona transiciones suaves entre temas."""
    
    def __init__(self, duration: int = 300):
        """Inicializa el gestor de transiciones.
        
        Args:
            duration: Duración de la animación en milisegundos
        """
        self.duration = duration
        self.animations = QParallelAnimationGroup()
        self.widgets: list[QWidget] = []
        self.current_theme: Optional[str] = None
        self.target_theme: Optional[str] = None
    
    def prepare_transition(self, widget: QWidget, target_theme: str) -> None:
        """Prepara la transición de tema para un widget.
        
        Args:
            widget: Widget al que aplicar la transición
            target_theme: Tema objetivo ("dark" o "light")
        """
        self.widgets.append(widget)
        self.target_theme = target_theme
        
        # Crear efecto de opacidad
        opacity_effect = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(opacity_effect)
        
        # Crear animación de fade out
        fade_out = QPropertyAnimation(opacity_effect, b"opacity")
        fade_out.setDuration(self.duration // 2)
        fade_out.setStartValue(1.0)
        fade_out.setEndValue(0.3)  # No llegamos a 0 para no hacer invisible el widget
        fade_out.setEasingCurve(QEasingCurve.Type.InOutCubic)
        
        self.animations.addAnimation(fade_out)
        
        # Al terminar el fade out, aplicamos el tema
        self.animations.finished.connect(self._apply_theme_and_fade_in)
    
    def _apply_theme_and_fade_in(self) -> None:
        """Aplica el tema y realiza la animación de fade in."""
        # Desconectar para evitar recursión
        self.animations.finished.disconnect(self._apply_theme_and_fade_in)
        
        # Aplicar el nuevo tema a todos los widgets
        from .theme import set_widget_style_class
        target_theme = self.target_theme
        if target_theme is None:
            return
        for widget in self.widgets:
            set_widget_style_class(widget, target_theme)
        
        # Crear grupo de animaciones para fade in
        fade_in_group = QParallelAnimationGroup()
        
        # Para cada widget, crear fade in
        for widget in self.widgets:
            opacity_effect = widget.graphicsEffect()
            fade_in = QPropertyAnimation(opacity_effect, b"opacity")
            fade_in.setDuration(self.duration // 2)
            fade_in.setStartValue(0.3)
            fade_in.setEndValue(1.0)
            fade_in.setEasingCurve(QEasingCurve.Type.InOutCubic)
            fade_in_group.addAnimation(fade_in)
        
        # Iniciar fade in
        fade_in_group.start()
        
        # Limpiar
        self.widgets = []
        self.target_theme = None
    
    def start_transition(self) -> None:
        """Inicia la transición de tema."""
        if not self.widgets or not self.target_theme:
            return
        
        self.animations.start()

def apply_theme_customizations(app: QApplication, config: Optional[Dict[str, Any]] = None) -> None:
    """Aplica personalizaciones adicionales del tema."""
    if config is None:
        config = DEFAULT_THEME_CONFIG
    
    # Aplicar stylesheet personalizado
    custom_styles = DarkThemeCustomizer.get_custom_stylesheet(config.get("accent_color", "blue"))
    
    # Obtener stylesheet actual y agregar personalizaciones
    current_stylesheet = app.styleSheet()
    app.setStyleSheet(current_stylesheet + custom_styles)

def create_glass_effect_stylesheet() -> str:
    """Crea efecto de vidrio/cristal para ciertos elementos."""
    return """
    /* Efecto de vidrio para frames especiales */
    QFrame[styleClass="glass"] {
        background-color: rgba(45, 45, 45, 180);
        border: 1px solid rgba(255, 255, 255, 30);
        border-radius: 8px;
    }
    
    /* Efecto blur para elementos de fondo */
    QWidget[styleClass="blur-background"] {
        background-color: rgba(30, 30, 30, 200);
        border-radius: 6px;
    }
    """