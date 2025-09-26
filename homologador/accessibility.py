"""
Sistema de accesibilidad para la aplicación Homologador.

Este módulo proporciona funcionalidades de accesibilidad incluyendo:
- Navegación completa por teclado
- Soporte para lectores de pantalla
- Modo alto contraste
- Atajos de teclado personalizables
- Navegación espacial mejorada
- Indicadores visuales de foco
"""

import json
import os
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from PyQt6.QtCore import (QEasingCurve, QEvent, QKeyCombination, QObject,
                          QPoint, QPropertyAnimation, QRect, QSettings, QSize,
                          Qt, QTimer, pyqtSignal)
from PyQt6.QtGui import (QAccessible, QAccessibleInterface, QAction, QBrush,
                         QColor, QFocusEvent, QFont, QIcon, QKeySequence,
                         QPainter, QPalette, QPen, QPixmap, QShortcut)
from PyQt6.QtWidgets import (QApplication, QButtonGroup, QCheckBox, QComboBox,
                             QDialog, QFrame, QGridLayout, QGroupBox,
                             QHBoxLayout, QKeySequenceEdit, QLabel, QLineEdit,
                             QListWidget, QListWidgetItem, QMessageBox,
                             QProgressBar, QPushButton, QRadioButton,
                             QScrollArea, QSlider, QSpinBox, QTabWidget,
                             QTextEdit, QVBoxLayout, QWidget)


class AccessibilityMode(Enum):
    """Modos de accesibilidad disponibles."""
    NORMAL = "normal"
    HIGH_CONTRAST = "high_contrast"
    LARGE_TEXT = "large_text"
    SCREEN_READER = "screen_reader"
    KEYBOARD_ONLY = "keyboard_only"


