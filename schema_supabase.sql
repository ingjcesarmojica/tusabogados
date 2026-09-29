-- ================================================
-- SCHEMA: Base de datos TusAbogados.com
-- Supabase (PostgreSQL)
-- Ejecutar en SQL Editor de Supabase Dashboard
-- ================================================

-- ── Tabla: usuarios ─────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS usuarios (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    nombre TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    telefono TEXT,
    rol TEXT,                    -- 'demandado' o 'demandante'
    categoria TEXT,              -- 'civil', 'laboral', 'penal', 'no_definida'
    descripcion_caso TEXT,
    tiene_pruebas BOOLEAN DEFAULT FALSE,
    paso_actual TEXT DEFAULT 'saludo_inicial',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ── Tabla: citas ────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS citas (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    usuario_email TEXT NOT NULL,
    usuario_nombre TEXT,
    usuario_telefono TEXT,
    categoria TEXT,
    descripcion_caso TEXT,
    fecha_cita DATE NOT NULL,
    hora_cita TEXT NOT NULL,        -- '09:00', '10:30', etc.
    estado TEXT DEFAULT 'confirmada', -- 'confirmada', 'reprogramada', 'cancelada', 'completada'
    codigo_acceso VARCHAR(3),       -- Código de 3 dígitos para agente de voz
    url_token TEXT,                 -- Token UUID único para URL de agente de voz
    url_agente_voz TEXT,            -- URL completa del agente de voz (uso único)
    notas TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ── Tabla: conversaciones ───────────────────────────────────────────
CREATE TABLE IF NOT EXISTS conversaciones (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    usuario_email TEXT,
    usuario_nombre TEXT,
    mensaje_usuario TEXT,
    respuesta_agente TEXT,
    paso TEXT,                      -- paso del guion en el que estaba
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ── Tabla: consultas_adicionales ────────────────────────────────────
CREATE TABLE IF NOT EXISTS consultas_adicionales (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    usuario_email TEXT NOT NULL,
    usuario_nombre TEXT,
    consulta TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ── Índices para búsquedas rápidas ──────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_usuarios_email ON usuarios(email);
CREATE INDEX IF NOT EXISTS idx_citas_email ON citas(usuario_email);
CREATE INDEX IF NOT EXISTS idx_citas_fecha ON citas(fecha_cita);
CREATE INDEX IF NOT EXISTS idx_citas_estado ON citas(estado);
CREATE INDEX IF NOT EXISTS idx_conversaciones_email ON conversaciones(usuario_email);
CREATE INDEX IF NOT EXISTS idx_consultas_email ON consultas_adicionales(usuario_email);

-- ══════════════════════════════════════════════════════════════════════
-- RLS (Row Level Security) — PROTECCIÓN DE DATOS
-- ══════════════════════════════════════════════════════════════════════
--
-- CÓMO FUNCIONA:
-- - Habilitar RLS bloquea TODOS los accesos por defecto
-- - La service_role key (usada en el backend) BYPASEA el RLS
-- - La anon key queda BLOQUEADA salvo que se creen políticas explícitas
-- - Esto protege contra filtraciones de la anon key
--
-- IMPORTANTE: En tu .env usa la SERVICE_ROLE key (no la anon):
-- SUPABASE_KEY=eyJhb... (service_role, empieza igual pero con más permisos)
-- Para obtenerla: Supabase Dashboard → Settings → API → service_role
-- ══════════════════════════════════════════════════════════════════════

-- ── Habilitar RLS en todas las tablas ───────────────────────────────
ALTER TABLE usuarios ENABLE ROW LEVEL SECURITY;
ALTER TABLE citas ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversaciones ENABLE ROW LEVEL SECURITY;
ALTER TABLE consultas_adicionales ENABLE ROW LEVEL SECURITY;

-- ── Política: Bloquear todo acceso anónimo (anon key) ───────────────
-- La service_role key bypassa estas políticas automáticamente.
-- Si alguien obtiene la anon key, NO podrá leer ni escribir nada.
CREATE POLICY "usuarios_deny_anon" ON usuarios
    FOR ALL USING (false) WITH CHECK (false);

CREATE POLICY "citas_deny_anon" ON citas
    FOR ALL USING (false) WITH CHECK (false);

CREATE POLICY "conversaciones_deny_anon" ON conversaciones
    FOR ALL USING (false) WITH CHECK (false);

CREATE POLICY "consultas_adicionales_deny_anon" ON consultas_adicionales
    FOR ALL USING (false) WITH CHECK (false);

-- ══════════════════════════════════════════════════════════════════════
-- FIN DEL RLS
-- ══════════════════════════════════════════════════════════════════════

-- ── Vista resumen de citas ──────────────────────────────────────────
CREATE OR REPLACE VIEW vista_citas_pendientes AS
SELECT
    c.id,
    c.usuario_nombre,
    c.usuario_email,
    c.usuario_telefono,
    c.categoria,
    c.fecha_cita,
    c.hora_cita,
    c.estado,
    c.created_at
FROM citas c
WHERE c.estado IN ('confirmada', 'reprogramada')
ORDER BY c.fecha_cita ASC, c.hora_cita ASC;

-- ── Vista de estadísticas ───────────────────────────────────────────
CREATE OR REPLACE VIEW vista_estadisticas AS
SELECT
    (SELECT COUNT(*) FROM usuarios) AS total_usuarios,
    (SELECT COUNT(*) FROM citas WHERE estado = 'confirmada') AS citas_pendientes,
    (SELECT COUNT(*) FROM citas WHERE estado = 'completada') AS citas_completadas,
    (SELECT COUNT(*) FROM conversaciones) AS total_conversaciones;

-- ── Migración: agregar columnas a citas (si la tabla ya existe) ─────
-- Ejecutar solo si la tabla citas ya existía antes de esta actualización
ALTER TABLE citas ADD COLUMN IF NOT EXISTS codigo_acceso VARCHAR(3);
ALTER TABLE citas ADD COLUMN IF NOT EXISTS url_token TEXT;
ALTER TABLE citas ADD COLUMN IF NOT EXISTS url_agente_voz TEXT;

-- ================================================
-- FIN DEL SCHEMA
-- ================================================
