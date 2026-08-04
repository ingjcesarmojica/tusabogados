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


def validar_nombre(respuesta):
    """
    Valida que el nombre sea válido:
    - Mínimo 2 caracteres
    - No puede ser solo números
    - No puede ser una sola letra
    - Debe tener al menos un espacio (nombre completo)
    - No puede contener caracteres especiales peligrosos
    - No puede ser palabras sin sentido como "asd", "123", etc.
    """
    import re

    if not respuesta or len(respuesta.strip()) < 2:
        return (
            False,
            "Por favor, indíqueme su nombre completo para proceder con la cita.",
        )

    respuesta = respuesta.strip()

    # No puede ser solo números
    if respuesta.isdigit():
        return (
            False,
            "El nombre no puede ser solo números. Por favor, indíqueme su nombre completo.",
        )

    # No puede ser una sola letra
    if len(respuesta) == 1:
        return False, "Por favor, indíqueme su nombre completo (nombre y apellido)."

    # Debe tener al menos 2 palabras (nombre y apellido)
    palabras = respuesta.split()
    if len(palabras) < 2:
        return (
            False,
            "Por favor, indíqueme tanto su nombre como su apellido (ejemplo: Juan Pérez).",
        )

    # No puede contener caracteres especiales peligrosos
    caracteres_prohibidos = set("@#$%&*(){}[]|/<>!£¥¢§¶™®©")
    if any(char in caracteres_prohibidos for char in respuesta):
        return (
            False,
            "El nombre contiene caracteres no válidos. Por favor, ingrese solo letras y espacios.",
        )

    # No puede tener números intercalados
    if re.search(r"[a-zA-Z]\d[a-zA-Z]", respuesta):
        return (
            False,
            "El nombre no debe contener números. Por favor, indíqueme su nombre completo.",
        )

    # Verificar que no sea una palabra sin sentido (todas las letras iguales o patrón repetitivo)
    if len(set(respuesta.replace(" ", ""))) < 3:
        return (
            False,
            "El nombre ingresado no parece válido. Por favor, indíqueme su nombre completo.",
        )

    # Cada palabra debe tener al menos 2 letras
    for palabra in palabras:
        if len(palabra) < 2:
            return (
                False,
                "Cada parte del nombre debe tener al menos 2 letras. Por favor, indíqueme su nombre completo.",
            )

    return True, respuesta.title()


def validar_correo(respuesta):
    """
    Valida que el correo electrónico sea válido:
    - Formato correcto
    - Dominio existe
    - No tiene caracteres extraños
    """
    import re

    if not respuesta:
        return (
            False,
            "¿Cuál es su correo electrónico? Lo necesito para enviarle la confirmación de la cita.",
        )

    respuesta = respuesta.strip().lower()

    # Formato básico
    patron = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.match(patron, respuesta):
        return (
            False,
            "El correo electrónico no tiene un formato válido. Ejemplo: nombre@correo.com",
        )

    # Verificar que no tenga caracteres extraños
    if ".." in respuesta or "--" in respuesta or "__" in respuesta:
        return (
            False,
            "El correo electrónico contiene caracteres repetidos. Por favor, verifíquelo.",
        )

    # Dominios comunes válidos
    dominios_validos = [
        "gmail.com",
        "hotmail.com",
        "outlook.com",
        "yahoo.com",
        "live.com",
        "icloud.com",
        "aol.com",
        "protonmail.com",
        "mail.com",
        "zoho.com",
        "yandex.com",
        "gmx.com",
        "fastmail.com",
        "tutanota.com",
        "colombia.com",
        "etb.net.co",
        "movistar.com.co",
        "claro.com.co",
        "une.net.co",
        "telmex.com",
        "prodigy.net",
        "comcast.net",
    ]

    dominio = respuesta.split("@")[1] if "@" in respuesta else ""
    if dominio and "." in dominio:
        # Verificar si es un dominio conocido o tiene formato válido
        partes_dominio = dominio.split(".")
        if len(partes_dominio) < 2:
            return False, "El dominio del correo electrónico no es válido."

    return True, respuesta


