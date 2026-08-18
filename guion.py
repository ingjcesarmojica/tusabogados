"""
Guion Conversacional - Agente IA Legal "Claudia García"
Tusabogados.com

Flujo conversacional estructurado para chat y llamadas.
"""

# PASOS DEL GUION CONVERSACIONAL
PASOS = {
    "saludo_inicial": {
        "id": "saludo_inicial",
        "siguiente": "identificacion_rol",
        "mensaje": "¡Bienvenido a TusAbogados.com! Somos un bufete de abogados especializado en brindarte asesoría legal confiable. Soy Claudia García, tu asistente virtual, y estoy aquí para orientarte de la mejor manera posible con tu caso. Para comenzar, ¿podrías indicarme tu nombre completo?",
        "validar": "nombre",
        "botones": None,
    },
    "identificacion_rol": {
        "id": "identificacion_rol",
        "siguiente": "categorizacion_caso",
        "mensaje": "Un gusto, {nombre}. Para darte una orientación más precisa, cuéntame: ¿cuál es tu situación en este caso?",
        "validar": None,
        "botones": [
            {
                "texto": "Demandado",
                "valor": "demandado",
                "descripcion": "Si sufrí un accidente, me deben dinero, fui estafado, o sufrí algún daño.",
            },
            {
                "texto": "Demandante",
                "valor": "demandante",
                "descripcion": "Si quiero iniciar una demanda por divorcio, herencia, contrato, o mis derechos laborales.",
            },
        ],
        "campo": "user_role",
    },
    "categorizacion_caso": {
        "id": "categorizacion_caso",
        "siguiente": "verificacion_pruebas",
        "mensaje": "Perfecto, quedas registrado como {rol}. Ahora cuéntame, ¿en qué categoría se enmarca tu caso?",
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
                "descripcion": "Un abogado te orientará.",
            },
        ],
        "campo": "case_category",
    },
    "descripcion_categoria": {
        "id": "descripcion_categoria",
        "siguiente": "verificacion_pruebas",
        "mensaje": "Para poder colaborarte y orientarte a qué categoría pertenece tu caso, por favor ingresa una pequeña descripción del mismo. Con esa información podré determinar si se trata de un caso civil, laboral o penal.",
        "validar": "descripcion",
        "botones": None,
        "campo": "case_description",
    },
    "verificacion_pruebas": {
        "id": "verificacion_pruebas",
        "siguiente": "descripcion_caso",
        "mensaje": "Perfecto, tu caso está relacionado con derecho laboral. Una pregunta importante: ¿cuentas con pruebas que respalden tu caso, como documentos, fotos, audios u otros?",
        "validar": None,
        "botones": [
            {
                "texto": "Sí, tengo pruebas",
                "valor": "si_pruebas",
                "descripcion": "Documentos, fotos, audios u otros.",
            },
            {
                "texto": "No, no tengo pruebas",
                "valor": "no_pruebas",
                "descripcion": "Continuar sin pruebas.",
            },
        ],
        "campo": "has_evidence",
    },
    "descripcion_caso": {
        "id": "descripcion_caso",
        "siguiente": "captura_correo",
        "mensaje": "Excelente. Cuéntame brevemente qué sucedió en tu caso — con eso podré entender mejor tu situación. También puedes adjuntar los archivos que consideres relevantes (documentos, fotos, audios, etc.).",
        "validar": "descripcion",
        "botones": None,
        "campo": "case_description",
    },
    "captura_correo": {
        "id": "captura_correo",
        "siguiente": "captura_telefono",
        "mensaje": "Gracias por la información. Para agendar tu cita y enviarte la confirmación, necesito tu correo electrónico. ¿Podrías compartírmelo?",
        "validar": "correo",
        "botones": None,
        "campo": "user_email",
    },
    "captura_telefono": {
        "id": "captura_telefono",
        "siguiente": "confirmacion_cita",
        "mensaje": "Correo registrado correctamente. Ahora, ¿cuál es tu número telefónico? Con este dato, uno de nuestros especialistas podrá contactarte sin ningún costo.",
        "validar": "telefono",
        "botones": None,
        "campo": "user_phone",
    },
    "confirmacion_cita": {
        "id": "confirmacion_cita",
        "siguiente": "confirmacion_cita_opcion",
        "mensaje": "¡Su cita ha sido confirmada! Recuerde: Tusabogados.com trabaja casos donde solamente cobramos comisión por el éxito de los procesos, es decir al final de haber ganado el caso.",
        "validar": None,
        "botones": None,
    },
    "confirmacion_cita_opcion": {
        "id": "confirmacion_cita_opcion",
        "siguiente": "manejo_post_cita",
        "mensaje": "📅 Fecha: Lunes 29 de septiembre - 10:30 a.m.\n📧 Confirmación enviada a: {correo}\n📱 Teléfono de contacto: {telefono}\n\nHe analizado tu caso. Te cuento cómo funciona: si el monto no supera los 10 millones de pesos, no tienes que pagar nada por adelantado — solo se cobra un honorario del 10% si ganamos el caso.\n\n¿Hay algo más en lo que pueda ayudarte? Por favor, seleccione una de las opciones.",
        "validar": None,
        "botones": [
            {
                "texto": "Sí, tengo otra duda",
                "valor": "consulta_adicional",
                "descripcion": "",
            },
            {"texto": "No, gracias", "valor": "despedida", "descripcion": ""},
        ],
    },
    "manejo_post_cita": {
        "id": "manejo_post_cita",
        "siguiente": None,
        "mensaje": "Perfecto, {nombre}. Ha sido un placer ayudarte. Un abogado se comunicará contigo en la fecha acordada. ¡Que tengas un excelente día!",
        "validar": None,
        "botones": None,
        "fin": True,
    },
    "consulta_adicional": {
        "id": "consulta_adicional",
        "siguiente": "pregunta_consultar",
        "mensaje": "Claro, con gusto. Cuéntame, ¿cuál es tu pregunta?",
        "validar": "pregunta",
        "botones": None,
        "campo": "pregunta_extra",
    },
    "pregunta_consultar": {
        "id": "pregunta_consultar",
        "siguiente": "consulta_adicional",
        "mensaje": "",
        "validar": None,
        "botones": [
            {
                "texto": "Sí, tengo otra duda",
                "valor": "consulta_adicional",
                "descripcion": "",
            },
            {"texto": "No, gracias", "valor": "despedida", "descripcion": ""},
        ],
    },
    "despedida": {
        "id": "despedida",
        "siguiente": None,
        "mensaje": "Gracias a ti por confiar en nosotros. Ha sido un gusto atenderte. Un abogado se pondrá en contacto contigo en la fecha acordada. ¡Que tengas un excelente día!",
        "validar": None,
        "botones": None,
        "fin": True,
    },
    "rechazo_horario": {
        "id": "rechazo_horario",
        "siguiente": "alternativa_horario",
        "mensaje": "Entiendo perfectamente. En ese caso, ¿te gustaría que te pongamos en contacto directamente con uno de nuestros abogados? Ellos podrán atender tu caso de forma personalizada. Por favor, seleccione una de las opciones.",
        "validar": None,
        "botones": [
            {
                "texto": "Sí, contáctenme",
                "valor": "contactar_abogado",
                "descripcion": "",
            },
            {
                "texto": "Propónme otra fecha",
                "valor": "otra_fecha",
                "descripcion": "",
            },
        ],
    },
    "alternativa_horario": {
        "id": "alternativa_horario",
        "siguiente": "confirmacion_cita_opcion",
        "mensaje": "Queda registrada tu cita.\n\n📅 Fecha: Miércoles 1 de octubre - 3:30 p.m.\n📧 Confirmación enviada a: {correo}\n📱 Teléfono de contacto: {telefono}\n\nHe revisado tu caso de {categoria}. Un abogado se comunicará contigo en la fecha acordada.\n\n¿Hay algo más en lo que pueda ayudarte? Por favor, seleccione una de las opciones.",
        "validar": None,
        "botones": [
            {
                "texto": "Sí, tengo otra duda",
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


MENSAJE_ERROR_GENERICO = (
    "Por favor, verifica que el dato ingresado sea válido e intenta de nuevo."
)


def validar_nombre(respuesta):
    """
    Valida que el nombre sea válido.
    Retorna (True, nombre_formateado) o (False, mensaje_error).
    """
    import re

    MENSAJE_NOMBRE = "Por favor, verifica que el nombre sea válido e intenta de nuevo. Debe ser tu nombre y apellido. Después de la señal, pronuncia claramente tu nombre y apellido."

    if not respuesta or len(respuesta.strip()) < 2:
        return False, MENSAJE_NOMBRE

    respuesta = respuesta.strip()

    # No puede ser solo números
    if respuesta.isdigit():
        return False, MENSAJE_NOMBRE

    # No puede ser una sola letra
    if len(respuesta) == 1:
        return False, MENSAJE_NOMBRE

    # Debe tener al menos 2 palabras (nombre y apellido)
    palabras = respuesta.split()
    if len(palabras) < 2:
        return False, MENSAJE_NOMBRE

    # No puede contener caracteres especiales
    caracteres_prohibidos = set("@#$%&*(){}[]|/<>!£¥¢§¶™®©0123456789")
    if any(char in caracteres_prohibidos for char in respuesta):
        return False, MENSAJE_NOMBRE

    # Verificar que no sea una palabra sin sentido
    if len(set(respuesta.replace(" ", ""))) < 3:
        return False, MENSAJE_NOMBRE

    # Cada palabra debe tener al menos 2 letras
    for palabra in palabras:
        if len(palabra) < 2:
            return False, MENSAJE_NOMBRE

    return True, respuesta.title()


def validar_correo(respuesta):
    """
    Valida que el correo electrónico sea válido.
    Retorna (True, correo) o (False, mensaje_error).
    """
    import re

    MENSAJE_CORREO = "Por favor, verifica que el correo electrónico sea válido e intenta de nuevo. Ejemplo: nombre@correo.com. Después de la señal, pronuncia claramente tu correo electrónico."

    if not respuesta:
        return False, MENSAJE_CORREO

    respuesta = respuesta.strip().lower()

    # Formato básico
    patron = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.match(patron, respuesta):
        return False, MENSAJE_CORREO

    # Verificar que no tenga caracteres extraños
    if ".." in respuesta or "--" in respuesta or "__" in respuesta:
        return False, MENSAJE_CORREO

    return True, respuesta


def validar_telefono(respuesta):
    """
    Valida número de teléfono colombiano.
    Retorna (True, telefono) o (False, mensaje_error).
    """
    import re

    MENSAJE_TELEFONO = "Por favor, verifica que el número de teléfono sea válido e intenta de nuevo. Debe tener 10 dígitos. Después de la señal, pronuncia claramente tu número de teléfono."

    if not respuesta:
        return False, "¿Cuál es su número de teléfono de contacto?"

    # Limpiar el número
    digits = re.sub(r"[^0-9]", "", respuesta)

    # Debe tener 10 dígitos
    if len(digits) != 10:
        return False, MENSAJE_TELEFONO

    # No puede ser todos los dígitos iguales
    if len(set(digits)) == 1:
        return False, MENSAJE_TELEFONO

    # Móviles colombianos: empiezan por 3
    if digits[0] == "3":
        prefijos_moviles = [
            "300",
            "301",
            "302",
            "303",
            "304",
            "305",
            "310",
            "311",
            "312",
            "313",
            "314",
            "315",
            "316",
            "317",
            "318",
            "319",
            "320",
            "321",
            "322",
            "323",
            "350",
        ]
        prefijo = digits[:3]
        if prefijo not in prefijos_moviles:
            return False, MENSAJE_TELEFONO
        return True, digits

    # Fijos colombianos: 60X
    if digits[0] == "6" and digits[1] == "0":
        ciudad = digits[2]
        ciudades_validas = {"1", "2", "4", "5", "6", "7"}
        if ciudad in ciudades_validas:
            return True, digits
        else:
            return False, MENSAJE_TELEFONO

    # Otros números fijos válidos
    if digits[0] in "14578":
        return True, digits

    return False, MENSAJE_TELEFONO


def validar_descripcion(respuesta):
    """
    Valida que la descripción sea lógica.
    Retorna (True, descripcion) o (False, mensaje_error).
    """
    import re

    MENSAJE_DESCRIPCION = "Por favor, verifica que la descripción sea válida e intenta de nuevo. Describe brevemente los hechos de tu caso. Después de la señal, describe brevemente tu caso."

    if not respuesta or len(respuesta.strip()) < 10:
        return False, MENSAJE_DESCRIPCION

    respuesta = respuesta.strip()

    # No puede ser solo números o caracteres especiales
    if re.sub(r"[^a-zA-ZáéíóúñüÁÉÍÓÚÑÜ]", "", respuesta).strip() == "":
        return False, MENSAJE_DESCRIPCION

    # Debe tener al menos 3 palabras
    palabras = respuesta.split()
    if len(palabras) < 3:
        return False, MENSAJE_DESCRIPCION

    # No puede tener solo caracteres repetidos
    texto_limpio = respuesta.replace(" ", "").replace(".", "").replace(",", "")
    if len(set(texto_limpio.lower())) < 4:
        return False, MENSAJE_DESCRIPCION

    # No puede ser solo signos de interrogación o exclamación
    if re.sub(r"[¿?!¡.,\s]", "", respuesta).strip() == "":
        return False, MENSAJE_DESCRIPCION

    return True, respuesta


def validar_respuesta(paso, respuesta):
    """Valida la respuesta del usuario según el tipo de campo del paso."""
    tipo_validacion = paso.get("validar")

    if tipo_validacion is None:
        return True, respuesta

    if tipo_validacion == "nombre":
        return validar_nombre(respuesta)

    if tipo_validacion == "correo":
        return validar_correo(respuesta)

    if tipo_validacion == "telefono":
        return validar_telefono(respuesta)

    if tipo_validacion == "descripcion":
        return validar_descripcion(respuesta)

    return True, respuesta
