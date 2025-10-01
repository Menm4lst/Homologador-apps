#!/usr/bin/env python3
"""Entry point for the Homologador application."""


# Agregar el directorio padre al path para imports absolutos

from pathlib import Path
import os
import sys
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.insert(0, str(parent_dir))

if __name__ == "__main__":
    try:
        # Intentar import relativo primero (para ejecución como módulo)
        from .app import main
    except ImportError:
        # Si falla, usar import absoluto (para PyInstaller)
        from homologador.app import main
    main()