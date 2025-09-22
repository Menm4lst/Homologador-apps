"""
Sistema de configuración para el Homologador de Aplicaciones.
Maneja la configuración desde múltiples fuentes: CLI, ENV, config.json, autodetección.
"""

import os
import json
import argparse
import logging
from pathlib import Path
from typing import Optional, Dict, Any, cast

logger = logging.getLogger(__name__)


class Settings:
    """Clase para manejar toda la configuración de la aplicación."""
    
    def __init__(self):
        self.config: Dict[str, Any] = {}
        self._load_config()
    
    def _load_config(self):
        """Carga la configuración desde múltiples fuentes en orden de prioridad."""
        # 1. Configuración por defecto
        self.config = {
            "db_path": "homologador.db",
            "backups_dir": "backups/",
            "backup_retention_days": 30,
            "auto_backup": True,
            "onedrive_paths": [
                "C:\\Users\\{username}\\OneDrive",
                "C:\\Users\\{username}\\OneDrive - {organization}",
                "\\\\APPS$\\homologador"
            ]
        }
        
        # 2. Cargar desde config.json
        self._load_from_config_file()
        
        # 3. Variables de entorno
        self._load_from_environment()
        
        # 4. Argumentos CLI
        self._load_from_cli()
        
        # 5. Resolver rutas finales
        self._resolve_paths()
    
    def _load_from_config_file(self):
        """Carga configuración desde config.json."""
        config_path = Path("config.json")
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    file_config = json.load(f)
                    self.config.update(file_config)
                    logger.info(f"Configuración cargada desde {config_path}")
            except Exception as e:
                logger.warning(f"Error leyendo config.json: {e}")
    
    def _load_from_environment(self):
        """Carga configuración desde variables de entorno."""
        env_mappings = {
            "HOMOLOGADOR_DB": "db_path",
            "HOMOLOGADOR_BACKUPS": "backups_dir",
            "HOMOLOGADOR_RETENTION_DAYS": "backup_retention_days"
        }
        
        for env_var, config_key in env_mappings.items():
            value = os.getenv(env_var)
            if value:
                # Convertir tipos según sea necesario
                if config_key == "backup_retention_days":
                    try:
                        value = int(value)
                    except ValueError:
                        logger.warning(f"Valor inválido para {env_var}: {value}")
                        continue
                
                self.config[config_key] = value
                logger.info(f"Configuración desde ENV: {config_key} = {value}")
    
    def _load_from_cli(self):
        """Carga configuración desde argumentos CLI."""
        parser = argparse.ArgumentParser(description="Homologador de Aplicaciones")
        parser.add_argument("--db", help="Ruta a la base de datos SQLite")
        parser.add_argument("--backups", help="Directorio de backups")
        parser.add_argument("--debug", action="store_true", help="Habilitar modo debug")
        
        # Solo parsear argumentos conocidos para evitar conflictos con PyQt
        args, unknown = parser.parse_known_args()
        
        if args.db:
            self.config["db_path"] = args.db
            logger.info(f"DB path desde CLI: {args.db}")
        
        if args.backups:
            self.config["backups_dir"] = args.backups
            logger.info(f"Backups dir desde CLI: {args.backups}")
        
        if args.debug:
            self.config["debug"] = True
            logging.getLogger().setLevel(logging.DEBUG)
    
    def _resolve_paths(self):
        """Resuelve las rutas finales, incluyendo autodetección de OneDrive."""
        # Si db_path es relativo, intentar autodetección
        if not os.path.isabs(self.config["db_path"]):
            detected_path = self._detect_onedrive_path()
            if detected_path:
                self.config["db_path"] = os.path.join(detected_path, self.config["db_path"])
                logger.info(f"DB autodetectada en: {self.config['db_path']}")
        
        # Resolver backups_dir relativo a la ubicación de la DB
        if not os.path.isabs(self.config["backups_dir"]):
            db_dir = os.path.dirname(self.config["db_path"])
            self.config["backups_dir"] = os.path.join(db_dir, self.config["backups_dir"])
        
        # Crear directorios si no existen
        self._ensure_directories()
    
    def _detect_onedrive_path(self) -> Optional[str]:
        """Detecta automáticamente la ruta de OneDrive o carpeta compartida."""
        username = os.getenv("USERNAME", "")
        
        # Rutas a probar
        paths_to_try = []
        
        # Expandir plantillas en config
        for path_template in self.config.get("onedrive_paths", []):
            path = path_template.format(username=username, organization="*")
            paths_to_try.append(path)
        
        # Rutas adicionales comunes
        if username:
            paths_to_try.extend([
                f"C:\\Users\\{username}\\OneDrive\\Documentos\\Homologador",
                f"C:\\Users\\{username}\\OneDrive\\Documents\\Homologador",
                f"C:\\Users\\{username}\\OneDrive",
            ])
        
        # Rutas de red
        paths_to_try.extend([
            "\\\\APPS$\\homologador",
            "\\\\shared\\homologador",
        ])
        
        for path in paths_to_try:
            try:
                # Para rutas con wildcard, usar glob
                if "*" in path:
                    import glob
                    matches = glob.glob(cast(str, path))
                    if matches and os.path.isdir(cast(str, matches[0])):
                        logger.info(f"OneDrive detectado (glob): {matches[0]}")
                        return matches[0]
                elif os.path.isdir(cast(str, path)):
                    logger.info(f"OneDrive detectado: {path}")
                    return path
            except Exception as e:
                logger.debug(f"Error probando ruta {path}: {e}")
        
        logger.warning("No se pudo detectar automáticamente OneDrive")
        return None
    
    def _ensure_directories(self):
        """Crea los directorios necesarios si no existen."""
        dirs_to_create = [
            os.path.dirname(self.config["db_path"]),
            self.config["backups_dir"]
        ]
        
        for dir_path in dirs_to_create:
            if dir_path:
                try:
                    Path(dir_path).mkdir(parents=True, exist_ok=True)
                    logger.debug(f"Directorio asegurado: {dir_path}")
                except Exception as e:
                    logger.error(f"Error creando directorio {dir_path}: {e}")
    
    def get_db_path(self) -> str:
        """Retorna la ruta completa de la base de datos."""
        return self.config["db_path"]
    
    def get_backups_dir(self) -> str:
        """Retorna el directorio de backups."""
        return self.config["backups_dir"]
    
    def get_backup_retention_days(self) -> int:
        """Retorna los días de retención de backups."""
        return self.config.get("backup_retention_days", 30)
    
    def is_auto_backup_enabled(self) -> bool:
        """Retorna si el backup automático está habilitado."""
        return self.config.get("auto_backup", True)
    
    def is_debug_enabled(self) -> bool:
        """Retorna si el modo debug está habilitado."""
        return self.config.get("debug", False)
    
    def get_config(self) -> Dict[str, Any]:
        """Retorna toda la configuración."""
        return self.config.copy()


# Instancia global de configuración
settings = Settings()


def get_settings() -> Settings:
    """Retorna la instancia global de configuración."""
    return settings


def setup_logging():
    """Configura el logging de la aplicación."""
    level = logging.DEBUG if settings.is_debug_enabled() else logging.INFO
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('homologador.log', encoding='utf-8')
        ]
    )
    
    logger.info("Sistema de logging configurado")


if __name__ == "__main__":
    # Test del sistema de configuración
    setup_logging()
    config = get_settings()
    
    print("=== Configuración del Homologador ===")
    print(f"DB Path: {config.get_db_path()}")
    print(f"Backups Dir: {config.get_backups_dir()}")
    print(f"Retention Days: {config.get_backup_retention_days()}")
    print(f"Auto Backup: {config.is_auto_backup_enabled()}")
    print(f"Debug Mode: {config.is_debug_enabled()}")