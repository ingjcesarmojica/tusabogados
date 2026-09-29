"""
Calendario de Citas - TusAbogados.com
Genera fechas disponibles de lunes a sábado, excluyendo festivos colombianos.
Rango: desde el día siguiente hasta 31 de diciembre de 2026.
"""

from datetime import date, timedelta, datetime

# ── Festivos Colombia 2026 (agosto - diciembre) ──────────────────────
FESTIVOS_COLOMBIA_2026 = {
    date(2026, 8, 7): "Batalla de Boyacá",
    date(2026, 8, 15): "Asunción de la Virgen",
    date(2026, 10, 12): "Día de la Raza",
    date(2026, 11, 1): "Día de todos los Santos",
    date(2026, 11, 11): "Independencia de Cartagena",
    date(2026, 12, 8): "Inmaculada Concepción",
    date(2026, 12, 25): "Navidad",
}

# ── Horarios disponibles ──────────────────────────────────────────────
# 8:00 AM a 11:00 AM (mañana), 2:00 PM a 4:00 PM (tarde)
# Se salta 12:00 PM - 2:00 PM (horas de almuerzo)
HORARIOS_DISPONIBLES = [
    "08:00",
    "09:00",
    "10:00",
    "11:00",
    "14:00",
    "15:00",
    "16:00",
]

# ── Rango del calendario ─────────────────────────────────────────────
FECHA_INICIO = date(2026, 8, 11)
FECHA_FIN = date(2026, 12, 31)


def _fecha_inicio_dinamica():
    """Retorna el día siguiente a la fecha actual como fecha mínima para agendar."""
    hoy = date.today()
    manana = hoy + timedelta(days=1)
    # Si el día siguiente es anterior a FECHA_INICIO, usar FECHA_INICIO
    if manana < FECHA_INICIO:
        return FECHA_INICIO
    return manana


def es_festivo(fecha):
    """Verifica si una fecha es festiva en Colombia."""
    return fecha in FESTIVOS_COLOMBIA_2026


def nombre_festivo(fecha):
    """Retorna el nombre del festivo si lo es, None en caso contrario."""
    return FESTIVOS_COLOMBIA_2026.get(fecha)


def es_domingo(fecha):
    """Verifica si una fecha es domingo (weekday 6)."""
    return fecha.weekday() == 6


def es_habil(fecha):
    """Verifica si una fecha es hábil (no domingo, no festivo, dentro del rango)."""
    if fecha < FECHA_INICIO or fecha > FECHA_FIN:
        return False
    if es_domingo(fecha):
        return False
    if es_festivo(fecha):
        return False
    return True


def obtener_nombre_dia(fecha):
    """Retorna el nombre del día en español."""
    dias = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
    return dias[fecha.weekday()]


def obtener_nombre_mes(mes):
    """Retorna el nombre del mes en español."""
    meses = [
        "",
        "enero",
        "febrero",
        "marzo",
        "abril",
        "mayo",
        "junio",
        "julio",
        "agosto",
        "septiembre",
        "octubre",
        "noviembre",
        "diciembre",
    ]
    return meses[mes]


def formatear_fecha(fecha):
    """Formatea una fecha como 'Lunes 24 de agosto'."""
    return f"{obtener_nombre_dia(fecha).title()} {fecha.day} de {obtener_nombre_mes(fecha.month)}"


def formatear_fecha_completa(fecha, hora):
    """Formatea fecha y hora como 'Lunes 24 de agosto - 10:30 a.m.'"""
    h, m = map(int, hora.split(":"))
    periodo = "a.m." if h < 12 else "p.m."
    h_12 = h if h <= 12 else h - 12
    if h == 0:
        h_12 = 12
    return f"{formatear_fecha(fecha)} - {h_12}:{m:02d} {periodo}"


def fechas_disponibles():
    """
    Retorna lista de todas las fechas hábiles en el rango.
    Retorna tuplas (fecha, nombre_festivo_si_aplica).
    """
    disponibles = []
    actual = FECHA_INICIO
    while actual <= FECHA_FIN:
        if es_habil(actual):
            disponibles.append(actual)
        actual += timedelta(days=1)
    return disponibles


def siguiente_fecha_disponible(desde=None):
    """
    Retorna la siguiente fecha hábil desde una fecha dada.
    Si no se provee fecha, usa el día siguiente a la fecha actual.
    """
    if desde is None:
        desde = _fecha_inicio_dinamica()
    actual = desde
    while actual <= FECHA_FIN:
        if es_habil(actual):
            return actual
        actual += timedelta(days=1)
    return None


def fecha_disponible(fecha):
    """Verifica si una fecha específica está disponible."""
    return es_habil(fecha)


def horarios_para_fecha(fecha):
    """
    Retorna los horarios disponibles para una fecha dada.
    Si la fecha no es hábil, retorna lista vacía.
    """
    if not es_habil(fecha):
        return []
    return HORARIOS_DISPONIBLES.copy()


def proxima_cita():
    """
    Retorna la próxima cita disponible (fecha + primer horario).
    Retorna dict con fecha, hora, y mensaje formateado.
    """
    fecha = siguiente_fecha_disponible()
    if fecha is None:
        return None

    hora = HORARIOS_DISPONIBLES[0]
    return {
        "fecha": fecha,
        "hora": hora,
        "fecha_str": fecha.isoformat(),
        "mensaje_fecha": formatear_fecha(fecha),
        "mensaje_completo": formatear_fecha_completa(fecha, hora),
    }


