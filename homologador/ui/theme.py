"""
Sistema de temas y estilos para el Homologador de Aplicaciones.
Proporciona estilos light y dark theme consistentes para toda la aplicación.
Incluye detección automática del tema del sistema operativo.
"""




import json
import os
import sys

from PyQt6.QtCore import QObject, QSettings, Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtWidgets import QApplication, QMessageBox, QWidget

from enum import Enum
import ctypes
import platform
class ThemeType(Enum):
    """Tipos de temas disponibles."""
    DARK = "dark"
    LIGHT = "light"
    SYSTEM = "system"  # Nuevo: seguir el tema del sistema

class ThemeMonitor(QObject):
    """Monitorea cambios en el tema del sistema y emite señales cuando cambia."""
    theme_changed = pyqtSignal(ThemeType)
    
    def __init__(self):
        super().__init__()
        self.current_system_theme = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_system_theme)
        # Verificar cada 5 segundos (podría ser más o menos frecuente según necesidad)
        self.timer.start(5000)
        # Verificar inmediatamente al iniciar
        self.check_system_theme()
        
    def check_system_theme(self):
        """Verifica si ha cambiado el tema del sistema."""
        detected_theme = detect_system_theme()
        
        # Si es la primera verificación o el tema ha cambiado
        if self.current_system_theme is None or self.current_system_theme != detected_theme:
            self.current_system_theme = detected_theme
            self.theme_changed.emit(detected_theme)

# Instancia global del monitor de tema
_theme_monitor = None

def get_theme_monitor():
    """Obtiene o crea la instancia del monitor de tema."""
    global _theme_monitor
    if _theme_monitor is None:
        _theme_monitor = ThemeMonitor()
    return _theme_monitor

class ThemeSettings:
    """Gestiona la configuración de temas."""
    
    CONFIG_PATH = os.path.join(os.path.expanduser("~"), ".homologador_config")
    
    @staticmethod
    def save_theme_preference(theme_type: ThemeType):
        """Guarda la preferencia de tema del usuario."""
        if not os.path.exists(ThemeSettings.CONFIG_PATH):
            os.makedirs(ThemeSettings.CONFIG_PATH)
            
        config_file = os.path.join(ThemeSettings.CONFIG_PATH, "theme_config.json")
        config = {"theme": theme_type.value}
        
        try:
            with open(config_file, "w") as f:
                json.dump(config, f)
            return True
        except Exception as e:
            print(f"Error guardando preferencia de tema: {e}")
            return False
    
    @staticmethod
    def load_theme_preference() -> ThemeType:
        """Carga la preferencia de tema guardada."""
        config_file = os.path.join(ThemeSettings.CONFIG_PATH, "theme_config.json")
        
        if not os.path.exists(config_file):
            return ThemeType.DARK  # Tema oscuro por defecto
            
        try:
            with open(config_file, "r") as f:
                config = json.load(f)
                theme_str = config.get("theme", ThemeType.DARK.value)
                if theme_str == "system":
                    return ThemeType.SYSTEM
                elif theme_str == "light":
                    return ThemeType.LIGHT
                else:
                    return ThemeType.DARK
        except Exception as e:
            print(f"Error cargando preferencia de tema: {e}")
            return ThemeType.DARK