class FocusIndicator(QWidget):
    """Indicador visual de foco mejorado."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.target_widget = None
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(200)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        self.setStyleSheet("""
            FocusIndicator {
                border: 3px solid #007acc;
                border-radius: 6px;
                background: rgba(0, 122, 204, 0.1);
            }
        """)
    
    def show_for_widget(self, widget: QWidget):
        """Muestra el indicador para un widget específico."""
        if not widget or not widget.isVisible():
            self.hide()
            return
        
        self.target_widget = widget
        
        # Calcular posición global
        global_rect = widget.rect()
        global_pos = widget.mapToGlobal(global_rect.topLeft())
        
        # Expandir ligeramente el rectángulo
        margin = 4
        final_rect = QRect(
            global_pos.x() - margin,
            global_pos.y() - margin,
            global_rect.width() + margin * 2,
            global_rect.height() + margin * 2
        )
        
        # Animar a la nueva posición
        self.animation.setStartValue(self.geometry())
        self.animation.setEndValue(final_rect)
        
        if not self.isVisible():
            self.setGeometry(final_rect)
            self.show()
        else:
            self.animation.start()
    
    def paintEvent(self, event):
        """Dibuja el indicador con efectos visuales."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Fondo semi-transparente
        painter.setBrush(QBrush(QColor(0, 122, 204, 25)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(self.rect(), 6, 6)
        
        # Borde pulsante
        pen = QPen(QColor(0, 122, 204), 3)
        pen.setStyle(Qt.PenStyle.SolidLine)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 6, 6)


class KeyboardNavigationManager(QObject):
    """Gestor de navegación por teclado."""
    
    focus_changed = pyqtSignal(QWidget)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.app = QApplication.instance()
        self.focus_indicator = FocusIndicator()
        self.navigation_history = []
        self.current_focus_index = -1
        
        # Instalar filtro de eventos global
        self.app.installEventFilter(self)
        
        # Conectar señales
        self.app.focusChanged.connect(self.on_focus_changed)
    
    def eventFilter(self, obj: QObject, event: QEvent) -> bool:
        """Filtra eventos para mejorar la navegación."""
        if event.type() == QEvent.Type.KeyPress:
            return self.handle_key_press(obj, event)
        elif event.type() == QEvent.Type.FocusIn:
            self.update_focus_indicator(obj)
        
        return super().eventFilter(obj, event)
    
    def handle_key_press(self, obj: QObject, event) -> bool:
        """Maneja las teclas de navegación."""
        key = event.key()
        modifiers = event.modifiers()
        
        # Navegación espacial con flechas
        if modifiers == Qt.KeyboardModifier.AltModifier:
            if key == Qt.Key.Key_Left:
                self.navigate_spatial(Qt.Key.Key_Left)
                return True
            elif key == Qt.Key.Key_Right:
                self.navigate_spatial(Qt.Key.Key_Right)
                return True
            elif key == Qt.Key.Key_Up:
                self.navigate_spatial(Qt.Key.Key_Up)
                return True
            elif key == Qt.Key.Key_Down:
                self.navigate_spatial(Qt.Key.Key_Down)
                return True
        
        # Navegación por historial
        if modifiers == Qt.KeyboardModifier.ControlModifier:
            if key == Qt.Key.Key_BracketLeft:  # Ctrl+[
                self.navigate_backward()
                return True
            elif key == Qt.Key.Key_BracketRight:  # Ctrl+]
                self.navigate_forward()
                return True
        
        # Escape para volver al elemento padre
        if key == Qt.Key.Key_Escape:
            current = self.app.focusWidget()
            if current and current.parent():
                parent = current.parent()
                if isinstance(parent, QWidget) and parent.focusPolicy() != Qt.FocusPolicy.NoFocus:
                    parent.setFocus()
                    return True
        
        return False
    
    def navigate_spatial(self, direction: Qt.Key):
        """Navega espacialmente en la dirección especificada."""
        current = self.app.focusWidget()
        if not current:
            return
        
        # Obtener todos los widgets focusables
        focusable_widgets = self.get_focusable_widgets()
        if not focusable_widgets:
            return
        
        current_pos = current.mapToGlobal(current.rect().center())
        best_widget = None
        best_distance = float('inf')
        
        for widget in focusable_widgets:
            if widget == current:
                continue
            
            widget_pos = widget.mapToGlobal(widget.rect().center())
            
            # Verificar si está en la dirección correcta
            if direction == Qt.Key.Key_Left and widget_pos.x() >= current_pos.x():
                continue
            elif direction == Qt.Key.Key_Right and widget_pos.x() <= current_pos.x():
                continue
            elif direction == Qt.Key.Key_Up and widget_pos.y() >= current_pos.y():
                continue
            elif direction == Qt.Key.Key_Down and widget_pos.y() <= current_pos.y():
                continue
            
            # Calcular distancia
            dx = widget_pos.x() - current_pos.x()
            dy = widget_pos.y() - current_pos.y()
            distance = (dx ** 2 + dy ** 2) ** 0.5
            
            if distance < best_distance:
                best_distance = distance
                best_widget = widget
        
        if best_widget:
            best_widget.setFocus()
    
    def get_focusable_widgets(self) -> List[QWidget]:
        """Obtiene todos los widgets focusables visibles."""
        focusable = []
        
        for window in self.app.topLevelWidgets():
            if window.isVisible():
                focusable.extend(self._get_focusable_children(window))
        
        return focusable
    
    def _get_focusable_children(self, widget: QWidget) -> List[QWidget]:
        """Obtiene recursivamente todos los widgets focusables hijos."""
        focusable = []
        
        if (widget.isVisible() and 
            widget.isEnabled() and 
            widget.focusPolicy() != Qt.FocusPolicy.NoFocus):
            focusable.append(widget)
        
        for child in widget.findChildren(QWidget):
            if (child.isVisible() and 
                child.isEnabled() and 
                child.focusPolicy() != Qt.FocusPolicy.NoFocus):
                focusable.append(child)
        
        return focusable
    
    def on_focus_changed(self, old: QWidget, new: QWidget):
        """Maneja el cambio de foco."""
        if new:
            # Agregar al historial
            if not self.navigation_history or self.navigation_history[-1] != new:
                self.navigation_history.append(new)
                if len(self.navigation_history) > 50:  # Límite del historial
                    self.navigation_history.pop(0)
                self.current_focus_index = len(self.navigation_history) - 1
            
            self.update_focus_indicator(new)
            self.focus_changed.emit(new)
    
    def update_focus_indicator(self, widget: QWidget):
        """Actualiza el indicador de foco."""
        if isinstance(widget, QWidget):
            self.focus_indicator.show_for_widget(widget)
    
    def navigate_backward(self):
        """Navega hacia atrás en el historial."""
        if self.current_focus_index > 0:
            self.current_focus_index -= 1
            widget = self.navigation_history[self.current_focus_index]
            if widget and widget.isVisible() and widget.isEnabled():
                widget.setFocus()
    
    def navigate_forward(self):
        """Navega hacia adelante en el historial."""
        if self.current_focus_index < len(self.navigation_history) - 1:
            self.current_focus_index += 1
            widget = self.navigation_history[self.current_focus_index]
            if widget and widget.isVisible() and widget.isEnabled():
                widget.setFocus()


class ScreenReaderSupport:
    """Soporte para lectores de pantalla."""
    
    @staticmethod
    def set_accessible_name(widget: QWidget, name: str):
        """Establece el nombre accesible del widget."""
        widget.setAccessibleName(name)
    
    @staticmethod
    def set_accessible_description(widget: QWidget, description: str):
        """Establece la descripción accesible del widget."""
        widget.setAccessibleDescription(description)
    
    @staticmethod
    def announce_text(text: str):
        """Anuncia texto al lector de pantalla."""
        # En una implementación real, esto podría usar APIs específicas
        # del sistema operativo para comunicarse con lectores de pantalla
        print(f"[SCREEN_READER]: {text}")
    
    @staticmethod
    def setup_widget_accessibility(widget: QWidget, name: str, description: str = "", role: str = ""):
        """Configura la accesibilidad de un widget."""
        ScreenReaderSupport.set_accessible_name(widget, name)
        if description:
            ScreenReaderSupport.set_accessible_description(widget, description)
        
        # Configurar propiedades adicionales según el tipo de widget
        if isinstance(widget, QPushButton):
            widget.setProperty("accessibleRole", "button")
        elif isinstance(widget, QLineEdit):
            widget.setProperty("accessibleRole", "textbox")
        elif isinstance(widget, QLabel):
            widget.setProperty("accessibleRole", "label")
        elif isinstance(widget, QListWidget):
            widget.setProperty("accessibleRole", "list")
        
        if role:
            widget.setProperty("accessibleRole", role)


class ThemeManager:
    """Gestor de temas y modos de alto contraste."""
    
    def __init__(self):
        self.current_mode = AccessibilityMode.NORMAL
        self.font_scale = 1.0
        
    def apply_high_contrast_theme(self, app: QApplication):
        """Aplica el tema de alto contraste."""
        palette = QPalette()
        
        # Colores de alto contraste
        palette.setColor(QPalette.ColorRole.Window, QColor(0, 0, 0))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.Base, QColor(0, 0, 0))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(42, 42, 42))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor(0, 0, 0))
        palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.Button, QColor(42, 42, 42))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.Link, QColor(100, 150, 255))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(255, 255, 0))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(0, 0, 0))
        
        app.setPalette(palette)
        
        # Estilos adicionales para mejor contraste
        app.setStyleSheet("""
            QWidget {
                background-color: #000000;
                color: #ffffff;
                border: 1px solid #ffffff;
            }
            
            QPushButton {
                background-color: #2a2a2a;
                border: 2px solid #ffffff;
                padding: 8px;
                font-weight: bold;
            }
            
            QPushButton:hover {
                background-color: #ffffff;
                color: #000000;
            }
            
            QPushButton:focus {
                border: 3px solid #ffff00;
                background-color: #ffff00;
                color: #000000;
            }
            
            QLineEdit {
                background-color: #000000;
                border: 2px solid #ffffff;
                padding: 6px;
            }
            
            QLineEdit:focus {
                border: 3px solid #ffff00;
            }
            
            QComboBox {
                background-color: #2a2a2a;
                border: 2px solid #ffffff;
                padding: 6px;
            }
            
            QListWidget {
                background-color: #000000;
                border: 2px solid #ffffff;
            }
            
            QListWidget::item:selected {
                background-color: #ffff00;
                color: #000000;
            }
            
            QTabWidget::pane {
                border: 2px solid #ffffff;
            }
            
            QTabBar::tab {
                background-color: #2a2a2a;
                border: 2px solid #ffffff;
                padding: 8px;
            }
            
            QTabBar::tab:selected {
                background-color: #ffff00;
                color: #000000;
            }
        """)
    
    def apply_large_text_theme(self, app: QApplication, scale: float = 1.5):
        """Aplica el tema de texto grande."""
        self.font_scale = scale
        
        # Obtener la fuente actual y escalarla
        font = app.font()
        original_size = font.pointSize()
        if original_size > 0:
            font.setPointSize(int(original_size * scale))
        else:
            font.setPointSize(int(12 * scale))
        
        app.setFont(font)
    
    def apply_normal_theme(self, app: QApplication):
        """Aplica el tema normal."""
        app.setPalette(QApplication.style().standardPalette())
        app.setStyleSheet("")
        
        # Restaurar fuente normal
        font = app.font()
        font.setPointSize(10)
        app.setFont(font)
    
    def set_mode(self, mode: AccessibilityMode, app: QApplication):
        """Establece el modo de accesibilidad."""
        self.current_mode = mode
        
        if mode == AccessibilityMode.HIGH_CONTRAST:
            self.apply_high_contrast_theme(app)
        elif mode == AccessibilityMode.LARGE_TEXT:
            self.apply_large_text_theme(app)
        elif mode == AccessibilityMode.SCREEN_READER:
            self.apply_normal_theme(app)
            # Configuraciones adicionales para lectores de pantalla
        elif mode == AccessibilityMode.KEYBOARD_ONLY:
            self.apply_normal_theme(app)
            # Configuraciones adicionales para navegación por teclado
        else:
            self.apply_normal_theme(app)


