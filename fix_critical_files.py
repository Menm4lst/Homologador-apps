#!/usr/bin/env python3
"""
Script simple para corregir los imports más críticos manualmente.
"""

fixes = {
    "homologador/ui/change_password_dialog.py": """#!/usr/bin/env python3
\"\"\"Dialog for changing user password.\"\"\"

import logging
import re
import secrets
import string

from PyQt6.QtCore import QTimer, Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QCheckBox, QDialog, QDialogButtonBox, QFormLayout,
    QFrame, QHBoxLayout, QLabel, QLineEdit, QMessageBox,
    QPushButton, QTextEdit, QVBoxLayout
)

from ..data.seed import get_auth_service
from .notification_system import send_error, send_info, send_success, send_warning

logger = logging.getLogger(__name__)""",

    "homologador/ui/final_login.py": """#!/usr/bin/env python3
\"\"\"
Ventana de login final con diseño mejorado y sistema de notificaciones integrado.
\"\"\"

import logging
from typing import Any, Dict, Optional

from PyQt6.QtCore import QEasingCurve, QPropertyAnimation, QRect, Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QIcon, QPixmap
from PyQt6.QtWidgets import (
    QApplication, QCheckBox, QDialog, QFrame, QHBoxLayout, QLabel,
    QLineEdit, QMessageBox, QPushButton, QSizePolicy, QSpacerItem,
    QVBoxLayout, QWidget
)

from ..data.seed import AuthenticationError, get_auth_service

# Importar sistema de notificaciones
try:
    from .notification_system import (
        send_error,
        send_info,
        send_success,
        send_system,
        send_warning
    )
    NOTIFICATIONS_AVAILABLE = True
except ImportError:
    NOTIFICATIONS_AVAILABLE = False""",

    "homologador/ui/details_view.py": """#!/usr/bin/env python3
\"\"\"Vista de detalles de homologaciones.\"\"\"

import logging
from datetime import datetime
from typing import Any, Dict, Optional

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QDialog, QFormLayout, QHBoxLayout, QLabel, QMessageBox,
    QPushButton, QScrollArea, QTextEdit, QVBoxLayout, QWidget
)

from ..core.storage import get_homologation_repository
from .notification_system import send_error, send_info

logger = logging.getLogger(__name__)"""
}

def apply_fixes():
    """Aplica las correcciones a los archivos problemáticos."""
    for file_path, content in fixes.items():
        try:
            # Leer archivo actual
            with open(file_path, 'r', encoding='utf-8') as f:
                current_content = f.read()
            
            # Extraer solo la parte después de los imports para mantener el resto del código
            if '"""' in current_content:
                # Buscar donde termina el docstring
                parts = current_content.split('"""')
                if len(parts) >= 3:
                    # Hay docstring, mantener el resto del código después del segundo """
                    rest_of_code = '"""'.join(parts[2:])
                    new_content = content + '\\n\\n"""' + rest_of_code
                else:
                    new_content = content + '\\n\\n' + current_content
            else:
                # No hay docstring, buscar primera función/clase
                lines = current_content.split('\\n')
                code_start = 0
                for i, line in enumerate(lines):
                    if line.strip().startswith(('class ', 'def ', 'logger = ')):
                        code_start = i
                        break
                
                if code_start > 0:
                    rest_of_code = '\\n'.join(lines[code_start:])
                    new_content = content + '\\n\\n' + rest_of_code
                else:
                    new_content = content + '\\n\\n' + current_content
            
            # Escribir archivo corregido
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"✅ Corregido: {file_path}")
            
        except Exception as e:
            print(f"❌ Error corrigiendo {file_path}: {e}")

if __name__ == "__main__":
    print("🔧 APLICANDO CORRECCIONES MANUALES")
    print("=" * 40)
    apply_fixes()
    print("✅ Correcciones aplicadas")