class DarkTheme:
    """Tema oscuro profesional con tonalidades negros y azules para toda la aplicación."""
    
    # Colores principales - Negro con toques azules
    BACKGROUND_PRIMARY = "#0d1117"      # Negro profundo (GitHub dark)
    BACKGROUND_SECONDARY = "#161b22"    # Negro azulado secundario
    BACKGROUND_TERTIARY = "#21262d"     # Gris azulado para controles
    BACKGROUND_HOVER = "#30363d"        # Hover con toque azul
    BACKGROUND_SELECTED = "#1f6feb"     # Azul vibrante para selección
    BACKGROUND_ACCENT = "#0969da"       # Azul de acento
    BACKGROUND_SIDEBAR = "#010409"      # Negro puro para sidebars
    
    # Texto con mejores contrastes
    TEXT_PRIMARY = "#f0f6fc"            # Blanco azulado suave
    TEXT_SECONDARY = "#7d8590"          # Gris azulado para texto secundario
    TEXT_DISABLED = "#484f58"           # Gris deshabilitado
    TEXT_PLACEHOLDER = "#6e7681"        # Placeholder azulado
    TEXT_ACCENT = "#58a6ff"             # Texto de acento azul
    
    # Bordes y separadores azulados
    BORDER_PRIMARY = "#30363d"          # Borde principal gris azulado
    BORDER_SECONDARY = "#21262d"        # Borde secundario
    BORDER_FOCUS = "#1f6feb"           # Borde de foco azul
    BORDER_ACCENT = "#388bfd"          # Borde de acento
    
    # Estados de botones con gradientes azules
    BUTTON_PRIMARY = "#238636"          # Verde GitHub para acciones principales
    BUTTON_PRIMARY_HOVER = "#2ea043"    # Verde hover
    BUTTON_PRIMARY_PRESSED = "#1a7f37"  # Verde presionado
    BUTTON_SECONDARY = "#21262d"        # Botón secundario
    BUTTON_SECONDARY_HOVER = "#30363d"  # Hover secundario
    BUTTON_DANGER = "#da3633"           # Rojo para eliminar
    BUTTON_DANGER_HOVER = "#f85149"     # Rojo hover
    BUTTON_INFO = "#1f6feb"             # Azul información
    BUTTON_INFO_HOVER = "#388bfd"       # Azul información hover
    
    # Estados especiales con paleta azul
    WARNING = "#d29922"                 # Amarillo anaranjado
    ERROR = "#f85149"                   # Rojo vibrante
    SUCCESS = "#238636"                 # Verde GitHub
    INFO = "#1f6feb"                    # Azul información
    
    # Gradientes especiales
    GRADIENT_PRIMARY = "qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #161b22, stop: 1 #0d1117)"
    GRADIENT_SECONDARY = "qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #30363d, stop: 1 #21262d)"
    GRADIENT_BLUE = "qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #1f6feb, stop: 1 #0969da)"
    GRADIENT_DARK = "qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #21262d, stop: 1 #161b22)"

    @staticmethod
    def get_stylesheet():
        """Retorna el stylesheet completo para la aplicación con tema negro-azul."""
        return f"""
        /* ===== CONFIGURACIÓN GLOBAL ===== */
        QWidget {{
            background: {DarkTheme.GRADIENT_PRIMARY};
            color: {DarkTheme.TEXT_PRIMARY};
            font-family: 'Segoe UI', 'San Francisco', 'Helvetica Neue', Arial, sans-serif;
            font-size: 9pt;
            selection-background-color: {DarkTheme.BACKGROUND_SELECTED};
            border: none;
        }}
        
        /* ===== VENTANAS PRINCIPALES ===== */
        QMainWindow {{
            background: {DarkTheme.GRADIENT_PRIMARY};
            border: 2px solid {DarkTheme.BORDER_ACCENT};
        }}
        
        QDialog {{
            background: {DarkTheme.GRADIENT_DARK};
            border: 2px solid {DarkTheme.BORDER_FOCUS};
            border-radius: 8px;
        }}
        
        /* ===== BARRAS DE TÍTULO Y MENÚS ===== */
        QMenuBar {{
            background: {DarkTheme.BACKGROUND_SIDEBAR};
            color: {DarkTheme.TEXT_PRIMARY};
            border-bottom: 2px solid {DarkTheme.BORDER_ACCENT};
            padding: 4px;
        }}
        
        QMenuBar::item {{
            background-color: transparent;
            padding: 8px 12px;
            border-radius: 4px;
            margin: 2px;
        }}
        
        QMenuBar::item:selected {{
            background: {DarkTheme.GRADIENT_BLUE};
            color: white;
        }}
        
        QMenu {{
            background: {DarkTheme.BACKGROUND_SECONDARY};
            border: 2px solid {DarkTheme.BORDER_FOCUS};
            border-radius: 6px;
            padding: 4px;
        }}
        
        QMenu::item {{
            padding: 8px 20px;
            border-radius: 4px;
            margin: 1px;
        }}
        
        QMenu::item:selected {{
            background: {DarkTheme.GRADIENT_BLUE};
            color: white;
        }}
        
        /* ===== ETIQUETAS ===== */
        QLabel {{
            color: {DarkTheme.TEXT_PRIMARY};
            background-color: transparent;
            border: none;
            font-weight: 500;
        }}
        
        QLabel[styleClass="title"] {{
            font-size: 16pt;
            font-weight: bold;
            color: {DarkTheme.TEXT_ACCENT};
            margin-bottom: 12px;
            text-shadow: 0px 1px 2px rgba(31, 111, 235, 0.3);
        }}
        
        QLabel[styleClass="subtitle"] {{
            font-size: 12pt;
            color: {DarkTheme.TEXT_SECONDARY};
            margin-bottom: 8px;
            font-weight: 600;
        }}
        
        QLabel[styleClass="error"] {{
            color: {DarkTheme.ERROR};
            font-weight: bold;
            background-color: rgba(248, 81, 73, 0.1);
            padding: 4px 8px;
            border-radius: 4px;
            border-left: 3px solid {DarkTheme.ERROR};
        }}
        
        QLabel[styleClass="success"] {{
            color: {DarkTheme.SUCCESS};
            font-weight: bold;
            background-color: rgba(35, 134, 54, 0.1);
            padding: 4px 8px;
            border-radius: 4px;
            border-left: 3px solid {DarkTheme.SUCCESS};
        }}
        
        QLabel[styleClass="info"] {{
            color: {DarkTheme.TEXT_ACCENT};
            background-color: rgba(31, 111, 235, 0.1);
            padding: 4px 8px;
            border-radius: 4px;
            border-left: 3px solid {DarkTheme.BORDER_FOCUS};
        }}
        
        /* ===== CAMPOS DE TEXTO ===== */
        QLineEdit {{
            background: {DarkTheme.GRADIENT_DARK};
            border: 2px solid {DarkTheme.BORDER_SECONDARY};
            border-radius: 6px;
            padding: 10px 12px;
            color: {DarkTheme.TEXT_PRIMARY};
            font-size: 10pt;
            min-height: 16px;
        }}
        
        QLineEdit:focus {{
            border: 2px solid {DarkTheme.BORDER_FOCUS};
            background: {DarkTheme.BACKGROUND_SECONDARY};
            box-shadow: 0px 0px 8px rgba(31, 111, 235, 0.3);
        }}
        
        QLineEdit:disabled {{
            background-color: {DarkTheme.BACKGROUND_PRIMARY};
            color: {DarkTheme.TEXT_DISABLED};
            border: 1px solid {DarkTheme.BORDER_SECONDARY};
        }}
        
        QLineEdit::placeholder {{
            color: {DarkTheme.TEXT_PLACEHOLDER};
        }}
        
        QTextEdit {{
            background-color: {DarkTheme.BACKGROUND_TERTIARY};
            border: 1px solid {DarkTheme.BORDER_SECONDARY};
            border-radius: 4px;
            padding: 8px;
            color: {DarkTheme.TEXT_PRIMARY};
        }}
        
        QTextEdit:focus {{
            border: 2px solid {DarkTheme.BORDER_FOCUS};
        }}
        
        /* ===== BOTONES MODERNOS ===== */
        QPushButton {{
            background: {DarkTheme.GRADIENT_BLUE};
            color: white;
            border: 2px solid {DarkTheme.BORDER_ACCENT};
            border-radius: 8px;
            padding: 12px 20px;
            font-weight: bold;
            font-size: 10pt;
            min-width: 100px;
            min-height: 20px;
        }}
        
        QPushButton:hover {{
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #388bfd, stop: 1 #1f6feb);
            border: 2px solid {DarkTheme.TEXT_ACCENT};
            transform: translateY(-1px);
        }}
        
        QPushButton:pressed {{
            background: {DarkTheme.BACKGROUND_ACCENT};
            border: 2px solid {DarkTheme.BORDER_FOCUS};
            transform: translateY(1px);
        }}
        
        QPushButton:disabled {{
            background: {DarkTheme.BACKGROUND_TERTIARY};
            color: {DarkTheme.TEXT_DISABLED};
            border: 2px solid {DarkTheme.BORDER_SECONDARY};
        }}
        
        /* Botón secundario con estilo negro-azul */
        QPushButton[styleClass="secondary"] {{
            background: {DarkTheme.GRADIENT_DARK};
            color: {DarkTheme.TEXT_PRIMARY};
            border: 2px solid {DarkTheme.BORDER_PRIMARY};
        }}
        
        QPushButton[styleClass="secondary"]:hover {{
            background: {DarkTheme.BACKGROUND_HOVER};
            border: 2px solid {DarkTheme.BORDER_FOCUS};
            color: {DarkTheme.TEXT_ACCENT};
        }}
        
        /* Botón de peligro */
        QPushButton[styleClass="danger"] {{
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #f85149, stop: 1 #da3633);
            color: white;
            border: 2px solid #b62324;
        }}
        
        QPushButton[styleClass="danger"]:hover {{
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #ff7875, stop: 1 #f85149);
            border: 2px solid #da3633;
        }}
        
        /* Botón de éxito */
        QPushButton[styleClass="success"] {{
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #2ea043, stop: 1 #238636);
            color: white;
            border: 2px solid #1a7f37;
        }}
        
        QPushButton[styleClass="success"]:hover {{
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #46954a, stop: 1 #2ea043);
            border: 2px solid #238636;
        }}
        
        /* Botón de información */
        QPushButton[styleClass="info"] {{
            background: {DarkTheme.GRADIENT_BLUE};
            color: white;
            border: 2px solid {DarkTheme.BUTTON_INFO};
        }}
        
        QPushButton[styleClass="info"]:hover {{
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #58a6ff, stop: 1 #388bfd);
            border: 2px solid {DarkTheme.BUTTON_INFO_HOVER};
        }}
        
        /* ===== COMBOBOX MODERNO ===== */
        QComboBox {{
            background: {DarkTheme.GRADIENT_SECONDARY};
            border: 2px solid {DarkTheme.BORDER_ACCENT};
            border-radius: 8px;
            padding: 8px 12px;
            color: {DarkTheme.TEXT_PRIMARY};
            min-width: 120px;
            font-weight: 500;
        }}
        
        QComboBox:hover {{
            background: {DarkTheme.GRADIENT_BLUE};
            border: 2px solid {DarkTheme.TEXT_ACCENT};
            color: white;
        }}
        
        QComboBox:focus {{
            border: 2px solid {DarkTheme.TEXT_ACCENT};
            background: {DarkTheme.GRADIENT_BLUE};
            color: white;
        }}
        
        QComboBox::drop-down {{
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 25px;
            border-left: 2px solid {DarkTheme.BORDER_ACCENT};
            border-top-right-radius: 6px;
            border-bottom-right-radius: 6px;
            background: {DarkTheme.GRADIENT_DARK};
        }}
        
        QComboBox::drop-down:hover {{
            background: {DarkTheme.GRADIENT_BLUE};
        }}
        
        QComboBox::down-arrow {{
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 5px solid {DarkTheme.TEXT_ACCENT};
            width: 0px;
            height: 0px;
        }}
        
        QComboBox QAbstractItemView {{
            background: {DarkTheme.GRADIENT_PRIMARY};
            border: 2px solid {DarkTheme.BORDER_ACCENT};
            border-radius: 8px;
            selection-background-color: {DarkTheme.GRADIENT_BLUE};
            color: {DarkTheme.TEXT_PRIMARY};
            padding: 4px;
        }}
        
        QComboBox QAbstractItemView::item {{
            padding: 8px;
            border-radius: 4px;
        }}
        
        QComboBox QAbstractItemView::item:hover {{
            background: {DarkTheme.BACKGROUND_HOVER};
            color: {DarkTheme.TEXT_ACCENT};
        }}
        
        QComboBox QAbstractItemView::item:selected {{
            background: {DarkTheme.GRADIENT_BLUE};
            color: white;
        }}
        
        /* ===== TABLAS MODERNAS ===== */
        QTableWidget {{
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #161b22, stop: 1 #0d1117);
            alternate-background-color: #21262d;
            gridline-color: #30363d;
            color: #f0f6fc;
            border: 2px solid {DarkTheme.BORDER_FOCUS};
            border-radius: 8px;
            selection-background-color: #1f6feb;
            font-size: 10pt;
            font-weight: 500;
        }}
        
        QTableWidget::item {{
            padding: 12px 8px;
            border-bottom: 1px solid #30363d;
            border-right: 1px solid #30363d;
            color: #f0f6fc;
            background: transparent;
        }}
        
        QTableWidget::item:selected {{
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #1f6feb, stop: 1 #0969da);
            color: #ffffff;
            border: 1px solid #58a6ff;
            font-weight: bold;
        }}
        
        QTableWidget::item:hover {{
            background-color: rgba(88, 166, 255, 0.2);
            border: 1px solid #58a6ff;
            color: #ffffff;
        }}
        
        QTableWidget::item:focus {{
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #1f6feb, stop: 1 #0969da);
            border: 2px solid #58a6ff;
            color: #ffffff;
            font-weight: bold;
        }}
        
        QHeaderView::section {{
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #30363d, stop: 1 #21262d);
            color: #ffffff;
            padding: 12px 8px;
            border: none;
            border-right: 2px solid #58a6ff;
            border-bottom: 2px solid #1f6feb;
            font-weight: bold;
            font-size: 11pt;
        }}
        
        QHeaderView::section:hover {{
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #1f6feb, stop: 1 #0969da);
            color: #ffffff;
        }}
        
        QHeaderView::section:first {{
            border-top-left-radius: 6px;
        }}
        
        QHeaderView::section:last {{
            border-top-right-radius: 6px;
        }}
        
        /* Estilos para filas alternadas */
        QTableWidget::item:alternate {{
            background-color: rgba(33, 38, 45, 0.8);
            color: #f0f6fc;
        }}
        
        QTableWidget::item:alternate:selected {{
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #1f6feb, stop: 1 #0969da);
            color: #ffffff;
            font-weight: bold;
        }}
        
        QTableWidget::item:alternate:hover {{
            background-color: rgba(88, 166, 255, 0.3);
            color: #ffffff;
        }}
        
        /* ===== SCROLLBARS MODERNOS ===== */
        QScrollBar:vertical {{
            background: {DarkTheme.BACKGROUND_SECONDARY};
            width: 14px;
            margin: 2px;
            border-radius: 7px;
            border: 1px solid {DarkTheme.BORDER_SECONDARY};
        }}
        
        QScrollBar::handle:vertical {{
            background: {DarkTheme.GRADIENT_BLUE};
            min-height: 30px;
            border-radius: 6px;
            margin: 2px;
            border: 1px solid {DarkTheme.BORDER_ACCENT};
        }}
        
        QScrollBar::handle:vertical:hover {{
            background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 #4fc3f7, stop: 1 #29b6f6);
            border: 1px solid {DarkTheme.TEXT_ACCENT};
        }}
        
        QScrollBar::handle:vertical:pressed {{
            background: {DarkTheme.GRADIENT_DARK};
        }}
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        
        QScrollBar:horizontal {{
            background: {DarkTheme.BACKGROUND_SECONDARY};
            height: 14px;
            margin: 2px;
            border-radius: 7px;
            border: 1px solid {DarkTheme.BORDER_SECONDARY};
        }}
        
        QScrollBar::handle:horizontal {{
            background: {DarkTheme.GRADIENT_BLUE};
            min-width: 30px;
            border-radius: 6px;
            margin: 2px;
            border: 1px solid {DarkTheme.BORDER_ACCENT};
        }}
        
        QScrollBar::handle:horizontal:hover {{
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #4fc3f7, stop: 1 #29b6f6);
            border: 1px solid {DarkTheme.TEXT_ACCENT};
        }}
        
        QScrollBar::handle:horizontal:pressed {{
            background: {DarkTheme.GRADIENT_DARK};
        }}
        
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            width: 0px;
        }}
        
        QScrollBar::corner {{
            background: {DarkTheme.BACKGROUND_SECONDARY};
        }}
        
        /* ===== CHECKBOX Y RADIOBUTTON ===== */
        QCheckBox {{
            color: {DarkTheme.TEXT_PRIMARY};
            spacing: 8px;
        }}
        
        QCheckBox::indicator {{
            width: 16px;
            height: 16px;
            border: 1px solid {DarkTheme.BORDER_SECONDARY};
            border-radius: 3px;
            background-color: {DarkTheme.BACKGROUND_TERTIARY};
        }}
        
        QCheckBox::indicator:checked {{
            background-color: {DarkTheme.BUTTON_PRIMARY};
            border: 1px solid {DarkTheme.BUTTON_PRIMARY};
        }}
        
        QCheckBox::indicator:checked {{
            image: none;
        }}
        
        QRadioButton {{
            color: {DarkTheme.TEXT_PRIMARY};
            spacing: 8px;
        }}
        
        QRadioButton::indicator {{
            width: 16px;
            height: 16px;
            border: 1px solid {DarkTheme.BORDER_SECONDARY};
            border-radius: 8px;
            background-color: {DarkTheme.BACKGROUND_TERTIARY};
        }}
        
        QRadioButton::indicator:checked {{
            background-color: {DarkTheme.BUTTON_PRIMARY};
            border: 1px solid {DarkTheme.BUTTON_PRIMARY};
        }}
        
        /* ===== GROUPBOX ===== */
        QGroupBox {{
            color: {DarkTheme.TEXT_PRIMARY};
            border: 1px solid {DarkTheme.BORDER_SECONDARY};
            border-radius: 6px;
            margin-top: 10px;
            padding-top: 10px;
            font-weight: bold;
        }}
        
        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 0 8px;
            background-color: {DarkTheme.BACKGROUND_PRIMARY};
            color: {DarkTheme.TEXT_PRIMARY};
        }}
        
        /* ===== SEPARADORES ===== */
        QFrame[frameShape="4"] {{ /* HLine */
            color: {DarkTheme.BORDER_SECONDARY};
            background-color: {DarkTheme.BORDER_SECONDARY};
            height: 1px;
            border: none;
        }}
        
        QFrame[frameShape="5"] {{ /* VLine */
            color: {DarkTheme.BORDER_SECONDARY};
            background-color: {DarkTheme.BORDER_SECONDARY};
            width: 1px;
            border: none;
        }}
        
        /* ===== TOOLBAR ===== */
        QToolBar {{
            background-color: {DarkTheme.BACKGROUND_SECONDARY};
            border: none;
            border-bottom: 1px solid {DarkTheme.BORDER_SECONDARY};
            padding: 4px;
        }}
        
        QToolBar::handle {{
            background-color: {DarkTheme.BORDER_SECONDARY};
            width: 2px;
            margin: 4px;
        }}
        
        QToolButton {{
            background-color: transparent;
            border: 1px solid transparent;
            border-radius: 4px;
            padding: 6px;
            margin: 2px;
        }}
        
        QToolButton:hover {{
            background-color: {DarkTheme.BACKGROUND_HOVER};
            border: 1px solid {DarkTheme.BORDER_SECONDARY};
        }}
        
        QToolButton:pressed {{
            background-color: {DarkTheme.BACKGROUND_SELECTED};
        }}
        
        /* ===== TABS ===== */
        QTabWidget::pane {{
            border: 1px solid {DarkTheme.BORDER_SECONDARY};
            background-color: {DarkTheme.BACKGROUND_PRIMARY};
            border-radius: 4px;
        }}
        
        QTabWidget::tab-bar {{
            alignment: left;
        }}
        
        QTabBar::tab {{
            background-color: {DarkTheme.BACKGROUND_TERTIARY};
            color: {DarkTheme.TEXT_SECONDARY};
            border: 1px solid {DarkTheme.BORDER_SECONDARY};
            padding: 8px 16px;
            margin-right: 2px;
            border-bottom: none;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        }}
        
        QTabBar::tab:selected {{
            background-color: {DarkTheme.BACKGROUND_PRIMARY};
            color: {DarkTheme.TEXT_PRIMARY};
            border-bottom: 2px solid {DarkTheme.BUTTON_PRIMARY};
        }}
        
        QTabBar::tab:hover {{
            background-color: {DarkTheme.BACKGROUND_HOVER};
            color: {DarkTheme.TEXT_PRIMARY};
        }}
        
        QTabBar::tab:!selected {{
            margin-top: 2px;
        }}
        QStatusBar {{
            background-color: {DarkTheme.BACKGROUND_SECONDARY};
            color: {DarkTheme.TEXT_PRIMARY};
            border-top: 1px solid {DarkTheme.BORDER_SECONDARY};
        }}
        
        /* ===== MENUBAR ===== */
        QMenuBar {{
            background-color: {DarkTheme.BACKGROUND_SECONDARY};
            color: {DarkTheme.TEXT_PRIMARY};
            border-bottom: 1px solid {DarkTheme.BORDER_SECONDARY};
        }}
        
        QMenuBar::item {{
            background-color: transparent;
            padding: 4px 8px;
        }}
        
        QMenuBar::item:selected {{
            background-color: {DarkTheme.BACKGROUND_HOVER};
        }}
        
        QMenu {{
            background-color: {DarkTheme.BACKGROUND_SECONDARY};
            color: {DarkTheme.TEXT_PRIMARY};
            border: 1px solid {DarkTheme.BORDER_PRIMARY};
        }}
        
        QMenu::item {{
            padding: 6px 20px;
        }}
        
        QMenu::item:selected {{
            background-color: {DarkTheme.BACKGROUND_SELECTED};
        }}
        
        /* ===== TOOLTIP ===== */
        QToolTip {{
            background-color: {DarkTheme.BACKGROUND_SECONDARY};
            color: {DarkTheme.TEXT_PRIMARY};
            border: 1px solid {DarkTheme.BORDER_PRIMARY};
            padding: 4px;
            border-radius: 4px;
        }}
        
        /* ===== PROGRESS BAR MODERNO ===== */
        QProgressBar {{
            background: {DarkTheme.BACKGROUND_SECONDARY};
            border: 2px solid {DarkTheme.BORDER_ACCENT};
            border-radius: 8px;
            text-align: center;
            color: {DarkTheme.TEXT_ACCENT};
            font-weight: bold;
            padding: 2px;
        }}
        
        QProgressBar::chunk {{
            background: {DarkTheme.GRADIENT_BLUE};
            border-radius: 6px;
            margin: 1px;
        }}
        
        /* ===== SPINBOX ===== */
        QSpinBox, QDoubleSpinBox {{
            background-color: {DarkTheme.BACKGROUND_TERTIARY};
            border: 1px solid {DarkTheme.BORDER_SECONDARY};
            border-radius: 4px;
            padding: 4px;
            color: {DarkTheme.TEXT_PRIMARY};
            min-width: 60px;
        }}
        
        QSpinBox:focus, QDoubleSpinBox:focus {{
            border: 2px solid {DarkTheme.BORDER_FOCUS};
        }}
        
        QSpinBox::up-button, QSpinBox::down-button {{
            background-color: {DarkTheme.BACKGROUND_SECONDARY};
            border: 1px solid {DarkTheme.BORDER_SECONDARY};
            border-radius: 2px;
        }}
        
        QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
            background-color: {DarkTheme.BACKGROUND_HOVER};
        }}
        
        /* ===== DATE/TIME EDIT ===== */
        QDateEdit, QTimeEdit, QDateTimeEdit {{
            background-color: {DarkTheme.BACKGROUND_TERTIARY};
            border: 1px solid {DarkTheme.BORDER_SECONDARY};
            border-radius: 4px;
            padding: 6px;
            color: {DarkTheme.TEXT_PRIMARY};
        }}
        
        QDateEdit:focus, QTimeEdit:focus, QDateTimeEdit:focus {{
            border: 2px solid {DarkTheme.BORDER_FOCUS};
        }}
        
        /* ===== SLIDER ===== */
        QSlider::groove:horizontal {{
            border: 1px solid {DarkTheme.BORDER_SECONDARY};
            height: 4px;
            background: {DarkTheme.BACKGROUND_TERTIARY};
            border-radius: 2px;
        }}
        
        QSlider::handle:horizontal {{
            background: {DarkTheme.BUTTON_PRIMARY};
            border: 1px solid {DarkTheme.BORDER_FOCUS};
            width: 16px;
            height: 16px;
            margin: -6px 0;
            border-radius: 8px;
        }}
        
        QSlider::handle:horizontal:hover {{
            background: {DarkTheme.BUTTON_PRIMARY_HOVER};
        }}
        
        /* ===== SPLITTER MODERNO ===== */
        QSplitter {{
            background: {DarkTheme.BACKGROUND_PRIMARY};
        }}
        
        QSplitter::handle {{
            background: {DarkTheme.BORDER_ACCENT};
            border: 1px solid {DarkTheme.BORDER_SECONDARY};
        }}
        
        QSplitter::handle:horizontal {{
            width: 3px;
            margin: 2px 0px;
        }}
        
        QSplitter::handle:vertical {{
            height: 3px;
            margin: 0px 2px;
        }}
        
        QSplitter::handle:hover {{
            background: {DarkTheme.TEXT_ACCENT};
        }}
        
        /* ===== DOCK WIDGET ===== */
        QDockWidget {{
            background: {DarkTheme.BACKGROUND_PRIMARY};
            border: 2px solid {DarkTheme.BORDER_ACCENT};
            border-radius: 8px;
            titlebar-close-icon: none;
            titlebar-normal-icon: none;
        }}
        
        QDockWidget::title {{
            background: {DarkTheme.GRADIENT_DARK};
            color: {DarkTheme.TEXT_ACCENT};
            padding: 8px;
            font-weight: bold;
            border-top-left-radius: 6px;
            border-top-right-radius: 6px;
        }}
        
        /* ===== STATUS BAR ===== */
        QStatusBar {{
            background: {DarkTheme.GRADIENT_DARK};
            color: {DarkTheme.TEXT_PRIMARY};
            border-top: 2px solid {DarkTheme.BORDER_ACCENT};
        }}
        
        QStatusBar::item {{
            border: none;
            padding: 4px 8px;
        }}
        """

