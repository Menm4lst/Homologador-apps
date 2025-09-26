"""
Esquema SQL embebido para compilación independiente.
Este módulo contiene el esquema de base de datos como cadena de texto
para evitar problemas con archivos externos en PyInstaller.
"""

SQL_SCHEMA = """-- Schema para el Homologador de Aplicaciones
-- SQLite Database Schema

-- ===============================
-- TABLA DE USUARIOS
-- ===============================
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('admin', 'editor', 'viewer')),
    full_name VARCHAR(100),
    email VARCHAR(100),
    is_active BOOLEAN DEFAULT 1,
    must_change_password BOOLEAN DEFAULT 0,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ===============================
-- TABLA DE HOMOLOGACIONES
-- ===============================
CREATE TABLE IF NOT EXISTS homologations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    real_name VARCHAR(200) NOT NULL,
    logical_name VARCHAR(200),
    kb_url TEXT,
    kb_sync BOOLEAN DEFAULT 0,
    homologation_date DATE,
    has_previous_versions BOOLEAN DEFAULT 0,
    repository_location VARCHAR(20) CHECK (repository_location IN ('AESA', 'APPS$')),
    details TEXT,
    created_by INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(id)
);

-- ===============================
-- TABLA DE AUDITORÍA
-- ===============================
CREATE TABLE IF NOT EXISTS audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    action VARCHAR(50) NOT NULL,
    table_name VARCHAR(50),
    record_id INTEGER,
    old_values TEXT,
    new_values TEXT,
    ip_address VARCHAR(45),
    user_agent TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- ===============================
-- ÍNDICES PARA OPTIMIZACIÓN
-- ===============================
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_users_active ON users(is_active);

CREATE INDEX IF NOT EXISTS idx_homologations_real_name ON homologations(real_name);
CREATE INDEX IF NOT EXISTS idx_homologations_logical_name ON homologations(logical_name);
CREATE INDEX IF NOT EXISTS idx_homologations_date ON homologations(homologation_date);
CREATE INDEX IF NOT EXISTS idx_homologations_repository ON homologations(repository_location);
CREATE INDEX IF NOT EXISTS idx_homologations_created_by ON homologations(created_by);
CREATE INDEX IF NOT EXISTS idx_homologations_created_at ON homologations(created_at);

CREATE INDEX IF NOT EXISTS idx_audit_user_id ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_action ON audit_logs(action);
CREATE INDEX IF NOT EXISTS idx_audit_table ON audit_logs(table_name);
CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_audit_record ON audit_logs(table_name, record_id);

-- ===============================
-- TRIGGERS PARA UPDATED_AT
-- ===============================
CREATE TRIGGER IF NOT EXISTS trigger_users_updated_at
    AFTER UPDATE ON users
    FOR EACH ROW
BEGIN
    UPDATE users SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS trigger_homologations_updated_at
    AFTER UPDATE ON homologations
    FOR EACH ROW
BEGIN
    UPDATE homologations SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- ===============================
-- TRIGGERS DE AUDITORÍA
-- ===============================
CREATE TRIGGER IF NOT EXISTS trigger_audit_homologations_insert
    AFTER INSERT ON homologations
    FOR EACH ROW
BEGIN
    INSERT INTO audit_logs (user_id, action, table_name, record_id, new_values, timestamp)
    VALUES (
        NEW.created_by,
        'CREATE',
        'homologations',
        NEW.id,
        json_object(
            'real_name', NEW.real_name,
            'logical_name', NEW.logical_name,
            'kb_url', NEW.kb_url,
            'homologation_date', NEW.homologation_date,
            'has_previous_versions', NEW.has_previous_versions,
            'repository_location', NEW.repository_location,
            'details', NEW.details
        ),
        CURRENT_TIMESTAMP
    );
END;

CREATE TRIGGER IF NOT EXISTS trigger_audit_homologations_update
    AFTER UPDATE ON homologations
    FOR EACH ROW
BEGIN
    INSERT INTO audit_logs (user_id, action, table_name, record_id, old_values, new_values, timestamp)
    VALUES (
        NEW.created_by,
        'UPDATE',
        'homologations',
        NEW.id,
        json_object(
            'real_name', OLD.real_name,
            'logical_name', OLD.logical_name,
            'kb_url', OLD.kb_url,
            'homologation_date', OLD.homologation_date,
            'has_previous_versions', OLD.has_previous_versions,
            'repository_location', OLD.repository_location,
            'details', OLD.details
        ),
        json_object(
            'real_name', NEW.real_name,
            'logical_name', NEW.logical_name,
            'kb_url', NEW.kb_url,
            'homologation_date', NEW.homologation_date,
            'has_previous_versions', NEW.has_previous_versions,
            'repository_location', NEW.repository_location,
            'details', NEW.details
        ),
        CURRENT_TIMESTAMP
    );
END;

CREATE TRIGGER IF NOT EXISTS trigger_audit_homologations_delete
    AFTER DELETE ON homologations
    FOR EACH ROW
BEGIN
    INSERT INTO audit_logs (user_id, action, table_name, record_id, old_values, timestamp)
    VALUES (
        OLD.created_by,
        'DELETE',
        'homologations',
        OLD.id,
        json_object(
            'real_name', OLD.real_name,
            'logical_name', OLD.logical_name,
            'kb_url', OLD.kb_url,
            'homologation_date', OLD.homologation_date,
            'has_previous_versions', OLD.has_previous_versions,
            'repository_location', OLD.repository_location,
            'details', OLD.details
        ),
        CURRENT_TIMESTAMP
    );
END;

-- ===============================
-- VISTAS ÚTILES
-- ===============================
CREATE VIEW IF NOT EXISTS v_homologations_with_user AS
SELECT 
    h.id,
    h.real_name,
    h.logical_name,
    h.kb_url,
    h.kb_sync,
    h.homologation_date,
    h.has_previous_versions,
    h.repository_location,
    h.details,
    u.username as created_by_username,
    u.full_name as created_by_full_name,
    h.created_at,
    h.updated_at
FROM homologations h
JOIN users u ON h.created_by = u.id
WHERE u.is_active = 1;

CREATE VIEW IF NOT EXISTS v_audit_with_user AS
SELECT 
    a.id,
    a.action,
    a.table_name,
    a.record_id,
    a.old_values,
    a.new_values,
    u.username,
    u.full_name,
    a.ip_address,
    a.timestamp
FROM audit_logs a
LEFT JOIN users u ON a.user_id = u.id
ORDER BY a.timestamp DESC;

-- ===============================
-- CONFIGURACIÓN DE PRAGMA
-- ===============================
PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;
PRAGMA busy_timeout = 30000;
PRAGMA cache_size = -2000;
PRAGMA synchronous = NORMAL;
PRAGMA temp_store = MEMORY;
"""

def get_schema_sql():
    """Retorna el esquema SQL completo."""
    return SQL_SCHEMA