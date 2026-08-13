import os
import io
import asyncio
import base64
import re
import json
import tempfile
import threading
import requests
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import logging
import edge_tts
import google.generativeai as genai
from dotenv import load_dotenv
from types import SimpleNamespace

chat = SimpleNamespace()

try:
    from rag import search_knowledge, add_pdf, list_documents, delete_document

    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False

load_dotenv()

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    gemini_model = genai.GenerativeModel("gemini-2.0-flash")
    GEMINI_CONFIGURED = True
else:
    gemini_model = None
    GEMINI_CONFIGURED = False
    app.logger.warning(
        "GEMINI_API_KEY no configurada - chat usar solo respuestas hardcoded"
    )

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
OPENROUTER_MODEL = os.environ.get("OPENROUTER_MODEL", "nvidia/nemotron-3-nano-30b-a3b")
OPENROUTER_CONFIGURED = bool(OPENROUTER_API_KEY)

TTS_VOICE = os.environ.get("TTS_VOICE", "es-US-PalomaNeural")


async def generate_edge_tts(text, voice=None):
    if voice is None:
        voice = TTS_VOICE
    communicate = edge_tts.Communicate(text, voice)
    tmp_path = os.path.join(os.path.dirname(__file__), "tmp_audio.mp3")
    await communicate.save(tmp_path)
    with open(tmp_path, "rb") as f:
        audio_data = f.read()
    os.remove(tmp_path)
    return base64.b64encode(audio_data).decode("utf-8")


@app.before_request
def log_config():
    app.logger.info(f"Gemini configured: {GEMINI_CONFIGURED}")
    app.logger.info(f"TTS Voice: {TTS_VOICE}")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/speak", methods=["POST"])
def speak_text():
    try:
        data = request.json
        text = data.get("text", "")

        if not text:
            return jsonify({"error": "No text provided"}), 400

        app.logger.info(f"Generando audio con edge-tts: {text[:50]}...")
        audio_content = asyncio.run(generate_edge_tts(text))

        return jsonify(
            {
                "audioContent": audio_content,
                "audioUrl": f"data:audio/mp3;base64,{audio_content}",
                "useBrowserTTS": False,
                "engine": "edge-tts",
            }
        )

    except Exception as e:
        app.logger.error(f"Error en edge-tts: {str(e)}")
        return jsonify(
            {
                "audioContent": None,
                "audioUrl": None,
                "useBrowserTTS": True,
                "text": text,
                "error": str(e),
            }
        )


def gemini_response(user_message, context=""):
    if not GEMINI_CONFIGURED or gemini_model is None:
        return None
    try:
        system_prompt = """Eres Claudia García, abogada virtual especializada en Derecho Laboral de TusAbogados.com.

## Tu personalidad
- Eres una abogada laboralista con experiencia.
- Hablas con profesionalismo y calidez, como lo haría un abogado real.
- Usas terminología legal cuando es apropiado, pero la explicas en lenguaje sencillo.
- Transmites confianza, seguridad y empatía.
- Ejemplos de expresiones naturales: "Entiendo perfectamente su situación", "Esto es algo que manejamos con frecuencia", "Le comento que en estos casos...", "Es importante que sepa que...", "Procederemos a..."

## Reglas
- Responde en máximo 2-3 oraciones.
- Si te preguntan algo de derecho laboral, responde con precisión legal pero explicando en lenguaje simple.
- Usa términos como: despido injustificado, justa causa, liquidación, prestaciones sociales, indemnización, conciliación, juzgado laboral, derecho laboral.
- Siempre orienta pero NO das asesoría legal definitiva, eso lo hace el abogado humano.
- Nunca uses expresiones informales como "genial", "perfecto", "listo", "dale". Usa: "Entiendo", "Comprendo", "Procederé a", "Le comento que"."""

        rag_context = ""
        if RAG_AVAILABLE:
            try:
                docs = search_knowledge(user_message, n_results=3)
                if docs:
                    rag_parts = []
                    for d in docs:
                        rag_parts.append(f"[Fuente: {d['source']}]\n{d['text']}")
                    rag_context = (
                        "\n\n## Base de conocimiento (usa esta información si es relevante):\n"
                        + "\n---\n".join(rag_parts)
                    )
                    app.logger.info(f"RAG: {len(docs)} docs encontrados")
                else:
                    app.logger.info("RAG: 0 docs encontrados")
            except Exception as e:
                app.logger.error(f"RAG error: {e}")

        prompt = f"""{system_prompt}{rag_context}

Contexto: {context}
Usuario: {user_message}"""
        response = gemini_model.generate_content(prompt)
        return response.text
    except Exception as e:
        app.logger.error(f"Error Gemini: {str(e)}")
        return None