def apply_dark_theme(app: QApplication):
    """Aplica el tema oscuro a toda la aplicación."""
    app.setStyleSheet(DarkTheme.get_stylesheet())
    
    # Configurar paleta oscura para elementos que no responden a CSS
    palette = QPalette()
    
    # Colores de ventana
    palette.setColor(QPalette.ColorRole.Window, QColor(DarkTheme.BACKGROUND_PRIMARY))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(DarkTheme.TEXT_PRIMARY))
    
    # Colores de base (campos de entrada)
    palette.setColor(QPalette.ColorRole.Base, QColor(DarkTheme.BACKGROUND_TERTIARY))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(DarkTheme.BACKGROUND_SECONDARY))
    
    # Colores de texto
    palette.setColor(QPalette.ColorRole.Text, QColor(DarkTheme.TEXT_PRIMARY))
    palette.setColor(QPalette.ColorRole.BrightText, QColor(DarkTheme.TEXT_PRIMARY))
    
    # Colores de botones
    palette.setColor(QPalette.ColorRole.Button, QColor(DarkTheme.BACKGROUND_TERTIARY))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(DarkTheme.TEXT_PRIMARY))
    
    # Colores de selección
    palette.setColor(QPalette.ColorRole.Highlight, QColor(DarkTheme.BACKGROUND_SELECTED))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(DarkTheme.TEXT_PRIMARY))
    
    # Colores deshabilitados
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, QColor(DarkTheme.TEXT_DISABLED))
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, QColor(DarkTheme.TEXT_DISABLED))
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, QColor(DarkTheme.TEXT_DISABLED))
    
    app.setPalette(palette)

