"""
Componente de visualización web integrada para previsualizar URLs de homologaciones.
"""

import sys
from typing import Optional, Dict, Any
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QLineEdit, QProgressBar, QMessageBox, QFrame, QSizePolicy
)
from PyQt6.QtCore import QUrl, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QIcon
import logging

logger = logging.getLogger(__name__)

try:
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    from PyQt6.QtWebEngineCore import QWebEngineSettings, QWebEnginePage
    WEB_ENGINE_AVAILABLE = True
except ImportError:
    WEB_ENGINE_AVAILABLE = False
    QWebEngineView = None


class WebPreviewWidget(QFrame):
    """Widget para previsualización de páginas web."""
    
    # Señales
    url_changed = pyqtSignal(str)  # Cuando cambia la URL
    loading_finished = pyqtSignal(bool)  # Cuando termina de cargar
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.current_url = ""
        self.setup_ui()
        
    def setup_ui(self):
        """Configura la interfaz del widget."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        # Barra de herramientas
        toolbar = self.create_toolbar()
        layout.addWidget(toolbar)
        
        # Contenedor web
        self.web_container = self.create_web_container()
        layout.addWidget(self.web_container)
        
        # Aplicar estilos
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
        toolbar.setFrameShape(QFrame.Shape.StyledPanel)
        toolbar.setStyleSheet("""
            QFrame {
                background-color: #f5f5f5;
                border-bottom: 1px solid #ddd;
                border-radius: 0;
                padding: 5px;
            }
        """)
        
        layout = QHBoxLayout(toolbar)
        layout.setContentsMargins(8, 5, 8, 5)
        
        # Botones de navegación
        self.back_btn = QPushButton("◀")
        self.back_btn.setToolTip("Atrás")
        self.back_btn.setFixedSize(30, 25)
        self.back_btn.setEnabled(False)
        
        self.forward_btn = QPushButton("▶")
        self.forward_btn.setToolTip("Adelante")  
        self.forward_btn.setFixedSize(30, 25)
        self.forward_btn.setEnabled(False)
        
        self.refresh_btn = QPushButton("🔄")
        self.refresh_btn.setToolTip("Recargar")
        self.refresh_btn.setFixedSize(30, 25)
        
        # Barra de URL
        self.url_edit = QLineEdit()
        self.url_edit.setPlaceholderText("Ingrese una URL para previsualizar...")
        self.url_edit.returnPressed.connect(self.load_url)
        
        # Botón ir
        self.go_btn = QPushButton("Ir")
        self.go_btn.clicked.connect(self.load_url)
        
        # Botón abrir en navegador externo
        self.external_btn = QPushButton("🌐")
        self.external_btn.setToolTip("Abrir en navegador externo")
        self.external_btn.setFixedSize(30, 25)
        self.external_btn.clicked.connect(self.open_external)
        
        # Agregar widgets al layout
        layout.addWidget(self.back_btn)
        layout.addWidget(self.forward_btn)
        layout.addWidget(self.refresh_btn)
        layout.addWidget(self.url_edit)
        layout.addWidget(self.go_btn)
        layout.addWidget(self.external_btn)
        
        return toolbar
        
    def create_web_container(self) -> QWidget:
        """Crea el contenedor para el componente web."""
        container = QFrame()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        
        if WEB_ENGINE_AVAILABLE and QWebEngineView:
            # Usar QWebEngineView si está disponible
            self.web_view = QWebEngineView()
            self.web_view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            
            # Configurar WebEngine
            settings = self.web_view.settings()
            settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
            settings.setAttribute(QWebEngineSettings.WebAttribute.PluginsEnabled, True)
            
            # Conectar señales
            self.web_view.loadStarted.connect(self.on_load_started)
            self.web_view.loadFinished.connect(self.on_load_finished)
            self.web_view.urlChanged.connect(self.on_url_changed)
            
            # Conectar botones de navegación
            self.back_btn.clicked.connect(self.web_view.back)
            self.forward_btn.clicked.connect(self.web_view.forward)
            self.refresh_btn.clicked.connect(self.web_view.reload)
            
            layout.addWidget(self.web_view)
            
            # Barra de progreso
            self.progress_bar = QProgressBar()
            self.progress_bar.setMaximum(100)
            self.progress_bar.setVisible(False)
            self.web_view.loadProgress.connect(self.progress_bar.setValue)
            layout.addWidget(self.progress_bar)
            
        else:
            # Fallback si WebEngine no está disponible
            self.create_fallback_view(layout)
            
        return container
        
    def create_fallback_view(self, layout: QVBoxLayout):
        """Crea una vista alternativa cuando WebEngine no está disponible."""
        fallback_widget = QFrame()
        fallback_layout = QVBoxLayout(fallback_widget)
        
        # Mensaje informativo
        info_label = QLabel("🌐 Visualización Web")
        info_font = QFont()
        info_font.setPointSize(14)
        info_font.setBold(True)
        info_label.setFont(info_font)
        info_label.setStyleSheet("color: #666; margin: 20px;")
        
        message_label = QLabel(
            "La visualización web integrada requiere PyQt6-WebEngine.\n\n"
            "Para instalar: pip install PyQt6-WebEngine\n\n"
            "Por ahora, puede usar el botón 🌐 para abrir URLs\n"
            "en su navegador web predeterminado."
        )
        message_label.setStyleSheet("color: #888; margin: 20px; line-height: 1.4;")
        message_label.setWordWrap(True)
        
        fallback_layout.addWidget(info_label)
        fallback_layout.addWidget(message_label)
        fallback_layout.addStretch()
        
        layout.addWidget(fallback_widget)
        
        # Desactivar botones de navegación
        self.back_btn.setEnabled(False)
        self.forward_btn.setEnabled(False) 
        self.refresh_btn.setEnabled(False)
        
        self.web_view = None
        self.progress_bar = None
        
    def load_url(self, url: str = ""):
        """Carga una URL en el visor web."""
        if not url:
            url = self.url_edit.text().strip()
            
        if not url:
            QMessageBox.warning(self, "URL Requerida", "Por favor ingrese una URL válida.")
            return
            
        # Agregar protocolo si no está presente
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            
        self.current_url = url
        self.url_edit.setText(url)
        
        if self.web_view:
            try:
                qurl = QUrl(url)
                self.web_view.setUrl(qurl)
                logger.info(f"Cargando URL: {url}")
            except Exception as e:
                logger.error(f"Error cargando URL {url}: {e}")
                QMessageBox.warning(self, "Error", f"No se pudo cargar la URL: {str(e)}")
        else:
            # Si no hay WebEngine, abrir en navegador externo
            self.open_external()
            
    def open_external(self):
        """Abre la URL actual en el navegador externo."""
        import webbrowser
        url = self.url_edit.text().strip()
        
        if not url:
            QMessageBox.warning(self, "URL Requerida", "No hay URL para abrir.")
            return
            
        try:
            webbrowser.open(url)
            logger.info(f"Abriendo URL externa: {url}")
        except Exception as e:
            logger.error(f"Error abriendo URL externa: {e}")
            QMessageBox.warning(self, "Error", f"No se pudo abrir la URL: {str(e)}")
            
    def on_load_started(self):
        """Maneja el inicio de carga de página."""
        if self.progress_bar:
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            
    def on_load_finished(self, success: bool):
        """Maneja la finalización de carga de página."""
        if self.progress_bar:
            self.progress_bar.setVisible(False)
            
        if self.web_view:
            # Actualizar estado de botones de navegación
            self.back_btn.setEnabled(self.web_view.history().canGoBack())
            self.forward_btn.setEnabled(self.web_view.history().canGoForward())
            
        self.loading_finished.emit(success)
        
        if not success:
            logger.warning(f"Error cargando página: {self.current_url}")
            
    def on_url_changed(self, qurl):
        """Maneja el cambio de URL."""
        url = qurl.toString()
        self.url_edit.setText(url)
        self.current_url = url
        self.url_changed.emit(url)
        
    def set_url(self, url: str):
        """Establece la URL a mostrar."""
        self.load_url(url)
        
    def get_current_url(self) -> str:
        """Obtiene la URL actual."""
        return self.current_url
        
    def clear(self):
        """Limpia el contenido del visor."""
        self.url_edit.clear()
        self.current_url = ""
        
        if self.web_view:
            self.web_view.setHtml("<html><body><h2>Seleccione una homologación para previsualizar</h2></body></html>")


class WebPreviewDialog(QWidget):
    """Diálogo independiente para previsualización web."""
    
    def __init__(self, url: str = "", parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setWindowTitle("🌐 Previsualización Web")
        self.setMinimumSize(900, 600)
        self.resize(1200, 800)
        
        # Layout principal
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Widget de previsualización
        self.preview_widget = WebPreviewWidget()
        layout.addWidget(self.preview_widget)
        
        # Cargar URL inicial si se proporciona
        if url:
            self.preview_widget.set_url(url)
            
    def set_url(self, url: str):
        """Establece la URL a previsualizar."""
        self.preview_widget.set_url(url)


def show_web_preview(url: str, parent: Optional[QWidget] = None) -> WebPreviewDialog:
    """Función de conveniencia para mostrar previsualización web."""
    dialog = WebPreviewDialog(url, parent)
    dialog.show()
    return dialog