"""
Componente simplificado de visualización web para previsualizar URLs.
"""

from __future__ import annotations

from typing import Any, Optional
import logging
import webbrowser

from PyQt6.QtCore import QUrl, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget)

logger = logging.getLogger(__name__)

# Verificar disponibilidad de WebEngine
try:
    from PyQt6.QtWebEngineWidgets import QWebEngineView  # type: ignore
    WEB_ENGINE_AVAILABLE = True
except ImportError:
    WEB_ENGINE_AVAILABLE = False
    QWebEngineView = None


class WebPreviewWidget(QFrame):
    """Widget simplificado para previsualización de páginas web."""
    
    # Señales
    url_changed = pyqtSignal(str)
    loading_finished = pyqtSignal(bool)
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.current_url = ""
        self.web_view: Any = None
        self.setup_ui()
        
    def setup_ui(self) -> None:
        """Configura la interfaz del widget."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Barra de herramientas
        toolbar = self.create_toolbar()
        layout.addWidget(toolbar)
        
        # Contenedor web
        web_container = self.create_web_container()
        layout.addWidget(web_container)
        
        self.setStyleSheet("""
            QFrame {
                border: 1px solid #ddd;
                border-radius: 6px;
                background-color: white;
            }
        """)
        
    def create_toolbar(self) -> QWidget:
        """Crea la barra de herramientas superior."""
        toolbar = QFrame()
        toolbar.setStyleSheet("""
            QFrame {
                background-color: #f5f5f5;
                border-bottom: 1px solid #ddd;
                padding: 5px;
            }
        """)
        
        layout = QHBoxLayout(toolbar)
        layout.setContentsMargins(8, 5, 8, 5)
        
        # Barra de URL
        self.url_edit = QLineEdit()
        self.url_edit.setPlaceholderText("Ingrese una URL para previsualizar...")
        self.url_edit.returnPressed.connect(self.load_url)
        
        # Botón ir
        go_btn = QPushButton("Ir")
        go_btn.clicked.connect(self.load_url)
        
        # Botón abrir en navegador externo
        external_btn = QPushButton("🌐")
        external_btn.setToolTip("Abrir en navegador externo")
        external_btn.setFixedSize(30, 25)
        external_btn.clicked.connect(self.open_external)
        
        layout.addWidget(self.url_edit)
        layout.addWidget(go_btn)
        layout.addWidget(external_btn)
        
        return toolbar
        
    def create_web_container(self) -> QWidget:
        """Crea el contenedor para el componente web."""
        container = QFrame()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(10, 10, 10, 10)
        
        if WEB_ENGINE_AVAILABLE and QWebEngineView:
            try:
                self.web_view = QWebEngineView()
                layout.addWidget(self.web_view)  # type: ignore[arg-type]
                
                # Conectar señales si están disponibles
                if hasattr(self.web_view, 'loadFinished'):  # type: ignore[arg-type]
                    self.web_view.loadFinished.connect(self.on_load_finished)
                if hasattr(self.web_view, 'urlChanged'):  # type: ignore[arg-type]
                    self.web_view.urlChanged.connect(self.on_url_changed)
                    
            except Exception as e:
                logger.warning(f"Error inicializando WebEngine: {e}")
                self.create_fallback_view(layout)
        else:
            self.create_fallback_view(layout)
            
        return container
        
    def create_fallback_view(self, layout: QVBoxLayout) -> None:
        """Crea una vista alternativa cuando WebEngine no está disponible."""
        info_label = QLabel("🌐 Visualización Web")
        info_font = QFont()
        info_font.setPointSize(14)
        info_font.setBold(True)
        info_label.setFont(info_font)
        info_label.setStyleSheet("color: #666; margin: 20px;")
        
        message_label = QLabel(
            "La visualización web integrada requiere PyQt6-WebEngine.\n\n"
            "Para instalar: pip install PyQt6-WebEngine\n\n"
            "Use el botón 🌐 para abrir URLs en su navegador predeterminado."
        )
        message_label.setStyleSheet("color: #888; margin: 20px;")
        message_label.setWordWrap(True)
        
        layout.addWidget(info_label)
        layout.addWidget(message_label)
        layout.addStretch()
        
        self.web_view = None
        
    def load_url(self) -> None:
        """Carga una URL en el visor."""
        url_text = self.url_edit.text().strip()
        if not url_text:
            return
            
        if not url_text.startswith(('http://', 'https://')):
            url_text = 'https://' + url_text
            
        self.current_url = url_text
        
        if self.web_view and hasattr(self.web_view, 'load'):
            try:
                self.web_view.load(QUrl(url_text))
                self.url_changed.emit(url_text)
            except Exception as e:
                logger.error(f"Error cargando URL: {e}")
                self.open_external()
        else:
            self.open_external()
            
    def open_external(self) -> None:
        """Abre la URL en el navegador externo."""
        url_text = self.url_edit.text().strip() or self.current_url
        if not url_text:
            QMessageBox.warning(self, "URL Vacía", "Por favor ingrese una URL.")
            return
            
        if not url_text.startswith(('http://', 'https://')):
            url_text = 'https://' + url_text
            
        try:
            webbrowser.open(url_text)
        except Exception as e:
            logger.error(f"Error abriendo navegador: {e}")
            QMessageBox.critical(self, "Error", f"No se pudo abrir el navegador: {e}")
            
    def set_url(self, url: str) -> None:
        """Establece la URL a mostrar."""
        self.url_edit.setText(url)
        self.load_url()
        
    def on_load_finished(self, success: bool) -> None:
        """Maneja el evento de carga finalizada."""
        self.loading_finished.emit(success)
        
    def on_url_changed(self, qurl: QUrl) -> None:
        """Maneja el cambio de URL."""
        url_str = qurl.toString()
        self.current_url = url_str
        self.url_edit.setText(url_str)
        self.url_changed.emit(url_str)


def create_web_preview(parent: Optional[QWidget] = None) -> WebPreviewWidget:
    """Función de conveniencia para crear un widget de previsualización web."""
    return WebPreviewWidget(parent)


def show_web_preview(url: str, parent: Optional[QWidget] = None) -> None:
    """
    Muestra una ventana de previsualización web para la URL especificada.
    
    Args:
        url: URL a mostrar
        parent: Widget padre opcional
    """
    try:
        # Crear widget de previsualización
        preview_widget = WebPreviewWidget(parent)
        preview_widget.setWindowTitle("Previsualización Web")
        preview_widget.resize(800, 600)
        
        # Establecer y cargar la URL
        preview_widget.set_url(url)
        
        # Mostrar la ventana
        preview_widget.show()
        
    except Exception as e:
        logger.error(f"Error al mostrar previsualización web: {e}")
        if parent:
            QMessageBox.warning(
                parent,
                "Error de Previsualización",
                f"No se pudo cargar la previsualización:\n{str(e)}"
            )


def is_web_engine_available() -> bool:
    """Verifica si WebEngine está disponible."""
    return WEB_ENGINE_AVAILABLE


__all__ = [
    'WebPreviewWidget',
    'create_web_preview',
    'show_web_preview',
    'is_web_engine_available'
]