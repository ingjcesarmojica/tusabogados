"""
Notificaciones - TusAbogados.com
Envío de correos de confirmación y recordatorio de citas vía SMTP.
Programación de recordatorios 15 minutos antes de cada cita.
"""

import os
import uuid
import random
import logging
import smtplib
import threading
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from string import Template

logger = logging.getLogger(__name__)

# ── Configuración SMTP ───────────────────────────────────────────────
SMTP_HOST = os.environ.get("SMTP_HOST", "")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USER = os.environ.get("SMTP_USER", "")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")
SMTP_FROM_NAME = os.environ.get("SMTP_FROM_NAME", "TusAbogados.com")
SMTP_USE_TLS = os.environ.get("SMTP_USE_TLS", "true").lower() == "true"

# ── URL del agente de voz ────────────────────────────────────────────
AGENTE_VOZ_BASE_URL = os.environ.get(
    "AGENTE_VOZ_BASE_URL", "https://agentcall-rkz3.onrender.com/"
).rstrip("/")

# ── WhatsApp API (placeholder) ───────────────────────────────────────
WHATSAPP_API_URL = os.environ.get("WHATSAPP_API_URL", "")
WHATSAPP_API_TOKEN = os.environ.get("WHATSAPP_API_TOKEN", "")

# ── Recordatorio: minutos antes de la cita ───────────────────────────
MINUTOS_RECORDATORIO = int(os.environ.get("MINUTOS_RECORDATORIO", "15"))

# ── Almacén de timers activos ────────────────────────────────────────
_timers_activos = {}


def generar_codigo_acceso():
    """Genera un código único de 3 dígitos (100-999)."""
    return str(random.randint(100, 999))


def generar_url_agente_voz():
    """Genera una URL única para el agente de voz con un token UUID."""
    token = uuid.uuid4().hex
    return f"{AGENTE_VOZ_BASE_URL}/cita/{token}", token


def _smtp_configurado():
    """Verifica que las variables SMTP estén configuradas."""
    if not SMTP_HOST or not SMTP_USER or not SMTP_PASSWORD:
        logger.warning(
            "SMTP no configurado (falta SMTP_HOST, SMTP_USER o SMTP_PASSWORD). "
            "No se enviarán correos."
        )
        return False
    return True


def _enviar_correo_smtp(destinatario, asunto, html_body, texto_plano=""):
    """Envía un correo electrónico vía SMTP."""
    if not _smtp_configurado():
        logger.warning(f"[SMTP DESHABILITADO] Correo a {destinatario}: {asunto}")
        return False

    try:
        msg = MIMEMultipart("alternative")
        msg["From"] = f"{SMTP_FROM_NAME} <{SMTP_USER}>"
        msg["To"] = destinatario
        msg["Subject"] = asunto

        if texto_plano:
            msg.attach(MIMEText(texto_plano, "plain", "utf-8"))
        msg.attach(MIMEText(html_body, "html", "utf-8"))

        logger.info(f"[SMTP] Conectando a {SMTP_HOST}:{SMTP_PORT} (TLS={SMTP_USE_TLS})...")
        if SMTP_USE_TLS:
            server = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30)
            server.ehlo()
            server.starttls()
            server.ehlo()
        else:
            server = smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=30)

        logger.info("[SMTP] Conexion OK, autenticando...")
        server.login(SMTP_USER, SMTP_PASSWORD)
        logger.info("[SMTP] Autenticacion OK, enviando...")
        server.sendmail(SMTP_USER, [destinatario], msg.as_string())
        server.quit()

        logger.info(f"✅ Correo enviado a {destinatario}: {asunto}")
        return True

    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"❌ Error de autenticación SMTP: {e}. Verifica SMTP_USER y SMTP_PASSWORD.")
        return False
    except smtplib.SMTPConnectError as e:
        logger.error(f"❌ Error de conexión SMTP a {SMTP_HOST}:{SMTP_PORT}: {e}")
        return False
    except TimeoutError:
        logger.error(f"❌ Timeout conectando a SMTP {SMTP_HOST}:{SMTP_PORT}. Puerto bloqueado?")
        return False
    except Exception as e:
        logger.error(f"❌ Error enviando correo a {destinatario}: {type(e).__name__}: {e}")
        return False


def _plantilla_html(nombre_archivo, variables):
    """Lee una plantilla HTML y reemplaza las variables."""
    template_dir = os.path.join(os.path.dirname(__file__), "templates")
    filepath = os.path.join(template_dir, nombre_archivo)
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            contenido = f.read()
        tmpl = Template(contenido)
        return tmpl.safe_substitute(variables)
    except FileNotFoundError:
        logger.error(f"Plantilla no encontrada: {filepath}")
        return None
    except Exception as e:
        logger.error(f"Error leyendo plantilla {filepath}: {e}")
        return None