def openrouter_response(user_message, context=""):
    if not OPENROUTER_CONFIGURED:
        return None
    try:
        system_prompt = """Eres Claudia García, abogada virtual especializada en Derecho Laboral de TusAbogados.com.

## Tu personalidad
- Eres una abogada laboralista con experiencia.
- Hablas con profesionalismo y calidez, como lo haría un abogado real.
- Usas terminología legal cuando es apropiado, pero la explicas en lenguaje sencillo.
- Transmites confianza, seguridad y empatía.
- Ejemplos de expresiones naturales: "Entiendo perfectamente su situación", "Esto es algo que manejamos con frecuencia", "Le comento que en estos casos...", "Es importante que sepa que...", "Procederemos a..."

## Reglas
- Responde en máximo 2-3 oraciones.
- Si te preguntan algo de derecho laboral, responde con precisión legal pero explicando en lenguaje simple.
- Usa términos como: despido injustificado, justa causa, liquidación, prestaciones sociales, indemnización, conciliación, juzgado laboral, derecho laboral.
- Siempre orienta pero NO das asesoría legal definitiva, eso lo hace el abogado humano.
- Nunca uses expresiones informales como "genial", "perfecto", "listo", "dale". Usa: "Entiendo", "Comprendo", "Procederé a", "Le comento que"."""

        rag_context = ""
        if RAG_AVAILABLE:
            try:
                docs = search_knowledge(user_message, n_results=3)
                if docs:
                    rag_parts = []
                    for d in docs:
                        rag_parts.append(f"[Fuente: {d['source']}]\n{d['text']}")
                    rag_context = (
                        "\n\n## Base de conocimiento (usa esta información si es relevante):\n"
                        + "\n---\n".join(rag_parts)
                    )
                    app.logger.info(f"RAG: {len(docs)} docs encontrados")
                else:
                    app.logger.info("RAG: 0 docs encontrados")
            except Exception as e:
                app.logger.error(f"RAG error: {e}")

        prompt = f"""{system_prompt}{rag_context}

Contexto: {context}
Usuario: {user_message}"""

        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://tusabogados.com",
            "X-Title": "TusAbogados.com - Asistente Legal IA",
        }
        payload = {
            "model": OPENROUTER_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
            "max_tokens": 500,
        }
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        app.logger.error(f"Error OpenRouter: {str(e)}")
        return None


def get_llm_response(user_message, context=""):
    if OPENROUTER_CONFIGURED:
        return openrouter_response(user_message, context)
    elif GEMINI_CONFIGURED:
        return gemini_response(user_message, context)
    return None


def validate_name(name):
    if not name or len(name.strip()) < 2:
        return (
            False,
            "Por favor, indíqueme su nombre completo para proceder con la cita.",
        )
    if re.match(r"^[\d\s]+$", name.strip()):
        return (
            False,
            "El nombre ingresado no parece válido. Por favor, indíqueme su nombre completo.",
        )
    return True, name.strip()


def validate_subtype(subtype):
    if not subtype or len(subtype.strip()) < 3:
        return (
            False,
            "¿Qué tipo de situación laboral está atrayendo? Por ejemplo, despido injustificado, acoso laboral, impago de prestaciones...",
        )
    return True, subtype.strip()


def validate_description(desc):
    if not desc or len(desc.strip()) < 5:
        return (
            False,
            "Le agradecería que me describa brevemente los hechos de su caso: fechas, personas involucradas y circunstancias.",
        )
    return True, desc.strip()


def validate_email(email):
    if not email:
        return (
            False,
            "¿Cuál es su correo electrónico? Lo necesito para enviarle la confirmación de la cita.",
        )
    if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email):
        return (
            False,
            "El correo electrónico ingresado no tiene un formato válido. Por favor, verifíquelo e ingréselo nuevamente (ejemplo: nombre@correo.com).",
        )
    return True, email.strip()


def validate_phone(phone):
    if not phone:
        return False, "¿Cuál es su número de teléfono de contacto?"
    digits = re.sub(r"[^0-9]", "", phone)
    if len(digits) < 7 or len(digits) > 15:
        return (
            False,
            "El número de teléfono ingresado no parece correcto. Por favor, verifíquelo e ingréselo sin espacios ni guiones (ejemplo: 3001234567).",
        )
    return True, digits


def limpiar_estado_chat():
    """Limpia el estado de la conversación."""
    attrs = [
        "user_name",
        "user_email",
        "user_phone",
        "case_description",
        "case_subtype",
        "appointment_time",
        "user_role",
        "case_category",
        "paso_actual",
        "datos_usuario",
    ]
    for attr in attrs:
        if hasattr(chat, attr):
            delattr(chat, attr)


def obtener_estado_chat():
    """Obtiene el estado actual de la conversación como diccionario."""
    user_name = getattr(chat, "user_name", "")
    user_role = getattr(chat, "user_role", "")
    case_category = getattr(chat, "case_category", "")
    user_email = getattr(chat, "user_email", "")
    user_phone = getattr(chat, "user_phone", "")
    return {
        "user_name": user_name,
        "nombre": user_name,
        "user_email": user_email,
        "correo": user_email,
        "user_phone": user_phone,
        "telefono": user_phone,
        "case_description": getattr(chat, "case_description", ""),
        "case_subtype": getattr(chat, "case_subtype", ""),
        "appointment_time": getattr(chat, "appointment_time", ""),
        "user_role": user_role,
        "rol": user_role,
        "case_category": case_category,
        "categoria": case_category,
        "paso_actual": getattr(chat, "paso_actual", "saludo_inicial"),
    }