class LightTheme:
    """Tema claro profesional para la aplicación."""
    
    # Colores principales
    BACKGROUND_PRIMARY = "#f5f5f5"      # Fondo principal claro
    BACKGROUND_SECONDARY = "#ffffff"    # Fondo secundario
    BACKGROUND_TERTIARY = "#efefef"     # Fondo de controles
    BACKGROUND_HOVER = "#e0e0e0"        # Hover sobre controles
    BACKGROUND_SELECTED = "#0078d4"     # Selección (azul Microsoft)
    
    # Texto
    TEXT_PRIMARY = "#212121"            # Texto principal negro
    TEXT_SECONDARY = "#505050"          # Texto secundario
    TEXT_DISABLED = "#a0a0a0"           # Texto deshabilitado
    TEXT_PLACEHOLDER = "#909090"        # Placeholder
    
    # Bordes y separadores
    BORDER_PRIMARY = "#d0d0d0"          # Bordes principales
    BORDER_SECONDARY = "#e0e0e0"        # Bordes secundarios
    BORDER_FOCUS = "#0078d4"           # Borde cuando tiene foco
    
    # Estados de botones
    BUTTON_PRIMARY = "#0078d4"          # Botón primario
    BUTTON_PRIMARY_HOVER = "#106ebe"    # Botón primario hover
    BUTTON_PRIMARY_PRESSED = "#005a9e"  # Botón primario presionado
    BUTTON_SECONDARY = "#f0f0f0"        # Botón secundario
    BUTTON_DANGER = "#d13438"           # Botón de eliminar
    BUTTON_SUCCESS = "#107c10"          # Botón de éxito
    
    # Estados especiales
    WARNING = "#ff8c00"                 # Advertencia
    ERROR = "#d13438"                   # Error
    SUCCESS = "#107c10"                 # Éxito
    INFO = "#0078d4"                    # Información

    @staticmethod
    def get_stylesheet():
        """Retorna el stylesheet completo para la aplicación."""
        return f"""
        /* ===== CONFIGURACIÓN GLOBAL ===== */
        QWidget {{
            background-color: {LightTheme.BACKGROUND_PRIMARY};
            color: {LightTheme.TEXT_PRIMARY};
            font-family: Segoe UI, Arial, sans-serif;
            font-size: 10pt;
        }}
        
        /* ===== VENTANAS PRINCIPALES ===== */
        QMainWindow, QDialog {{
            background-color: {LightTheme.BACKGROUND_PRIMARY};
            color: {LightTheme.TEXT_PRIMARY};
        }}
        
        /* ===== MENÚS ===== */
        QMenuBar {{
            background-color: {LightTheme.BACKGROUND_SECONDARY};
            color: {LightTheme.TEXT_PRIMARY};
            border-bottom: 1px solid {LightTheme.BORDER_PRIMARY};
        }}
        
        QMenuBar::item {{
            background-color: transparent;
            padding: 6px 12px;
        }}
        
        QMenuBar::item:selected {{
            background-color: {LightTheme.BACKGROUND_SELECTED};
            color: white;
        }}
        
        QMenu {{
            background-color: {LightTheme.BACKGROUND_SECONDARY};
            color: {LightTheme.TEXT_PRIMARY};
            border: 1px solid {LightTheme.BORDER_PRIMARY};
        }}
        
        QMenu::item {{
            padding: 6px 24px 6px 20px;
            background-color: transparent;
        }}
        
        QMenu::item:selected {{
            background-color: {LightTheme.BACKGROUND_SELECTED};
            color: white;
        }}
        
        QMenu::separator {{
            height: 1px;
            background-color: {LightTheme.BORDER_PRIMARY};
            margin: 4px 0;
        }}
        
        /* ===== BARRAS DE HERRAMIENTAS ===== */
        QToolBar {{
            background-color: {LightTheme.BACKGROUND_SECONDARY};
            border: none;
            padding: 2px;
            spacing: 2px;
        }}
        
        QToolButton {{
            background-color: transparent;
            border-radius: 3px;
            padding: 4px;
        }}
        
        QToolButton:hover {{
            background-color: {LightTheme.BACKGROUND_HOVER};
        }}
        
        QToolButton:pressed {{
            background-color: {LightTheme.BACKGROUND_TERTIARY};
        }}
        
        /* ===== LABELS ===== */
        QLabel {{
            color: {LightTheme.TEXT_PRIMARY};
            background-color: transparent;
        }}
        
        QLabel[styleClass="header"] {{
            font-size: 14pt;
            font-weight: bold;
        }}
        
        QLabel[styleClass="subheader"] {{
            font-size: 12pt;
            font-weight: bold;
        }}
        
        /* ===== BOTONES ===== */
        QPushButton {{
            background-color: {LightTheme.BUTTON_SECONDARY};
            color: {LightTheme.TEXT_PRIMARY};
            border: 1px solid {LightTheme.BORDER_SECONDARY};
            border-radius: 4px;
            padding: 8px 16px;
            min-width: 80px;
        }}
        
        QPushButton:hover {{
            background-color: {LightTheme.BACKGROUND_HOVER};
        }}
        
        QPushButton:pressed {{
            background-color: {LightTheme.BACKGROUND_TERTIARY};
        }}
        
        QPushButton:disabled {{
            color: {LightTheme.TEXT_DISABLED};
            background-color: {LightTheme.BACKGROUND_TERTIARY};
        }}
        
        QPushButton[styleClass="primary"] {{
            background-color: {LightTheme.BUTTON_PRIMARY};
            border: none;
            color: white;
        }}
        
        QPushButton[styleClass="primary"]:hover {{
            background-color: {LightTheme.BUTTON_PRIMARY_HOVER};
        }}
        
        QPushButton[styleClass="primary"]:pressed {{
            background-color: {LightTheme.BUTTON_PRIMARY_PRESSED};
        }}
        
        QPushButton[styleClass="danger"] {{
            background-color: {LightTheme.BUTTON_DANGER};
            border: none;
            color: white;
        }}
        
        QPushButton[styleClass="success"] {{
            background-color: {LightTheme.BUTTON_SUCCESS};
            border: none;
            color: white;
        }}
        
        /* ===== CAMPOS DE ENTRADA ===== */
        QLineEdit, QTextEdit {{
            background-color: white;
            border: 1px solid {LightTheme.BORDER_PRIMARY};
            border-radius: 4px;
            padding: 6px;
            color: #333333;
            selection-background-color: {LightTheme.BACKGROUND_SELECTED};
            selection-color: white;
        }}
        
        QLineEdit::placeholder {{
            color: #909090;
        }}
        
        QLineEdit:focus, QTextEdit:focus {{
            border: 2px solid {LightTheme.BORDER_FOCUS};
        }}
        
        QLineEdit:disabled, QTextEdit:disabled {{
            background-color: {LightTheme.BACKGROUND_TERTIARY};
            color: {LightTheme.TEXT_DISABLED};
        }}
        
        /* ===== COMBOBOX ===== */
        QComboBox {{
            background-color: white;
            border: 1px solid {LightTheme.BORDER_PRIMARY};
            border-radius: 4px;
            padding: 6px;
            color: #333333;
            min-width: 100px;
        }}
        
        QComboBox:focus {{
            border: 2px solid {LightTheme.BORDER_FOCUS};
        }}
        
        QComboBox::drop-down {{
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 20px;
            border-left: 1px solid {LightTheme.BORDER_PRIMARY};
        }}
        
        QComboBox QAbstractItemView {{
            background-color: {LightTheme.BACKGROUND_SECONDARY};
            border: 1px solid {LightTheme.BORDER_PRIMARY};
            color: {LightTheme.TEXT_PRIMARY};
            selection-background-color: {LightTheme.BACKGROUND_SELECTED};
            selection-color: white;
        }}
        
        /* ===== CHECKBOX ===== */
        QCheckBox {{
            color: {LightTheme.TEXT_PRIMARY};
            spacing: 8px;
        }}
        
        QCheckBox::indicator {{
            width: 18px;
            height: 18px;
            border: 1px solid {LightTheme.BORDER_PRIMARY};
            border-radius: 2px;
            background-color: {LightTheme.BACKGROUND_SECONDARY};
        }}
        
        QCheckBox::indicator:checked {{
            background-color: {LightTheme.BACKGROUND_SELECTED};
        }}
        
        QCheckBox::indicator:hover {{
            border: 1px solid {LightTheme.BORDER_FOCUS};
        }}
        
        /* ===== TABLAS ===== */
        QTableView, QTreeView, QListView {{
            background-color: {LightTheme.BACKGROUND_SECONDARY};
            alternate-background-color: {LightTheme.BACKGROUND_TERTIARY};
            color: {LightTheme.TEXT_PRIMARY};
            gridline-color: {LightTheme.BORDER_PRIMARY};
            selection-background-color: {LightTheme.BACKGROUND_SELECTED};
            selection-color: white;
            border: 1px solid {LightTheme.BORDER_PRIMARY};
        }}
        
        QHeaderView::section {{
            background-color: {LightTheme.BACKGROUND_TERTIARY};
            color: {LightTheme.TEXT_PRIMARY};
            padding: 6px;
            border: 1px solid {LightTheme.BORDER_PRIMARY};
            font-weight: bold;
        }}
        
        /* ===== SCROLLBAR ===== */
        QScrollBar:vertical {{
            border: none;
            background-color: {LightTheme.BACKGROUND_TERTIARY};
            width: 14px;
            margin: 15px 0 15px 0;
        }}
        
        QScrollBar::handle:vertical {{
            background-color: #c0c0c0;
            min-height: 30px;
            border-radius: 4px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background-color: #a0a0a0;
        }}
        
        QScrollBar:horizontal {{
            border: none;
            background-color: {LightTheme.BACKGROUND_TERTIARY};
            height: 14px;
            margin: 0 15px 0 15px;
        }}
        
        QScrollBar::handle:horizontal {{
            background-color: #c0c0c0;
            min-width: 30px;
            border-radius: 4px;
        }}
        
        QScrollBar::handle:horizontal:hover {{
            background-color: #a0a0a0;
        }}
        
        QScrollBar::add-line, QScrollBar::sub-line {{
            border: none;
            background: none;
        }}
        
        QScrollBar::up-arrow, QScrollBar::down-arrow,
        QScrollBar::add-page, QScrollBar::sub-page {{
            background: none;
        }}
        
        /* ===== FRAMES Y GRUPOS ===== */
        QFrame {{
            border: 1px solid {LightTheme.BORDER_PRIMARY};
            border-radius: 4px;
        }}
        
        QGroupBox {{
            margin-top: 12px;
            font-weight: bold;
            border: 1px solid {LightTheme.BORDER_PRIMARY};
            border-radius: 4px;
        }}
        
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
        }}
        
        /* ===== STATUSBAR ===== */
        QStatusBar {{
            background-color: {LightTheme.BACKGROUND_SECONDARY};
            color: {LightTheme.TEXT_PRIMARY};
        }}
        
        /* ===== TABS ===== */
        QTabWidget::pane {{
            border: 1px solid {LightTheme.BORDER_PRIMARY};
        }}
        
        QTabBar::tab {{
            background-color: {LightTheme.BACKGROUND_TERTIARY};
            color: {LightTheme.TEXT_PRIMARY};
            padding: 8px 12px;
            border: 1px solid {LightTheme.BORDER_PRIMARY};
            border-bottom: none;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
            margin-right: 2px;
        }}
        
        QTabBar::tab:selected {{
            background-color: {LightTheme.BACKGROUND_SECONDARY};
        }}
        
        /* ===== SPINBOX ===== */
        QSpinBox, QDoubleSpinBox {{
            background-color: white;
            border: 1px solid {LightTheme.BORDER_PRIMARY};
            border-radius: 4px;
            padding: 6px;
            color: #333333;
            min-width: 60px;
        }}
        
        QSpinBox:focus, QDoubleSpinBox:focus {{
            border: 2px solid {LightTheme.BORDER_FOCUS};
        }}
        
        QSpinBox::up-button, QSpinBox::down-button {{
            background-color: {LightTheme.BACKGROUND_TERTIARY};
            border: 1px solid {LightTheme.BORDER_PRIMARY};
            border-radius: 2px;
        }}
        
        QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
            background-color: {LightTheme.BACKGROUND_HOVER};
        }}
        
        /* ===== DATE/TIME EDIT ===== */
        QDateEdit, QTimeEdit, QDateTimeEdit {{
            background-color: white;
            border: 1px solid {LightTheme.BORDER_PRIMARY};
            border-radius: 4px;
            padding: 6px;
            color: #333333;
        }}
        
        QDateEdit:focus, QTimeEdit:focus, QDateTimeEdit:focus {{
            border: 2px solid {LightTheme.BORDER_FOCUS};
        }}
        
        /* ===== SLIDER ===== */
        QSlider::groove:horizontal {{
            height: 8px;
            background: {LightTheme.BACKGROUND_TERTIARY};
            border-radius: 4px;
        }}
        
        QSlider::handle:horizontal {{
            background: {LightTheme.BACKGROUND_SELECTED};
            border: none;
            width: 16px;
            margin: -4px 0;
            border-radius: 8px;
        }}
        
        QSlider::handle:horizontal:hover {{
            background: {LightTheme.BUTTON_PRIMARY_HOVER};
        }}
        
        /* ===== PROGRESS BAR ===== */
        QProgressBar {{
            border: 1px solid {LightTheme.BORDER_PRIMARY};
            border-radius: 4px;
            background-color: {LightTheme.BACKGROUND_TERTIARY};
            text-align: center;
            color: {LightTheme.TEXT_PRIMARY};
        }}
        
        QProgressBar::chunk {{
            background-color: {LightTheme.BACKGROUND_SELECTED};
            width: 20px;
        }}
        """

