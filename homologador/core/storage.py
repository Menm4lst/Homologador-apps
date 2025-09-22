"""
Core de almacenamiento para el Homologador de Aplicaciones.
Maneja la base de datos SQLite con WAL mode, file locking y backups automáticos.
"""

import sqlite3
import os
import shutil
import json
import logging
import portalocker
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple, cast
from contextlib import contextmanager

from .settings import get_settings

logger = logging.getLogger(__name__)


class DatabaseError(Exception):
    """Excepción personalizada para errores de base de datos."""
    pass


class DatabaseManager:
    """Administrador de la base de datos SQLite con funcionalidades avanzadas."""
    
    def __init__(self):
        self.settings = get_settings()
        self.db_path = self.settings.get_db_path()
        self.backups_dir = self.settings.get_backups_dir()
        self._lock_file = None
        self._connection = None
        
    def initialize_database(self):
        """Inicializa la base de datos creando el esquema si no existe."""
        try:
            # Crear backup antes de cualquier operación
            if os.path.exists(self.db_path):
                self.create_backup("pre_init")
            
            with self.get_connection() as conn:
                # Cargar y ejecutar el esquema
                schema_path = Path(__file__).parent.parent / "data" / "schema.sql"
                with open(schema_path, 'r', encoding='utf-8') as f:
                    schema_sql = f.read()
                
                conn.executescript(schema_sql)
                conn.commit()
                
                logger.info("Base de datos inicializada correctamente")
                
                # Aplicar migraciones
                self._apply_migrations(conn)
                
        except Exception as e:
            logger.error(f"Error inicializando base de datos: {e}")
            raise DatabaseError(f"Error inicializando base de datos: {e}")
    
    def _apply_migrations(self, conn):
        """Aplica las migraciones disponibles en la carpeta de migraciones."""
        try:
            migrations_dir = Path(__file__).parent.parent / "data" / "migrations"
            if not migrations_dir.exists():
                migrations_dir.mkdir(parents=True, exist_ok=True)
                return
            
            for migration_file in sorted(migrations_dir.glob("*.sql")):
                logger.info(f"Aplicando migración: {migration_file.name}")
                with open(migration_file, 'r', encoding='utf-8') as f:
                    migration_sql = f.read()
                
                try:
                    conn.executescript(migration_sql)
                    conn.commit()
                    logger.info(f"Migración {migration_file.name} aplicada con éxito")
                except sqlite3.Error as e:
                    # Si falla una migración, logueamos pero seguimos con las demás
                    logger.warning(f"Error al aplicar migración {migration_file.name}: {e}")
                    
        except Exception as e:
            logger.error(f"Error al aplicar migraciones: {e}")
    
    @contextmanager
    def get_connection(self):
        """Context manager para obtener una conexión con lock automático."""
        lock_acquired = False
        conn = None
        
        try:
            # Adquirir lock del archivo
            self._acquire_file_lock()
            lock_acquired = True
            
            # Conectar a la base de datos
            conn = sqlite3.connect(
                self.db_path,
                timeout=30.0,
                check_same_thread=False
            )
            
            # Configurar la conexión
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON")
            conn.execute("PRAGMA journal_mode = WAL")
            conn.execute("PRAGMA busy_timeout = 30000")
            
            yield conn
            
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Error en conexión de base de datos: {e}")
            raise DatabaseError(f"Error de base de datos: {e}")
            
        finally:
            if conn:
                conn.close()
            if lock_acquired:
                self._release_file_lock()
    
    def _acquire_file_lock(self):
        """Adquiere un lock exclusivo del archivo de base de datos."""
        try:
            lock_path = f"{self.db_path}.lock"
            self._lock_file = open(lock_path, 'w')
            portalocker.lock(self._lock_file, portalocker.LOCK_EX | portalocker.LOCK_NB)
            logger.debug("File lock adquirido")
            
        except portalocker.LockException:
            if self._lock_file:
                self._lock_file.close()
                self._lock_file = None
            raise DatabaseError("La base de datos está siendo usada por otra instancia")
        except Exception as e:
            if self._lock_file:
                self._lock_file.close()
                self._lock_file = None
            raise DatabaseError(f"Error adquiriendo lock: {e}")
    
    def _release_file_lock(self):
        """Libera el lock del archivo de base de datos."""
        if self._lock_file:
            try:
                portalocker.unlock(self._lock_file)
                self._lock_file.close()
                
                # Eliminar archivo de lock
                lock_path = f"{self.db_path}.lock"
                if os.path.exists(lock_path):
                    os.remove(lock_path)
                    
                logger.debug("File lock liberado")
            except Exception as e:
                logger.warning(f"Error liberando lock: {e}")
            finally:
                self._lock_file = None
    
    def create_backup(self, suffix: Optional[str] = None) -> Optional[str]:
        """Crea un backup de la base de datos."""
        if not os.path.exists(self.db_path):
            logger.warning("No se puede hacer backup: base de datos no existe")
            return None
        
        try:
            # Asegurar directorio de backups
            Path(self.backups_dir).mkdir(parents=True, exist_ok=True)
            
            # Generar nombre del backup
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            if suffix:
                backup_name = f"homologador_backup_{timestamp}_{suffix}.db"
            else:
                backup_name = f"homologador_backup_{timestamp}.db"
            
            backup_path = os.path.join(self.backups_dir, backup_name)
            
            # Copiar archivo
            shutil.copy2(self.db_path, backup_path)
            
            logger.info(f"Backup creado: {backup_path}")
            
            # Limpiar backups antiguos
            self._cleanup_old_backups()
            
            return backup_path
            
        except Exception as e:
            logger.error(f"Error creando backup: {e}")
            return None
    
    def _cleanup_old_backups(self):
        """Elimina backups más antiguos que el período de retención."""
        try:
            retention_days = self.settings.get_backup_retention_days()
            cutoff_date = datetime.now() - timedelta(days=retention_days)
            
            backups_path = Path(self.backups_dir)
            if not backups_path.exists():
                return
            
            deleted_count = 0
            for backup_file in backups_path.glob("homologador_backup_*.db"):
                file_time = datetime.fromtimestamp(backup_file.stat().st_mtime)
                if file_time < cutoff_date:
                    backup_file.unlink()
                    deleted_count += 1
            
            if deleted_count > 0:
                logger.info(f"Eliminados {deleted_count} backups antiguos")
                
        except Exception as e:
            logger.warning(f"Error limpiando backups antiguos: {e}")
    
    def execute_query(self, query: str, params: Optional[Tuple[Any, ...]] = None) -> List[sqlite3.Row]:
        """Ejecuta una consulta SELECT y retorna los resultados."""
        with self.get_connection() as conn:
            if params:
                cursor = conn.execute(query, params)
            else:
                cursor = conn.execute(query)
            return cursor.fetchall()
    
    def execute_non_query(self, query: str, params: Optional[Tuple[Any, ...]] = None) -> int:
        """Ejecuta una consulta INSERT/UPDATE/DELETE y retorna rowcount."""
        # Crear backup automático antes de modificaciones
        if self.settings.is_auto_backup_enabled() and any(
            keyword in query.upper() for keyword in ['INSERT', 'UPDATE', 'DELETE']
        ):
            self.create_backup("auto")
        
        with self.get_connection() as conn:
            if params:
                cursor = conn.execute(query, params)
            else:
                cursor = conn.execute(query)
            conn.commit()
            return cursor.rowcount
    
    def execute_insert(self, query: str, params: Optional[Tuple[Any, ...]] = None) -> int:
        """Ejecuta un INSERT y retorna el ID del registro insertado."""
        # Crear backup automático
        if self.settings.is_auto_backup_enabled():
            self.create_backup("auto")
        
        with self.get_connection() as conn:
            if params:
                cursor = conn.execute(query, params)
            else:
                cursor = conn.execute(query)
            conn.commit()
            return cursor.lastrowid or 0


