-- ================================================
-- MIGRACIÓN: Agregar campos de agente de voz a citas
-- TusAbogados.com
-- 
-- INSTRUCCIONES:
-- 1. Ve a tu panel de Supabase → SQL Editor
-- 2. Pega este script completo
-- 3. Haz clic en "Run"
--
-- Esto agrega 3 columnas nuevas a la tabla citas:
--   - codigo_acceso: código de 3 dígitos para el agente de voz
--   - url_token: token UUID único para la URL
--   - url_agente_voz: URL completa de uso único
-- ================================================

-- Agregar columnas (seguro: no falla si ya existen)
ALTER TABLE citas ADD COLUMN IF NOT EXISTS codigo_acceso VARCHAR(3);
ALTER TABLE citas ADD COLUMN IF NOT EXISTS url_token TEXT;
ALTER TABLE citas ADD COLUMN IF NOT EXISTS url_agente_voz TEXT;

-- Verificar que las columnas se agregaron
DO $$
BEGIN
    RAISE NOTICE '✅ Migración completada. Columnas agregadas a tabla citas.';
END $$;
