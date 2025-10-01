"""
Sistema de autenticación y gestión de usuarios para el Homologador.
Maneja roles, contraseñas con Argon2 y seed de datos inicial.
"""



from datetime import datetime
from typing import Any, Dict, Optional, cast
import logging

from argon2 import PasswordHasher
from argon2.exceptions import HashingError, VerifyMismatchError

from ..core.storage import get_audit_repository, get_user_repository
logger = logging.getLogger(__name__)


class AuthenticationError(Exception):
    """Excepción para errores de autenticación."""
    pass


class AuthService:
    """Servicio de autenticación y gestión de usuarios."""
    
    def __init__(self):
        self.password_hasher = PasswordHasher()
        self.user_repo = get_user_repository()
        self.audit_repo = get_audit_repository()
        self.current_user = None
    
    def hash_password(self, password: str) -> str:
        """Genera un hash seguro de la contraseña usando Argon2."""
        try:
            return self.password_hasher.hash(password)
        except HashingError as e:
            logger.error(f"Error hasheando contraseña: {e}")
            raise AuthenticationError("Error procesando contraseña")
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verifica si una contraseña coincide con su hash."""
        try:
            self.password_hasher.verify(hashed_password, password)
            return True
        except VerifyMismatchError:
            return False
        except Exception as e:
            logger.error(f"Error verificando contraseña: {e}")
            return False
    
    def authenticate(self, username: str, password: str, ip_address: Optional[str] = None) -> Dict[str, Any]:
        """
        Autentica un usuario y retorna información de la sesión.
        
        Returns:
            Dict con información del usuario si exitoso, None si falla
        """
        try:
            # Buscar usuario
            user = self.user_repo.get_by_username(username)
            if not user:
                logger.warning(f"Intento de login con usuario inexistente: {username}")
                self.audit_repo.log_action(
                    user_id=0,  # Usuario especial para intentos fallidos
                    action="LOGIN_FAILED",
                    new_values={"username": username, "reason": "user_not_found"},
                    ip_address=ip_address
                )
                raise AuthenticationError("Usuario o contraseña incorrectos")
            
            # Verificar contraseña
            if not self.verify_password(password, user['password_hash']):
                logger.warning(f"Contraseña incorrecta para usuario: {username}")
                self.audit_repo.log_action(
                    user_id=user['id'],
                    action="LOGIN_FAILED",
                    new_values={"username": username, "reason": "wrong_password"},
                    ip_address=ip_address
                )
                raise AuthenticationError("Usuario o contraseña incorrectos")
            
            # Usuario autenticado exitosamente
            self.current_user = dict(user)
            
            # Actualizar último login
            self.user_repo.update_last_login(user['id'])
            
            # Log de login exitoso
            self.audit_repo.log_action(
                user_id=user['id'],
                action="LOGIN_SUCCESS",
                new_values={"username": username},
                ip_address=ip_address
            )
            
            logger.info(f"Login exitoso para usuario: {username}")
            
            return {
                'user_id': user['id'],
                'username': user['username'],
                'role': user['role'],
                'full_name': user['full_name'],
                'must_change_password': bool(user['must_change_password']),
                'last_login': user['last_login']
            }
            
        except AuthenticationError:
            raise
        except Exception as e:
            logger.error(f"Error durante autenticación: {e}")
            raise AuthenticationError("Error interno durante autenticación")
    
    def logout(self, user_id: Optional[int] = None, ip_address: Optional[str] = None):
        """Cierra la sesión del usuario actual."""
        if self.current_user:
            self.audit_repo.log_action(
                user_id=user_id or self.current_user['id'],
                action="LOGOUT",
                ip_address=ip_address
            )
            logger.info(f"Logout para usuario: {self.current_user['username']}")
            self.current_user = None
    
    def change_password(self, user_id: int, old_password: str, new_password: str, 
                       ip_address: Optional[str] = None) -> bool:
        """Cambia la contraseña de un usuario."""
        try:
            # Obtener usuario actual
            user = self.user_repo.get_by_id(user_id)
            if not user:
                raise AuthenticationError("Usuario no encontrado")
            
            # Verificar contraseña actual (a menos que sea primer cambio obligatorio)
            if not user['must_change_password']:
                if not self.verify_password(old_password, user['password_hash']):
                    raise AuthenticationError("Contraseña actual incorrecta")
            
            # Validar nueva contraseña
            self._validate_password_strength(new_password)
            
            # Generar nuevo hash
            new_hash = self.hash_password(new_password)
            
            # Actualizar en base de datos
            success = self.user_repo.update_password(user_id, new_hash)
            
            if success:
                # Log de cambio de contraseña
                self.audit_repo.log_action(
                    user_id=user_id,
                    action="PASSWORD_CHANGED",
                    new_values={"forced": user['must_change_password']},
                    ip_address=ip_address
                )
                
                logger.info(f"Contraseña cambiada para usuario ID: {user_id}")
                return True
            else:
                raise AuthenticationError("Error actualizando contraseña")
                
        except AuthenticationError:
            raise
        except Exception as e:
            logger.error(f"Error cambiando contraseña: {e}")
            raise AuthenticationError("Error interno cambiando contraseña")
    
    def _validate_password_strength(self, password: str):
        """Valida la fortaleza de una contraseña."""
        if len(password) < 6:
            raise AuthenticationError("La contraseña debe tener al menos 6 caracteres")
        
        # Aquí se pueden agregar más validaciones según políticas de seguridad
        # Ejemplo: requerir mayúsculas, números, símbolos, etc.
    
    def create_user(self, username: str, password: str, role: str, 
                   full_name: Optional[str] = None, email: Optional[str] = None,
                   must_change_password: bool = False, creator_id: Optional[int] = None) -> int:
        """Crea un nuevo usuario."""
        try:
            # Validar role
            if role not in ['admin', 'editor', 'viewer']:
                raise AuthenticationError("Rol inválido")
            
            # Validar fortaleza de contraseña
            self._validate_password_strength(password)
            
            # Hash de contraseña
            password_hash = self.hash_password(password)
            
            # Crear usuario
            user_data = {
                'username': username,
                'password_hash': password_hash,
                'role': role,
                'full_name': full_name,
                'email': email,
                'must_change_password': must_change_password
            }
            
            user_id = self.user_repo.create(cast(Dict[str, Any], user_data))
            
            # Log de creación de usuario
            if creator_id:
                self.audit_repo.log_action(
                    user_id=creator_id,
                    action="USER_CREATED",
                    table_name="users",
                    record_id=user_id,
                    new_values={
                        'username': username,
                        'role': role,
                        'full_name': full_name
                    }
                )
            
            logger.info(f"Usuario creado: {username} (ID: {user_id})")
            return user_id
            
        except Exception as e:
            logger.error(f"Error creando usuario: {e}")
            raise AuthenticationError(f"Error creando usuario: {e}")
    
    def has_permission(self, action: str, role: Optional[str] = None) -> bool:
        """
        Verifica si el usuario actual tiene permisos para una acción.
        
        Args:
            action: 'create', 'read', 'update', 'delete'
            role: rol a verificar (por defecto usa el usuario actual)
        """
        if not role and self.current_user:
            role = self.current_user['role']
        
        if not role:
            return False
        
        permissions = {
            'admin': ['create', 'read', 'update', 'delete'],
            'editor': ['create', 'read', 'update'],
            'viewer': ['read']
        }
        
        return action in permissions.get(role, [])
    
    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """Retorna información del usuario actualmente autenticado."""
        return self.current_user.copy() if self.current_user else None
    
    def is_authenticated(self) -> bool:
        """Verifica si hay un usuario autenticado."""
        return self.current_user is not None


def create_seed_data():
    """Crea los datos iniciales (seed) para la aplicación."""
    try:
        auth_service = AuthService()
        user_repo = get_user_repository()
        audit_repo = get_audit_repository()
        
        # Verificar si ya existe el usuario admin
        existing_admin = user_repo.get_by_username('admin')
        if existing_admin:
            logger.info("Usuario admin ya existe, omitiendo seed")
            return
        
        # Crear usuario administrador por defecto
        admin_user_data = {
            'username': 'admin',
            'password_hash': auth_service.hash_password('admin123'),
            'role': 'admin',
            'full_name': 'Administrador del Sistema',
            'email': 'admin@empresa.com',
            'must_change_password': True  # Forzar cambio en primer login
        }
        
        admin_id = user_repo.create(cast(Dict[str, Any], admin_user_data))
        
        # Log de creación del seed
        audit_repo.log_action(
            user_id=admin_id,
            action="SEED_DATA_CREATED",
            new_values={
                'description': 'Datos iniciales creados',
                'admin_user_created': True
            }
        )
        
        logger.info(f"Seed data creado exitosamente. Usuario admin ID: {admin_id}")
        print("=" * 50)
        print("DATOS INICIALES CREADOS")
        print("=" * 50)
        print("Usuario: admin")
        print("Contraseña: admin123")
        print("¡IMPORTANTE: Cambie la contraseña en el primer login!")
        print("=" * 50)
        
    except Exception as e:
        logger.error(f"Error creando seed data: {e}")
        raise


# Instancia global del servicio de autenticación
_auth_service = None

def get_auth_service() -> AuthService:
    """Retorna la instancia global del servicio de autenticación."""
    global _auth_service
    if _auth_service is None:
        _auth_service = AuthService()
    return _auth_service


if __name__ == "__main__":
    # Test del sistema de autenticación
    

    from core.settings import setup_logging
    setup_logging()
    
    print("=== Test del Sistema de Autenticación ===")
    
    try:
        # Crear seed data
        create_seed_data()
        
        # Test de autenticación
        auth = get_auth_service()
        
        print("\n--- Test de Login ---")
        user_info = auth.authenticate('admin', 'admin123')
        print(f"Login exitoso: {user_info}")
        
        print("\n--- Test de Permisos ---")
        print(f"Puede crear: {auth.has_permission('create')}")
        print(f"Puede eliminar: {auth.has_permission('delete')}")
        
        print("\n--- Test de Cambio de Contraseña ---")
        # auth.change_password(user_info['user_id'], 'admin123', 'nueva_password123')
        # print("Contraseña cambiada exitosamente")
        
        auth.logout(user_info['user_id'])
        print("Logout exitoso")
        
        print("\n=== Test completado exitosamente ===")
        
    except Exception as e:
        print(f"Error en test: {e}")
        logger.error(f"Error en test: {e}")