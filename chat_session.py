"""
ChatSession - Manejo de sesiones aisladas por usuario.
TusAbogados.com - Multi-usuario concurrente

Cada sesión de chat tiene su propio estado independiente.
No hay interferencia entre usuarios diferentes.
"""

import time
import threading
import uuid
import logging

logger = logging.getLogger(__name__)

SESSION_TTL_SECONDS = 30 * 60  # 30 min inactividad
CLEANUP_INTERVAL_SECONDS = 5 * 60


class ChatState:
    """Estado conversacional de UN solo usuario."""

    def __init__(self):
        now = time.time()
        self.user_name = ""
        self.user_email = ""
        self.user_phone = ""
        self.case_description = ""
        self.case_subtype = ""
        self.appointment_time = ""
        self.appointment_fecha_str = ""
        self.appointment_hora = ""
        self.user_role = ""
        self.case_category = ""
        self.paso_actual = "saludo_inicial"
        self.datos_usuario = {}
        self.has_evidence = ""
        self.agent_name = ""
        self.codigo_acceso = ""
        self.url_token = ""
        self.url_agente_voz = ""
        self.created_at = now
        self.last_access = now

    def touch(self):
        self.last_access = time.time()

    def clear(self):
        self.user_name = ""
        self.user_email = ""
        self.user_phone = ""
        self.case_description = ""
        self.case_subtype = ""
        self.appointment_time = ""
        self.appointment_fecha_str = ""
        self.appointment_hora = ""
        self.user_role = ""
        self.case_category = ""
        self.paso_actual = "saludo_inicial"
        self.datos_usuario = {}
        self.has_evidence = ""
        self.codigo_acceso = ""
        self.url_token = ""
        self.url_agente_voz = ""

    def to_dict(self):
        return {
            "user_name": self.user_name,
            "nombre": self.user_name,
            "user_email": self.user_email,
            "correo": self.user_email,
            "user_phone": self.user_phone,
            "telefono": self.user_phone,
            "case_description": self.case_description,
            "case_subtype": self.case_subtype,
            "appointment_time": self.appointment_time,
            "fecha_cita": self.appointment_time,
            "user_role": self.user_role,
            "rol": self.user_role,
            "case_category": self.case_category,
            "categoria": self.case_category,
            "paso_actual": self.paso_actual or "saludo_inicial",
        }


class ChatSession:
    """Registro central de sesiones. Thread-safe."""

    _sessions = {}
    _lock = threading.Lock()
    _cleanup_started = False

    @classmethod
    def _start_cleanup_if_needed(cls):
        if cls._cleanup_started:
            return
        cls._cleanup_started = True
        def _loop():
            while True:
                time.sleep(CLEANUP_INTERVAL_SECONDS)
                cls._cleanup_expired()
        threading.Thread(target=_loop, daemon=True).start()

    @classmethod
    def _cleanup_expired(cls):
        now = time.time()
        expired = []
        with cls._lock:
            for sid, st in cls._sessions.items():
                if now - st.last_access > SESSION_TTL_SECONDS:
                    expired.append(sid)
            for sid in expired:
                del cls._sessions[sid]
        if expired:
            logger.info(f"Sesiones expiradas: {len(expired)}")

    @classmethod
    def get_or_create(cls, session_id=None):
        cls._start_cleanup_if_needed()
        if not session_id:
            session_id = uuid.uuid4().hex
        with cls._lock:
            if session_id in cls._sessions:
                state = cls._sessions[session_id]
                state.touch()
                return session_id, state
            state = ChatState()
            cls._sessions[session_id] = state
            logger.info(f"Nueva sesión: {session_id[:8]}... "
                       f"(activas: {len(cls._sessions)})")
            return session_id, state

    @classmethod
    def get_state(cls, session_id):
        with cls._lock:
            state = cls._sessions.get(session_id)
            if state:
                state.touch()
            return state

    @classmethod
    def remove(cls, session_id):
        with cls._lock:
            cls._sessions.pop(session_id, None)

    @classmethod
    def active_count(cls):
        with cls._lock:
            return len(cls._sessions)