def apply_dark_palette(app):
    """Aplica la paleta de colores oscuros a la aplicación."""
    palette = QPalette()
    
    # Colores de ventana
    palette.setColor(QPalette.ColorRole.Window, QColor(DarkTheme.BACKGROUND_PRIMARY))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(DarkTheme.TEXT_PRIMARY))
    
    # Colores de base (campos de entrada)
    palette.setColor(QPalette.ColorRole.Base, QColor(DarkTheme.BACKGROUND_TERTIARY))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(DarkTheme.BACKGROUND_SECONDARY))
    
    # Colores de texto
    palette.setColor(QPalette.ColorRole.Text, QColor(DarkTheme.TEXT_PRIMARY))
    palette.setColor(QPalette.ColorRole.BrightText, QColor(DarkTheme.TEXT_PRIMARY))
    
    # Colores de botones
    palette.setColor(QPalette.ColorRole.Button, QColor(DarkTheme.BACKGROUND_TERTIARY))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(DarkTheme.TEXT_PRIMARY))
    
    # Colores de selección
    palette.setColor(QPalette.ColorRole.Highlight, QColor(DarkTheme.BACKGROUND_SELECTED))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(DarkTheme.TEXT_PRIMARY))
    
    # Colores deshabilitados
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, QColor(DarkTheme.TEXT_DISABLED))
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, QColor(DarkTheme.TEXT_DISABLED))
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, QColor(DarkTheme.TEXT_DISABLED))
    
    app.setPalette(palette)