def guardar_estado_campo(campo, valor):
    """Guarda un campo en el estado de la conversación."""
    setattr(chat, campo, valor)


@app.route("/api/chat", methods=["POST"])
def chat():
    try:
        from guion import PASOS, obtener_paso, formatear_mensaje, validar_respuesta

        data = request.json
        message = data.get("message", "")
        accion_boton = data.get("action", None)

        if not message and not accion_boton:
            return jsonify({"error": "No message provided"}), 400

        if accion_boton == "nueva_llamada":
            limpiar_estado_chat()
            chat.paso_actual = "saludo_inicial"
            chat.datos_usuario = {}
            paso = obtener_paso("saludo_inicial")
            response = paso["mensaje"]
            return jsonify(
                {
                    "response": response,
                    "end_call": False,
                    "buttons": None,
                    "step": "saludo_inicial",
                }
            )

        message_lower = (message or "").lower().strip()

        is_greeting = any(
            word in message_lower
            for word in [
                "hola",
                "buenos días",
                "buenas tardes",
                "saludos",
                "buenas",
                "buenos",
                "iniciar",
                "empezar",
            ]
        )

        is_farewell = (
            message_lower
            in ["gracias", "adiós", "chao", "hasta luego", "no gracias", "eso es todo"]
            or message_lower.startswith("gracias ")
            or message_lower.startswith("adiós ")
            or message_lower.startswith("chao ")
            or message_lower.startswith("hasta luego")
            or message_lower.startswith("no gracias")
            or message_lower.startswith("eso es todo")
            or message_lower.endswith("gracias")
            or message_lower.endswith("adiós")
            or message_lower.endswith("chao")
        )

        is_question = (
            "¿" in message_lower
            or "?" in message_lower
            or message_lower.startswith("qué ")
            or message_lower.startswith("que ")
            or message_lower.startswith("cómo ")
            or message_lower.startswith("como ")
            or message_lower.startswith("cuál ")
            or message_lower.startswith("cual ")
            or message_lower.startswith("cuáles ")
            or message_lower.startswith("cuales ")
            or message_lower.startswith("cuánto ")
            or message_lower.startswith("cuanto ")
            or message_lower.startswith("dónde ")
            or message_lower.startswith("donde ")
            or message_lower.startswith("quién ")
            or message_lower.startswith("quien ")
            or message_lower.startswith("por qué ")
            or message_lower.startswith("por que ")
            or message_lower.startswith("para qué ")
            or message_lower.startswith("para que ")
        )

        paso_actual_id = getattr(chat, "paso_actual", "saludo_inicial")
        paso_actual = obtener_paso(paso_actual_id)

        if is_greeting and paso_actual_id == "saludo_inicial":
            limpiar_estado_chat()
            chat.paso_actual = "saludo_inicial"
            chat.datos_usuario = {}
            paso = obtener_paso("saludo_inicial")
            response = paso["mensaje"]
            return jsonify(
                {
                    "response": response,
                    "end_call": False,
                    "buttons": None,
                    "step": "saludo_inicial",
                }
            )

        if paso_actual and paso_actual.get("fin"):
            if is_farewell or accion_boton == "despedida":
                name = getattr(chat, "user_name", "")
                response = f"Gracias a usted. Ha sido un gusto atenderte. Un abogado se comunicará contigo en la fecha acordada. ¡Que tengas un excelente día!"
                limpiar_estado_chat()
                return jsonify(
                    {
                        "response": response,
                        "end_call": True,
                        "buttons": None,
                        "step": "final",
                    }
                )

        if paso_actual_id in ["manejo_post_cita", "despedida", "final"]:
            if is_farewell or accion_boton == "despedida":
                name = getattr(chat, "user_name", "")
                response = f"Gracias a usted. ¡Que tengas un excelente día!"
                limpiar_estado_chat()
                return jsonify(
                    {
                        "response": response,
                        "end_call": True,
                        "buttons": None,
                        "step": "final",
                    }
                )
            if is_question:
                context = (
                    f"Usuario: {getattr(chat, 'user_name', 'usuario')}. Pregunta libre."
                )
                rag_response = None
                if RAG_AVAILABLE:
                    try:
                        docs = search_knowledge(message, n_results=3)
                        if docs:
                            rag_parts = []
                            for d in docs:
                                rag_parts.append(
                                    f"[Fuente: {d['source']}]\n{d['text']}"
                                )
                            rag_context = "\n---\n".join(rag_parts)
                            rag_response = (
                                f"Según la información disponible:\n\n{rag_context}"
                            )
                    except Exception as e:
                        app.logger.error(f"RAG error: {e}")
                if rag_response:
                    response = (
                        f"{rag_response}\n\n¿Hay algo más en lo que pueda asistirle?"
                    )
                else:
                    llm_resp = get_llm_response(message, context=context)
                    if llm_resp:
                        response = (
                            f"{llm_resp}\n\n¿Hay algo más en lo que pueda asistirle?"
                        )
                    else:
                        response = "No tengo información específica sobre esa consulta. Un abogado podrá orientarte personalmente."
                buttons = [
                    {
                        "texto": "Sí, tengo otra duda",
                        "valor": "consulta_adicional",
                        "descripcion": "",
                    },
                    {"texto": "No, gracias", "valor": "despedida", "descripcion": ""},
                ]
                return jsonify(
                    {
                        "response": response,
                        "end_call": False,
                        "buttons": buttons,
                        "step": paso_actual_id,
                    }
                )
            response = "¿Hay algo más en lo que pueda ayudarte?"
            buttons = [
                {
                    "texto": "Sí, tengo otra pregunta",
                    "valor": "consulta_adicional",
                    "descripcion": "",
                },
                {"texto": "No, gracias", "valor": "despedida", "descripcion": ""},
            ]
            return jsonify(
                {
                    "response": response,
                    "end_call": False,
                    "buttons": buttons,
                    "step": paso_actual_id,
                }
            )

        if is_question and paso_actual_id not in [
            "saludo_inicial",
            "identificacion_rol",
            "categorizacion_caso",
            "verificacion_pruebas",
            "descripcion_caso",
            "captura_correo",
            "captura_telefono",
            "confirmacion_cita",
            "propuesta_horario",
            "rechazo_horario",
        ]:
            context = (
                f"Usuario: {getattr(chat, 'user_name', 'usuario')}. Pregunta libre."
            )
            rag_response = None
            if RAG_AVAILABLE:
                try:
                    docs = search_knowledge(message, n_results=3)
                    if docs:
                        rag_parts = []
                        for d in docs:
                            rag_parts.append(f"[Fuente: {d['source']}]\n{d['text']}")
                        rag_context = "\n---\n".join(rag_parts)
                        rag_response = (
                            f"Según la información disponible:\n\n{rag_context}"
                        )
                except Exception as e:
                    app.logger.error(f"RAG error: {e}")
            if rag_response:
                response = f"{rag_response}\n\n¿Hay algo más en lo que pueda asistirle?"
            else:
                llm_resp = get_llm_response(message, context=context)
                if llm_resp:
                    response = f"{llm_resp}\n\n¿Hay algo más en lo que pueda asistirle?"
                else:
                    response = "No tengo información específica sobre esa consulta. Un abogado podrá orientarte personalmente."
            buttons = [
                {
                    "texto": "Continuar con mi caso",
                    "valor": "continuar",
                    "descripcion": "",
                },
                {"texto": "No, gracias", "valor": "despedida", "descripcion": ""},
            ]
            return jsonify(
                {
                    "response": response,
                    "end_call": False,
                    "buttons": buttons,
                    "step": paso_actual_id,
                }
            )

        if is_farewell and paso_actual_id not in [
            "saludo_inicial",
            "identificacion_rol",
            "categorizacion_caso",
            "verificacion_pruebas",
            "descripcion_caso",
            "captura_correo",
            "captura_telefono",
            "confirmacion_cita",
            "confirmacion_cita_opcion",
            "rechazo_horario",
        ]:
            name = getattr(chat, "user_name", "")
            if hasattr(chat, "appointment_time"):
                response = f"Entendido, {name}. Un abogado se comunicará contigo en la fecha acordada. Saludos cordiales."
            else:
                response = f"Entendido, {name}. Un abogado se comunicará contigo a la brevedad. Saludos cordiales."
            limpiar_estado_chat()
            return jsonify(
                {
                    "response": response,
                    "end_call": True,
                    "buttons": None,
                    "step": "final",
                }
            )

        if accion_boton:
            if accion_boton == "aceptar_cita":
                chat.paso_actual = "propuesta_horario"
                response = f"Perfecto, {getattr(chat, 'user_name', 'usuario')}. Te propongo el próximo Lunes 29 de Septiembre a las 10:30 de la mañana. ¿Te parece bien esa fecha y hora?"
                buttons = [
                    {
                        "texto": "Sí, confirmo",
                        "valor": "confirmar",
                        "descripcion": "",
                    },
                    {
                        "texto": "No, no me viene bien",
                        "valor": "rechazar",
                        "descripcion": "",
                    },
                ]
                return jsonify(
                    {
                        "response": response,
                        "end_call": False,
                        "buttons": buttons,
                        "step": "propuesta_horario",
                    }
                )

            if accion_boton == "rechazar_cita":
                chat.paso_actual = "manejo_post_cita"
                name = getattr(chat, "user_name", "")
                response = f"Entendido, {name}. Uno de nuestros abogados especializados se contactará con usted según los datos agendados y le ampliará toda la información al respecto. ¿Hay alguna otra cosa en la que pueda asistirle?"
                buttons = [
                    {
                        "texto": "Sí, tengo otra duda",
                        "valor": "consulta_adicional",
                        "descripcion": "",
                    },
                    {"texto": "No, gracias", "valor": "despedida", "descripcion": ""},
                ]
                return jsonify(
                    {
                        "response": response,
                        "end_call": False,
                        "buttons": buttons,
                        "step": "manejo_post_cita",
                    }
                )

            if accion_boton == "continuar":
                paso_actual = obtener_paso(paso_actual_id)
                if paso_actual:
                    datos = obtener_estado_chat()
                    response = formatear_mensaje(paso_actual, datos)
                    return jsonify(
                        {
                            "response": response,
                            "end_call": False,
                            "buttons": paso_actual.get("botones"),
                            "step": paso_actual_id,
                        }
                    )
                response = "¿Hay algo más en lo que pueda ayudarte?"
                return jsonify(
                    {
                        "response": response,
                        "end_call": False,
                        "buttons": None,
                        "step": paso_actual_id,
                    }
                )

            if accion_boton in ["demandado", "demandante"]:
                guardar_estado_campo(
                    "user_role",
                    "demandado" if accion_boton == "demandado" else "demandante",
                )
                chat.paso_actual = "categorizacion_caso"
                paso_cat = obtener_paso("categorizacion_caso")
                datos = obtener_estado_chat()
                response = formatear_mensaje(paso_cat, datos)
                return jsonify(
                    {
                        "response": response,
                        "end_call": False,
                        "buttons": paso_cat.get("botones"),
                        "step": "categorizacion_caso",
                    }
                )

            if accion_boton in ["civil", "laboral", "penal", "no_definida"]:
                guardar_estado_campo("case_category", accion_boton)
                chat.paso_actual = "verificacion_pruebas"
                paso_pruebas = obtener_paso("verificacion_pruebas")
                datos = obtener_estado_chat()
                response = formatear_mensaje(paso_pruebas, datos)
                return jsonify(
                    {
                        "response": response,
                        "end_call": False,
                        "buttons": paso_pruebas["botones"],
                        "step": "verificacion_pruebas",
                    }
                )

            if accion_boton in ["si_pruebas", "no_pruebas"]:
                guardar_estado_campo("has_evidence", accion_boton)
                chat.paso_actual = "descripcion_caso"
                paso_desc = obtener_paso("descripcion_caso")
                datos = obtener_estado_chat()
                if accion_boton == "si_pruebas":
                    response = "Excelente. Cuéntame brevemente qué sucedió en tu caso — con eso podré entender mejor tu situación. También puedes adjuntar los archivos que consideres relevantes (documentos, fotos, audios, etc.)."
                else:
                    response = formatear_mensaje(paso_desc, datos)
                return jsonify(
                    {
                        "response": response,
                        "end_call": False,
                        "buttons": None,
                        "step": "descripcion_caso",
                        "show_upload": accion_boton == "si_pruebas",
                    }
                )

            if accion_boton == "confirmar":
                chat.appointment_time = "Lunes 29 de Septiembre - 10:30 am"
                chat.paso_actual = "manejo_post_cita"
                name = getattr(chat, "user_name", "")
                email = getattr(chat, "user_email", "")
                phone = getattr(chat, "user_phone", "")
                category = getattr(chat, "case_category", "")
                response = f"""📅 Fecha: Lunes 29 de septiembre - 10:30 a.m.
📧 Correo de confirmación: {email}
📱 Teléfono de contacto: {phone}

He analizado tu caso de {category}. Te comento que, si el monto supera los 10 millones de pesos, no hay costo inicial: solo se aplica un honoratorio del 10% en caso de éxito.

¿Hay algo más en lo que pueda ayudarte?"""
                buttons = [
                    {
                        "texto": "Sí, tengo otra duda",
                        "valor": "consulta_adicional",
                        "descripcion": "",
                    },
                    {"texto": "No, gracias", "valor": "despedida", "descripcion": ""},
                ]
                return jsonify(
                    {
                        "response": response,
                        "end_call": False,
                        "buttons": buttons,
                        "step": "manejo_post_cita",
                    }
                )

            if accion_boton == "rechazar":
                chat.paso_actual = "rechazo_horario"
                paso_rechazo = obtener_paso("rechazo_horario")
                datos = obtener_estado_chat()
                response = formatear_mensaje(paso_rechazo, datos)
                return jsonify(
                    {
                        "response": response,
                        "end_call": False,
                        "buttons": paso_rechazo.get("botones"),
                        "step": "rechazo_horario",
                    }
                )

            if accion_boton == "otra_fecha":
                chat.appointment_time = "Miércoles 1 de Octubre - 3:30 pm"
                chat.paso_actual = "manejo_post_cita"
                name = getattr(chat, "user_name", "")
                email = getattr(chat, "user_email", "")
                phone = getattr(chat, "user_phone", "")
                category = getattr(chat, "case_category", "")
                response = f"""📅 Fecha: Miércoles 1 de octubre - 3:30 p.m.
📧 Correo de confirmación: {email}
📱 Teléfono de contacto: {phone}

He revisado tu caso de {category}. Un abogado se comunicará contigo en la fecha acordada.

¿Hay algo más en lo que pueda ayudarte?"""
                buttons = [
                    {
                        "texto": "Sí, tengo otra duda",
                        "valor": "consulta_adicional",
                        "descripcion": "",
                    },
                    {"texto": "No, gracias", "valor": "despedida", "descripcion": ""},
                ]
                return jsonify(
                    {
                        "response": response,
                        "end_call": False,
                        "buttons": buttons,
                        "step": "manejo_post_cita",
                    }
                )

            if accion_boton == "contactar_abogado":
                chat.paso_actual = "manejo_post_cita"
                name = getattr(chat, "user_name", "")
                response = f"Perfecto, {name}. Un abogado se comunicará contigo a la brevedad para atender tu caso de forma personalizada. ¿Hay algo más en lo que pueda ayudarte?"
                buttons = [
                    {
                        "texto": "Sí, tengo otra duda",
                        "valor": "consulta_adicional",
                        "descripcion": "",
                    },
                    {"texto": "No, gracias", "valor": "despedida", "descripcion": ""},
                ]
                return jsonify(
                    {
                        "response": response,
                        "end_call": False,
                        "buttons": buttons,
                        "step": "manejo_post_cita",
                    }
                )

            if accion_boton == "consulta_adicional":
                chat.paso_actual = "manejo_post_cita"
                name = getattr(chat, "user_name", "")
                response = f"Entendido, {name}. Listo, he registrado tu consulta adicional. Un abogado especializado se pondrá en contacto contigo según la cita agendada y te brindará toda la información que necesitas. ¿Hay algo más en lo que pueda ayudarte?"
                buttons = [
                    {
                        "texto": "Sí, tengo otra duda",
                        "valor": "consulta_adicional",
                        "descripcion": "",
                    },
                    {"texto": "No, gracias", "valor": "despedida", "descripcion": ""},
                ]
                return jsonify(
                    {
                        "response": response,
                        "end_call": False,
                        "buttons": buttons,
                        "step": "manejo_post_cita",
                    }
                )

            if accion_boton == "despedida":
                name = getattr(chat, "user_name", "")
                response = f"Gracias a usted. Ha sido un gusto atenderte. Un abogado se comunicará contigo en la fecha acordada. ¡Que tengas un excelente día!"
                limpiar_estado_chat()
                return jsonify(
                    {
                        "response": response,
                        "end_call": True,
                        "buttons": None,
                        "step": "final",
                    }
                )

        if paso_actual_id == "saludo_inicial":
            valid, result = validar_respuesta(paso_actual, message)
            if valid:
                chat.user_name = result
                chat.paso_actual = "identificacion_rol"
                paso_rol = obtener_paso("identificacion_rol")
                datos = obtener_estado_chat()
                response = formatear_mensaje(paso_rol, datos)
                return jsonify(
                    {
                        "response": response,
                        "end_call": False,
                        "buttons": paso_rol.get("botones"),
                        "step": "identificacion_rol",
                    }
                )
            else:
                return jsonify(
                    {
                        "response": result,
                        "end_call": False,
                        "buttons": None,
                        "step": paso_actual_id,
                    }
                )

        if paso_actual_id == "descripcion_caso":
            valid, result = validar_respuesta(paso_actual, message)
            if valid:
                chat.case_description = result
                chat.paso_actual = "captura_correo"
                paso_correo = obtener_paso("captura_correo")
                datos = obtener_estado_chat()
                response = formatear_mensaje(paso_correo, datos)
                return jsonify(
                    {
                        "response": response,
                        "end_call": False,
                        "buttons": None,
                        "step": "captura_correo",
                    }
                )
            else:
                return jsonify(
                    {
                        "response": result,
                        "end_call": False,
                        "buttons": None,
                        "step": paso_actual_id,
                    }
                )

        if paso_actual_id == "captura_correo":
            valid, result = validar_respuesta(paso_actual, message)
            if valid:
                chat.user_email = result
                chat.paso_actual = "captura_telefono"
                paso_tel = obtener_paso("captura_telefono")
                datos = obtener_estado_chat()
                response = formatear_mensaje(paso_tel, datos)
                return jsonify(
                    {
                        "response": response,
                        "end_call": False,
                        "buttons": paso_tel.get("botones"),
                        "step": "captura_telefono",
                    }
                )
            else:
                return jsonify(
                    {
                        "response": result,
                        "end_call": False,
                        "buttons": None,
                        "step": paso_actual_id,
                    }
                )

        if paso_actual_id == "captura_telefono":
            valid, result = validar_respuesta(paso_actual, message)
            if valid:
                chat.user_phone = result
                chat.paso_actual = "confirmacion_cita"
                datos = obtener_estado_chat()
                response = f"Perfecto, ya tengo toda la información necesaria para orientarte en tu proceso. ¿Te parece bien si agendamos una cita con uno de nuestros abogados especializados para que te ayude con tu caso?"
                buttons = [
                    {
                        "texto": "Sí, agendar cita",
                        "valor": "consulta_adicional",
                        "descripcion": "",
                    },
                    {
                        "texto": "No, por ahora no",
                        "valor": "despedida",
                        "descripcion": "",
                    },
                ]
                return jsonify(
                    {
                        "response": response,
                        "end_call": False,
                        "buttons": buttons,
                        "step": "confirmacion_cita_opcion",
                    }
                )
            else:
                return jsonify(
                    {
                        "response": result,
                        "end_call": False,
                        "buttons": None,
                        "step": paso_actual_id,
                    }
                )

        if paso_actual_id == "confirmacion_cita":
            if accion_boton == "confirmar" or any(
                w in message_lower for w in ["sí", "si", "ok", "confirmo", "de acuerdo"]
            ):
                chat.appointment_time = "Lunes 29 de Septiembre - 10:30 am"
                chat.paso_actual = "manejo_post_cita"
                name = getattr(chat, "user_name", "")
                email = getattr(chat, "user_email", "")
                phone = getattr(chat, "user_phone", "")
                category = getattr(chat, "case_category", "")
                appointment_date = getattr(
                    chat, "appointment_time", "Lunes 29 de septiembre - 10:30 a.m."
                )
                response = f"""📅 Fecha: {appointment_date}
📧 Correo de confirmación: {email}
📱 Teléfono de contacto: {phone}

He analizado tu caso de {category}. Te comento que, si el monto supera los 10 millones de pesos, no hay costo inicial: solo se aplica un honoratorio del 10% en caso de éxito.

¿Hay algo más en lo que pueda ayudarte?"""
                buttons = [
                    {
                        "texto": "Sí, tengo otra duda",
                        "valor": "consulta_adicional",
                        "descripcion": "",
                    },
                    {"texto": "No, gracias", "valor": "despedida", "descripcion": ""},
                ]
                return jsonify(
                    {
                        "response": response,
                        "end_call": False,
                        "buttons": buttons,
                        "step": "manejo_post_cita",
                    }
                )
            if accion_boton == "rechazar" or any(
                w in message_lower
                for w in ["no", "no me viene", "otro horario", "otra hora"]
            ):
                chat.paso_actual = "rechazo_horario"
                paso_rechazo = obtener_paso("rechazo_horario")
                datos = obtener_estado_chat()
                response = formatear_mensaje(paso_rechazo, datos)
                return jsonify(
                    {
                        "response": response,
                        "end_call": False,
                        "buttons": paso_rechazo.get("botones"),
                        "step": "rechazo_horario",
                    }
                )

        response = "¿Hay algo más en lo que pueda ayudarte?"
        buttons = [
            {
                "texto": "Sí, tengo otra duda",
                "valor": "consulta_adicional",
                "descripcion": "",
            },
            {"texto": "No, gracias", "valor": "despedida", "descripcion": ""},
        ]
        return jsonify(
            {
                "response": response,
                "end_call": False,
                "buttons": buttons,
                "step": paso_actual_id,
            }
        )

    except Exception as e:
        app.logger.error(f"Exception in chat: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/knowledge/upload", methods=["POST"])
