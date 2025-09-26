"""
Sistema de Respaldos Automáticos para Homologador de Aplicaciones.
Maneja respaldos programados, restauración y verificación de integridad.
"""

import hashlib
import json
import logging
import os
import shutil
import sqlite3
import zipfile
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from PyQt6.QtCore import QObject, QThread, QTimer, pyqtSignal
from PyQt6.QtWidgets import QMessageBox

from .settings import get_settings
from .storage import get_database_manager

logger = logging.getLogger(__name__)

@dataclass
class BackupInfo:
    """Información de un respaldo."""
    filename: str
    filepath: str
    timestamp: datetime
    size_bytes: int
    type: str  # 'manual', 'auto', 'scheduled'
    checksum: str
    description: str = ""
    
    @property
    def size_mb(self) -> float:
        """Tamaño en MB."""
        return self.size_bytes / (1024 * 1024)
    
    @property
    def age_days(self) -> int:
        """Días desde la creación."""
        return (datetime.now() - self.timestamp).days


class BackupManager(QObject):
    """Gestor principal de respaldos."""
    
    # Señales
    backup_started = pyqtSignal(str)  # tipo de respaldo
    backup_progress = pyqtSignal(int, str)  # progreso, mensaje
    backup_completed = pyqtSignal(str, bool, str)  # archivo, éxito, mensaje
    restoration_completed = pyqtSignal(bool, str)  # éxito, mensaje
    
    def __init__(self):
        super().__init__()
        self.settings = get_settings()
        self.db_manager = get_database_manager()
        
        # Configuración de respaldos
        self.backup_dir = self.get_backup_directory()
        self.max_backups = self.settings.get_backup_retention_days()
        self.auto_backup_enabled = self.settings.is_auto_backup_enabled()
        self.backup_interval_hours = 24  # Por defecto 24 horas
        
        # Timer para respaldos automáticos
        self.backup_timer = QTimer()
        self.backup_timer.timeout.connect(self.perform_auto_backup)
        
        # Crear directorio de respaldos
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Iniciar respaldos automáticos si están habilitados
        if self.auto_backup_enabled:
            self.start_auto_backup_schedule()
    
    def get_backup_directory(self) -> Path:
        """Obtiene el directorio de respaldos."""
        backup_path = self.settings.get_backups_dir()
        if backup_path:
            return Path(backup_path)
        
        # Directorio por defecto junto a la base de datos
        db_path = Path(self.db_manager.db_path)
        return db_path.parent / "backups"
    
    def start_auto_backup_schedule(self):
        """Inicia el cronograma de respaldos automáticos."""
        if not self.auto_backup_enabled:
            return
        
        # Convertir horas a milisegundos
        interval_ms = self.backup_interval_hours * 60 * 60 * 1000
        self.backup_timer.start(interval_ms)
        
        logger.info(f"Respaldos automáticos iniciados cada {self.backup_interval_hours} horas")
    
    def stop_auto_backup_schedule(self):
        """Detiene el cronograma de respaldos automáticos."""
        self.backup_timer.stop()
        logger.info("Respaldos automáticos detenidos")
    
    def perform_auto_backup(self):
        """Realiza un respaldo automático."""
        try:
            self.create_backup("auto", "Respaldo automático programado")
        except Exception as e:
            logger.error(f"Error en respaldo automático: {e}")
    
    def create_backup(self, backup_type: str = "manual", description: str = "") -> Optional[BackupInfo]:
        """Crea un respaldo completo del sistema."""
        try:
            self.backup_started.emit(backup_type)
            
            # Generar nombre de archivo
            timestamp = datetime.now()
            filename = f"homologador_backup_{timestamp.strftime('%Y%m%d_%H%M%S')}.zip"
            backup_path = self.backup_dir / filename
            
            self.backup_progress.emit(10, "Preparando respaldo...")
            
            # Crear archivo ZIP
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                
                # 1. Respaldo de base de datos
                self.backup_progress.emit(25, "Respaldando base de datos...")
                db_path = Path(self.db_manager.db_path)
                if db_path.exists():
                    zipf.write(db_path, f"database/{db_path.name}")
                
                # 2. Respaldo de configuraciones
                self.backup_progress.emit(50, "Respaldando configuraciones...")
                config_data = {
                    'settings': self.settings.get_config(),
                    'backup_info': {
                        'timestamp': timestamp.isoformat(),
                        'type': backup_type,
                        'description': description,
                        'version': '1.0.0'
                    }
                }
                
                config_json = json.dumps(config_data, indent=2, default=str)
                zipf.writestr("config/settings.json", config_json)
                
                # 3. Respaldo de logs (últimos 7 días)
                self.backup_progress.emit(75, "Respaldando logs...")
                self._backup_logs(zipf)
                
                # 4. Metadatos del respaldo
                self.backup_progress.emit(90, "Finalizando respaldo...")
                metadata = {
                    'created': timestamp.isoformat(),
                    'type': backup_type,
                    'description': description,
                    'files_included': ['database', 'config', 'logs']
                }
                zipf.writestr("backup_metadata.json", json.dumps(metadata, indent=2))
            
            # Calcular checksum
            checksum = self._calculate_file_checksum(backup_path)
            
            # Crear información del respaldo
            backup_info = BackupInfo(
                filename=filename,
                filepath=str(backup_path),
                timestamp=timestamp,
                size_bytes=backup_path.stat().st_size,
                type=backup_type,
                checksum=checksum,
                description=description
            )
            
            # Limpiar respaldos antiguos
            self._cleanup_old_backups()
            
            self.backup_progress.emit(100, "Respaldo completado")
            self.backup_completed.emit(str(backup_path), True, f"Respaldo creado exitosamente: {filename}")
            
            logger.info(f"Respaldo creado: {filename} ({backup_info.size_mb:.2f} MB)")
            return backup_info
            
        except Exception as e:
            error_msg = f"Error creando respaldo: {e}"
            logger.error(error_msg)
            self.backup_completed.emit("", False, error_msg)
            return None
    
    def _backup_logs(self, zipf: zipfile.ZipFile):
        """Respalda archivos de log recientes."""
        try:
            # Buscar archivos de log en directorio de la aplicación
            app_dir = Path(__file__).parent.parent
            log_files = []
            
            # Buscar archivos .log en varios directorios posibles
            for log_dir in [app_dir, app_dir / "logs", Path.home()]:
                if log_dir.exists():
                    log_files.extend(log_dir.glob("*.log"))
            
            # Filtrar logs recientes (últimos 7 días)
            cutoff_date = datetime.now() - timedelta(days=7)
            
            for log_file in log_files:
                try:
                    if log_file.stat().st_mtime > cutoff_date.timestamp():
                        zipf.write(log_file, f"logs/{log_file.name}")
                except (OSError, IOError):
                    continue  # Archivo no accesible, continuar
                    
        except Exception as e:
            logger.warning(f"Error respaldando logs: {e}")
    
    def _calculate_file_checksum(self, filepath: Path) -> str:
        """Calcula el checksum SHA-256 de un archivo."""
        sha256_hash = hashlib.sha256()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    
    def _cleanup_old_backups(self):
        """Elimina respaldos antiguos según la configuración."""
        try:
            backups = self.list_backups()
            
            # Ordenar por fecha (más recientes primero)
            backups.sort(key=lambda x: x.timestamp, reverse=True)
            
            # Eliminar respaldos que excedan el límite
            if len(backups) > self.max_backups:
                for backup in backups[self.max_backups:]:
                    try:
                        Path(backup.filepath).unlink()
                        logger.info(f"Respaldo antiguo eliminado: {backup.filename}")
                    except OSError as e:
                        logger.warning(f"No se pudo eliminar respaldo {backup.filename}: {e}")
            
        except Exception as e:
            logger.error(f"Error limpiando respaldos antiguos: {e}")
    
    def list_backups(self) -> List[BackupInfo]:
        """Lista todos los respaldos disponibles."""
        backups = []
        
        try:
            if not self.backup_dir.exists():
                return backups
            
            for backup_file in self.backup_dir.glob("homologador_backup_*.zip"):
                try:
                    # Extraer timestamp del nombre del archivo
                    name_parts = backup_file.stem.split('_')
                    if len(name_parts) >= 3:
                        date_str = name_parts[2]
                        time_str = name_parts[3] if len(name_parts) > 3 else "000000"
                        
                        timestamp = datetime.strptime(f"{date_str}_{time_str}", "%Y%m%d_%H%M%S")
                        
                        # Obtener información del archivo
                        stat = backup_file.stat()
                        checksum = self._calculate_file_checksum(backup_file)
                        
                        # Intentar obtener metadatos del respaldo
                        backup_type, description = self._extract_backup_metadata(backup_file)
                        
                        backup_info = BackupInfo(
                            filename=backup_file.name,
                            filepath=str(backup_file),
                            timestamp=timestamp,
                            size_bytes=stat.st_size,
                            type=backup_type,
                            checksum=checksum,
                            description=description
                        )
                        
                        backups.append(backup_info)
                        
                except Exception as e:
                    logger.warning(f"Error procesando respaldo {backup_file.name}: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"Error listando respaldos: {e}")
        
        return backups
    
    def _extract_backup_metadata(self, backup_file: Path) -> Tuple[str, str]:
        """Extrae metadatos de un archivo de respaldo."""
        try:
            with zipfile.ZipFile(backup_file, 'r') as zipf:
                if "backup_metadata.json" in zipf.namelist():
                    metadata_content = zipf.read("backup_metadata.json").decode('utf-8')
                    metadata = json.loads(metadata_content)
                    return metadata.get('type', 'unknown'), metadata.get('description', '')
        except Exception:
            pass
        
        return 'unknown', ''
    
    def restore_backup(self, backup_info: BackupInfo, restore_database: bool = True, 
                      restore_config: bool = False) -> bool:
        """Restaura un respaldo."""
        try:
            self.backup_progress.emit(0, "Iniciando restauración...")
            
            backup_path = Path(backup_info.filepath)
            if not backup_path.exists():
                raise FileNotFoundError(f"Archivo de respaldo no encontrado: {backup_path}")
            
            # Verificar integridad
            current_checksum = self._calculate_file_checksum(backup_path)
            if current_checksum != backup_info.checksum:
                raise ValueError("El archivo de respaldo está corrupto (checksum no coincide)")
            
            # Crear respaldo de seguridad antes de restaurar
            self.backup_progress.emit(20, "Creando respaldo de seguridad...")
            safety_backup = self.create_backup("safety", "Respaldo de seguridad antes de restauración")
            
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                
                if restore_database:
                    self.backup_progress.emit(50, "Restaurando base de datos...")
                    
                    # Buscar archivo de base de datos en el respaldo
                    db_files = [name for name in zipf.namelist() if name.startswith('database/')]
                    
                    if db_files:
                        # Cerrar conexiones actuales
                        self.db_manager.close_all_connections()
                        
                        # Restaurar base de datos
                        db_content = zipf.read(db_files[0])
                        
                        # Hacer backup del archivo actual
                        current_db = Path(self.db_manager.db_path)
                        if current_db.exists():
                            backup_db = current_db.with_suffix('.db.backup')
                            shutil.copy2(current_db, backup_db)
                        
                        # Escribir nueva base de datos
                        with open(current_db, 'wb') as f:
                            f.write(db_content)
                        
                        # Verificar integridad de la base de datos restaurada
                        if not self._verify_database_integrity(current_db):
                            # Restaurar backup si la verificación falla
                            if backup_db.exists():
                                shutil.copy2(backup_db, current_db)
                            raise ValueError("La base de datos restaurada falló la verificación de integridad")
                
                if restore_config:
                    self.backup_progress.emit(75, "Restaurando configuración...")
                    
                    config_files = [name for name in zipf.namelist() if name.startswith('config/')]
                    
                    if config_files:
                        config_content = zipf.read(config_files[0]).decode('utf-8')
                        config_data = json.loads(config_content)
                        
                        # Restaurar configuraciones seleccionadas
                        if 'settings' in config_data:
                            # Nota: La restauración de configuraciones requiere reinicialización
                            logger.info("Configuraciones encontradas en el respaldo (requiere reinicio para aplicar)")
            
            self.backup_progress.emit(100, "Restauración completada")
            self.restoration_completed.emit(True, f"Respaldo restaurado exitosamente desde {backup_info.filename}")
            
            logger.info(f"Respaldo restaurado: {backup_info.filename}")
            return True
            
        except Exception as e:
            error_msg = f"Error restaurando respaldo: {e}"
            logger.error(error_msg)
            self.restoration_completed.emit(False, error_msg)
            return False
    
    def _verify_database_integrity(self, db_path: Path) -> bool:
        """Verifica la integridad de una base de datos SQLite."""
        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Verificación rápida de integridad
            cursor.execute("PRAGMA integrity_check")
            result = cursor.fetchone()
            
            conn.close()
            
            return result and result[0] == "ok"
            
        except Exception as e:
            logger.error(f"Error verificando integridad de BD: {e}")
            return False
    
    def delete_backup(self, backup_info: BackupInfo) -> bool:
        """Elimina un respaldo específico."""
        try:
            backup_path = Path(backup_info.filepath)
            if backup_path.exists():
                backup_path.unlink()
                logger.info(f"Respaldo eliminado: {backup_info.filename}")
                return True
            else:
                logger.warning(f"Respaldo no encontrado: {backup_path}")
                return False
                
        except Exception as e:
            logger.error(f"Error eliminando respaldo {backup_info.filename}: {e}")
            return False
    
    def get_backup_statistics(self) -> Dict[str, Any]:
        """Obtiene estadísticas de respaldos."""
        try:
            backups = self.list_backups()
            
            if not backups:
                return {
                    'total_backups': 0,
                    'total_size_mb': 0.0,
                    'latest_backup': None,
                    'oldest_backup': None,
                    'auto_backups': 0,
                    'manual_backups': 0
                }
            
            total_size = sum(backup.size_bytes for backup in backups)
            auto_count = sum(1 for backup in backups if backup.type == 'auto')
            manual_count = sum(1 for backup in backups if backup.type == 'manual')
            
            # Ordenar por fecha
            backups_by_date = sorted(backups, key=lambda x: x.timestamp)
            
            return {
                'total_backups': len(backups),
                'total_size_mb': total_size / (1024 * 1024),
                'latest_backup': backups_by_date[-1] if backups_by_date else None,
                'oldest_backup': backups_by_date[0] if backups_by_date else None,
                'auto_backups': auto_count,
                'manual_backups': manual_count,
                'average_size_mb': (total_size / len(backups)) / (1024 * 1024) if backups else 0
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas de respaldos: {e}")
            return {}


# Instancia global del gestor de respaldos
_backup_manager = None

def get_backup_manager() -> BackupManager:
    """Obtiene la instancia global del gestor de respaldos."""
    global _backup_manager
    if _backup_manager is None:
        _backup_manager = BackupManager()
    return _backup_manager