class HomologationRepository:
    """Repositorio para operaciones CRUD de homologaciones."""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def create(self, homologation_data: Dict[str, Any]) -> int:
        """Crea una nueva homologación."""
        query = """
        INSERT INTO homologations 
        (real_name, logical_name, kb_url, kb_sync, homologation_date, 
         has_previous_versions, repository_location, details, created_by)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        params = (
            homologation_data['real_name'],
            homologation_data.get('logical_name'),
            homologation_data.get('kb_url'),
            homologation_data.get('kb_sync', False),
            homologation_data.get('homologation_date'),
            homologation_data.get('has_previous_versions', False),
            homologation_data.get('repository_location'),
            homologation_data.get('details'),
            homologation_data['created_by']
        )
        
        return self.db.execute_insert(query, params)
    
    def get_by_id(self, homologation_id: int) -> Optional[sqlite3.Row]:
        """Obtiene una homologación por ID."""
        query = "SELECT * FROM v_homologations_with_user WHERE id = ?"
        results = self.db.execute_query(query, (homologation_id,))
        return results[0] if results else None
    
    def get_all(self, filters: Optional[Dict[str, Any]] = None) -> List[sqlite3.Row]:
        """Obtiene todas las homologaciones con filtros opcionales."""
        query = "SELECT * FROM v_homologations_with_user"
        params: List[Any] = []
        where_clauses = []
        
        if filters:
            if filters.get('real_name'):
                where_clauses.append("real_name LIKE ?")
                params.append(f"%{filters['real_name']}%")
            
            if filters.get('logical_name'):
                where_clauses.append("logical_name LIKE ?")
                params.append(f"%{filters['logical_name']}%")
            
            if filters.get('date_from'):
                where_clauses.append("homologation_date >= ?")
                params.append(filters['date_from'])
            
            if filters.get('date_to'):
                where_clauses.append("homologation_date <= ?")
                params.append(filters['date_to'])
            
            if filters.get('repository_location'):
                where_clauses.append("repository_location = ?")
                params.append(filters['repository_location'])
        
        if where_clauses:
            query += " WHERE " + " AND ".join(cast(List[str], where_clauses))
        
        query += " ORDER BY created_at DESC"
        
        return self.db.execute_query(query, tuple(params))
    
    def update(self, homologation_id: int, update_data: Dict[str, Any]) -> bool:
        """Actualiza una homologación."""
        # Construir query dinámicamente basado en los campos a actualizar
        set_clauses = []
        params: List[Any] = []
        
        updatable_fields = [
            'real_name', 'logical_name', 'kb_url', 'kb_sync', 'homologation_date',
            'has_previous_versions', 'repository_location', 'details'
        ]
        
        for field in updatable_fields:
            if field in update_data:
                set_clauses.append(f"{field} = ?")
                params.append(update_data[field])
        
        if not set_clauses:
            return False
        
        query = f"UPDATE homologations SET {', '.join(cast(List[str], set_clauses))} WHERE id = ?"
        params.append(homologation_id)
        
        return self.db.execute_non_query(query, tuple(params)) > 0
    
    def delete(self, homologation_id: int) -> bool:
        """Elimina una homologación."""
        query = "DELETE FROM homologations WHERE id = ?"
        return self.db.execute_non_query(query, (homologation_id,)) > 0
    
    def search(self, search_term: str) -> List[sqlite3.Row]:
        """Busca homologaciones por término de búsqueda."""
        query = """
        SELECT * FROM v_homologations_with_user 
        WHERE real_name LIKE ? 
           OR logical_name LIKE ? 
           OR details LIKE ?
           OR kb_url LIKE ?
        ORDER BY 
            CASE 
                WHEN real_name LIKE ? THEN 1
                WHEN logical_name LIKE ? THEN 2
                ELSE 3
            END,
            created_at DESC
        """
        
        search_pattern = f"%{search_term}%"
        params = (search_pattern, search_pattern, search_pattern, search_pattern,
                 search_pattern, search_pattern)
        
        return self.db.execute_query(query, params)


class UserRepository:
    """Repositorio para operaciones CRUD de usuarios."""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def create(self, user_data: Dict[str, Any]) -> int:
        """Crea un nuevo usuario."""
        query = """
        INSERT INTO users 
        (username, password_hash, role, full_name, email, must_change_password)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        
        params = (
            user_data['username'],
            user_data['password_hash'],
            user_data['role'],
            user_data.get('full_name'),
            user_data.get('email'),
            user_data.get('must_change_password', False)
        )
        
        return self.db.execute_insert(query, params)
    
    def get_by_username(self, username: str) -> Optional[sqlite3.Row]:
        """Obtiene un usuario por nombre de usuario."""
        query = "SELECT * FROM users WHERE username = ? AND is_active = 1"
        results = self.db.execute_query(query, (username,))
        return results[0] if results else None
    
    def get_by_id(self, user_id: int) -> Optional[sqlite3.Row]:
        """Obtiene un usuario por ID."""
        query = "SELECT * FROM users WHERE id = ?"
        results = self.db.execute_query(query, (user_id,))
        return results[0] if results else None
    
    def update_password(self, user_id: int, new_password_hash: str) -> bool:
        """Actualiza la contraseña de un usuario."""
        query = """
        UPDATE users 
        SET password_hash = ?, must_change_password = 0 
        WHERE id = ?
        """
        return self.db.execute_non_query(query, (new_password_hash, user_id)) > 0
    
    def update_last_login(self, user_id: int) -> bool:
        """Actualiza la fecha del último login."""
        query = "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?"
        return self.db.execute_non_query(query, (user_id,)) > 0
    
    def get_all_active(self) -> List[sqlite3.Row]:
        """Obtiene todos los usuarios activos."""
        query = "SELECT * FROM users WHERE is_active = 1 ORDER BY username"
        return self.db.execute_query(query)