def _formatear_fecha_display(fecha_cita, hora_cita):
    """Formatea fecha y hora para mostrar en correos."""
    try:
        fecha_dt = datetime.strptime(f"{fecha_cita} {hora_cita}", "%Y-%m-%d %H:%M")
        dias_es = {
            "Monday": "Lunes", "Tuesday": "Martes", "Wednesday": "Miércoles",
            "Thursday": "Jueves", "Friday": "Viernes", "Saturday": "Sábado",
            "Sunday": "Domingo",
        }
        meses_es = {
            1: "enero", 2: "febrero", 3: "marzo", 4: "abril",
            5: "mayo", 6: "junio", 7: "julio", 8: "agosto",
            9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre",
        }
        dia_semana = dias_es.get(fecha_dt.strftime("%A"), fecha_dt.strftime("%A"))
        mes = meses_es.get(fecha_dt.month, fecha_dt.strftime("%B"))
        fecha_display = f"{dia_semana} {fecha_dt.day} de {mes}"
        hora_12 = fecha_dt.hour if fecha_dt.hour <= 12 else fecha_dt.hour - 12
        if fecha_dt.hour == 0:
            hora_12 = 12
        periodo = "a.m." if fecha_dt.hour < 12 else "p.m."
        hora_display = f"{hora_12}:{fecha_dt.minute:02d} {periodo}"
        return fecha_display, hora_display
    except ValueError:
        return fecha_cita, hora_cita


# ── Funciones públicas ───────────────────────────────────────────────

def enviar_correo_confirmacion(datos_cita):
    """
    Envía el correo de confirmación de cita con URL única y código de acceso.

    datos_cita: dict con campos:
        nombre, email, fecha_cita, hora_cita, categoria,
        codigo_acceso, url_agente_voz
    """
    nombre = datos_cita.get("nombre", "")
    email = datos_cita.get("email", "")
    fecha_cita = datos_cita.get("fecha_cita", "")
    hora_cita = datos_cita.get("hora_cita", "")
    categoria = datos_cita.get("categoria", "")
    codigo = datos_cita.get("codigo_acceso", "")
    url_voz = datos_cita.get("url_agente_voz", "")

    if not email:
        logger.warning("No se puede enviar correo: email vacío")
        return False

    fecha_display, hora_display = _formatear_fecha_display(fecha_cita, hora_cita)

    variables = {
        "nombre_usuario": nombre,
        "fecha_cita_display": fecha_display,
        "hora_cita_display": hora_display,
        "categoria_caso": categoria,
        "codigo_acceso": codigo,
        "url_agente_voz": url_voz,
        "anio": datetime.now().year,
    }

    html_body = _plantilla_html("email_confirmacion_cita.html", variables)
    if html_body is None:
        html_body = (
            f"<h2>Confirmación de Cita - TusAbogados.com</h2>"
            f"<p>Hola <strong>{nombre}</strong>,</p>"
            f"<p>Tu cita ha sido registrada exitosamente:</p>"
            f"<ul>"
            f"<li>📅 <strong>Fecha:</strong> {fecha_display}</li>"
            f"<li>🕐 <strong>Hora:</strong> {hora_display}</li>"
            f"<li>📋 <strong>Categoría:</strong> {categoria}</li>"
            f"</ul>"
            f"<p><strong>Código de acceso:</strong> "
            f"<span style='font-size:24px;color:#1a73e8;font-weight:bold;'>"
            f"{codigo}</span></p>"
            f"<p><strong>Link para tu asesoría:</strong></p>"
            f"<p><a href='{url_voz}' style='background-color:#1a73e8;color:white;"
            f"padding:12px 24px;text-decoration:none;border-radius:6px;"
            f"display:inline-block;'>Entrar a la asesoría</a></p>"
            f"<p><small>El link es de uso único. 15 minutos antes de tu cita "
            f"recibirás un recordatorio.</small></p>"
            f"<hr><p><small>© {datetime.now().year} TusAbogados.com</small></p>"
        )

    texto_plano = (
        f"Confirmación de Cita - TusAbogados.com\n\n"
        f"Hola {nombre},\n\n"
        f"Tu cita ha sido registrada:\n"
        f"Fecha: {fecha_display}\nHora: {hora_display}\n"
        f"Categoría: {categoria}\n\n"
        f"Código de acceso: {codigo}\nLink: {url_voz}\n\n"
        f"El link es de uso único. Recibirás un recordatorio 15 min antes.\n\n"
        f"© {datetime.now().year} TusAbogados.com"
    )

    asunto = f"Confirmación de tu cita - TusAbogados.com | {fecha_display}"
    return _enviar_correo_smtp(email, asunto, html_body, texto_plano)