class ShortcutManager:
    """Gestor de atajos de teclado personalizables."""
    
    def __init__(self, parent_widget: QWidget):
        self.parent = parent_widget
        self.shortcuts = {}
        self.actions = {}
        self.settings = QSettings()
        
        self.load_shortcuts()
    
    def register_action(self, name: str, description: str, callback: Callable, 
                       default_shortcut: str = ""):
        """Registra una acción con su atajo."""
        action = QAction(description, self.parent)
        action.triggered.connect(callback)
        
        self.actions[name] = {
            'action': action,
            'description': description,
            'callback': callback,
            'default_shortcut': default_shortcut
        }
        
        # Cargar atajo personalizado o usar el por defecto
        shortcut = self.settings.value(f"shortcuts/{name}", default_shortcut)
        if shortcut:
            self.set_shortcut(name, shortcut)
    
    def set_shortcut(self, action_name: str, shortcut: str):
        """Establece un atajo para una acción."""
        if action_name not in self.actions:
            return False
        
        # Remover atajo anterior si existe
        if action_name in self.shortcuts:
            self.shortcuts[action_name].setParent(None)
        
        # Crear nuevo atajo
        if shortcut:
            shortcut_obj = QShortcut(QKeySequence(shortcut), self.parent)
            shortcut_obj.activated.connect(self.actions[action_name]['callback'])
            self.shortcuts[action_name] = shortcut_obj
            
            # Guardar en configuración
            self.settings.setValue(f"shortcuts/{action_name}", shortcut)
            
            return True
        
        return False
    
    def get_shortcut(self, action_name: str) -> str:
        """Obtiene el atajo actual de una acción."""
        if action_name in self.shortcuts:
            return self.shortcuts[action_name].key().toString()
        return ""
    
    def get_all_shortcuts(self) -> Dict[str, Dict[str, str]]:
        """Obtiene todos los atajos registrados."""
        result = {}
        for name, action_data in self.actions.items():
            result[name] = {
                'description': action_data['description'],
                'shortcut': self.get_shortcut(name),
                'default_shortcut': action_data['default_shortcut']
            }
        return result
    
    def load_shortcuts(self):
        """Carga los atajos desde la configuración."""
        # Los atajos se cargarán automáticamente cuando se registren las acciones
        pass
    
    def reset_to_defaults(self):
        """Restaura todos los atajos a sus valores por defecto."""
        for name, action_data in self.actions.items():
            default_shortcut = action_data['default_shortcut']
            self.set_shortcut(name, default_shortcut)


