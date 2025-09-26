"""
Gestión de autoguardado para formularios de homologación.
Guarda borradores automáticos periódicamente para evitar pérdida de datos.
"""

import json
import logging
import tempfile
from datetime import datetime
from pathlib import Path

from PyQt6.QtCore import QTimer


class AutoSaveManager:
    """Gestiona el autoguardado de los datos del formulario."""
    
    def __init__(self, form_dialog):
        """Inicializa el gestor de autoguardado.
        
        Args:
            form_dialog: Instancia de HomologationFormDialog
        """
        self.form_dialog = form_dialog
        self.autosave_timer = QTimer()
        self.autosave_timer.setInterval(30000)  # 30 segundos
        self.autosave_timer.timeout.connect(self.auto_save)
        
        # Crear directorio para borradores si no existe
        self.drafts_dir = Path(tempfile.gettempdir()) / "homologador_drafts"
        self.drafts_dir.mkdir(exist_ok=True)
    
    def start(self):
        """Inicia el temporizador de autoguardado."""
        self.autosave_timer.start()
    
    def stop(self):
        """Detiene el temporizador de autoguardado."""
        self.autosave_timer.stop()
    
    def auto_save(self):
        """Guarda automáticamente el estado actual del formulario."""
        # Solo guardar si hay cambios
        if not self.form_dialog or not hasattr(self.form_dialog, "real_name_edit"):
            return
        
        # Si no hay un nombre real, no guardar borrador
        if not self.form_dialog.real_name_edit.text().strip():
            return
        
        try:
            # Obtener datos actuales
            form_data = self.form_dialog.get_form_data()
            
            # Generar nombre de archivo para el borrador
            draft_id = self.form_dialog.homologation_data.get('id', 'new')
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            filename = f"draft_{draft_id}_{timestamp}.json"
            draft_path = self.drafts_dir / filename
            
            # Guardar borrador
            with open(draft_path, 'w', encoding='utf-8') as f:
                json.dump(form_data, f, ensure_ascii=False, indent=2)
            
            # Limpiar borradores antiguos (mantener solo los 5 más recientes)
            self._cleanup_old_drafts(draft_id)
            
            # Mostrar información de autoguardado
            self.form_dialog.status_label.setText("Borrador guardado automáticamente")
            QTimer.singleShot(3000, lambda: self.form_dialog.status_label.clear())
            
        except Exception as e:
            logging.error(f"Error al guardar borrador: {e}")
    
    def _cleanup_old_drafts(self, draft_id):
        """Limpia borradores antiguos, manteniendo solo los más recientes."""
        pattern = f"draft_{draft_id}_*.json"
        drafts = sorted(self.drafts_dir.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)
        
        # Mantener solo los 5 más recientes
        for old_draft in drafts[5:]:
            try:
                old_draft.unlink()
            except Exception as e:
                logging.error(f"Error al eliminar borrador antiguo {old_draft}: {e}")
    
    def get_latest_draft(self, draft_id="new"):
        """Recupera el borrador más reciente para el ID especificado."""
        pattern = f"draft_{draft_id}_*.json"
        drafts = sorted(self.drafts_dir.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)
        
        if not drafts:
            return None
        
        try:
            with open(drafts[0], 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Error al cargar borrador: {e}")
            return None