def enviar_correo_recordatorio(datos_cita):
    """
    Envía el correo de recordatorio 15 minutos antes de la cita.
    """
    nombre = datos_cita.get("nombre", "")
    email = datos_cita.get("email", "")
    fecha_cita = datos_cita.get("fecha_cita", "")
    hora_cita = datos_cita.get("hora_cita", "")
    categoria = datos_cita.get("categoria", "")
    codigo = datos_cita.get("codigo_acceso", "")
    url_voz = datos_cita.get("url_agente_voz", "")
    telefono = datos_cita.get("telefono", "")

    if not email:
        logger.warning("No se puede enviar recordatorio: email vacío")
        return False

    fecha_display, hora_display = _formatear_fecha_display(fecha_cita, hora_cita)

    variables = {
        "nombre_usuario": nombre,
        "fecha_cita_display": fecha_display,
        "hora_cita_display": hora_display,
        "categoria_caso": categoria,
        "codigo_acceso": codigo,
        "url_agente_voz": url_voz,
        "minutos_recordatorio": MINUTOS_RECORDATORIO,
        "anio": datetime.now().year,
    }

    html_body = _plantilla_html("email_recordatorio_cita.html", variables)
    if html_body is None:
        html_body = (
            f"<h2>Recordatorio de Cita - TusAbogados.com</h2>"
            f"<p>Hola <strong>{nombre}</strong>,</p>"
            f"<p>Tu asesoría legal comienza en "
            f"<strong>{MINUTOS_RECORDATORIO} minutos</strong>.</p>"
            f"<ul>"
            f"<li>📅 <strong>Fecha:</strong> {fecha_display}</li>"
            f"<li>🕐 <strong>Hora:</strong> {hora_display}</li>"
            f"</ul>"
            f"<p><strong>Código de acceso:</strong> "
            f"<span style='font-size:28px;color:#d93025;font-weight:bold;'>"
            f"{codigo}</span></p>"
            f"<p><a href='{url_voz}' style='background-color:#d93025;color:white;"
            f"padding:14px 28px;text-decoration:none;border-radius:6px;"
            f"font-size:18px;display:inline-block;'>📞 Entrar ahora</a></p>"
            f"<hr><p><small>© {datetime.now().year} TusAbogados.com</small></p>"
        )

    texto_plano = (
        f"Recordatorio de Cita - TusAbogados.com\n\n"
        f"Hola {nombre},\n\n"
        f"Tu asesoría legal comienza en {MINUTOS_RECORDATORIO} minutos.\n"
        f"Fecha: {fecha_display}\nHora: {hora_display}\n\n"
        f"Código de acceso: {codigo}\nLink: {url_voz}\n\n"
        f"© {datetime.now().year} TusAbogados.com"
    )

    asunto = (f"Tu asesoría legal comienza en "
              f"{MINUTOS_RECORDATORIO} min | TusAbogados.com")

    resultado_email = _enviar_correo_smtp(email, asunto, html_body, texto_plano)

    # También enviar por WhatsApp si está configurado
    if telefono:
        enviar_whatsapp_recordatorio(
            telefono, nombre, fecha_display, hora_display, codigo, url_voz
        )

    return resultado_email


def enviar_whatsapp_recordatorio(telefono, nombre, fecha_display, hora_display,
                                  codigo, url_voz):
    """
    Envía recordatorio por WhatsApp.
    Requiere configuración de API de WhatsApp (Twilio, Meta Business, etc.)
    """
    if not WHATSAPP_API_URL or not WHATSAPP_API_TOKEN:
        logger.info(
            f"[WhatsApp no configurado] Recordatorio pendiente para {telefono}: "
            f"{nombre} - {fecha_display} {hora_display}"
        )
        return False

    mensaje = (
        f"Recordatorio - TusAbogados.com\n\n"
        f"Hola {nombre}, tu asesoría legal comienza en "
        f"{MINUTOS_RECORDATORIO} minutos.\n\n"
        f"Fecha: {fecha_display}\nHora: {hora_display}\n\n"
        f"Código de acceso: {codigo}\n\n"
        f"Ingresa aquí: {url_voz}\n\n"
        f"Un abogado especializado te atenderá por videollamada. "
        f"Ten a mano tu código de 3 dígitos."
    )

    try:
        import requests

        payload = {
            "to": f"+57{telefono}",
            "message": mensaje,
        }
        headers = {
            "Authorization": f"Bearer {WHATSAPP_API_TOKEN}",
            "Content-Type": "application/json",
        }
        response = requests.post(
            WHATSAPP_API_URL, json=payload, headers=headers, timeout=15
        )

        if response.status_code in (200, 201):
            logger.info(f"WhatsApp enviado a {telefono}")
            return True
        else:
            logger.warning(
                f"WhatsApp respondió {response.status_code}: {response.text}"
            )
            return False

    except Exception as e:
        logger.error(f"Error enviando WhatsApp a {telefono}: {e}")
        return False