def apply_light_palette(app):
    """Aplica la paleta de colores claros a la aplicación."""
    palette = QPalette()
    
    # Colores de ventana
    palette.setColor(QPalette.ColorRole.Window, QColor(LightTheme.BACKGROUND_PRIMARY))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(LightTheme.TEXT_PRIMARY))
    
    # Colores de base (campos de entrada)
    palette.setColor(QPalette.ColorRole.Base, QColor(LightTheme.BACKGROUND_SECONDARY))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(LightTheme.BACKGROUND_TERTIARY))
    
    # Colores de texto
    palette.setColor(QPalette.ColorRole.Text, QColor(LightTheme.TEXT_PRIMARY))
    palette.setColor(QPalette.ColorRole.BrightText, QColor(LightTheme.TEXT_PRIMARY))
    
    # Colores de botones
    palette.setColor(QPalette.ColorRole.Button, QColor(LightTheme.BUTTON_SECONDARY))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(LightTheme.TEXT_PRIMARY))
    
    # Colores de selección
    palette.setColor(QPalette.ColorRole.Highlight, QColor(LightTheme.BACKGROUND_SELECTED))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))
    
    # Colores deshabilitados
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, QColor(LightTheme.TEXT_DISABLED))
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, QColor(LightTheme.TEXT_DISABLED))
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, QColor(LightTheme.TEXT_DISABLED))
    
    app.setPalette(palette)

