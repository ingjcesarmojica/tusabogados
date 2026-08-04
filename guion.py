"""
Guion Conversacional - Agente IA Legal "Claudia García"
Tusabogados.com

Flujo conversacional estructurado para chat y llamadas.
"""

# PASOS DEL GUION CONVERSACIONAL
PASOS = {
    "saludo_inicial": {
        "id": "saludo_inicial",
        "siguiente": "captura_nombre",
        "mensaje": "Bienvenido a TusAbogados.com. Para personalizar su atención, ¿con quién tengo el gusto de hablar? Por favor, dígame su nombre.",
        "validar": None,
        "botones": None,
    },
    "captura_nombre": {
        "id": "captura_nombre",
        "siguiente": "identificacion_rol",
        "mensaje": "Mucho gusto {nombre}. Para orientarle mejor, necesito saber su rol en el caso.",
        "validar": "nombre",
        "botones": None,
        "campo": "user_name",
    },
    "identificacion_rol": {
        "id": "identificacion_rol",
        "siguiente": "identificacion_rol_opcion",
        "mensaje": "¿Se considera víctima o demandante en esta situación?",
        "validar": None,
        "botones": [
            {
                "texto": "Víctima",
                "valor": "victima",
                "descripcion": "Si sufrió un accidente, le deben dinero, fue estafado, o sufrió algún daño o perjuicio.",
            },
            {
                "texto": "Demandante",
                "valor": "demandante",
                "descripcion": "Si quiere iniciar una demanda por divorcio, reclamar una herencia, demandar por incumplimiento de contrato, o exigir sus derechos laborales.",
            },
        ],
        "campo": "user_role",
    },
    "identificacion_rol_opcion": {
        "id": "identificacion_rol_opcion",
        "siguiente": "categorizacion_caso",
        "mensaje": "Entendido {nombre}, como {rol}. Ahora necesito saber el tipo de caso.",
        "validar": None,
        "botones": None,
    },
    "categorizacion_caso": {
        "id": "categorizacion_caso",
        "siguiente": "categorizacion_caso_opcion",
        "mensaje": "¿En qué categoría cree que está su caso?",
        "validar": None,
        "botones": [
            {
                "texto": "Categoría Civil",
                "valor": "civil",
                "descripcion": "Divorcio, herencias, contratos, propiedad.",
            },
            {
                "texto": "Categoría Laboral",
                "valor": "laboral",
                "descripcion": "Despido injustificado, acoso laboral, prestaciones.",
            },
            {
                "texto": "Categoría Penal",
                "valor": "penal",
                "descripcion": "Robos, agresiones, amenazas, estafas.",
            },
            {
                "texto": "No sé cuál es mi categoría",
                "valor": "no_definida",
                "descripcion": "Un abogado le orientará.",
            },
        ],
        "campo": "case_category",
    },
    "categorizacion_caso_opcion": {
        "id": "categorizacion_caso_opcion",
        "siguiente": "descripcion_caso",
        "mensaje": "Categoría {categoria} registrada. Por favor, descríbame brevemente su caso para entender mejor su situación.",
        "validar": None,
        "botones": None,
    },
    "descripcion_caso": {
        "id": "descripcion_caso",
        "siguiente": "captura_correo",
        "mensaje": "Gracias {nombre} por la información. Para agendar su cita y enviarle la confirmación, necesito su correo electrónico. ¿Cuál es su correo electrónico?",
        "validar": "descripcion",
        "botones": None,
        "campo": "case_description",
    },
    "captura_correo": {
        "id": "captura_correo",
        "siguiente": "captura_telefono",
        "mensaje": "Correo registrado correctamente. Ahora necesito un número de teléfono para contactarle. ¿Cuál es su número de contacto?",
        "validar": "correo",
        "botones": None,
        "campo": "user_email",
    },
    "captura_telefono": {
        "id": "captura_telefono",
        "siguiente": "confirmacion_cita",
        "mensaje": "Perfecto {nombre}. Tenemos toda la información necesaria. Le propongo el primer horario disponible: ¿Le viene bien el Lunes 29 de Septiembre a las 10:30 de la mañana?",
        "validar": "telefono",
        "botones": [
            {"texto": "Sí, confirmo", "valor": "confirmar", "descripcion": ""},
            {"texto": "No, otro horario", "valor": "rechazar", "descripcion": ""},
        ],
        "campo": "user_phone",
    },
    "confirmacion_cita": {
        "id": "confirmacion_cita",
        "siguiente": "confirmacion_cita_opcion",
        "mensaje": "Cita confirmada {nombre}.",
        "validar": None,
        "botones": None,
    },
    "confirmacion_cita_opcion": {
        "id": "confirmacion_cita_opcion",
        "siguiente": "manejo_post_cita",
        "mensaje": "📅 Fecha: Lunes 29 de septiembre - 10:30 a.m.\n📧 Correo de confirmación: {correo}\n📱 Teléfono de contacto: {telefono}\n\nHe analizado su caso de {categoria}. Le comento que, si el monto supera los 10 millones de pesos, no hay costo inicial: solo se aplica un honoratorio del 10% en caso de éxito.\n\n¿Hay algo más en lo que pueda ayudarle?",
        "validar": None,
        "botones": [
            {
                "texto": "Sí, tengo otra pregunta",
                "valor": "consulta_adicional",
                "descripcion": "",
            },
            {"texto": "No, gracias", "valor": "despedida", "descripcion": ""},
        ],
    },
    "manejo_post_cita": {
        "id": "manejo_post_cita",
        "siguiente": None,
        "mensaje": "Perfecto {nombre}. Ha sido un placer ayudarle. Un abogado se contactará con usted en la fecha acordada. Esta llamada se finalizará automáticamente. ¡Que tenga un excelente día!",
        "validar": None,
        "botones": None,
        "fin": True,
    },
    "consulta_adicional": {
        "id": "consulta_adicional",
        "siguiente": "manejo_post_cita",
        "mensaje": "Entendido {nombre}. He registrado su consulta adicional. Uno de nuestros abogados especializados se contactará con usted según los datos agendados y le ampliará toda la información al respecto. ¿Hay alguna otra cosa en la que pueda asistirle?",
        "validar": None,
        "botones": [
            {
                "texto": "Sí, tengo otra pregunta",
                "valor": "consulta_adicional",
                "descripcion": "",
            },
            {"texto": "No, gracias", "valor": "despedida", "descripcion": ""},
        ],
    },
    "despedida": {
        "id": "despedida",
        "siguiente": None,
        "mensaje": "Gracias a usted {nombre}. Ha sido un placer atenderle. Un abogado se comunicará con usted en la fecha acordada. ¡Que tenga un excelente día!",
        "validar": None,
        "botones": None,
        "fin": True,
    },
    "rechazo_horario": {
        "id": "rechazo_horario",
        "siguiente": "alternativa_horario",
        "mensaje": "Entiendo perfectamente. En ese caso, ¿le gustaría que le pongamos en contacto directamente con uno de nuestros abogados? Ellos podrán atender su caso de forma personalizada.",
        "validar": None,
        "botones": [
            {
                "texto": "Sí, contáctenme",
                "valor": "contactar_abogado",
                "descripcion": "",
            },
            {
                "texto": "Propóngame otra fecha",
                "valor": "otra_fecha",
                "descripcion": "",
            },
        ],
    },
    "alternativa_horario": {
        "id": "alternativa_horario",
        "siguiente": "confirmacion_cita_opcion",
        "mensaje": "Queda registrada su cita.\n\n📅 Fecha: Miércoles 1 de octubre - 3:30 p.m.\n📧 Correo de confirmación: {correo}\n📱 Teléfono de contacto: {telefono}\n\nHe revisado su caso de {categoria}. Un abogado se comunicará con usted en la fecha acordada.\n\n¿Hay algo más en lo que pueda ayudarle?",
        "validar": None,
        "botones": [
            {
                "texto": "Sí, tengo otra pregunta",
                "valor": "consulta_adicional",
                "descripcion": "",
            },
            {"texto": "No, gracias", "valor": "despedida", "descripcion": ""},
        ],
    },
}