def upload_knowledge():
    if not RAG_AVAILABLE:
        return jsonify(
            {"error": "Módulo RAG no disponible. Verifique dependencias."}
        ), 500
    if "file" not in request.files:
        return jsonify({"error": "No se envió ningún archivo."}), 400
    file = request.files["file"]
    if not file.filename.endswith(".pdf"):
        return jsonify({"error": "Solo se permiten archivos PDF."}), 400

    # Check file size (max 5MB to prevent OOM on Render free tier)
    file.seek(0, 2)  # Seek to end
    file_size = file.tell()
    file.seek(0)  # Seek back to start
    max_size = 5 * 1024 * 1024  # 5MB
    if file_size > max_size:
        return jsonify(
            {
                "error": f"El archivo excede el límite de 5MB. Tamaño actual: {file_size // (1024 * 1024)}MB"
            }
        ), 400

    try:
        tmp_dir = tempfile.mkdtemp()
        tmp_path = os.path.join(tmp_dir, file.filename)
        file.save(tmp_path)
        app.logger.info(f"PDF guardado temporalmente: {tmp_path}")

        num_chunks, msg = add_pdf(tmp_path)
        app.logger.info(f"Resultado add_pdf: {msg}")

        # Cleanup
        try:
            os.remove(tmp_path)
            os.rmdir(tmp_dir)
        except Exception:
            pass

        if num_chunks == 0:
            return jsonify({"error": msg}), 400
        return jsonify({"message": msg, "chunks": num_chunks})
    except Exception as e:
        app.logger.error(f"Error uploading PDF: {str(e)}", exc_info=True)
        return jsonify({"error": f"Error al procesar el PDF: {str(e)}"}), 500