def set_widget_style_class(widget: QWidget, style_class: str) -> None:
    """Asigna una clase de estilo a un widget."""
    if not isinstance(style_class, str) or style_class not in ["dark", "light"]:
        style_class = "dark"  # Default to dark theme
    
    widget.setProperty("styleClass", style_class)
    widget.style().unpolish(widget)
    widget.style().polish(widget)
    
    # Aplicar estilo a la aplicación
    app = QApplication.instance()
    if app and isinstance(app, QApplication):
        if style_class == "dark":
            apply_dark_palette(app)
            app.setStyleSheet(DarkTheme.get_stylesheet())
        else:
            apply_light_palette(app)
            app.setStyleSheet(LightTheme.get_stylesheet())

def toggle_theme(widget: QWidget) -> str:
    """Cambia el tema del widget y retorna el nuevo tema."""
    current_theme = widget.property("styleClass") or "dark"
    new_theme = "light" if current_theme == "dark" else "dark"
    
    # Usar transición suave si está disponible
    try:
        # Crear gestor de transición
        from .theme_effects import ThemeTransitionManager
        transition = ThemeTransitionManager(duration=300)
        transition.prepare_transition(widget, new_theme)
        
        # Iniciar transición
        transition.start_transition()
        
    except ImportError:
        # Fallback: cambio instantáneo si no está disponible el efecto
        set_widget_style_class(widget, new_theme)
    
    # Guardar preferencia
    ThemeSettings.save_theme_preference(ThemeType.LIGHT if new_theme == "light" else ThemeType.DARK)
    
    # Mostrar mensaje de confirmación
    theme_name = "Claro" if new_theme == "light" else "Oscuro"
    QMessageBox.information(widget, "Tema Cambiado", f"Se ha cambiado al tema {theme_name}.")
    
    return new_theme