def obtener_siguiente_cita_disponible(horas_ocupadas_fn=None):
    """
    Retorna la siguiente cita disponible consultando las horas ya ocupadas.
    Siempre busca a partir del día siguiente a la fecha actual.

    horas_ocupadas_fn: callable(fecha_str) -> list[str] de horas ocupadas para esa fecha.
                       Ejemplo: ["08:00", "10:00"] si esas horas ya están agendadas.

    Retorna dict con:
      - fecha: date object
      - hora: str ("08:00", "09:00", etc.)
      - fecha_str: str ("2026-09-09")
      - mensaje_fecha: str ("Miércoles 9 de septiembre")
      - mensaje_completo: str ("Miércoles 9 de septiembre - 8:00 a.m.")
    o None si no hay disponibilidad.
    """
    manana = _fecha_inicio_dinamica()
    actual = manana

    while actual <= FECHA_FIN:
        if es_habil(actual):
            horas_ocupadas = horas_ocupadas_fn(actual.isoformat()) if horas_ocupadas_fn else []
            for hora in HORARIOS_DISPONIBLES:
                if hora not in horas_ocupadas:
                    return {
                        "fecha": actual,
                        "hora": hora,
                        "fecha_str": actual.isoformat(),
                        "mensaje_fecha": formatear_fecha(actual),
                        "mensaje_completo": formatear_fecha_completa(actual, hora),
                    }
        actual += timedelta(days=1)

    return None


def obtener_cita_despues_de(fecha_despues, hora_despues, horas_ocupadas_fn=None):
    """
    Retorna la siguiente cita disponible DESPUÉS de una fecha y hora específicas.
    Útil cuando el usuario rechaza la primera opción y se ofrece la siguiente.

    fecha_despues: str en formato 'YYYY-MM-DD'
    hora_despues: str en formato 'HH:MM'
    horas_ocupadas_fn: callable(fecha_str) -> list[str] de horas ocupadas.

    Retorna dict con fecha, hora, fecha_str, mensaje_fecha, mensaje_completo.
    """
    try:
        fecha_base = date.fromisoformat(fecha_despues)
    except (ValueError, TypeError):
        # Si hay error, empezar desde mañana
        fecha_base = _fecha_inicio_dinamica()

    actual = fecha_base
    encontre_posicion = False

    while actual <= FECHA_FIN:
        if es_habil(actual):
            horas_ocupadas = horas_ocupadas_fn(actual.isoformat()) if horas_ocupadas_fn else []
            for hora in HORARIOS_DISPONIBLES:
                if not encontre_posicion:
                    # Primero, encontrar la posición DESPUÉS de la hora dada
                    if actual > fecha_base or (actual == fecha_base and hora > hora_despues):
                        encontre_posicion = True
                    else:
                        continue

                if hora not in horas_ocupadas:
                    return {
                        "fecha": actual,
                        "hora": hora,
                        "fecha_str": actual.isoformat(),
                        "mensaje_fecha": formatear_fecha(actual),
                        "mensaje_completo": formatear_fecha_completa(actual, hora),
                    }
        actual += timedelta(days=1)

    return None


def citas_disponibles_cantidad(dias=5):
    """
    Retorna las próximas N fechas disponibles con sus horarios.
    """
    resultados = []
    actual = _fecha_inicio_dinamica()
    while len(resultados) < dias and actual <= FECHA_FIN:
        if es_habil(actual):
            for hora in HORARIOS_DISPONIBLES:
                resultados.append(
                    {
                        "fecha": actual,
                        "hora": hora,
                        "fecha_str": actual.isoformat(),
                        "mensaje_fecha": formatear_fecha(actual),
                        "mensaje_completo": formatear_fecha_completa(actual, hora),
                    }
                )
                if len(resultados) >= dias:
                    break
        actual += timedelta(days=1)
    return resultados


def obtener_festivos():
    """Retorna diccionario de festivos en el rango del calendario."""
    return {
        k: v
        for k, v in sorted(FESTIVOS_COLOMBIA_2026.items())
        if FECHA_INICIO <= k <= FECHA_FIN
    }


# ── Testing rápido ───────────────────────────────────────────────────
if __name__ == "__main__":
    print("=== Calendario de Citas TusAbogados.com ===\n")
    print(f"Rango: {formatear_fecha(FECHA_INICIO)} al {formatear_fecha(FECHA_FIN)}")
    print(f"Horarios: {', '.join(HORARIOS_DISPONIBLES)}\n")

    print("Festivos en el rango:")
    for f, nombre in obtener_festivos().items():
        print(f"  {formatear_fecha(f)} - {nombre}")

    print(f"\nTotal de fechas hábiles: {len(fechas_disponibles())}")

    print("\nPróximas 5 fechas disponibles:")
    for i, fecha in enumerate(fechas_disponibles()[:5], 1):
        print(f"  {i}. {formatear_fecha(fecha)}")

    print("\nPróxima cita:")
    cita = proxima_cita()
    if cita:
        print(f"  {cita['mensaje_completo']}")
