"""
Sistema de iconos y recursos visuales para el Homologador de Aplicaciones.
Proporciona iconos SVG y imágenes para una interfaz moderna.
"""

import io

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QBrush, QColor, QIcon, QPainter, QPen, QPixmap
# from PyQt6.QtSvg import QSvgRenderer  # Comentado temporalmente
from PyQt6.QtWidgets import QApplication


class IconProvider:
    """Proveedor de iconos SVG para la aplicación."""
    
    # Cache de iconos para mejor rendimiento
    _icon_cache = {}
    
    @staticmethod
    def create_svg_icon(svg_content: str, size: QSize = QSize(16, 16)) -> QIcon:
        """Crea un icono desde contenido SVG."""
        cache_key = f"{hash(svg_content)}_{size.width()}x{size.height()}"
        
        if cache_key in IconProvider._icon_cache:
            return IconProvider._icon_cache[cache_key]
        
        # Por ahora retornar icono vacío - SVG deshabilitado temporalmente
        icon = QIcon()
        IconProvider._icon_cache[cache_key] = icon
        
        return icon
    
    @staticmethod
    def get_icon(name: str, size: QSize = QSize(16, 16)) -> QIcon:
        """Obtiene un icono por nombre."""
        svg_content = IconProvider._get_svg_content(name)
        if svg_content:
            return IconProvider.create_svg_icon(svg_content, size)
        return QIcon()  # Icono vacío si no se encuentra
    
    @staticmethod
    def _get_svg_content(name: str) -> str:
        """Obtiene el contenido SVG para un icono específico."""
        icons = {
            "add": """
                <svg viewBox="0 0 24 24" fill="none" stroke="#ffffff" stroke-width="2">
                    <line x1="12" y1="5" x2="12" y2="19"></line>
                    <line x1="5" y1="12" x2="19" y2="12"></line>
                </svg>
            """,
            "edit": """
                <svg viewBox="0 0 24 24" fill="none" stroke="#ffffff" stroke-width="2">
                    <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                    <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                </svg>
            """,
            "delete": """
                <svg viewBox="0 0 24 24" fill="none" stroke="#ffffff" stroke-width="2">
                    <polyline points="3,6 5,6 21,6"></polyline>
                    <path d="m19,6v14a2,2 0 0,1 -2,2H7a2,2 0 0,1 -2,-2V6m3,0V4a2,2 0 0,1 2,-2h4a2,2 0 0,1 2,2v2"></path>
                    <line x1="10" y1="11" x2="10" y2="17"></line>
                    <line x1="14" y1="11" x2="14" y2="17"></line>
                </svg>
            """,
            "view": """
                <svg viewBox="0 0 24 24" fill="none" stroke="#ffffff" stroke-width="2">
                    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                    <circle cx="12" cy="12" r="3"></circle>
                </svg>
            """,
            "search": """
                <svg viewBox="0 0 24 24" fill="none" stroke="#ffffff" stroke-width="2">
                    <circle cx="11" cy="11" r="8"></circle>
                    <path d="m21 21-4.35-4.35"></path>
                </svg>
            """,
            "filter": """
                <svg viewBox="0 0 24 24" fill="none" stroke="#ffffff" stroke-width="2">
                    <polygon points="22,3 2,3 10,12.46 10,19 14,21 14,12.46 22,3"></polygon>
                </svg>
            """,
            "export": """
                <svg viewBox="0 0 24 24" fill="none" stroke="#ffffff" stroke-width="2">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                    <polyline points="7,10 12,15 17,10"></polyline>
                    <line x1="12" y1="15" x2="12" y2="3"></line>
                </svg>
            """,
            "refresh": """
                <svg viewBox="0 0 24 24" fill="none" stroke="#ffffff" stroke-width="2">
                    <polyline points="23,4 23,10 17,10"></polyline>
                    <polyline points="1,20 1,14 7,14"></polyline>
                    <path d="M20.49 9A9 9 0 0 0 5.64 5.64L1 10m22 4l-4.64 4.36A9 9 0 0 1 3.51 15"></path>
                </svg>
            """,
            "settings": """
                <svg viewBox="0 0 24 24" fill="none" stroke="#ffffff" stroke-width="2">
                    <circle cx="12" cy="12" r="3"></circle>
                    <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1 1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
                </svg>
            """,
            "logout": """
                <svg viewBox="0 0 24 24" fill="none" stroke="#ffffff" stroke-width="2">
                    <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
                    <polyline points="16,17 21,12 16,7"></polyline>
                    <line x1="21" y1="12" x2="9" y2="12"></line>
                </svg>
            """,
            "save": """
                <svg viewBox="0 0 24 24" fill="none" stroke="#ffffff" stroke-width="2">
                    <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"></path>
                    <polyline points="17,21 17,13 7,13 7,21"></polyline>
                    <polyline points="7,3 7,8 15,8"></polyline>
                </svg>
            """,
            "cancel": """
                <svg viewBox="0 0 24 24" fill="none" stroke="#ffffff" stroke-width="2">
                    <line x1="18" y1="6" x2="6" y2="18"></line>
                    <line x1="6" y1="6" x2="18" y2="18"></line>
                </svg>
            """,
            "copy": """
                <svg viewBox="0 0 24 24" fill="none" stroke="#ffffff" stroke-width="2">
                    <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                    <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
                </svg>
            """,
            "info": """
                <svg viewBox="0 0 24 24" fill="none" stroke="#ffffff" stroke-width="2">
                    <circle cx="12" cy="12" r="10"></circle>
                    <line x1="12" y1="16" x2="12" y2="12"></line>
                    <line x1="12" y1="8" x2="12.01" y2="8"></line>
                </svg>
            """,
            "home": """
                <svg viewBox="0 0 24 24" fill="none" stroke="#ffffff" stroke-width="2">
                    <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
                    <polyline points="9,22 9,12 15,12 15,22"></polyline>
                </svg>
            """,
            "file": """
                <svg viewBox="0 0 24 24" fill="none" stroke="#ffffff" stroke-width="2">
                    <path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z"></path>
                </svg>
            """
        }
        
        return icons.get(name, "")