def programar_recordatorio(datos_cita):
    """
    Programa el envío de recordatorio 15 minutos antes de la cita.

    datos_cita: dict con campos:
        fecha_cita, hora_cita, nombre, email, telefono,
        categoria, codigo_acceso, url_agente_voz, cita_id
    """
    fecha_cita = datos_cita.get("fecha_cita", "")
    hora_cita = datos_cita.get("hora_cita", "")

    if not fecha_cita or not hora_cita:
        logger.warning("No se puede programar recordatorio: fecha/hora vacía")
        return False

    try:
        fecha_hora_cita = datetime.strptime(
            f"{fecha_cita} {hora_cita}", "%Y-%m-%d %H:%M"
        )
    except ValueError:
        logger.error(
            f"Error parseando fecha/hora: {fecha_cita} {hora_cita}"
        )
        return False

    fecha_recordatorio = fecha_hora_cita - timedelta(
        minutes=MINUTOS_RECORDATORIO
    )
    ahora = datetime.now()

    if fecha_recordatorio <= ahora:
        logger.warning(
            f"La fecha de recordatorio ya pasó ({fecha_recordatorio}). "
            f"No se programa para {datos_cita.get('email', '')}."
        )
        return False

    delay_seconds = (fecha_recordatorio - ahora).total_seconds()
    cita_id = datos_cita.get("cita_id", "sin_id")

    logger.info(
        f"Recordatorio programado para {fecha_recordatorio} "
        f"(en {int(delay_seconds)}s) - {datos_cita.get('email', '')}"
    )

    def _enviar_recordatorio():
        try:
            logger.info(f"Enviando recordatorio para cita {cita_id}...")
            enviar_correo_recordatorio(datos_cita)
            logger.info(f"Recordatorio enviado para cita {cita_id}")
        except Exception as e:
            logger.error(f"Error en recordatorio para cita {cita_id}: {e}")
        finally:
            _timers_activos.pop(cita_id, None)

    timer = threading.Timer(delay_seconds, _enviar_recordatorio)
    timer.daemon = True
    timer.start()

    _timers_activos[cita_id] = {
        "timer": timer,
        "fecha_recordatorio": fecha_recordatorio.isoformat(),
        "datos_cita": datos_cita,
    }

    return True


def cancelar_recordatorio(cita_id):
    """Cancela un recordatorio programado por ID de cita."""
    info = _timers_activos.pop(cita_id, None)
    if info and info.get("timer"):
        info["timer"].cancel()
        logger.info(f"Recordatorio cancelado para cita {cita_id}")
        return True
    return False


def recordatorios_pendientes():
    """Retorna información sobre recordatorios activos."""
    return {
        cita_id: {
            "fecha_recordatorio": info["fecha_recordatorio"],
            "email": info["datos_cita"].get("email", ""),
        }
        for cita_id, info in _timers_activos.items()
    }


def iniciar_recordatorios_pendientes(citas_proximas):
    """
    Al iniciar la aplicación, reprograma recordatorios para citas
    que aún no han pasado.

    citas_proximas: lista de dicts con datos de citas de la BD
    """
    ahora = datetime.now()
    count = 0
    for cita in citas_proximas:
        try:
            fecha_hora = datetime.strptime(
                f"{cita.get('fecha_cita', '')} {cita.get('hora_cita', '')}",
                "%Y-%m-%d %H:%M",
            )
            fecha_recordatorio = fecha_hora - timedelta(
                minutes=MINUTOS_RECORDATORIO
            )

            if fecha_recordatorio > ahora:
                programar_recordatorio(cita)
                count += 1
        except Exception as e:
            logger.error(f"Error procesando recordatorio: {e}")

    logger.info(f"{count} recordatorios reprogramados al iniciar")
    return count
