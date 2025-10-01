"""
Módulo de autenticación y manejo de contraseñas.

Proporciona funciones para:
- Hash de contraseñas de forma segura
- Generación de contraseñas aleatorias
- Validación de contraseñas
- Gestión de sesiones de usuario
"""


from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, cast
import logging

import hashlib
import secrets
import string
logger = logging.getLogger(__name__)


def hash_password(password: str) -> str:
    """
    Genera un hash seguro de la contraseña usando SHA-256 con salt.
    
    Args:
        password: Contraseña en texto plano
        
    Returns:
        Hash de la contraseña con salt incluido
    """
    # Generar salt aleatorio
    salt = secrets.token_hex(32)
    
    # Crear hash con salt
    password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    
    # Retornar hash con salt concatenado
    return f"{salt}:{password_hash}"


def verify_password(password: str, hashed_password: str) -> bool:
    """
    Verifica si una contraseña coincide con su hash.
    
    Args:
        password: Contraseña en texto plano
        hashed_password: Hash almacenado (puede ser Argon2, SHA-256 con salt, o SHA-256 simple)
        
    Returns:
        True si la contraseña coincide, False en caso contrario
    """
    try:
        # Verificar si es hash de Argon2
        if hashed_password.startswith('$argon2'):
            try:
                import argon2
                ph = argon2.PasswordHasher()
                ph.verify(hashed_password, password)
                return True
            except ImportError:
                logger.warning("Argon2 no disponible, intentando con passlib")
                try:
                    from passlib.hash import argon2
                    return argon2.verify(password, hashed_password)
                except ImportError:
                    logger.error("No se puede verificar hash Argon2: librerías no disponibles")
                    return False
            except Exception as e:
                logger.debug(f"Hash Argon2 no coincide: {e}")
                return False
        
        # Hash SHA-256 con salt (formato: salt:hash)
        elif ':' in hashed_password:
            salt, stored_hash = hashed_password.split(':', 1)
            password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
            return password_hash == stored_hash
        
        # Hash SHA-256 simple (sin salt) - compatibilidad con versiones antiguas
        else:
            simple_hash = hashlib.sha256(password.encode()).hexdigest()
            return simple_hash == hashed_password
        
    except Exception as e:
        logger.error(f"Error verificando contraseña: {e}")
        return False


def generate_password(length: int = 12, include_symbols: bool = True) -> str:
    """
    Genera una contraseña aleatoria segura.
    
    Args:
        length: Longitud de la contraseña (mínimo 8)
        include_symbols: Si incluir símbolos especiales
        
    Returns:
        Contraseña generada
    """
    if length < 8:
        length = 8
    
    # Caracteres disponibles
    lowercase = string.ascii_lowercase
    uppercase = string.ascii_uppercase
    digits = string.digits
    symbols = "!@#$%^&*()_+-=[]{}|;:,.<>?" if include_symbols else ""
    
    # Asegurar al menos un caracter de cada tipo
    password_chars = [
        secrets.choice(lowercase),
        secrets.choice(uppercase),
        secrets.choice(digits)
    ]
    
    if include_symbols:
        password_chars.append(secrets.choice(symbols))
    
    # Completar la longitud restante
    all_chars = lowercase + uppercase + digits + symbols
    for _ in range(length - len(password_chars)):
        password_chars.append(secrets.choice(all_chars))
    
    # Mezclar caracteres
    secrets.SystemRandom().shuffle(password_chars)
    
    return ''.join(password_chars)