def validar_telefono(respuesta):
    """
    Valida número de teléfono colombiano:
    - 10 dígitos exactos
    - Móviles: empiezan por 3 (300-350)
    - Fijos Bogotá: empiezan por 1 (601xxxxxxx)
    - Fijos Medellín: empiezan por 4 (604xxxxxxx)
    - Fijos Cali: empiezan por 2 (602xxxxxxx)
    - Fijos Barranquilla: empiezan por 5 (605xxxxxxx)
    - Fijos Bucaramanga: empiezan por 7 (607xxxxxxx)
    - Fijos Pereira: empiezan por 6 (606xxxxxxx)
    """
    import re

    if not respuesta:
        return False, "¿Cuál es su número de teléfono de contacto?"

    # Limpiar el número
    digits = re.sub(r"[^0-9]", "", respuesta)

    # Debe tener 10 dígitos
    if len(digits) != 10:
        return (
            False,
            "El número de teléfono debe tener exactamente 10 dígitos. Ejemplo: 3001234567",
        )

    # No puede ser todos los dígitos iguales
    if len(set(digits)) == 1:
        return False, "El número de teléfono no es válido. Por favor, verifíquelo."

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
            return (
                False,
                f"El prefijo {prefijo} no corresponde a una operadora válida en Colombia. Prefijos móviles válidos: 300-323, 350",
            )
        return True, digits

    # Fijos colombianos: segundo dígito indica la ciudad
    if digits[0] == "6" and digits[1] == "0":
        ciudad = digits[2]
        ciudades_validas = {
            "1": "Bogotá",
            "2": "Cali",
            "4": "Medellín",
            "5": "Barranquilla",
            "6": "Pereira",
            "7": "Bucaramanga",
        }
        if ciudad in ciudades_validas:
            return True, digits
        else:
            return (
                False,
                f"El prefijo 60{ciudad} no corresponde a una ciudad válida en Colombia.",
            )

    # Otros números fijos válidos (empiezan por 1, 4, 5, 7, 8)
    if digits[0] in "14578":
        return True, digits

    return (
        False,
        "El número no corresponde a un teléfono válido en Colombia. Los móviles empiezan por 3 y los fijos por 60X.",
    )


def validar_descripcion(respuesta):
    """
    Valida que la descripción sea lógica:
    - Mínimo 10 caracteres
    - Al menos 3 palabras
    - No puede ser solo números
    - Debe contener letras
    """
    import re

    if not respuesta or len(respuesta.strip()) < 10:
        return (
            False,
            "La descripción debe tener al menos 10 caracteres. Por favor, describa brevemente su caso.",
        )

    respuesta = respuesta.strip()

    # No puede ser solo números o caracteres especiales
    if re.sub(r"[^a-zA-ZáéíóúñüÁÉÍÓÚÑÜ]", "", respuesta).strip() == "":
        return (
            False,
            "La descripción debe contener texto. Por favor, describa los hechos de su caso.",
        )

    # Debe tener al menos 3 palabras
    palabras = respuesta.split()
    if len(palabras) < 3:
        return (
            False,
            "Por favor, proporcione más detalles. Describe qué pasó, cuándo y con quién.",
        )

    # No puede tener solo caracteres repetidos
    texto_limpio = respuesta.replace(" ", "").replace(".", "").replace(",", "")
    if len(set(texto_limpio.lower())) < 4:
        return (
            False,
            "La descripción no parece contener información relevante. Por favor, describa su caso.",
        )

    # No puede ser solo signos de interrogación o exclamación
    if re.sub(r"[¿?!¡.,\s]", "", respuesta).strip() == "":
        return (
            False,
            "La descripción debe contener el relato de los hechos. Por favor, describa su caso.",
        )

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
