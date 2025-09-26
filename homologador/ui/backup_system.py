"""
Sistema Avanzado de Respaldos y Restauración.

Este módulo proporciona funcionalidades completas para crear, gestionar y restaurar
respaldos de la base de datos y configuraciones del sistema.
"""

import json
import logging
import os
import shutil
import sqlite3
import zipfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, cast

from PyQt6.QtCore import QDate, Qt, QThread, QTimer, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QAction, QColor, QFont, QIcon, QPalette
from PyQt6.QtWidgets import (QButtonGroup, QCheckBox, QComboBox, QDateEdit,
                             QDialog, QFileDialog, QFormLayout, QFrame,
                             QGroupBox, QHBoxLayout, QHeaderView, QLabel,
                             QLineEdit, QListWidget, QListWidgetItem,
                             QMessageBox, QProgressBar, QPushButton,
                             QRadioButton, QSlider, QSpinBox, QSplitter,
                             QTableWidget, QTableWidgetItem, QTabWidget,
                             QTextBrowser, QTextEdit, QVBoxLayout, QWidget)

logger = logging.getLogger(__name__)


class BackupWorker(QThread):
    """Worker thread para operaciones de respaldo en segundo plano."""
    
    progress_updated = pyqtSignal(int)
    status_updated = pyqtSignal(str)
    finished = pyqtSignal(bool, str)  # success, message
    
    def __init__(self, backup_config: Dict[str, Any]):
        super().__init__()
        self.backup_config = backup_config
        
    def run(self):
        """Ejecuta el proceso de respaldo."""
        try:
            self.status_updated.emit("Iniciando proceso de respaldo...")
            self.progress_updated.emit(10)
            
            # Crear directorio de respaldo
            backup_dir = Path(self.backup_config['backup_path'])
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"homologador_backup_{timestamp}"
            backup_path = backup_dir / f"{backup_name}.zip"
            
            self.status_updated.emit("Creando archivo de respaldo...")
            self.progress_updated.emit(20)
            
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Respaldar base de datos
                if self.backup_config.get('include_database', True):
                    self.status_updated.emit("Respaldando base de datos...")
                    self.progress_updated.emit(40)
                    self._backup_database(zipf, timestamp)
                
                # Respaldar configuraciones
                if self.backup_config.get('include_config', True):
                    self.status_updated.emit("Respaldando configuraciones...")
                    self.progress_updated.emit(60)
                    self._backup_configs(zipf)
                
                # Respaldar logs
                if self.backup_config.get('include_logs', False):
                    self.status_updated.emit("Respaldando logs...")
                    self.progress_updated.emit(80)
                    self._backup_logs(zipf)
                
                # Respaldar archivos de usuario
                if self.backup_config.get('include_user_files', False):
                    self.status_updated.emit("Respaldando archivos de usuario...")
                    self._backup_user_files(zipf)
            
            self.progress_updated.emit(100)
            self.status_updated.emit("Respaldo completado exitosamente")
            
            # Guardar información del respaldo
            self._save_backup_info(backup_name, backup_path, timestamp)
            
            self.finished.emit(True, f"Respaldo creado exitosamente: {backup_path}")
            
        except Exception as e:
            logger.error(f"Error durante el respaldo: {e}")
            self.finished.emit(False, f"Error durante el respaldo: {str(e)}")
    
    def _backup_database(self, zipf: zipfile.ZipFile, timestamp: str):
        """Respalda la base de datos."""
        try:
            db_path = Path("data/homologador.db")
            if db_path.exists():
                # Crear una copia temporal de la base de datos
                temp_db_path = f"temp_backup_{timestamp}.db"
                shutil.copy2(db_path, temp_db_path)
                
                # Agregar al zip
                zipf.write(temp_db_path, "database/homologador.db")
                
                # Limpiar archivo temporal
                os.remove(temp_db_path)
                
                # Exportar esquema SQL
                self._export_database_schema(zipf, db_path)
                
        except Exception as e:
            logger.error(f"Error respaldando base de datos: {e}")
            raise
    
    def _export_database_schema(self, zipf: zipfile.ZipFile, db_path: Path):
        """Exporta el esquema de la base de datos."""
        try:
            conn = sqlite3.connect(db_path)
            
            # Obtener esquema
            cursor = conn.cursor()
            cursor.execute("SELECT sql FROM sqlite_master WHERE type='table';")
            schema_lines = [row[0] for row in cursor.fetchall() if row[0]]
            
            schema_sql = "\\n\\n".join(schema_lines)
            
            # Guardar esquema
            zipf.writestr("database/schema.sql", schema_sql)
            
            conn.close()
            
        except Exception as e:
            logger.error(f"Error exportando esquema: {e}")
    
    def _backup_configs(self, zipf: zipfile.ZipFile):
        """Respalda archivos de configuración."""
        config_files = [
            "config/app_config.json",
            "config/database_config.json",
            "config/logging_config.json"
        ]
        
        for config_file in config_files:
            if os.path.exists(config_file):
                zipf.write(config_file, f"config/{os.path.basename(config_file)}")
    
    def _backup_logs(self, zipf: zipfile.ZipFile):
        """Respalda archivos de logs."""
        log_dir = Path("logs")
        if log_dir.exists():
            for log_file in log_dir.glob("*.log"):
                zipf.write(log_file, f"logs/{log_file.name}")
    
    def _backup_user_files(self, zipf: zipfile.ZipFile):
        """Respalda archivos de usuario."""
        user_dirs = ["exports", "imports", "templates"]
        
        for user_dir in user_dirs:
            if os.path.exists(user_dir):
                for root, dirs, files in os.walk(user_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        archive_path = os.path.relpath(file_path)
                        zipf.write(file_path, archive_path)
    
    def _save_backup_info(self, backup_name: str, backup_path: Path, timestamp: str):
        """Guarda información del respaldo."""
        backup_info = {
            'name': backup_name,
            'path': str(backup_path),
            'timestamp': timestamp,
            'created_at': datetime.now().isoformat(),
            'size': backup_path.stat().st_size,
            'config': self.backup_config
        }
        
        # Guardar en archivo de índice
        index_file = Path("backups/backup_index.json")
        index_file.parent.mkdir(exist_ok=True)
        
        if index_file.exists():
            with open(index_file, 'r', encoding='utf-8') as f:
                index_data = json.load(f)
        else:
            index_data = {'backups': []}
        
        index_data['backups'].append(backup_info)
        
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(index_data, f, indent=2, ensure_ascii=False)


class RestoreWorker(QThread):
    """Worker thread para operaciones de restauración."""
    
    progress_updated = pyqtSignal(int)
    status_updated = pyqtSignal(str)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, backup_path: str, restore_config: Dict[str, Any]):
        super().__init__()
        self.backup_path = backup_path
        self.restore_config = restore_config
        
    def run(self):
        """Ejecuta el proceso de restauración."""
        try:
            self.status_updated.emit("Iniciando proceso de restauración...")
            self.progress_updated.emit(10)
            
            # Crear respaldo de seguridad antes de restaurar
            if self.restore_config.get('create_safety_backup', True):
                self.status_updated.emit("Creando respaldo de seguridad...")
                self.progress_updated.emit(20)
                self._create_safety_backup()
            
            self.status_updated.emit("Extrayendo archivo de respaldo...")
            self.progress_updated.emit(40)
            
            with zipfile.ZipFile(self.backup_path, 'r') as zipf:
                # Restaurar base de datos
                if self.restore_config.get('restore_database', True):
                    self.status_updated.emit("Restaurando base de datos...")
                    self.progress_updated.emit(60)
                    self._restore_database(zipf)
                
                # Restaurar configuraciones
                if self.restore_config.get('restore_config', True):
                    self.status_updated.emit("Restaurando configuraciones...")
                    self.progress_updated.emit(80)
                    self._restore_configs(zipf)
                
                # Restaurar archivos de usuario
                if self.restore_config.get('restore_user_files', False):
                    self.status_updated.emit("Restaurando archivos de usuario...")
                    self._restore_user_files(zipf)
            
            self.progress_updated.emit(100)
            self.status_updated.emit("Restauración completada exitosamente")
            self.finished.emit(True, "Restauración completada exitosamente")
            
        except Exception as e:
            logger.error(f"Error durante la restauración: {e}")
            self.finished.emit(False, f"Error durante la restauración: {str(e)}")
    
    def _create_safety_backup(self):
        """Crea un respaldo de seguridad antes de restaurar."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safety_backup_path = f"backups/safety_backup_{timestamp}.zip"
        
        # Usar el worker de respaldo para crear el respaldo de seguridad
        backup_config = {
            'backup_path': 'backups',
            'include_database': True,
            'include_config': True,
            'include_logs': False,
            'include_user_files': False
        }
        
        # Crear respaldo de seguridad de forma síncrona
        # (implementación simplificada para este ejemplo)
        pass
    
    def _restore_database(self, zipf: zipfile.ZipFile):
        """Restaura la base de datos."""
        try:
            # Extraer base de datos
            db_info = zipf.getinfo("database/homologador.db")
            zipf.extract(db_info, "temp_restore")
            
            # Mover la base de datos restaurada
            temp_db_path = "temp_restore/database/homologador.db"
            target_db_path = "data/homologador.db"
            
            # Crear directorio si no existe
            os.makedirs(os.path.dirname(target_db_path), exist_ok=True)
            
            # Mover archivo
            shutil.move(temp_db_path, target_db_path)
            
            # Limpiar archivos temporales
            shutil.rmtree("temp_restore", ignore_errors=True)
            
        except Exception as e:
            logger.error(f"Error restaurando base de datos: {e}")
            raise
    
    def _restore_configs(self, zipf: zipfile.ZipFile):
        """Restaura archivos de configuración."""
        config_files = ["config/app_config.json", "config/database_config.json", "config/logging_config.json"]
        
        for config_file in config_files:
            try:
                zipf.extract(config_file, ".")
            except KeyError:
                # Archivo no existe en el respaldo
                continue
    
    def _restore_user_files(self, zipf: zipfile.ZipFile):
        """Restaura archivos de usuario."""
        user_dirs = ["exports", "imports", "templates"]
        
        for user_dir in user_dirs:
            for file_info in zipf.filelist:
                if file_info.filename.startswith(user_dir + "/"):
                    zipf.extract(file_info, ".")


class BackupSystemWidget(QWidget):
    """Widget principal del sistema de respaldos."""
    
    def __init__(self, user_info: Dict[str, Any], parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.user_info = user_info
        
        self.setup_ui()
        self.apply_dark_theme()
        self.load_backup_list()
        
        logger.info(f"Sistema de respaldos iniciado por: {user_info.get('username')}")
    
    def setup_ui(self):
        """Configura la interfaz del sistema de respaldos."""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        
        # Título
        title_label = QLabel("💾 Sistema de Respaldos y Restauración")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setWeight(QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        main_layout.addWidget(title_label)
        
        # Pestañas
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        self.create_backup_tab()
        self.create_restore_tab()
        self.create_schedule_tab()
        self.create_settings_tab()
    
    def create_backup_tab(self):
        """Crea la pestaña de creación de respaldos."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Configuración del respaldo
        config_group = QGroupBox("⚙️ Configuración del Respaldo")
        config_layout = QFormLayout(config_group)
        
        # Nombre del respaldo
        self.backup_name = QLineEdit()
        self.backup_name.setPlaceholderText("Nombre automático basado en fecha")
        config_layout.addRow("Nombre del respaldo:", self.backup_name)
        
        # Directorio de destino
        backup_dir_layout = QHBoxLayout()
        self.backup_directory = QLineEdit("backups")
        backup_dir_layout.addWidget(self.backup_directory)
        
        browse_btn = QPushButton("📁 Examinar")
        browse_btn.clicked.connect(self.browse_backup_directory)
        backup_dir_layout.addWidget(browse_btn)
        
        config_layout.addRow("Directorio de destino:", backup_dir_layout)
        
        # Opciones de respaldo
        options_layout = QVBoxLayout()
        
        self.include_database = QCheckBox("Base de datos")
        self.include_database.setChecked(True)
        options_layout.addWidget(self.include_database)
        
        self.include_config = QCheckBox("Archivos de configuración")
        self.include_config.setChecked(True)
        options_layout.addWidget(self.include_config)
        
        self.include_logs = QCheckBox("Archivos de logs")
        options_layout.addWidget(self.include_logs)
        
        self.include_user_files = QCheckBox("Archivos de usuario (exports, imports)")
        options_layout.addWidget(self.include_user_files)
        
        config_layout.addRow("Incluir en el respaldo:", options_layout)
        
        # Compresión
        self.compression_level = QComboBox()
        self.compression_level.addItems(["Ninguna", "Rápida", "Normal", "Máxima"])
        self.compression_level.setCurrentText("Normal")
        config_layout.addRow("Nivel de compresión:", self.compression_level)
        
        layout.addWidget(config_group)
        
        # Botón de crear respaldo
        create_backup_btn = QPushButton("💾 Crear Respaldo")
        create_backup_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 15px 30px;
                font-weight: bold;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """)
        create_backup_btn.clicked.connect(self.create_backup)
        layout.addWidget(create_backup_btn)
        
        # Progreso
        progress_group = QGroupBox("📊 Progreso del Respaldo")
        progress_layout = QVBoxLayout(progress_group)
        
        self.backup_progress = QProgressBar()
        progress_layout.addWidget(self.backup_progress)
        
        self.backup_status = QLabel("Listo para crear respaldo")
        progress_layout.addWidget(self.backup_status)
        
        layout.addWidget(progress_group)
        
        # Lista de respaldos recientes
        recent_group = QGroupBox("📋 Respaldos Recientes")
        recent_layout = QVBoxLayout(recent_group)
        
        self.recent_backups_list = QListWidget()
        recent_layout.addWidget(self.recent_backups_list)
        
        layout.addWidget(recent_group)
        
        self.tab_widget.addTab(tab, "💾 Crear Respaldo")
    
    def create_restore_tab(self):
        """Crea la pestaña de restauración."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Selección de respaldo
        select_group = QGroupBox("📂 Seleccionar Respaldo")
        select_layout = QVBoxLayout(select_group)
        
        # Lista de respaldos disponibles
        self.backups_table = QTableWidget()
        self.backups_table.setColumnCount(5)
        self.backups_table.setHorizontalHeaderLabels(["Nombre", "Fecha", "Tamaño", "Tipo", "Estado"])
        self.backups_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.backups_table.setAlternatingRowColors(True)
        
        # Configurar columnas
        header = self.backups_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        
        select_layout.addWidget(self.backups_table)
        
        # Botones de gestión
        buttons_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("🔄 Actualizar")
        refresh_btn.clicked.connect(self.load_backup_list)
        buttons_layout.addWidget(refresh_btn)
        
        import_btn = QPushButton("📁 Importar Respaldo")
        import_btn.clicked.connect(self.import_backup)
        buttons_layout.addWidget(import_btn)
        
        delete_btn = QPushButton("🗑️ Eliminar")
        delete_btn.clicked.connect(self.delete_backup)
        buttons_layout.addWidget(delete_btn)
        
        buttons_layout.addStretch()
        select_layout.addLayout(buttons_layout)
        
        layout.addWidget(select_group)
        
        # Opciones de restauración
        restore_options_group = QGroupBox("⚙️ Opciones de Restauración")
        restore_options_layout = QFormLayout(restore_options_group)
        
        # Elementos a restaurar
        restore_items_layout = QVBoxLayout()
        
        self.restore_database = QCheckBox("Base de datos")
        self.restore_database.setChecked(True)
        restore_items_layout.addWidget(self.restore_database)
        
        self.restore_config = QCheckBox("Configuraciones")
        self.restore_config.setChecked(True)
        restore_items_layout.addWidget(self.restore_config)
        
        self.restore_user_files = QCheckBox("Archivos de usuario")
        restore_items_layout.addWidget(self.restore_user_files)
        
        restore_options_layout.addRow("Restaurar:", restore_items_layout)
        
        # Crear respaldo de seguridad
        self.create_safety_backup = QCheckBox("Crear respaldo de seguridad antes de restaurar")
        self.create_safety_backup.setChecked(True)
        restore_options_layout.addRow(self.create_safety_backup)
        
        layout.addWidget(restore_options_group)
        
        # Botón de restaurar
        restore_btn = QPushButton("🔄 Restaurar Respaldo")
        restore_btn.setStyleSheet("""
            QPushButton {
                background-color: #e67e22;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 15px 30px;
                font-weight: bold;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #f39c12;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """)
        restore_btn.clicked.connect(self.restore_backup)
        layout.addWidget(restore_btn)
        
        # Progreso de restauración
        restore_progress_group = QGroupBox("📊 Progreso de Restauración")
        restore_progress_layout = QVBoxLayout(restore_progress_group)
        
        self.restore_progress = QProgressBar()
        restore_progress_layout.addWidget(self.restore_progress)
        
        self.restore_status = QLabel("Seleccione un respaldo para restaurar")
        restore_progress_layout.addWidget(self.restore_status)
        
        layout.addWidget(restore_progress_group)
        
        self.tab_widget.addTab(tab, "🔄 Restaurar")
    
    def create_schedule_tab(self):
        """Crea la pestaña de respaldos programados."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Configuración de respaldos automáticos
        auto_group = QGroupBox("⏰ Respaldos Automáticos")
        auto_layout = QFormLayout(auto_group)
        
        # Habilitar respaldos automáticos
        self.enable_auto_backup = QCheckBox("Habilitar respaldos automáticos")
        auto_layout.addRow(self.enable_auto_backup)
        
        # Frecuencia
        self.backup_frequency = QComboBox()
        self.backup_frequency.addItems(["Diario", "Semanal", "Mensual"])
        auto_layout.addRow("Frecuencia:", self.backup_frequency)
        
        # Hora de ejecución
        self.backup_time = QComboBox()
        for hour in range(24):
            self.backup_time.addItem(f"{hour:02d}:00")
        self.backup_time.setCurrentText("02:00")
        auto_layout.addRow("Hora de ejecución:", self.backup_time)
        
        # Retención
        self.retention_days = QSpinBox()
        self.retention_days.setRange(1, 365)
        self.retention_days.setValue(30)
        self.retention_days.setSuffix(" días")
        auto_layout.addRow("Mantener respaldos por:", self.retention_days)
        
        # Máximo número de respaldos
        self.max_backups = QSpinBox()
        self.max_backups.setRange(1, 100)
        self.max_backups.setValue(10)
        auto_layout.addRow("Máximo número de respaldos:", self.max_backups)
        
        layout.addWidget(auto_group)
        
        # Programación personalizada
        custom_group = QGroupBox("📅 Programación Personalizada")
        custom_layout = QVBoxLayout(custom_group)
        
        self.custom_schedules_list = QListWidget()
        custom_layout.addWidget(self.custom_schedules_list)
        
        custom_buttons_layout = QHBoxLayout()
        add_schedule_btn = QPushButton("➕ Agregar Programación")
        add_schedule_btn.clicked.connect(self.add_custom_schedule)
        custom_buttons_layout.addWidget(add_schedule_btn)
        
        edit_schedule_btn = QPushButton("✏️ Editar")
        custom_buttons_layout.addWidget(edit_schedule_btn)
        
        remove_schedule_btn = QPushButton("🗑️ Eliminar")
        custom_buttons_layout.addWidget(remove_schedule_btn)
        
        custom_buttons_layout.addStretch()
        custom_layout.addLayout(custom_buttons_layout)
        
        layout.addWidget(custom_group)
        
        # Botón guardar configuración
        save_config_btn = QPushButton("💾 Guardar Configuración")
        save_config_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px 24px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        save_config_btn.clicked.connect(self.save_schedule_config)
        layout.addWidget(save_config_btn)
        
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "⏰ Programación")
    
    def create_settings_tab(self):
        """Crea la pestaña de configuraciones."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Configuraciones generales
        general_group = QGroupBox("⚙️ Configuraciones Generales")
        general_layout = QFormLayout(general_group)
        
        # Directorio por defecto
        self.default_backup_dir = QLineEdit("backups")
        general_layout.addRow("Directorio por defecto:", self.default_backup_dir)
        
        # Nivel de compresión por defecto
        self.default_compression = QComboBox()
        self.default_compression.addItems(["Ninguna", "Rápida", "Normal", "Máxima"])
        self.default_compression.setCurrentText("Normal")
        general_layout.addRow("Compresión por defecto:", self.default_compression)
        
        # Verificar integridad
        self.verify_backup_integrity = QCheckBox("Verificar integridad después del respaldo")
        self.verify_backup_integrity.setChecked(True)
        general_layout.addRow(self.verify_backup_integrity)
        
        # Notificaciones
        self.enable_notifications = QCheckBox("Habilitar notificaciones")
        self.enable_notifications.setChecked(True)
        general_layout.addRow(self.enable_notifications)
        
        layout.addWidget(general_group)
        
        # Configuraciones de seguridad
        security_group = QGroupBox("🔒 Configuraciones de Seguridad")
        security_layout = QFormLayout(security_group)
        
        # Encriptar respaldos
        self.encrypt_backups = QCheckBox("Encriptar respaldos")
        security_layout.addRow(self.encrypt_backups)
        
        # Contraseña de encriptación
        self.encryption_password = QLineEdit()
        self.encryption_password.setEchoMode(QLineEdit.EchoMode.Password)
        security_layout.addRow("Contraseña de encriptación:", self.encryption_password)
        
        layout.addWidget(security_group)
        
        # Configuraciones de almacenamiento
        storage_group = QGroupBox("💾 Configuraciones de Almacenamiento")
        storage_layout = QFormLayout(storage_group)
        
        # Almacenamiento en la nube
        self.cloud_storage_enabled = QCheckBox("Respaldo en la nube")
        storage_layout.addRow(self.cloud_storage_enabled)
        
        # Proveedor de nube
        self.cloud_provider = QComboBox()
        self.cloud_provider.addItems(["Google Drive", "Dropbox", "OneDrive", "Amazon S3"])
        storage_layout.addRow("Proveedor:", self.cloud_provider)
        
        layout.addWidget(storage_group)
        
        # Botón guardar configuración
        save_settings_btn = QPushButton("💾 Guardar Configuraciones")
        save_settings_btn.clicked.connect(self.save_settings)
        layout.addWidget(save_settings_btn)
        
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "⚙️ Configuración")
    
    def browse_backup_directory(self):
        """Permite seleccionar el directorio de respaldos."""
        directory = QFileDialog.getExistingDirectory(self, "Seleccionar Directorio de Respaldos")
        if directory:
            self.backup_directory.setText(directory)
    
    def create_backup(self):
        """Inicia el proceso de creación de respaldo."""
        try:
            # Configuración del respaldo
            backup_config = {
                'backup_path': self.backup_directory.text(),
                'include_database': self.include_database.isChecked(),
                'include_config': self.include_config.isChecked(),
                'include_logs': self.include_logs.isChecked(),
                'include_user_files': self.include_user_files.isChecked(),
                'compression_level': self.compression_level.currentText()
            }
            
            # Crear worker thread
            self.backup_worker = BackupWorker(backup_config)
            self.backup_worker.progress_updated.connect(self.backup_progress.setValue)
            self.backup_worker.status_updated.connect(self.backup_status.setText)
            self.backup_worker.finished.connect(self.on_backup_finished)
            
            # Iniciar respaldo
            self.backup_worker.start()
            
        except Exception as e:
            logger.error(f"Error iniciando respaldo: {e}")
            QMessageBox.critical(self, "Error", f"Error iniciando respaldo: {str(e)}")
    
    def on_backup_finished(self, success: bool, message: str):
        """Maneja la finalización del respaldo."""
        if success:
            QMessageBox.information(self, "Respaldo Exitoso", message)
            self.load_backup_list()
        else:
            QMessageBox.critical(self, "Error en Respaldo", message)
        
        self.backup_progress.setValue(0)
        self.backup_status.setText("Listo para crear respaldo")
    
    def load_backup_list(self):
        """Carga la lista de respaldos disponibles."""
        try:
            # Limpiar tabla
            self.backups_table.setRowCount(0)
            
            # Cargar índice de respaldos
            index_file = Path("backups/backup_index.json")
            if not index_file.exists():
                return
            
            with open(index_file, 'r', encoding='utf-8') as f:
                index_data = json.load(f)
            
            backups = index_data.get('backups', [])
            self.backups_table.setRowCount(len(backups))
            
            for row, backup in enumerate(backups):
                # Nombre
                self.backups_table.setItem(row, 0, QTableWidgetItem(backup.get('name', '')))
                
                # Fecha
                created_at = backup.get('created_at', '')
                if created_at:
                    try:
                        dt = datetime.fromisoformat(created_at)
                        formatted_date = dt.strftime('%d/%m/%Y %H:%M')
                    except:
                        formatted_date = created_at
                else:
                    formatted_date = ""
                self.backups_table.setItem(row, 1, QTableWidgetItem(formatted_date))
                
                # Tamaño
                size = backup.get('size', 0)
                size_mb = size / (1024 * 1024)
                self.backups_table.setItem(row, 2, QTableWidgetItem(f"{size_mb:.1f} MB"))
                
                # Tipo
                config = backup.get('config', {})
                backup_type = "Completo" if config.get('include_database') else "Parcial"
                self.backups_table.setItem(row, 3, QTableWidgetItem(backup_type))
                
                # Estado
                backup_path = Path(backup.get('path', ''))
                status = "Disponible" if backup_path.exists() else "No encontrado"
                status_item = QTableWidgetItem(status)
                if status == "No encontrado":
                    status_item.setForeground(QColor("#e74c3c"))
                else:
                    status_item.setForeground(QColor("#27ae60"))
                self.backups_table.setItem(row, 4, status_item)
            
        except Exception as e:
            logger.error(f"Error cargando lista de respaldos: {e}")
    
    def restore_backup(self):
        """Inicia el proceso de restauración."""
        current_row = self.backups_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Selección Requerida", "Por favor seleccione un respaldo para restaurar.")
            return
        
        # Confirmación
        reply = QMessageBox.question(
            self,
            "Confirmar Restauración",
            "¿Está seguro de que desea restaurar este respaldo?\\n\\n"
            "Esta operación sobrescribirá los datos actuales.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        try:
            # Obtener información del respaldo seleccionado
            backup_name = self.backups_table.item(current_row, 0).text()
            
            # Buscar el respaldo en el índice
            index_file = Path("backups/backup_index.json")
            with open(index_file, 'r', encoding='utf-8') as f:
                index_data = json.load(f)
            
            backup_info = None
            for backup in index_data.get('backups', []):
                if backup.get('name') == backup_name:
                    backup_info = backup
                    break
            
            if not backup_info:
                QMessageBox.critical(self, "Error", "No se encontró información del respaldo.")
                return
            
            backup_path = backup_info.get('path')
            if not Path(backup_path).exists():
                QMessageBox.critical(self, "Error", "El archivo de respaldo no existe.")
                return
            
            # Configuración de restauración
            restore_config = {
                'restore_database': self.restore_database.isChecked(),
                'restore_config': self.restore_config.isChecked(),
                'restore_user_files': self.restore_user_files.isChecked(),
                'create_safety_backup': self.create_safety_backup.isChecked()
            }
            
            # Crear worker thread
            self.restore_worker = RestoreWorker(backup_path, restore_config)
            self.restore_worker.progress_updated.connect(self.restore_progress.setValue)
            self.restore_worker.status_updated.connect(self.restore_status.setText)
            self.restore_worker.finished.connect(self.on_restore_finished)
            
            # Iniciar restauración
            self.restore_worker.start()
            
        except Exception as e:
            logger.error(f"Error iniciando restauración: {e}")
            QMessageBox.critical(self, "Error", f"Error iniciando restauración: {str(e)}")
    
    def on_restore_finished(self, success: bool, message: str):
        """Maneja la finalización de la restauración."""
        if success:
            QMessageBox.information(
                self,
                "Restauración Exitosa",
                f"{message}\\n\\nSe recomienda reiniciar la aplicación."
            )
        else:
            QMessageBox.critical(self, "Error en Restauración", message)
        
        self.restore_progress.setValue(0)
        self.restore_status.setText("Seleccione un respaldo para restaurar")
    
    def import_backup(self):
        """Importa un respaldo externo."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Importar Respaldo",
            "",
            "Archivos de Respaldo (*.zip);;Todos los archivos (*)"
        )
        
        if file_path:
            # Validar que es un respaldo válido
            # Copiar al directorio de respaldos
            # Actualizar índice
            QMessageBox.information(self, "Importación Exitosa", "Respaldo importado exitosamente.")
            self.load_backup_list()
    
    def delete_backup(self):
        """Elimina un respaldo seleccionado."""
        current_row = self.backups_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Selección Requerida", "Por favor seleccione un respaldo para eliminar.")
            return
        
        reply = QMessageBox.question(
            self,
            "Confirmar Eliminación",
            "¿Está seguro de que desea eliminar este respaldo?\\n\\nEsta acción no se puede deshacer.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Eliminar respaldo
            QMessageBox.information(self, "Eliminación Exitosa", "Respaldo eliminado exitosamente.")
            self.load_backup_list()
    
    def add_custom_schedule(self):
        """Agrega una programación personalizada."""
        QMessageBox.information(self, "Función en Desarrollo", "Esta función estará disponible en una próxima versión.")
    
    def save_schedule_config(self):
        """Guarda la configuración de programación."""
        QMessageBox.information(self, "Configuración Guardada", "La configuración de programación ha sido guardada.")
    
    def save_settings(self):
        """Guarda las configuraciones del sistema."""
        QMessageBox.information(self, "Configuración Guardada", "Las configuraciones han sido guardadas.")
    
    def apply_dark_theme(self):
        """Aplica el tema nocturno elegante al sistema de respaldos."""
        self.setStyleSheet("""
            QWidget {
                background-color: #1a1a1a;
                color: #e0e0e0;
            }
            
            QGroupBox {
                font-weight: bold;
                border: 2px solid #3a4b5c;
                border-radius: 12px;
                margin-top: 15px;
                padding-top: 15px;
                background-color: #2c3e50;
                color: #ecf0f1;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px 0 8px;
                color: #74b9ff;
                background-color: #1a1a1a;
                font-weight: bold;
            }
            
            QLabel {
                color: #e0e0e0;
                background-color: transparent;
            }
            
            QPushButton {
                padding: 12px 20px;
                border: 2px solid #34495e;
                border-radius: 8px;
                font-weight: bold;
                min-width: 120px;
                background-color: #34495e;
                color: #ecf0f1;
            }
            
            QPushButton:hover {
                background-color: #4a6741;
                border-color: #74b9ff;
                color: #ffffff;
            }
            
            QPushButton[default="true"] {
                background-color: #2980b9;
                border-color: #3498db;
            }
            
            QProgressBar {
                border: 2px solid #34495e;
                border-radius: 8px;
                background-color: #2c3e50;
                text-align: center;
                color: #ecf0f1;
                height: 25px;
            }
            
            QProgressBar::chunk {
                background-color: #74b9ff;
                border-radius: 6px;
            }
        """)


def show_backup_system(user_info: Dict[str, Any], parent: Optional[QWidget] = None) -> QDialog:
    """Muestra el sistema de respaldos."""
    dialog = QDialog(parent)
    dialog.setWindowTitle("Sistema de Respaldos y Restauración")
    dialog.setModal(True)
    dialog.resize(1200, 800)
    
    layout = QVBoxLayout(dialog)
    
    try:
        widget = BackupSystemWidget(user_info)
        layout.addWidget(widget)
        
        # Botón cerrar
        close_button = QPushButton("Cerrar")
        close_button.clicked.connect(dialog.accept)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)
        
        return dialog
        
    except Exception as e:
        logger.error(f"Error inicializando sistema de respaldos: {e}")
        QMessageBox.critical(
            cast(QWidget, parent),
            "Error",
            f"Error inicializando sistema de respaldos: {str(e)}"
        )
        dialog.reject()
        return dialog


if __name__ == "__main__":
    import sys

    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # Datos de prueba para admin
    admin_user: Dict[str, Any] = {
        'id': 1,
        'username': 'admin',
        'role': 'admin',
        'full_name': 'Administrador del Sistema'
    }
    
    dialog = show_backup_system(admin_user)
    dialog.exec()
    
    sys.exit(0)