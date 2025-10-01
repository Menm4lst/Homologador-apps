"""
Sistema de búsqueda avanzada para la aplicación Homologador.

Este módulo proporciona funcionalidades avanzadas de búsqueda incluyendo:
- Búsqueda en tiempo real con autocompletado
- Sintaxis avanzada (AND, OR, NOT, comillas para frases exactas)
- Búsqueda por múltiples campos
- Resultados destacados
- Historial y sugerencias inteligentes
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set, Tuple, cast
import json

import re
from PyQt6.QtCore import (
    QDate,
    QEasingCurve,
    QPropertyAnimation,
    QRect,
    QSize,
    QStringListModel,
    Qt,
    QThread,
    QTimer,
    QRegularExpression,
    pyqtSignal,
)
from PyQt6.QtGui import (
    QColor,
    QFont,
    QIcon,
    QPainter,
    QPalette,
    QPixmap,
    QSyntaxHighlighter,
    QTextCharFormat,
    QTextCursor,
    QTextDocument)
from PyQt6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QCompleter,
    QDialog,
    QDateEdit,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QProgressBar,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QSlider,
    QSpinBox,
    QSplitter,
    QTabWidget,
    QTextEdit,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget)


class SearchSyntaxHighlighter(QSyntaxHighlighter):
    """Resaltador de sintaxis para la búsqueda avanzada."""
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(cast(QWidget, parent))
        self.highlighting_rules: List[Tuple[QRegularExpression, QTextCharFormat]] = []
        self.setup_highlighting_rules()
    
    def setup_highlighting_rules(self) -> None:
        """Configura las reglas de resaltado."""
        self.highlighting_rules.clear()
        
        # Operadores
        operator_format = QTextCharFormat()
        operator_format.setForeground(QColor("#FF6B6B"))
        operator_format.setFontWeight(QFont.Weight.Bold)
        operators = [r'\bAND\b', r'\bOR\b', r'\bNOT\b', r'\+', r'\-']
        for pattern in operators:
            self.highlighting_rules.append((QRegularExpression(pattern), operator_format))
        
        # Frases entre comillas
        quote_format = QTextCharFormat()
        quote_format.setForeground(QColor("#4ECDC4"))
        self.highlighting_rules.append((QRegularExpression(r'"[^"]*"'), quote_format))
        
        # Campos específicos (field:value)
        field_format = QTextCharFormat()
        field_format.setForeground(QColor("#45B7D1"))
        field_format.setFontWeight(QFont.Weight.Bold)
        self.highlighting_rules.append((QRegularExpression(r'\w+:'), field_format))
        
        # Comodines
        wildcard_format = QTextCharFormat()
        wildcard_format.setForeground(QColor("#96CEB4"))
        self.highlighting_rules.append((QRegularExpression(r'\*|\?'), wildcard_format))
    
    def highlightBlock(self, text: str) -> None:
        """Aplica el resaltado al bloque de texto."""
        for pattern, format_obj in self.highlighting_rules:
            expression = pattern
            iterator = expression.globalMatch(text)
            while iterator.hasNext():
                match = iterator.next()
                index = match.capturedStart()
                length = match.capturedLength()
                self.setFormat(cast(int, index), cast(int, length), cast(QTextCharFormat, format_obj))


class SearchEngine:
    """Motor de búsqueda avanzada."""
    
    def __init__(self):
        self.data: List[Dict[str, Any]] = []
        self.search_fields: List[str] = ['title', 'description', 'tags', 'repository', 'status']
        self.search_history: List[str] = []
        self.suggestions: Set[str] = set()
    
    def set_data(self, data: List[Dict[str, Any]]):
        """Establece los datos para la búsqueda."""
        self.data = data
        self._build_suggestions()
    
    def _build_suggestions(self):
        """Construye las sugerencias basadas en los datos."""
        self.suggestions.clear()
        for item in self.data:
            for field in self.search_fields:
                value = item.get(field, '')
                if isinstance(value, str) and value:
                    # Agregar palabras individuales
                    words = re.findall(r'\w+', value.lower())
                    self.suggestions.update(words)
                    
                    # Agregar frases cortas
                    if len(value) < 50:
                        self.suggestions.add(value.lower())
                elif isinstance(value, list):
                    # Para tags
                    self.suggestions.update(str(tag).lower() for tag in value if tag is not None and isinstance(tag, (str, int, float)))
    
    def get_suggestions(self, query: str) -> List[str]:
        """Obtiene sugerencias para autocompletado."""
        if len(query) < 2:
            return []
        
        query_lower = query.lower()
        matches = []
        
        # Buscar coincidencias exactas al inicio
        for suggestion in self.suggestions:
            if suggestion.startswith(query_lower):
                matches.append(cast(str, suggestion))
        
        # Buscar coincidencias parciales
        for suggestion in self.suggestions:
            if query_lower in suggestion and not suggestion.startswith(query_lower):
                matches.append(cast(str, suggestion))
        
        # Ordenar por relevancia (longitud y frecuencia)
        matches.sort(key=lambda x: (len(cast(str, x)), cast(str, x)))
        
        return matches[:10]
    
    def parse_query(self, query: str) -> Dict[str, Any]:
        """Parsea la consulta de búsqueda avanzada."""
        parsed = {
            'terms': [],
            'excluded_terms': [],
            'phrases': [],
            'field_searches': {},
            'operators': []
        }
        
        # Extraer frases entre comillas
        phrases = re.findall(r'"([^"]*)"', query)
        parsed['phrases'] = phrases
        query = re.sub(r'"[^"]*"', '', query)
        
        # Extraer búsquedas por campo (field:value)
        field_matches = re.findall(r'(\w+):(\S+)', query)
        for field, value in field_matches:
            if field.lower() in self.search_fields:
                parsed['field_searches'][field.lower()] = value
        query = re.sub(r'\w+:\S+', '', query)
        
        # Extraer términos excluidos (con -)
        excluded = re.findall(r'-(\w+)', query)
        parsed['excluded_terms'] = excluded
        query = re.sub(r'-\w+', '', query)
        
        # Extraer operadores
        operators = re.findall(r'\b(AND|OR|NOT)\b', query, re.IGNORECASE)
        parsed['operators'] = [op.upper() for op in operators]
        query = re.sub(r'\b(AND|OR|NOT)\b', '', query, flags=re.IGNORECASE)
        
        # Extraer términos restantes
        terms = re.findall(r'\w+', query)
        parsed['terms'] = [term.lower() for term in terms]
        
        return parsed
    
    def search(self, query: str, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Realiza la búsqueda."""
        if not query.strip():
            return self.data
        
        parsed_query = self.parse_query(query)
        results = []
        
        for item in self.data:
            if self._matches_item(item, parsed_query, filters):
                # Calcular puntuación de relevancia
                score = self._calculate_relevance_score(item, parsed_query)
                result = item.copy()
                result['_search_score'] = score
                result['_highlighted_fields'] = self._get_highlighted_fields(item, parsed_query)
                results.append(result)
        
        # Ordenar por relevancia
        results.sort(key=lambda x: x['_search_score'], reverse=True)
        
        # Agregar a historial
        self._add_to_history(query)
        
        return results
    
    def _matches_item(self, item: Dict[str, Any], parsed_query: Dict[str, Any], 
                     filters: Optional[Dict[str, Any]] = None) -> bool:
        """Verifica si un elemento coincide con la consulta."""
        # Aplicar filtros adicionales
        if filters:
            for field, value in filters.items():
                if field in item and item[field] != value:
                    return False
        
        # Verificar términos excluidos
        for term in parsed_query['excluded_terms']:
            if self._term_in_item(item, term):
                return False
        
        # Verificar frases exactas
        for phrase in parsed_query['phrases']:
            if not self._phrase_in_item(item, phrase):
                return False
        
        # Verificar búsquedas por campo
        for field, value in parsed_query['field_searches'].items():
            if not self._field_search_matches(item, field, value):
                return False
        
        # Verificar términos con operadores
        if parsed_query['terms']:
            if 'OR' in parsed_query['operators']:
                # Al menos un término debe coincidir
                return any(self._term_in_item(item, term) for term in parsed_query['terms'])
            else:
                # Todos los términos deben coincidir (AND implícito)
                return all(self._term_in_item(item, term) for term in parsed_query['terms'])
        
        return True
    
    def _term_in_item(self, item: Dict[str, Any], term: str) -> bool:
        """Verifica si un término está presente en el elemento."""
        term_lower = term.lower()
        for field in self.search_fields:
            value = item.get(field, '')
            if isinstance(value, str):
                if term_lower in value.lower():
                    return True
            elif isinstance(value, list):
                if any(term_lower in str(v).lower() for v in value if v is not None and isinstance(v, (str, int, float))):
                    return True
        return False
    
    def _phrase_in_item(self, item: Dict[str, Any], phrase: str) -> bool:
        """Verifica si una frase exacta está presente en el elemento."""
        phrase_lower = phrase.lower()
        for field in self.search_fields:
            value = item.get(field, '')
            if isinstance(value, str) and phrase_lower in value.lower():
                return True
        return False
    
    def _field_search_matches(self, item: Dict[str, Any], field: str, value: str) -> bool:
        """Verifica si la búsqueda por campo coincide."""
        item_value = item.get(field, '')
        if isinstance(item_value, str):
            # Soporte para comodines
            if '*' in value or '?' in value:
                pattern = value.replace('*', '.*').replace('?', '.')
                return bool(re.search(pattern, item_value, re.IGNORECASE))
            else:
                return value.lower() in item_value.lower()
        elif isinstance(item_value, list):
            return any(value.lower() in str(v).lower() for v in item_value if v is not None and isinstance(v, (str, int, float)))
        return False
    
    def _calculate_relevance_score(self, item: Dict[str, Any], parsed_query: Dict[str, Any]) -> float:
        """Calcula la puntuación de relevancia."""
        score = 0.0
        
        # Puntuación por términos encontrados
        for term in parsed_query['terms']:
            for field in self.search_fields:
                value = item.get(field, '')
                if isinstance(value, str):
                    # Más puntos si está en el título
                    multiplier = 3.0 if field == 'title' else 1.0
                    # Más puntos por coincidencias exactas
                    if term.lower() == value.lower():
                        score += 10.0 * multiplier
                    elif value.lower().startswith(term.lower()):
                        score += 5.0 * multiplier
                    elif term.lower() in value.lower():
                        score += 2.0 * multiplier
        
        # Puntuación por frases exactas
        for phrase in parsed_query['phrases']:
            for field in self.search_fields:
                value = item.get(field, '')
                if isinstance(value, str) and phrase.lower() in value.lower():
                    multiplier = 3.0 if field == 'title' else 1.0
                    score += 15.0 * multiplier
        
        # Puntuación por búsquedas de campo específico
        for field, value in parsed_query['field_searches'].items():
            if self._field_search_matches(item, field, value):
                score += 20.0
        
        return score
    
    def _get_highlighted_fields(self, item: Dict[str, Any], parsed_query: Dict[str, Any]) -> Dict[str, str]:
        """Obtiene los campos con términos resaltados."""
        highlighted = {}
        
        all_terms = parsed_query['terms'] + parsed_query['phrases']
        
        for field in self.search_fields:
            value = item.get(field, '')
            if isinstance(value, str) and value:
                highlighted_value = value
                
                # Resaltar términos
                for term in all_terms:
                    if term.lower() in value.lower():
                        pattern = re.compile(re.escape(term), re.IGNORECASE)
                        highlighted_value = pattern.sub(
                            f'<mark>{term}</mark>', 
                            highlighted_value
                        )
                
                if highlighted_value != value:
                    highlighted[field] = highlighted_value
        
        return highlighted
    
    def _add_to_history(self, query: str):
        """Agrega la consulta al historial."""
        if query not in self.search_history:
            self.search_history.insert(0, query)
            # Mantener solo los últimos 20
            self.search_history = self.search_history[:20]
    
    def get_search_history(self) -> List[str]:
        """Obtiene el historial de búsquedas."""
        return self.search_history.copy()


