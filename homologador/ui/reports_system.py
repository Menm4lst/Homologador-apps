"""
Sistema de reportes simplificado.

Este módulo ofrece un marcador de posición liviano para el sistema de
reportes avanzado original, evitando dependencias pesadas mientras
mantiene la interfaz pública requerida por el resto de la aplicación.
"""

from __future__ import annotations

from typing import Any, Dict, Mapping, Optional
import logging

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QVBoxLayout,
    QWidget,
)

logger = logging.getLogger(__name__)

PLACEHOLDER_MESSAGE = (
    "El sistema avanzado de reportes no está disponible en esta "
    "construcción.\n\n"
    "Funciones previstas:\n"
    " • Gráficos interactivos\n"
    " • Análisis de tendencias\n"
    " • Exportación automatizada\n"
    " • Programación de reportes"
)


class ReportsFeatureUnavailableError(RuntimeError):
    """Error lanzado cuando se solicita el sistema de reportes real."""

    def __init__(self, message: str = PLACEHOLDER_MESSAGE) -> None:
        super().__init__(message)


class ReportsManager:
    """Administrador liviano encargado de construir el diálogo placeholder."""

    def __init__(self, user_info: Mapping[str, Any]):
        self._user_info: Dict[str, Any] = dict(user_info)

    @property
    def user_info(self) -> Dict[str, Any]:
        """Retorna una copia defensiva de la información del usuario."""

        return dict(self._user_info)

    def create_dialog(self, parent: Optional[QWidget] = None) -> QDialog:
        """Construye el diálogo modal que informa la ausencia del sistema."""

        dialog = QDialog(parent)
        dialog.setWindowTitle("Sistema de reportes (en desarrollo)")
        dialog.setModal(True)

        layout = QVBoxLayout(dialog)

        header = QLabel("Sistema de reportes en desarrollo")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(header)

        message = QLabel(PLACEHOLDER_MESSAGE)
        message.setWordWrap(True)
        message.setAlignment(Qt.AlignmentFlag.AlignJustify)
        message.setStyleSheet("font-size: 13px; line-height: 1.4;")
        layout.addWidget(message)

        footer_text = f"Usuario: {self._user_info.get('username', 'desconocido')}"
        footer = QLabel(footer_text)
        footer.setAlignment(Qt.AlignmentFlag.AlignRight)
        footer.setStyleSheet("color: #7f8c8d; font-size: 11px;")
        layout.addWidget(footer)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)

        close_button = button_box.button(QDialogButtonBox.StandardButton.Close)
        if close_button is not None:
            close_button.setDefault(True)
            close_button.setFocus()

        return dialog


def create_reports_dialog(
    user_info: Mapping[str, Any], parent: Optional[QWidget] = None
) -> QDialog:
    """Devuelve el diálogo placeholder reutilizable."""

    manager = ReportsManager(user_info)
    return manager.create_dialog(parent)


def show_reports_system(
    user_info: Dict[str, Any], parent: Optional[QWidget] = None
) -> QDialog:
    """Carga el diálogo placeholder y lo devuelve para que el caller lo ejecute."""

    logger.info("Mostrando placeholder del sistema de reportes para %s", user_info.get("username", "usuario"))
    dialog = create_reports_dialog(user_info, parent)
    return dialog


def is_available() -> bool:
    """Indica si el sistema real está disponible (siempre falso en el placeholder)."""

    return False


__all__ = [
    "ReportsFeatureUnavailableError",
    "ReportsManager",
    "create_reports_dialog",
    "show_reports_system",
    "is_available",
]