class AuditRepository:
    """Repositorio para consultas de auditoría."""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def log_action(self, user_id: int, action: str, table_name: Optional[str] = None,
                   record_id: Optional[int] = None, old_values: Optional[Dict] = None,
                   new_values: Optional[Dict] = None, ip_address: Optional[str] = None) -> int:
        """Registra una acción en el log de auditoría."""
        query = """
        INSERT INTO audit_logs 
        (user_id, action, table_name, record_id, old_values, new_values, ip_address)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        
        params = (
            user_id,
            action,
            table_name,
            record_id,
            json.dumps(old_values) if old_values else None,
            json.dumps(new_values) if new_values else None,
            ip_address
        )
        
        return self.db.execute_insert(query, params)
    
    def get_audit_trail(self, filters: Optional[Dict[str, Any]] = None) -> List[sqlite3.Row]:
        """Obtiene el trail de auditoría con filtros opcionales."""
        query = "SELECT * FROM v_audit_with_user"
        params: List[Any] = []
        where_clauses = []
        
        if filters:
            if filters.get('user_id'):
                where_clauses.append("user_id = ?")
                params.append(filters['user_id'])
            
            if filters.get('action'):
                where_clauses.append("action = ?")
                params.append(filters['action'])
            
            if filters.get('table_name'):
                where_clauses.append("table_name = ?")
                params.append(filters['table_name'])
            
            if filters.get('date_from'):
                where_clauses.append("timestamp >= ?")
                params.append(filters['date_from'])
            
            if filters.get('date_to'):
                where_clauses.append("timestamp <= ?")
                params.append(filters['date_to'])
        
        if where_clauses:
            query += " WHERE " + " AND ".join(cast(List[str], where_clauses))
        
        query += " ORDER BY timestamp DESC LIMIT 1000"
        
        return self.db.execute_query(query, tuple(params))


# Instancia global del administrador de base de datos
_db_manager = None

def get_database_manager() -> DatabaseManager:
    """Retorna la instancia global del administrador de base de datos."""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
        _db_manager.initialize_database()
    return _db_manager


def get_homologation_repository() -> HomologationRepository:
    """Retorna una instancia del repositorio de homologaciones."""
    return HomologationRepository(get_database_manager())


def get_user_repository() -> UserRepository:
    """Retorna una instancia del repositorio de usuarios."""
    return UserRepository(get_database_manager())


def get_audit_repository() -> AuditRepository:
    """Retorna una instancia del repositorio de auditoría."""
    return AuditRepository(get_database_manager())


if __name__ == "__main__":
    # Test del sistema de almacenamiento
    from .settings import setup_logging
    
    setup_logging()
    
    print("=== Test del Sistema de Almacenamiento ===")
    
    try:
        # Inicializar base de datos
        db_manager = get_database_manager()
        print(f"Base de datos inicializada en: {db_manager.db_path}")
        
        # Test de repositorios
        user_repo = get_user_repository()
        homolog_repo = get_homologation_repository()
        audit_repo = get_audit_repository()
        
        print("Repositorios creados exitosamente")
        
        # Test de backup
        backup_path = db_manager.create_backup("test")
        if backup_path:
            print(f"Backup de prueba creado: {backup_path}")
        
        print("=== Test completado exitosamente ===")
        
    except Exception as e:
        print(f"Error en test: {e}")
        logger.error(f"Error en test: {e}")