def obtener_paso(paso_id):
    """Obtiene un paso del guion por su ID."""
    return PASOS.get(paso_id)


def obtener_siguiente_paso(paso_id):
    """Obtiene el siguiente paso del guion."""
    paso = PASOS.get(paso_id)
    if paso and paso.get("siguiente"):
        return PASOS.get(paso["siguiente"])
    return None


def formatear_mensaje(paso, datos):
    """Formatea el mensaje del paso con los datos del usuario."""
    mensaje = paso["mensaje"]
    try:
        return mensaje.format(**datos)
    except KeyError:
        return mensaje


def validar_respuesta(paso, respuesta):
    """Valida la respuesta del usuario según el tipo de campo del paso."""
    tipo_validacion = paso.get("validar")

    if tipo_validacion is None:
        return True, respuesta

    if tipo_validacion == "nombre":
        if not respuesta or len(respuesta.strip()) < 2:
            return (
                False,
                "Por favor, indíqueme su nombre completo para proceder con la cita.",
            )
        if any(char.isdigit() for char in respuesta):
            return (
                False,
                "El nombre ingresado no parece válido. Por favor, indíqueme su nombre completo.",
            )
        return True, respuesta.strip()

    if tipo_validacion == "correo":
        import re

        if not respuesta:
            return (
                False,
                "¿Cuál es su correo electrónico? Lo necesito para enviarle la confirmación de la cita.",
            )
        if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", respuesta):
            return (
                False,
                "El correo electrónico ingresado no tiene un formato válido. Por favor, verifíquelo e ingréselo nuevamente (ejemplo: nombre@correo.com).",
            )
        return True, respuesta.strip()

    if tipo_validacion == "telefono":
        import re

        if not respuesta:
            return False, "¿Cuál es su número de teléfono de contacto?"
        digits = re.sub(r"[^0-9]", "", respuesta)
        if len(digits) < 7 or len(digits) > 15:
            return (
                False,
                "El número de teléfono ingresado no parece correcto. Por favor, verifíquelo e ingréselo sin espacios ni guiones (ejemplo: 3001234567).",
            )
        return True, digits

    if tipo_validacion == "descripcion":
        if not respuesta or len(respuesta.strip()) < 5:
            return (
                False,
                "Le agradecería que me describa brevemente los hechos de su caso: fechas, personas involucradas y circunstancias.",
            )
        return True, respuesta.strip()

    return True, respuesta
