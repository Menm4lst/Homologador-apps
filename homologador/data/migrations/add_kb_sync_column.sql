-- Migración para agregar la columna kb_sync a la tabla homologations
-- Fecha: 18/09/2025
-- Versión segura que verifica si la columna existe

-- Agregar la columna kb_sync si no existe (será verificado por el sistema)
ALTER TABLE homologations ADD COLUMN kb_sync BOOLEAN DEFAULT 0;