class AccessibilitySettingsWidget(QWidget):
    """Widget de configuración de accesibilidad."""
    
    settings_changed = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme_manager = ThemeManager()
        self.settings = QSettings()
        
        self.setup_ui()
        self.load_settings()
    
    def setup_ui(self):
        """Configura la interfaz."""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        
        # Título
        title_label = QLabel("♿ Configuración de Accesibilidad")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setWeight(QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        main_layout.addWidget(title_label)
        
        # Crear pestañas
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        self.create_visual_tab()
        self.create_navigation_tab()
        self.create_shortcuts_tab()
        self.create_screen_reader_tab()
        
        # Botones de acción
        buttons_layout = QHBoxLayout()
        
        self.apply_button = QPushButton("Aplicar Cambios")
        self.apply_button.setStyleSheet("""
            QPushButton {
                background-color: #45B7D1;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3498db;
            }
        """)
        self.apply_button.clicked.connect(self.apply_settings)
        
        self.reset_button = QPushButton("Restaurar Valores por Defecto")
        self.reset_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        self.reset_button.clicked.connect(self.reset_settings)
        
        buttons_layout.addWidget(self.apply_button)
        buttons_layout.addWidget(self.reset_button)
        buttons_layout.addStretch()
        
        main_layout.addLayout(buttons_layout)
    
    def create_visual_tab(self):
        """Crea la pestaña de configuración visual."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Modo de tema
        theme_group = QGroupBox("Tema y Contraste")
        theme_layout = QVBoxLayout(theme_group)
        
        self.theme_normal = QRadioButton("Tema Normal")
        self.theme_high_contrast = QRadioButton("Alto Contraste")
        self.theme_large_text = QRadioButton("Texto Grande")
        
        self.theme_group = QButtonGroup()
        self.theme_group.addButton(self.theme_normal, 0)
        self.theme_group.addButton(self.theme_high_contrast, 1)
        self.theme_group.addButton(self.theme_large_text, 2)
        
        theme_layout.addWidget(self.theme_normal)
        theme_layout.addWidget(self.theme_high_contrast)
        theme_layout.addWidget(self.theme_large_text)
        
        layout.addWidget(theme_group)
        
        # Tamaño de fuente
        font_group = QGroupBox("Tamaño de Fuente")
        font_layout = QHBoxLayout(font_group)
        
        font_layout.addWidget(QLabel("Escala:"))
        self.font_scale_slider = QSlider(Qt.Orientation.Horizontal)
        self.font_scale_slider.setRange(80, 200)
        self.font_scale_slider.setValue(100)
        self.font_scale_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.font_scale_slider.setTickInterval(20)
        
        self.font_scale_label = QLabel("100%")
        self.font_scale_slider.valueChanged.connect(
            lambda v: self.font_scale_label.setText(f"{v}%")
        )
        
        font_layout.addWidget(self.font_scale_slider)
        font_layout.addWidget(self.font_scale_label)
        
        layout.addWidget(font_group)
        
        # Indicadores visuales
        visual_group = QGroupBox("Indicadores Visuales")
        visual_layout = QVBoxLayout(visual_group)
        
        self.show_focus_indicator = QCheckBox("Mostrar indicador de foco mejorado")
        self.highlight_hover = QCheckBox("Resaltar elementos al pasar el mouse")
        self.animate_transitions = QCheckBox("Animaciones de transición")
        
        visual_layout.addWidget(self.show_focus_indicator)
        visual_layout.addWidget(self.highlight_hover)
        visual_layout.addWidget(self.animate_transitions)
        
        layout.addWidget(visual_group)
        
        layout.addStretch()
        self.tab_widget.addTab(tab, "🎨 Visual")
    
    def create_navigation_tab(self):
        """Crea la pestaña de configuración de navegación."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Navegación por teclado
        keyboard_group = QGroupBox("Navegación por Teclado")
        keyboard_layout = QVBoxLayout(keyboard_group)
        
        self.enable_spatial_navigation = QCheckBox("Habilitar navegación espacial (Alt + flechas)")
        self.enable_tab_cycling = QCheckBox("Permitir navegación circular con Tab")
        self.enable_escape_to_parent = QCheckBox("Escape para ir al elemento padre")
        
        keyboard_layout.addWidget(self.enable_spatial_navigation)
        keyboard_layout.addWidget(self.enable_tab_cycling)
        keyboard_layout.addWidget(self.enable_escape_to_parent)
        
        layout.addWidget(keyboard_group)
        
        # Velocidad de navegación
        speed_group = QGroupBox("Velocidad de Navegación")
        speed_layout = QHBoxLayout(speed_group)
        
        speed_layout.addWidget(QLabel("Velocidad:"))
        self.navigation_speed = QSlider(Qt.Orientation.Horizontal)
        self.navigation_speed.setRange(1, 10)
        self.navigation_speed.setValue(5)
        
        self.speed_label = QLabel("Normal")
        self.navigation_speed.valueChanged.connect(self.update_speed_label)
        
        speed_layout.addWidget(self.navigation_speed)
        speed_layout.addWidget(self.speed_label)
        
        layout.addWidget(speed_group)
        
        # Orden de navegación
        order_group = QGroupBox("Orden de Navegación")
        order_layout = QVBoxLayout(order_group)
        
        self.nav_order_logical = QRadioButton("Orden lógico (izquierda a derecha, arriba a abajo)")
        self.nav_order_spatial = QRadioButton("Orden espacial (basado en posición)")
        self.nav_order_custom = QRadioButton("Orden personalizado")
        
        self.nav_order_group = QButtonGroup()
        self.nav_order_group.addButton(self.nav_order_logical, 0)
        self.nav_order_group.addButton(self.nav_order_spatial, 1)
        self.nav_order_group.addButton(self.nav_order_custom, 2)
        
        order_layout.addWidget(self.nav_order_logical)
        order_layout.addWidget(self.nav_order_spatial)
        order_layout.addWidget(self.nav_order_custom)
        
        layout.addWidget(order_group)
        
        layout.addStretch()
        self.tab_widget.addTab(tab, "⌨️ Navegación")
    
    def create_shortcuts_tab(self):
        """Crea la pestaña de configuración de atajos."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Lista de atajos
        shortcuts_group = QGroupBox("Atajos de Teclado Personalizados")
        shortcuts_layout = QVBoxLayout(shortcuts_group)
        
        # Tabla de atajos
        self.shortcuts_list = QListWidget()
        self.shortcuts_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #ddd;
                border-radius: 6px;
                background-color: white;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #eee;
            }
            QListWidget::item:selected {
                background-color: #e3f2fd;
            }
        """)
        shortcuts_layout.addWidget(self.shortcuts_list)
        
        # Botones de edición
        edit_layout = QHBoxLayout()
        
        self.edit_shortcut_button = QPushButton("Editar Atajo")
        self.reset_shortcut_button = QPushButton("Restaurar")
        
        edit_layout.addWidget(self.edit_shortcut_button)
        edit_layout.addWidget(self.reset_shortcut_button)
        edit_layout.addStretch()
        
        shortcuts_layout.addLayout(edit_layout)
        
        layout.addWidget(shortcuts_group)
        
        # Información
        info_label = QLabel("""
        💡 <b>Consejos:</b><br>
        • Use Ctrl, Alt, Shift + una tecla para crear atajos únicos<br>
        • Evite atajos que puedan conflictar con el sistema<br>
        • Los atajos son específicos de esta aplicación
        """)
        info_label.setStyleSheet("""
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 6px;
            padding: 12px;
            margin-top: 10px;
        """)
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        layout.addStretch()
        self.tab_widget.addTab(tab, "🔗 Atajos")
    
    def create_screen_reader_tab(self):
        """Crea la pestaña de configuración de lector de pantalla."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Configuración de lector de pantalla
        reader_group = QGroupBox("Lector de Pantalla")
        reader_layout = QVBoxLayout(reader_group)
        
        self.enable_screen_reader = QCheckBox("Habilitar soporte para lector de pantalla")
        self.verbose_descriptions = QCheckBox("Descripciones detalladas")
        self.announce_focus_changes = QCheckBox("Anunciar cambios de foco")
        self.announce_state_changes = QCheckBox("Anunciar cambios de estado")
        
        reader_layout.addWidget(self.enable_screen_reader)
        reader_layout.addWidget(self.verbose_descriptions)
        reader_layout.addWidget(self.announce_focus_changes)
        reader_layout.addWidget(self.announce_state_changes)
        
        layout.addWidget(reader_group)
        
        # Configuración de voz
        voice_group = QGroupBox("Configuración de Voz")
        voice_layout = QGridLayout(voice_group)
        
        voice_layout.addWidget(QLabel("Velocidad:"), 0, 0)
        self.voice_speed = QSlider(Qt.Orientation.Horizontal)
        self.voice_speed.setRange(1, 10)
        self.voice_speed.setValue(5)
        voice_layout.addWidget(self.voice_speed, 0, 1)
        
        voice_layout.addWidget(QLabel("Volumen:"), 1, 0)
        self.voice_volume = QSlider(Qt.Orientation.Horizontal)
        self.voice_volume.setRange(1, 10)
        self.voice_volume.setValue(8)
        voice_layout.addWidget(self.voice_volume, 1, 1)
        
        voice_layout.addWidget(QLabel("Tono:"), 2, 0)
        self.voice_pitch = QSlider(Qt.Orientation.Horizontal)
        self.voice_pitch.setRange(1, 10)
        self.voice_pitch.setValue(5)
        voice_layout.addWidget(self.voice_pitch, 2, 1)
        
        layout.addWidget(voice_group)
        
        # Prueba de voz
        test_group = QGroupBox("Prueba")
        test_layout = QVBoxLayout(test_group)
        
        self.test_text = QLineEdit("Este es un texto de prueba para el lector de pantalla")
        test_button = QPushButton("🔊 Probar Voz")
        test_button.clicked.connect(self.test_voice)
        
        test_layout.addWidget(self.test_text)
        test_layout.addWidget(test_button)
        
        layout.addWidget(test_group)
        
        layout.addStretch()
        self.tab_widget.addTab(tab, "🔊 Lector")
    
    def update_speed_label(self, value: int):
        """Actualiza la etiqueta de velocidad."""
        labels = ["Muy Lenta", "Lenta", "Lenta", "Normal", "Normal", 
                 "Normal", "Rápida", "Rápida", "Muy Rápida", "Muy Rápida"]
        if 1 <= value <= 10:
            self.speed_label.setText(labels[value - 1])
    
    def test_voice(self):
        """Prueba la configuración de voz."""
        text = self.test_text.text()
        ScreenReaderSupport.announce_text(f"Prueba de voz: {text}")
    
    def load_settings(self):
        """Carga la configuración guardada."""
        # Tema
        theme_mode = self.settings.value("accessibility/theme_mode", "normal")
        if theme_mode == "high_contrast":
            self.theme_high_contrast.setChecked(True)
        elif theme_mode == "large_text":
            self.theme_large_text.setChecked(True)
        else:
            self.theme_normal.setChecked(True)
        
        # Fuente
        font_scale = self.settings.value("accessibility/font_scale", 100, type=int)
        self.font_scale_slider.setValue(font_scale)
        
        # Indicadores visuales
        self.show_focus_indicator.setChecked(
            self.settings.value("accessibility/show_focus_indicator", True, type=bool)
        )
        self.highlight_hover.setChecked(
            self.settings.value("accessibility/highlight_hover", True, type=bool)
        )
        self.animate_transitions.setChecked(
            self.settings.value("accessibility/animate_transitions", True, type=bool)
        )
        
        # Navegación
        self.enable_spatial_navigation.setChecked(
            self.settings.value("accessibility/spatial_navigation", True, type=bool)
        )
        self.enable_tab_cycling.setChecked(
            self.settings.value("accessibility/tab_cycling", True, type=bool)
        )
        self.enable_escape_to_parent.setChecked(
            self.settings.value("accessibility/escape_to_parent", True, type=bool)
        )
        
        navigation_speed = self.settings.value("accessibility/navigation_speed", 5, type=int)
        self.navigation_speed.setValue(navigation_speed)
        
        # Orden de navegación
        nav_order = self.settings.value("accessibility/navigation_order", "logical")
        if nav_order == "spatial":
            self.nav_order_spatial.setChecked(True)
        elif nav_order == "custom":
            self.nav_order_custom.setChecked(True)
        else:
            self.nav_order_logical.setChecked(True)
        
        # Lector de pantalla
        self.enable_screen_reader.setChecked(
            self.settings.value("accessibility/screen_reader", False, type=bool)
        )
        self.verbose_descriptions.setChecked(
            self.settings.value("accessibility/verbose_descriptions", True, type=bool)
        )
        self.announce_focus_changes.setChecked(
            self.settings.value("accessibility/announce_focus", True, type=bool)
        )
        self.announce_state_changes.setChecked(
            self.settings.value("accessibility/announce_state", True, type=bool)
        )
        
        # Voz
        self.voice_speed.setValue(
            self.settings.value("accessibility/voice_speed", 5, type=int)
        )
        self.voice_volume.setValue(
            self.settings.value("accessibility/voice_volume", 8, type=int)
        )
        self.voice_pitch.setValue(
            self.settings.value("accessibility/voice_pitch", 5, type=int)
        )
    
    def apply_settings(self):
        """Aplica la configuración actual."""
        settings = self.get_current_settings()
        
        # Guardar configuración
        for key, value in settings.items():
            self.settings.setValue(f"accessibility/{key}", value)
        
        self.settings_changed.emit(settings)
        
        QMessageBox.information(
            self, 
            "Configuración Aplicada", 
            "La configuración de accesibilidad se ha aplicado correctamente."
        )
    
    def reset_settings(self):
        """Restaura la configuración por defecto."""
        reply = QMessageBox.question(
            self,
            "Restaurar Configuración",
            "¿Está seguro de que desea restaurar todos los valores por defecto?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Limpiar configuración
            self.settings.beginGroup("accessibility")
            self.settings.remove("")
            self.settings.endGroup()
            
            # Recargar valores por defecto
            self.load_settings()
            
            QMessageBox.information(
                self,
                "Configuración Restaurada",
                "La configuración se ha restaurado a los valores por defecto."
            )
    
    def get_current_settings(self) -> Dict[str, Any]:
        """Obtiene la configuración actual."""
        settings = {}
        
        # Tema
        if self.theme_high_contrast.isChecked():
            settings['theme_mode'] = 'high_contrast'
        elif self.theme_large_text.isChecked():
            settings['theme_mode'] = 'large_text'
        else:
            settings['theme_mode'] = 'normal'
        
        # Fuente
        settings['font_scale'] = self.font_scale_slider.value()
        
        # Indicadores visuales
        settings['show_focus_indicator'] = self.show_focus_indicator.isChecked()
        settings['highlight_hover'] = self.highlight_hover.isChecked()
        settings['animate_transitions'] = self.animate_transitions.isChecked()
        
        # Navegación
        settings['spatial_navigation'] = self.enable_spatial_navigation.isChecked()
        settings['tab_cycling'] = self.enable_tab_cycling.isChecked()
        settings['escape_to_parent'] = self.enable_escape_to_parent.isChecked()
        settings['navigation_speed'] = self.navigation_speed.value()
        
        # Orden de navegación
        if self.nav_order_spatial.isChecked():
            settings['navigation_order'] = 'spatial'
        elif self.nav_order_custom.isChecked():
            settings['navigation_order'] = 'custom'
        else:
            settings['navigation_order'] = 'logical'
        
        # Lector de pantalla
        settings['screen_reader'] = self.enable_screen_reader.isChecked()
        settings['verbose_descriptions'] = self.verbose_descriptions.isChecked()
        settings['announce_focus'] = self.announce_focus_changes.isChecked()
        settings['announce_state'] = self.announce_state_changes.isChecked()
        
        # Voz
        settings['voice_speed'] = self.voice_speed.value()
        settings['voice_volume'] = self.voice_volume.value()
        settings['voice_pitch'] = self.voice_pitch.value()
        
        return settings


class AccessibilityManager:
    """Gestor principal de accesibilidad."""
    
    def __init__(self, app: QApplication, main_window: QWidget):
        self.app = app
        self.main_window = main_window
        self.theme_manager = ThemeManager()
        self.keyboard_manager = KeyboardNavigationManager()
        self.shortcut_manager = ShortcutManager(main_window)
        self.settings = QSettings()
        
        self.setup_default_shortcuts()
        self.load_accessibility_settings()
    
    def setup_default_shortcuts(self):
        """Configura los atajos por defecto."""
        # Atajos principales
        self.shortcut_manager.register_action(
            "toggle_search", "Alternar búsqueda", 
            lambda: None, "Ctrl+F"
        )
        self.shortcut_manager.register_action(
            "new_item", "Nuevo elemento", 
            lambda: None, "Ctrl+N"
        )
        self.shortcut_manager.register_action(
            "save", "Guardar", 
            lambda: None, "Ctrl+S"
        )
        self.shortcut_manager.register_action(
            "export", "Exportar datos", 
            lambda: None, "Ctrl+E"
        )
        self.shortcut_manager.register_action(
            "help", "Mostrar ayuda", 
            lambda: None, "F1"
        )
        self.shortcut_manager.register_action(
            "accessibility", "Configuración de accesibilidad", 
            self.show_accessibility_settings, "Ctrl+Alt+A"
        )
        
        # Atajos de navegación
        self.shortcut_manager.register_action(
            "focus_search", "Enfocar búsqueda", 
            lambda: None, "Ctrl+K"
        )
        self.shortcut_manager.register_action(
            "focus_main", "Enfocar contenido principal", 
            lambda: None, "Ctrl+M"
        )
        self.shortcut_manager.register_action(
            "toggle_high_contrast", "Alternar alto contraste", 
            self.toggle_high_contrast, "Ctrl+Alt+H"
        )
    
    def load_accessibility_settings(self):
        """Carga la configuración de accesibilidad."""
        theme_mode = self.settings.value("accessibility/theme_mode", "normal")
        
        if theme_mode == "high_contrast":
            self.theme_manager.set_mode(AccessibilityMode.HIGH_CONTRAST, self.app)
        elif theme_mode == "large_text":
            self.theme_manager.set_mode(AccessibilityMode.LARGE_TEXT, self.app)
        else:
            self.theme_manager.set_mode(AccessibilityMode.NORMAL, self.app)
    
    def show_accessibility_settings(self):
        """Muestra el diálogo de configuración de accesibilidad."""
        dialog = QDialog(self.main_window)
        dialog.setWindowTitle("Configuración de Accesibilidad")
        dialog.setModal(True)
        dialog.resize(600, 500)
        
        layout = QVBoxLayout(dialog)
        
        settings_widget = AccessibilitySettingsWidget()
        settings_widget.settings_changed.connect(self.apply_accessibility_settings)
        layout.addWidget(settings_widget)
        
        # Botón cerrar
        close_button = QPushButton("Cerrar")
        close_button.clicked.connect(dialog.accept)
        layout.addWidget(close_button)
        
        dialog.exec()
    
    def apply_accessibility_settings(self, settings: Dict[str, Any]):
        """Aplica la configuración de accesibilidad."""
        theme_mode = settings.get('theme_mode', 'normal')
        
        if theme_mode == 'high_contrast':
            self.theme_manager.set_mode(AccessibilityMode.HIGH_CONTRAST, self.app)
        elif theme_mode == 'large_text':
            font_scale = settings.get('font_scale', 100) / 100.0
            self.theme_manager.apply_large_text_theme(self.app, font_scale)
        else:
            self.theme_manager.set_mode(AccessibilityMode.NORMAL, self.app)
    
    def toggle_high_contrast(self):
        """Alterna el modo de alto contraste."""
        current_mode = self.theme_manager.current_mode
        
        if current_mode == AccessibilityMode.HIGH_CONTRAST:
            self.theme_manager.set_mode(AccessibilityMode.NORMAL, self.app)
        else:
            self.theme_manager.set_mode(AccessibilityMode.HIGH_CONTRAST, self.app)
    
    def setup_widget_accessibility(self, widget: QWidget, name: str, description: str = ""):
        """Configura la accesibilidad de un widget."""
        ScreenReaderSupport.setup_widget_accessibility(widget, name, description)
    
    def announce_to_screen_reader(self, text: str):
        """Anuncia texto al lector de pantalla."""
        if self.settings.value("accessibility/screen_reader", False, type=bool):
            ScreenReaderSupport.announce_text(text)


if __name__ == "__main__":
    import sys
    
    app = QApplication(sys.argv)
    
    # Crear ventana principal de prueba
    main_window = QWidget()
    main_window.setWindowTitle("Prueba de Accesibilidad")
    main_window.resize(800, 600)
    
    layout = QVBoxLayout(main_window)
    
    # Agregar algunos widgets de prueba
    layout.addWidget(QLabel("Etiqueta de prueba"))
    layout.addWidget(QLineEdit("Campo de texto"))
    layout.addWidget(QPushButton("Botón de prueba"))
    
    # Inicializar gestor de accesibilidad
    accessibility_manager = AccessibilityManager(app, main_window)
    
    # Mostrar configuración de accesibilidad
    settings_widget = AccessibilitySettingsWidget()
    layout.addWidget(settings_widget)
    
    main_window.show()
    sys.exit(app.exec())