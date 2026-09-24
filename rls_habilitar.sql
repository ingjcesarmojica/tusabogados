-- ================================================
-- EJECUTAR EN: Supabase Dashboard → SQL Editor
-- ================================================
-- Esto habilita Row Level Security en todas las tablas
-- y bloquea el acceso con la anon key.
-- La service_role key bypassa estas políticas automáticamente.
-- ================================================

-- 1. Habilitar RLS en todas las tablas
ALTER TABLE usuarios ENABLE ROW LEVEL SECURITY;
ALTER TABLE citas ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversaciones ENABLE ROW LEVEL SECURITY;
ALTER TABLE consultas_adicionales ENABLE ROW LEVEL SECURITY;

-- 2. Política: bloquear todo acceso de la anon key
CREATE POLICY "usuarios_deny_anon" ON usuarios
    FOR ALL USING (false) WITH CHECK (false);

CREATE POLICY "citas_deny_anon" ON citas
    FOR ALL USING (false) WITH CHECK (false);

CREATE POLICY "conversaciones_deny_anon" ON conversaciones
    FOR ALL USING (false) WITH CHECK (false);

CREATE POLICY "consultas_adicionales_deny_anon" ON consultas_adicionales
    FOR ALL USING (false) WITH CHECK (false);

-- 3. Verificar que RLS está activo (debe mostrar true en todas)
SELECT
    tablename,
    rowsecurity AS rls_activo
FROM pg_tables
WHERE schemaname = 'public'
  AND tablename IN ('usuarios', 'citas', 'conversaciones', 'consultas_adicionales');

-- 4. Verificar políticas creadas
SELECT
    schemaname,
    tablename,
    policyname,
    cmd,
    qual,
    with_check
FROM pg_policies
WHERE schemaname = 'public'
  AND tablename IN ('usuarios', 'citas', 'conversaciones', 'consultas_adicionales');