@app.route("/api/knowledge/documents", methods=["GET"])
def list_knowledge():
    if not RAG_AVAILABLE:
        return jsonify({"documents": [], "rag_available": False})
    docs = list_documents()
    return jsonify({"documents": docs, "rag_available": True})


@app.route("/api/knowledge/delete", methods=["POST"])
def delete_knowledge():
    if not RAG_AVAILABLE:
        return jsonify({"error": "Módulo RAG no disponible."}), 500
    data = request.json
    source = data.get("source", "")
    if not source:
        return jsonify({"error": "Nombre del documento no proporcionado."}), 400
    success, msg = delete_document(source)
    if success:
        return jsonify({"message": msg})
    return jsonify({"error": msg}), 404


@app.route("/api/health", methods=["GET"])
def health_check():
    llm_provider = (
        "openrouter"
        if OPENROUTER_CONFIGURED
        else ("gemini" if GEMINI_CONFIGURED else "none")
    )
    llm_model = (
        OPENROUTER_MODEL
        if OPENROUTER_CONFIGURED
        else ("gemini-2.0-flash" if GEMINI_CONFIGURED else "none")
    )
    return jsonify(
        {
            "status": "healthy",
            "gemini_configured": GEMINI_CONFIGURED,
            "openrouter_configured": OPENROUTER_CONFIGURED,
            "llm_provider": llm_provider,
            "llm_model": llm_model,
            "tts_voice": TTS_VOICE,
            "service": f"edge-tts ({TTS_VOICE}) + {llm_model}",
        }
    )