def validate_password_strength(password: str) -> Dict[str, Any]:
    """
    Valida la fortaleza de una contraseña.
    
    Args:
        password: Contraseña a validar
        
    Returns:
        Diccionario con información de validación
    """
    result: Dict[str, Any] = {
        'valid': False,
        'score': 0,
        'strength': 'Muy Débil',
        'issues': [],
        'suggestions': []
    }
    
    if not password:
        result['issues'].append("La contraseña no puede estar vacía")
        return result
    
    # Verificar longitud mínima
    if len(password) < 8:
        result['issues'].append("Debe tener al menos 8 caracteres")
    else:
        result['score'] += 1
        if len(password) >= 12:
            result['score'] += 1
    
    # Verificar tipos de caracteres
    has_lower = any(c.islower() for c in password)
    has_upper = any(c.isupper() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_symbol = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
    
    if has_lower:
        result['score'] += 1
    else:
        result['issues'].append("Debe incluir letras minúsculas")
        result['suggestions'].append("Agregue letras minúsculas (a-z)")
    
    if has_upper:
        result['score'] += 1
    else:
        result['issues'].append("Debe incluir letras mayúsculas")
        result['suggestions'].append("Agregue letras mayúsculas (A-Z)")
    
    if has_digit:
        result['score'] += 1
    else:
        result['issues'].append("Debe incluir números")
        result['suggestions'].append("Agregue números (0-9)")
    
    if has_symbol:
        result['score'] += 1
    else:
        result['suggestions'].append("Considere agregar símbolos (!@#$%^&*)")
    
    # Verificar patrones comunes
    common_patterns = ['123', 'abc', 'password', 'admin', 'user', 'qwerty']
    if any(pattern in password.lower() for pattern in common_patterns):
        result['issues'].append("Evite patrones comunes")
        result['score'] = max(0, result['score'] - 1)
    
    # Determinar fortaleza
    if result['score'] <= 2:
        result['strength'] = 'Muy Débil'
    elif result['score'] == 3:
        result['strength'] = 'Débil'
    elif result['score'] == 4:
        result['strength'] = 'Media'
    elif result['score'] == 5:
        result['strength'] = 'Fuerte'
    else:
        result['strength'] = 'Muy Fuerte'
    
    # La contraseña es válida si tiene score >= 4 y no hay issues críticos
    issues_list = cast(List[str], result.get('issues', []))
    result['valid'] = result['score'] >= 4 and len(issues_list) == 0
    
    return result


class SessionManager:
    """Maneja las sesiones de usuario."""
    
    def __init__(self):
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.session_timeout = timedelta(hours=8)  # 8 horas por defecto
    
    def create_session(self, user_id: int, username: str) -> str:
        """
        Crea una nueva sesión para el usuario.
        
        Args:
            user_id: ID del usuario
            username: Nombre de usuario
            
        Returns:
            Token de sesión
        """
        session_token = secrets.token_urlsafe(32)
        
        self.sessions[session_token] = {
            'user_id': user_id,
            'username': username,
            'created_at': datetime.now(),
            'last_activity': datetime.now(),
            'is_active': True
        }
        
        logger.info(f"Sesión creada para usuario: {username}")
        return session_token
    
    def validate_session(self, session_token: str) -> Optional[Dict[str, Any]]:
        """
        Valida un token de sesión.
        
        Args:
            session_token: Token a validar
            
        Returns:
            Información de sesión si es válida, None en caso contrario
        """
        if session_token not in self.sessions:
            return None
        
        session = self.sessions[session_token]
        
        # Verificar si la sesión ha expirado
        if datetime.now() - session['last_activity'] > self.session_timeout:
            self.invalidate_session(session_token)
            return None
        
        # Verificar si la sesión está activa
        if not session.get('is_active', False):
            return None
        
        # Actualizar última actividad
        session['last_activity'] = datetime.now()
        
        return session.copy()
    
    def invalidate_session(self, session_token: str) -> bool:
        """
        Invalida una sesión.
        
        Args:
            session_token: Token de sesión a invalidar
            
        Returns:
            True si se invalidó exitosamente
        """
        if session_token in self.sessions:
            username = self.sessions[session_token].get('username', 'unknown')
            del self.sessions[session_token]
            logger.info(f"Sesión invalidada para usuario: {username}")
            return True
        return False
    
    def cleanup_expired_sessions(self) -> int:
        """
        Limpia sesiones expiradas.
        
        Returns:
            Número de sesiones eliminadas
        """
        expired_tokens: List[str] = []
        current_time = datetime.now()
        
        for token, session in self.sessions.items():
            if current_time - session['last_activity'] > self.session_timeout:
                expired_tokens.append(token)
        
        for token in expired_tokens:
            self.invalidate_session(cast(str, token))
        
        if expired_tokens:
            logger.info(f"Eliminadas {len(expired_tokens)} sesiones expiradas")
        
        return len(expired_tokens)
    
    def get_active_sessions(self) -> List[Dict[str, Any]]:
        """
        Obtiene información de todas las sesiones activas.
        
        Returns:
            Lista de sesiones activas
        """
        self.cleanup_expired_sessions()
        
        active_sessions = []
        for token, session in self.sessions.items():
            if session.get('is_active', False):
                session_info = session.copy()
                session_info['token'] = token[:8] + "..."  # Ocultar token completo
                active_sessions.append(session_info)
        
        return active_sessions


# Instancia global del manejador de sesiones
session_manager = SessionManager()


def get_session_manager() -> SessionManager:
    """Obtiene la instancia del manejador de sesiones."""
    return session_manager


# Funciones de conveniencia para autenticación
def authenticate_user(username: str, password: str, user_repository) -> Optional[Dict[str, Any]]:
    """
    Autentica un usuario con username y password.
    
    Args:
        username: Nombre de usuario
        password: Contraseña
        user_repository: Repositorio de usuarios
        
    Returns:
        Información del usuario si la autenticación es exitosa
    """
    try:
        # Obtener usuario de la base de datos
        user = user_repository.get_user_by_username(username)
        
        if not user:
            logger.warning(f"Intento de login con usuario inexistente: {username}")
            return None
        
        # Verificar si el usuario está activo
        if not user.get('is_active', True):
            logger.warning(f"Intento de login con usuario inactivo: {username}")
            return None
        
        # Verificar contraseña
        stored_password = cast(str, user.get('password', ''))
        if not verify_password(password, stored_password):
            logger.warning(f"Contraseña incorrecta para usuario: {username}")
            return None
        
        # Actualizar último login
        user_repository.update_user({
            'id': user['id'],
            'last_login': datetime.now().isoformat()
        })
        
        logger.info(f"Login exitoso para usuario: {username}")
        return user
        
    except Exception as e:
        logger.error(f"Error durante autenticación: {e}")
        return None


def create_user_session(user: Dict[str, Any]) -> str:
    """
    Crea una sesión para un usuario autenticado.
    
    Args:
        user: Información del usuario
        
    Returns:
        Token de sesión
    """
    return session_manager.create_session(
        user_id=user['id'],
        username=user['username']
    )


def validate_user_session(session_token: str) -> Optional[Dict[str, Any]]:
    """
    Valida un token de sesión de usuario.
    
    Args:
        session_token: Token a validar
        
    Returns:
        Información de sesión si es válida
    """
    return session_manager.validate_session(session_token)


def logout_user(session_token: str) -> bool:
    """
    Cierra la sesión de un usuario.
    
    Args:
        session_token: Token de sesión
        
    Returns:
        True si se cerró exitosamente
    """
    return session_manager.invalidate_session(session_token)


if __name__ == "__main__":
    # Pruebas del módulo
    print("=== PRUEBAS DEL MÓDULO DE AUTENTICACIÓN ===")
    
    # Prueba de hash de contraseña
    password = "mi_password_seguro"
    hashed = hash_password(password)
    print(f"Contraseña: {password}")
    print(f"Hash: {hashed}")
    print(f"Verificación: {verify_password(password, hashed)}")
    print()
    
    # Prueba de generación de contraseña
    generated = generate_password(12)
    print(f"Contraseña generada: {generated}")
    print()
    
    # Prueba de validación de fortaleza
    test_passwords = [
        "123",
        "password",
        "Password1",
        "MySecure123!",
        "VeryComplexPassword2024!"
    ]
    
    for pwd in test_passwords:
        validation = validate_password_strength(pwd)
        print(f"Contraseña: {pwd}")
        print(f"Fortaleza: {validation['strength']} (Score: {validation['score']})")
        if validation['issues']:
            print(f"Problemas: {', '.join(validation['issues'])}")
        print()