class AppIcons:
    """Iconos específicos de la aplicación con tamaños predefinidos."""
    
    # Tamaños estándar
    SMALL = QSize(16, 16)
    MEDIUM = QSize(24, 24)
    LARGE = QSize(32, 32)
    
    @staticmethod
    def get_toolbar_icon(name: str) -> QIcon:
        """Obtiene icono para barra de herramientas."""
        return IconProvider.get_icon(name, AppIcons.MEDIUM)
    
    @staticmethod
    def get_button_icon(name: str) -> QIcon:
        """Obtiene icono para botones."""
        return IconProvider.get_icon(name, AppIcons.SMALL)
    
    @staticmethod
    def get_large_icon(name: str) -> QIcon:
        """Obtiene icono grande."""
        return IconProvider.get_icon(name, AppIcons.LARGE)

def setup_application_icon(app: QApplication):
    """Configura el icono principal de la aplicación."""
    # Crear icono de aplicación personalizado
    app_icon_svg = """
    <svg viewBox="0 0 48 48" fill="none">
        <!-- Fondo -->
        <rect width="48" height="48" rx="8" fill="#0078d4"/>
        
        <!-- Símbolo principal -->
        <rect x="12" y="14" width="24" height="3" rx="1.5" fill="white"/>
        <rect x="12" y="20" width="18" height="3" rx="1.5" fill="white"/>
        <rect x="12" y="26" width="20" height="3" rx="1.5" fill="white"/>
        <rect x="12" y="32" width="16" height="3" rx="1.5" fill="white"/>
        
        <!-- Marca de verificación -->
        <path d="M33 19L36 22L42 16" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
    """
    
    app_icon = IconProvider.create_svg_icon(app_icon_svg, QSize(48, 48))
    app.setWindowIcon(app_icon)

class ThemeAwareIcons:
    """Iconos que se adaptan al tema actual."""
    
    @staticmethod
    def get_themed_icon(name: str, theme: str = "dark", size: QSize = QSize(16, 16)) -> QIcon:
        """Obtiene un icono adaptado al tema."""
        if theme == "dark":
            # Para tema oscuro, usar iconos blancos
            svg_content = IconProvider._get_svg_content(name)
            return IconProvider.create_svg_icon(svg_content, size)
        else:
            # Para tema claro, usar iconos oscuros
            svg_content = IconProvider._get_svg_content(name).replace('stroke="#ffffff"', 'stroke="#000000"')
            return IconProvider.create_svg_icon(svg_content, size)

# Utilidades adicionales
def create_colored_icon(name: str, color: str, size: QSize = QSize(16, 16)) -> QIcon:
    """Crea un icono con un color específico."""
    svg_content = IconProvider._get_svg_content(name).replace('#ffffff', color)
    return IconProvider.create_svg_icon(svg_content, size)

def apply_icons_to_application():
    """Aplica iconos a la aplicación automáticamente."""
    app = QApplication.instance()
    if app:
        setup_application_icon(app)