def detect_system_theme():
    """Detecta el tema del sistema operativo."""
    # Windows
    if platform.system() == "Windows":
        try:
            # Verificar si Windows está usando tema oscuro
            import winreg
            registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
            key = winreg.OpenKey(registry, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
            value, regtype = winreg.QueryValueEx(key, "AppsUseLightTheme")
            return ThemeType.LIGHT if value == 1 else ThemeType.DARK
        except Exception as e:
            print(f"Error detectando tema de Windows: {e}")
            return ThemeType.DARK  # Por defecto
    
    # macOS
    elif platform.system() == "Darwin":
        try:
            # En macOS podemos verificar la preferencia de apariencia
            import subprocess
            result = subprocess.run(
                ['defaults', 'read', '-g', 'AppleInterfaceStyle'], 
                capture_output=True, text=True
            )
            return ThemeType.DARK if result.stdout.strip() == "Dark" else ThemeType.LIGHT
        except Exception as e:
            print(f"Error detectando tema de macOS: {e}")
            return ThemeType.LIGHT  # macOS usa claro por defecto
    
    # Linux/otros
    else:
        # Para Linux sería necesario verificar según el entorno de escritorio
        # Por simplicidad, usamos un tema por defecto
        return ThemeType.DARK

def get_current_theme():
    """Obtiene el tema actual según la configuración guardada."""
    user_preference = ThemeSettings.load_theme_preference()
    
    # Si está configurado para seguir el tema del sistema, detectamos el tema actual
    if user_preference == ThemeType.SYSTEM:
        return detect_system_theme()
    
    return user_preference

def apply_theme_from_settings(widget: QWidget) -> None:
    """Aplica el tema según las configuraciones guardadas."""
    theme = get_current_theme()
    set_widget_style_class(widget, "light" if theme == ThemeType.LIGHT else "dark")