@app.route("/api/test-embedding", methods=["GET"])
def test_embedding():
    """Test endpoint to check if Gemini embeddings work."""
    try:
        import google.generativeai as genai

        api_key = os.environ.get("GEMINI_API_KEY", "")
        if not api_key:
            return jsonify({"error": "GEMINI_API_KEY no configurada"}), 500
        genai.configure(api_key=api_key)
        result = genai.embed_content(
            model="models/gemini-embedding-001",
            content="Test de embedding",
            output_dimensionality=768,
        )
        return jsonify(
            {
                "status": "ok",
                "dimension": len(result["embedding"]),
                "first_5_values": result["embedding"][:5],
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/test-search", methods=["POST"])
def test_search():
    """Test RAG search directly."""
    if not RAG_AVAILABLE:
        return jsonify({"error": "RAG not available"}), 500
    data = request.json or {}
    query = data.get("query", "Convención de Viena tratados")
    try:
        docs = search_knowledge(query, n_results=3)
        return jsonify({"query": query, "results": docs, "count": len(docs)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/pinecone-status", methods=["GET"])
def pinecone_status():
    """Check Pinecone index status directly."""
    if not RAG_AVAILABLE:
        return jsonify({"error": "RAG not available"}), 500
    try:
        from rag import get_pc, get_index, INDEX_NAME, DIMENSION

        pc = get_pc()
        if pc is None:
            return jsonify({"error": "Pinecone not connected"}), 500

        existing = pc.list_indexes()
        index_names = [idx.name for idx in existing.indexes]

        if INDEX_NAME not in index_names:
            return jsonify(
                {"status": "no_index", "indexes": index_names, "expected": INDEX_NAME}
            )

        idx = pc.Index(INDEX_NAME)
        stats = idx.describe_index_stats()

        return jsonify(
            {
                "status": "ok",
                "index": INDEX_NAME,
                "dimension": DIMENSION,
                "total_vectors": stats.total_vector_count,
                "namespaces": {k: v.vector_count for k, v in stats.namespaces.items()}
                if stats.namespaces
                else {},
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/voices", methods=["GET"])
def list_voices():
    voices = [
        {
            "id": "es-US-PalomaNeural",
            "name": "Paloma",
            "gender": "Femenina",
            "region": "Estados Unidos (español)",
            "recommended": True,
        },
        {
            "id": "es-MX-DaliaNeural",
            "name": "Dalia",
            "gender": "Femenina",
            "region": "México",
        },
        {
            "id": "es-MX-JorgeNeural",
            "name": "Jorge",
            "gender": "Masculino",
            "region": "México",
        },
        {
            "id": "es-ES-ElviraNeural",
            "name": "Elvira",
            "gender": "Femenina",
            "region": "España",
        },
        {
            "id": "es-ES-AlvaroNeural",
            "name": "Álvaro",
            "gender": "Masculino",
            "region": "España",
        },
    ]
    return jsonify({"voices": voices, "current": TTS_VOICE})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
