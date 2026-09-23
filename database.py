"""
Módulo Supabase - Base de datos en la nube para TusAbogados.com
Almacena datos de usuarios, casos y citas.

Seguridad:
- Usar SERVICE_ROLE key (no anon key) en SUPABASE_KEY
- RLS habilitado en todas las tablas
- Validación de datos antes de insertar
"""

import os
import re
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")

_supabase = None


# ── Validación de datos ─────────────────────────────────────────────
_EMAIL_RE = re.compile(r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$")
_PHONE_RE = re.compile(r"^[0-9]{10}$")


def _validar_email(email):
    """Retorna True si el email tiene formato válido."""
    return bool(email) and bool(_EMAIL_RE.match(email.strip()))


def _validar_telefono(telefono):
    """Retorna True si el teléfono tiene 10 dígitos."""
    digits = re.sub(r"[^0-9]", "", str(telefono))
    return len(digits) == 10


def _sanitizar(texto):
    """Limpia texto básico para evitar inyección de caracteres peligrosos."""
    if not isinstance(texto, str):
        return texto
    # Eliminar caracteres nulos y control peligrosos
    return texto.replace("\x00", "").strip()


def get_supabase():
    """Obtiene cliente Supabase (singleton)."""
    global _supabase
    if _supabase is not None:
        return _supabase

    if not SUPABASE_URL or not SUPABASE_KEY:
        logger.warning("SUPABASE_URL/SUPABASE_KEY no configuradas - modo sin BD")
        return None

    try:
        from supabase import create_client

        _supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        logger.info("Supabase conectado correctamente")
        return _supabase
    except Exception as e:
        logger.error(f"Error conectando Supabase: {e}")
        return None


def guardar_usuario(datos):
    """
    Guarda o actualiza un usuario en la tabla 'usuarios'.
    datos: dict con campos del usuario.
    Retorna (True, id) o (False, error).
    """
    sb = get_supabase()
    if sb is None:
        return False, "Supabase no disponible"

    # ── Validaciones ──────────────────────────────────────────────────
    email = _sanitizar(datos.get("email", ""))
    if not _validar_email(email):
        return False, f"Email inválido: {email}"

    nombre = _sanitizar(datos.get("nombre", ""))
    if not nombre or len(nombre) < 2:
        return False, "Nombre requerido (mínimo 2 caracteres)"

    try:
        registro = {
            "nombre": nombre,
            "email": email,
            "telefono": _sanitizar(datos.get("telefono", "")),
            "rol": _sanitizar(datos.get("rol", "")),
            "categoria": _sanitizar(datos.get("categoria", "")),
            "descripcion_caso": _sanitizar(datos.get("descripcion_caso", "")),
            "tiene_pruebas": datos.get("tiene_pruebas", False),
            "paso_actual": _sanitizar(datos.get("paso_actual", "")),
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }

        result = sb.table("usuarios").upsert(registro, on_conflict="email").execute()

        user_id = None
        if hasattr(result, "data") and result.data:
            user_id = result.data[0].get("id")

        logger.info(f"Usuario guardado: {registro['nombre']} ({registro['email']})")
        return True, user_id

    except Exception as e:
        logger.error(f"Error guardando usuario: {e}")
        return False, str(e)


def guardar_cita(datos):
    """
    Guarda una cita en la tabla 'citas'.
    Verifica que no exista otra cita en la misma fecha/hora antes de insertar.
    datos: dict con campos de la cita.
    Retorna (True, id) o (False, error).
    """
    sb = get_supabase()
    if sb is None:
        return False, "Supabase no disponible"

    # ── Validaciones ──────────────────────────────────────────────────
    email = _sanitizar(datos.get("email", ""))
    if not _validar_email(email):
        return False, f"Email inválido: {email}"

    fecha_cita = datos.get("fecha_cita", "")
    hora_cita = _sanitizar(datos.get("hora_cita", ""))
    if not fecha_cita or not hora_cita:
        return False, "Fecha y hora de cita son requeridas"

    # ── Verificar que no haya doble agendamiento ──────────────────────
    try:
        existentes = (
            sb.table("citas")
            .select("id")
            .eq("fecha_cita", fecha_cita)
            .eq("hora_cita", hora_cita)
            .in_("estado", ["confirmada", "reprogramada"])
            .execute()
        )
        if hasattr(existentes, "data") and existentes.data:
            return False, f"La fecha {fecha_cita} a las {hora_cita} ya está ocupada"
    except Exception as e:
        logger.warning(f"Error verificando disponibilidad: {e}")

    try:
        registro = {
            "usuario_email": email,
            "usuario_nombre": _sanitizar(datos.get("nombre", "")),
            "usuario_telefono": _sanitizar(datos.get("telefono", "")),
            "categoria": _sanitizar(datos.get("categoria", "")),
            "descripcion_caso": _sanitizar(datos.get("descripcion_caso", "")),
            "fecha_cita": fecha_cita,
            "hora_cita": hora_cita,
            "estado": _sanitizar(datos.get("estado", "confirmada")),
            "codigo_acceso": _sanitizar(datos.get("codigo_acceso", "")),
            "url_token": _sanitizar(datos.get("url_token", "")),
            "url_agente_voz": _sanitizar(datos.get("url_agente_voz", "")),
            "created_at": datetime.utcnow().isoformat(),
        }

        result = sb.table("citas").insert(registro).execute()

        cita_id = None
        if hasattr(result, "data") and result.data:
            cita_id = result.data[0].get("id")

        logger.info(
            f"Cita guardada: {registro['fecha_cita']} {registro['hora_cita']} - {registro['usuario_nombre']}"
        )
        return True, cita_id

    except Exception as e:
        logger.error(f"Error guardando cita: {e}")
        return False, str(e)


def guardar_conversacion(datos):
    """
    Guarda registro de la conversación en 'conversaciones'.
    datos: dict con campos de la conversación.
    Retorna (True, id) o (False, error).
    """
    sb = get_supabase()
    if sb is None:
        return False, "Supabase no disponible"

    try:
        registro = {
            "usuario_email": _sanitizar(datos.get("email", "")),
            "usuario_nombre": _sanitizar(datos.get("nombre", "")),
            "mensaje_usuario": _sanitizar(datos.get("mensaje_usuario", "")),
            "respuesta_agente": _sanitizar(datos.get("respuesta_agente", "")),
            "paso": _sanitizar(datos.get("paso", "")),
            "created_at": datetime.utcnow().isoformat(),
        }

        result = sb.table("conversaciones").insert(registro).execute()

        conv_id = None
        if hasattr(result, "data") and result.data:
            conv_id = result.data[0].get("id")

        return True, conv_id

    except Exception as e:
        logger.error(f"Error guardando conversación: {e}")
        return False, str(e)


def guardar_consulta_adicional(datos):
    """
    Guarda una consulta adicional en 'consultas_adicionales'.
    """
    sb = get_supabase()
    if sb is None:
        return False, "Supabase no disponible"

    try:
        registro = {
            "usuario_email": _sanitizar(datos.get("email", "")),
            "usuario_nombre": _sanitizar(datos.get("nombre", "")),
            "consulta": _sanitizar(datos.get("consulta", "")),
            "created_at": datetime.utcnow().isoformat(),
        }

        result = sb.table("consultas_adicionales").insert(registro).execute()

        consulta_id = None
        if hasattr(result, "data") and result.data:
            consulta_id = result.data[0].get("id")

        return True, consulta_id

    except Exception as e:
        logger.error(f"Error guardando consulta adicional: {e}")
        return False, str(e)


def obtener_citas_por_fecha(fecha_str):
    """
    Obtiene todas las horas ocupadas para una fecha específica.
    fecha_str: string en formato 'YYYY-MM-DD' (ej: '2026-09-09').
    Retorna lista de horas ocupadas como strings ('08:00', '09:00', etc.).
    """
    sb = get_supabase()
    if sb is None:
        return []

    try:
        result = (
            sb.table("citas")
            .select("hora_cita")
            .eq("fecha_cita", fecha_str)
            .in_("estado", ["confirmada", "reprogramada"])
            .execute()
        )
        if hasattr(result, "data") and result.data:
            return [c["hora_cita"] for c in result.data]
        return []
    except Exception as e:
        logger.error(f"Error obteniendo citas por fecha {fecha_str}: {e}")
        return []


def obtener_usuario(email):
    """
    Obtiene un usuario por email.
    Retorna dict con datos o None.
    """
    sb = get_supabase()
    if sb is None:
        return None

    try:
        result = sb.table("usuarios").select("*").eq("email", email).execute()
        if hasattr(result, "data") and result.data:
            return result.data[0]
        return None
    except Exception as e:
        logger.error(f"Error obteniendo usuario: {e}")
        return None


def obtener_citas_usuario(email):
    """
    Obtiene todas las citas de un usuario por email.
    Retorna lista de dicts.
    """
    sb = get_supabase()
    if sb is None:
        return []

    try:
        result = (
            sb.table("citas")
            .select("*")
            .eq("usuario_email", email)
            .order("created_at", desc=True)
            .execute()
        )
        if hasattr(result, "data"):
            return result.data
        return []
    except Exception as e:
        logger.error(f"Error obteniendo citas: {e}")
        return []


def obtener_citas_proximas_para_recordatorio():
    """
    Obtiene todas las citas confirmadas de hoy y mañana que necesitan recordatorio.
    Retorna lista de dicts con los campos necesarios para notificaciones.
    """
    sb = get_supabase()
    if sb is None:
        return []

    try:
        from datetime import date, timedelta
        hoy = date.today().isoformat()
        manana = (date.today() + timedelta(days=1)).isoformat()

        result = (
            sb.table("citas")
            .select("id, usuario_email, usuario_nombre, usuario_telefono, "
                    "categoria, fecha_cita, hora_cita, estado, "
                    "codigo_acceso, url_agente_voz")
            .in_("estado", ["confirmada", "reprogramada"])
            .or_(f"fecha_cita.eq.{hoy},fecha_cita.eq.{manana}")
            .execute()
        )

        if hasattr(result, "data") and result.data:
            citas = []
            for c in result.data:
                citas.append({
                    "cita_id": c.get("id", ""),
                    "email": c.get("usuario_email", ""),
                    "nombre": c.get("usuario_nombre", ""),
                    "telefono": c.get("usuario_telefono", ""),
                    "categoria": c.get("categoria", ""),
                    "fecha_cita": c.get("fecha_cita", ""),
                    "hora_cita": c.get("hora_cita", ""),
                    "codigo_acceso": c.get("codigo_acceso", ""),
                    "url_agente_voz": c.get("url_agente_voz", ""),
                })
            return citas
        return []
    except Exception as e:
        logger.error(f"Error obteniendo citas próximas: {e}")
        return []
