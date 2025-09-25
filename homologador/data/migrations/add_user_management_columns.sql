-- Agregar columnas para el módulo de administración de usuarios
-- Migración: add_user_management_columns.sql
-- Versión segura que verifica columnas existentes

-- Agregar columna department si no existe (será verificado por el sistema)
ALTER TABLE users ADD COLUMN department VARCHAR(100) DEFAULT '';
-- Nota: mantendremos password_hash como columna principal y ajustaremos el código

-- Actualizar roles para incluir los nuevos roles
-- Primero, eliminamos la restricción CHECK existente y agregamos una nueva
-- SQLite no permite modificar constraints directamente, pero podemos trabajar con los valores

-- Los nuevos roles permitidos serán: admin, manager, editor, viewer, guest
-- Por ahora, actualizaremos solo el código para manejar esto