class SearchResultWidget(QWidget):
    """Widget para mostrar un resultado de búsqueda."""
    
    clicked = pyqtSignal(dict)
    
    def __init__(self, result_data: Dict[str, Any], parent: Optional[QWidget] = None):
        super().__init__(cast(QWidget, parent))
        self.result_data = result_data
        self.setup_ui()
    
    def setup_ui(self):
        """Configura la interfaz del widget."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(4)
        
        # Contenedor principal
        main_frame = QFrame()
        main_frame.setFrameStyle(QFrame.Shape.Box)
        main_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #e9ecef;
                border-radius: 8px;
                padding: 8px;
            }
            QFrame:hover {
                background-color: #e8f4ff;
                border-color: #45B7D1;
            }
        """)
        layout.addWidget(main_frame)
        
        frame_layout = QVBoxLayout(main_frame)
        frame_layout.setSpacing(6)
        
        # Header con título y puntuación
        header_layout = QHBoxLayout()
        
        # Título
        title_label = QLabel(self.result_data.get('title', 'Sin título'))
        title_font = QFont()
        title_font.setPointSize(11)
        title_font.setWeight(QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #2c3e50;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Puntuación de relevancia
        score = self.result_data.get('_search_score', 0)
        if score > 0:
            score_label = QLabel(f"Relevancia: {score:.1f}")
            score_label.setStyleSheet("color: #7f8c8d; font-size: 10px;")
            header_layout.addWidget(score_label)
        
        frame_layout.addLayout(header_layout)
        
        # Información básica
        info_layout = QHBoxLayout()
        
        # Estado
        status = self.result_data.get('status', 'Desconocido')
        status_label = QLabel(f"Estado: {status}")
        status_label.setStyleSheet(f"""
            background-color: {'#d4edda' if status == 'Completado' else '#fff3cd'};
            color: {'#155724' if status == 'Completado' else '#856404'};
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 10px;
        """)
        info_layout.addWidget(status_label)
        
        # Repositorio
        repository = self.result_data.get('repository', 'N/A')
        repo_label = QLabel(f"📁 {repository}")
        repo_label.setStyleSheet("color: #6c757d; font-size: 10px;")
        info_layout.addWidget(repo_label)
        
        info_layout.addStretch()
        
        frame_layout.addLayout(info_layout)
        
        # Descripción resaltada
        highlighted_fields = self.result_data.get('_highlighted_fields', {})
        
        if 'description' in highlighted_fields:
            desc_label = QLabel(highlighted_fields['description'])
            desc_label.setWordWrap(True)
            desc_label.setTextFormat(Qt.TextFormat.RichText)
        else:
            description = self.result_data.get('description', '')
            if len(description) > 150:
                description = description[:150] + '...'
            desc_label = QLabel(description)
            desc_label.setWordWrap(True)
        
        desc_label.setStyleSheet("color: #495057; font-size: 10px; margin-top: 4px;")
        frame_layout.addWidget(desc_label)
        
        # Tags resaltados
        tags = self.result_data.get('tags', [])
        if tags:
            tags_layout = QHBoxLayout()
            tags_layout.setSpacing(4)
            
            for tag in tags[:5]:  # Mostrar máximo 5 tags
                tag_label = QLabel(f"#{tag}")
                tag_label.setStyleSheet("""
                    background-color: #e7f3ff;
                    color: #0366d6;
                    padding: 2px 6px;
                    border-radius: 12px;
                    font-size: 9px;
                """)
                tags_layout.addWidget(tag_label)
            
            if len(tags) > 5:
                more_label = QLabel(f"+{len(tags) - 5} más")
                more_label.setStyleSheet("color: #6c757d; font-size: 9px;")
                tags_layout.addWidget(more_label)
            
            tags_layout.addStretch()
            frame_layout.addLayout(tags_layout)
        
        # Hacer clickeable
        main_frame.mousePressEvent = self.on_click
    
    def on_click(self, a0):
        """Maneja el click en el resultado."""
        self.clicked.emit(self.result_data)


class AdvancedSearchWidget(QWidget):
    """Widget principal para búsqueda avanzada."""
    
    search_requested = pyqtSignal(str, dict)
    result_selected = pyqtSignal(dict)
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(cast(QWidget, parent))
        self.search_engine = SearchEngine()
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.perform_search)
        
        self.setup_ui()
        self.setup_connections()
    
    def setup_ui(self):
        """Configura la interfaz."""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        
        # Header con título
        header_layout = QHBoxLayout()
        
        title_label = QLabel("🔍 Búsqueda Avanzada")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setWeight(QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #2c3e50; margin-bottom: 5px;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Botón de ayuda
        help_button = QPushButton("❓ Ayuda de Sintaxis")
        help_button.setStyleSheet("""
            QPushButton {
                background-color: #e3f2fd;
                border: 1px solid #90caf9;
                border-radius: 6px;
                padding: 4px 8px;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #bbdefb;
            }
        """)
        help_button.clicked.connect(self.show_syntax_help)
        header_layout.addWidget(help_button)
        
        main_layout.addLayout(header_layout)
        
        # Área de búsqueda
        search_frame = QFrame()
        search_frame.setFrameStyle(QFrame.Shape.Box)
        search_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 2px solid #e9ecef;
                border-radius: 10px;
                padding: 8px;
            }
        """)
        main_layout.addWidget(search_frame)
        
        search_layout = QVBoxLayout(search_frame)
        
        # Campo de búsqueda principal
        search_input_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(
            "Buscar... (ej: python AND django OR \"API REST\" -deprecated repository:proyecto1)"
        )
        self.search_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #ced4da;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 12px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #45B7D1;
                outline: none;
            }
        """)
        
        # Configurar resaltador de sintaxis
        # Nota: QLineEdit no soporta syntax highlighting como QTextEdit
        # self.syntax_highlighter = SearchSyntaxHighlighter(self.search_input.document())
        
        search_input_layout.addWidget(self.search_input)
        
        # Botón de búsqueda
        search_button = QPushButton("🔍")
        search_button.setFixedSize(40, 40)
        search_button.setStyleSheet("""
            QPushButton {
                background-color: #45B7D1;
                border: none;
                border-radius: 20px;
                color: white;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3498db;
            }
            QPushButton:pressed {
                background-color: #2980b9;
            }
        """)
        search_button.clicked.connect(self.perform_search)
        search_input_layout.addWidget(search_button)
        
        search_layout.addLayout(search_input_layout)
        
        # Autocompletado y historial
        self.setup_autocomplete()
        
        # Filtros rápidos
        filters_layout = QHBoxLayout()
        
        # Filtro por estado
        self.status_filter = QComboBox()
        self.status_filter.addItems(['Todos los estados', 'Pendiente', 'En Progreso', 'Completado', 'Cancelado'])
        self.status_filter.setStyleSheet("""
            QComboBox {
                border: 1px solid #ced4da;
                border-radius: 4px;
                padding: 4px 8px;
                background-color: white;
                min-width: 120px;
            }
        """)
        filters_layout.addWidget(QLabel("Estado:"))
        filters_layout.addWidget(self.status_filter)
        
        # Filtro por repositorio
        self.repo_filter = QComboBox()
        self.repo_filter.addItem('Todos los repositorios')
        self.repo_filter.setStyleSheet("""
            QComboBox {
                border: 1px solid #ced4da;
                border-radius: 4px;
                padding: 4px 8px;
                background-color: white;
                min-width: 120px;
            }
        """)
        filters_layout.addWidget(QLabel("Repositorio:"))
        filters_layout.addWidget(self.repo_filter)
        
        filters_layout.addStretch()
        
        # Limpiar filtros
        clear_button = QPushButton("🗑️ Limpiar")
        clear_button.setStyleSheet("""
            QPushButton {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #e9ecef;
            }
        """)
        clear_button.clicked.connect(self.clear_search)
        filters_layout.addWidget(clear_button)
        
        search_layout.addLayout(filters_layout)
        
        # Área de resultados
        results_splitter = QSplitter(Qt.Orientation.Vertical)
        main_layout.addWidget(results_splitter, 1)
        
        # Información de resultados
        self.results_info = QLabel("Ingresa una búsqueda para ver resultados")
        self.results_info.setStyleSheet("color: #6c757d; font-style: italic; padding: 8px;")
        results_splitter.addWidget(self.results_info)
        
        # Lista de resultados
        self.results_scroll = QScrollArea()
        self.results_scroll.setWidgetResizable(True)
        self.results_scroll.setStyleSheet("""
            QScrollArea {
                border: 1px solid #e9ecef;
                border-radius: 8px;
                background-color: white;
            }
        """)
        
        self.results_widget = QWidget()
        self.results_layout = QVBoxLayout(self.results_widget)
        self.results_layout.setSpacing(8)
        self.results_layout.addStretch()
        
        self.results_scroll.setWidget(self.results_widget)
        results_splitter.addWidget(self.results_scroll)
        
        # Configurar proporciones del splitter
        results_splitter.setSizes([50, 400])
    
    def setup_autocomplete(self):
        """Configura el autocompletado."""
        self.completer = QCompleter()
        self.completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self.search_input.setCompleter(self.completer)
    
    def setup_connections(self):
        """Configura las conexiones de señales."""
        self.search_input.textChanged.connect(self.on_search_text_changed)
        self.search_input.returnPressed.connect(self.perform_search)
        self.status_filter.currentTextChanged.connect(self.on_filter_changed)
        self.repo_filter.currentTextChanged.connect(self.on_filter_changed)
    
    def set_data(self, data: List[Dict[str, Any]]):
        """Establece los datos para la búsqueda."""
        self.search_engine.set_data(data)
        
        # Actualizar filtros de repositorio
        repositories = set()
        for item in data:
            repo = item.get('repository', '')
            if repo:
                repositories.add(repo)
        
        self.repo_filter.clear()
        self.repo_filter.addItem('Todos los repositorios')
        self.repo_filter.addItems(sorted(cast(Set[str], repositories)))
        
        # Actualizar autocompletado
        suggestions = self.search_engine.get_suggestions('')
        if suggestions:
            model = QStringListModel(suggestions)
            self.completer.setModel(model)
    
    def on_search_text_changed(self, text: str):
        """Maneja el cambio en el texto de búsqueda."""
        # Búsqueda en tiempo real con delay
        self.search_timer.stop()
        if text.strip():
            self.search_timer.start(300)  # 300ms delay
    
    def on_filter_changed(self):
        """Maneja el cambio en los filtros."""
        if self.search_input.text().strip():
            self.perform_search()
    
    def perform_search(self):
        """Realiza la búsqueda."""
        query = self.search_input.text().strip()
        
        # Preparar filtros
        filters = {}
        
        status = self.status_filter.currentText()
        if status != 'Todos los estados':
            filters['status'] = status
        
        repo = self.repo_filter.currentText()
        if repo != 'Todos los repositorios':
            filters['repository'] = repo
        
        # Realizar búsqueda
        if query:
            results = self.search_engine.search(query, cast(Dict[str, Any], filters))
        else:
            results = self.search_engine.data if not filters else [
                item for item in self.search_engine.data
                if all(item.get(str(k)) == v for k, v in cast(Dict[str, Any], filters).items() if k is not None)
            ]
        
        self.display_results(results, query)
        self.search_requested.emit(query, filters)
    
    def display_results(self, results: List[Dict[str, Any]], query: str = ""):
        """Muestra los resultados de la búsqueda."""
        # Limpiar resultados anteriores
        for i in reversed(range(self.results_layout.count())):
            item = self.results_layout.itemAt(i)
            if item and item.widget():
                widget = item.widget()
                if widget:
                    widget.deleteLater()
        
        # Actualizar información de resultados
        if query:
            if results:
                self.results_info.setText(
                    f"Se encontraron {len(results)} resultado(s) para '{query}'"
                )
            else:
                self.results_info.setText(f"No se encontraron resultados para '{query}'")
        else:
            self.results_info.setText(f"Mostrando {len(results)} elemento(s)")
        
        # Mostrar resultados
        if results:
            for result in results:
                result_widget = SearchResultWidget(result)
                result_widget.clicked.connect(self.result_selected.emit)
                self.results_layout.insertWidget(
                    self.results_layout.count() - 1, result_widget
                )
        else:
            # Mensaje de sin resultados
            no_results = QLabel("🔍 No se encontraron resultados")
            no_results.setAlignment(Qt.AlignmentFlag.AlignCenter)
            no_results.setStyleSheet("""
                color: #6c757d;
                font-size: 14px;
                font-style: italic;
                padding: 40px;
            """)
            self.results_layout.insertWidget(
                self.results_layout.count() - 1, no_results
            )
    
    def clear_search(self):
        """Limpia la búsqueda y filtros."""
        self.search_input.clear()
        self.status_filter.setCurrentIndex(0)
        self.repo_filter.setCurrentIndex(0)
        
        # Mostrar todos los datos
        if hasattr(self.search_engine, 'data'):
            self.display_results(self.search_engine.data)
    
    def show_syntax_help(self):
        """Muestra la ayuda de sintaxis."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Ayuda de Sintaxis de Búsqueda")
        dialog.setModal(True)
        dialog.resize(500, 400)
        
        layout = QVBoxLayout(dialog)
        
        help_text = QTextEdit()
        help_text.setReadOnly(True)
        help_text.setHtml("""
        <h3>🔍 Sintaxis de Búsqueda Avanzada</h3>
        
        <h4>Operadores Básicos:</h4>
        <ul>
            <li><code>palabra</code> - Busca la palabra en todos los campos</li>
            <li><code>"frase exacta"</code> - Busca la frase exacta</li>
            <li><code>palabra1 AND palabra2</code> - Ambas palabras deben estar presentes</li>
            <li><code>palabra1 OR palabra2</code> - Al menos una palabra debe estar presente</li>
            <li><code>-palabra</code> - Excluye resultados que contengan esta palabra</li>
        </ul>
        
        <h4>Búsqueda por Campo:</h4>
        <ul>
            <li><code>title:python</code> - Busca "python" solo en el título</li>
            <li><code>repository:proyecto1</code> - Busca en el repositorio específico</li>
            <li><code>status:completado</code> - Busca por estado específico</li>
            <li><code>tags:api</code> - Busca en las etiquetas</li>
        </ul>
        
        <h4>Comodines:</h4>
        <ul>
            <li><code>*</code> - Coincide con cualquier secuencia de caracteres</li>
            <li><code>?</code> - Coincide con un solo carácter</li>
        </ul>
        
        <h4>Ejemplos:</h4>
        <ul>
            <li><code>python AND django</code> - Busca elementos que contengan tanto "python" como "django"</li>
            <li><code>"API REST" OR "GraphQL"</code> - Busca elementos con cualquiera de estas frases</li>
            <li><code>repository:web* -deprecated</code> - Busca en repositorios que empiecen con "web", excluyendo los marcados como "deprecated"</li>
            <li><code>title:auth* status:pendiente</code> - Busca títulos que empiecen con "auth" y estén pendientes</li>
        </ul>
        """)
        
        layout.addWidget(help_text)
        
        close_button = QPushButton("Cerrar")
        close_button.clicked.connect(dialog.accept)
        layout.addWidget(close_button)
        
        dialog.exec()


if __name__ == "__main__":

    
    import sys

    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    
    # Datos de prueba
    test_data = [
        {
            'title': 'Implementar API REST para usuarios',
            'description': 'Crear endpoints para gestión de usuarios con autenticación JWT',
            'repository': 'web-backend',
            'status': 'En Progreso',
            'tags': ['api', 'usuarios', 'jwt', 'backend']
        },
        {
            'title': 'Diseño responsive para dashboard',
            'description': 'Adaptar el dashboard principal para dispositivos móviles',
            'repository': 'web-frontend',
            'status': 'Pendiente',
            'tags': ['frontend', 'responsive', 'css', 'dashboard']
        },
        {
            'title': 'Migración a Python 3.11',
            'description': 'Actualizar todo el código base para usar Python 3.11 y sus nuevas características',
            'repository': 'core-system',
            'status': 'Completado',
            'tags': ['python', 'migración', 'upgrade']
        }
    ]
    
    window = AdvancedSearchWidget()
    window.set_data(cast(List[Dict[str, Any]], test_data))
    window.show()
    
    sys.exit(app.exec())