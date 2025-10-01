"""
Sistema de respaldos simplificado.

Este módulo actúa como un marcador de posición liviano para el sistema
avanzado de respaldos. Mantiene la interfaz pública utilizada por el
resto de la aplicación sin depender de operaciones pesadas ni bibliotecas
externas.
"""


from __future__ import annotations

from typing import Any, Dict, Mapping, Optional
import logging

from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

logger = logging.getLogger(__name__)

PLACEHOLDER_DESCRIPTION = (
    "El sistema completo de respaldos se encuentra en desarrollo.\n\n"
    "Las funciones previstas incluyen:\n"
    " • Respaldos programados y manuales\n"
    " • Compresión y cifrado\n"
    " • Restauración guiada\n"
    " • Monitoreo de tareas"
)


class BackupFeatureUnavailableError(RuntimeError):
    """Señala que la característica avanzada no está disponible."""

    def __init__(self, message: str = PLACEHOLDER_DESCRIPTION) -> None:
        super().__init__(message)


class BackupWorker(QThread):
    """Worker placeholder que simula la creación de un respaldo."""

    progress_updated = pyqtSignal(int)
    status_updated = pyqtSignal(str)
    finished = pyqtSignal(bool, str)

    def __init__(self, config: Mapping[str, Any]):
        super().__init__()
        self._config: Dict[str, Any] = dict(config)

    @property
    def config(self) -> Dict[str, Any]:
        return dict(self._config)

    def run(self) -> None:  # pragma: no cover - flujo trivial
        logger.info("Simulando respaldo con configuración: %s", self._config)
        self.status_updated.emit("Sistema de respaldos en desarrollo")
        self.progress_updated.emit(100)
        self.finished.emit(False, "Funcionalidad de respaldo en desarrollo")


class RestoreWorker(QThread):
    """Worker placeholder para restauraciones."""

    progress_updated = pyqtSignal(int)
    status_updated = pyqtSignal(str)
    finished = pyqtSignal(bool, str)

    def __init__(self, backup_path: str, config: Optional[Mapping[str, Any]] = None):
        super().__init__()
        self.backup_path = backup_path
        self._config: Dict[str, Any] = dict(config or {})

    @property
    def config(self) -> Dict[str, Any]:
        return dict(self._config)

    def run(self) -> None:  # pragma: no cover - flujo trivial
        logger.info("Simulando restauración desde %s", self.backup_path)
        self.status_updated.emit("Sistema de restauración en desarrollo")
        self.progress_updated.emit(100)
        self.finished.emit(False, "Funcionalidad de restauración en desarrollo")


class BackupSystemWidget(QWidget):
    """Widget mínimo que informa el estado de la característica."""

    def __init__(self, user_info: Mapping[str, Any], parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._user_info: Dict[str, Any] = dict(user_info)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        header = QLabel("Sistema de respaldos en desarrollo", self)
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(header)

        description = QLabel(PLACEHOLDER_DESCRIPTION, self)
        description.setWordWrap(True)
        description.setAlignment(Qt.AlignmentFlag.AlignJustify)
        layout.addWidget(description)

        user_label = QLabel(
            f"Usuario activo: {self._user_info.get('username', 'desconocido')}",
            self,
        )
        user_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        user_label.setStyleSheet("color: #7f8c8d; font-size: 11px;")
        layout.addWidget(user_label)

        simulate_button = QPushButton("Simular respaldo", self)
        simulate_button.clicked.connect(self._simulate_backup)
        layout.addWidget(simulate_button)

        simulate_restore_button = QPushButton("Simular restauración", self)
        simulate_restore_button.clicked.connect(self._simulate_restore)
        layout.addWidget(simulate_restore_button)

        layout.addStretch()

    def _simulate_backup(self) -> None:
        logger.info("Solicitud de respaldo recibida (placeholder)")
        raise BackupFeatureUnavailableError()

    def _simulate_restore(self) -> None:
        logger.info("Solicitud de restauración recibida (placeholder)")
        raise BackupFeatureUnavailableError()


def create_backup_dialog(
    user_info: Mapping[str, Any], parent: Optional[QWidget] = None
) -> QDialog:
    """Construye un diálogo modal con el widget placeholder."""

    dialog = QDialog(parent)
    dialog.setWindowTitle("Sistema de respaldos (en desarrollo)")
    dialog.setModal(True)

    layout = QVBoxLayout(dialog)
    widget = BackupSystemWidget(user_info, dialog)
    layout.addWidget(widget)

    buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
    buttons.rejected.connect(dialog.reject)
    layout.addWidget(buttons)

    close_button = buttons.button(QDialogButtonBox.StandardButton.Close)
    if close_button is not None:
        close_button.setDefault(True)
        close_button.setFocus()

    return dialog


def show_backup_system(
    user_info: Dict[str, Any], parent: Optional[QWidget] = None
) -> QDialog:
    """Devuelve el diálogo placeholder para que el caller lo muestre."""

    logger.info("Mostrando placeholder de respaldos para %s", user_info.get("username", "usuario"))
    return create_backup_dialog(user_info, parent)


def is_available() -> bool:
    """Indica si la funcionalidad avanzada está disponible."""

    return False


__all__ = [
    "BackupFeatureUnavailableError",
    "BackupWorker",
    "RestoreWorker",
    "BackupSystemWidget",
    "create_backup_dialog",
    "show_backup_system",
    "is_available",
]