# Flujo Conversacional - Agente IA TusAbogados.com

**Agente:** Claudia García - Agente Especializada en Derecho
**Versión:** 2.0 (Modo Chat)
**Fecha:** Agosto 2026

---

## Diagrama de Flujo Principal

```
┌─────────────────────────────────────────────────────────────────────┐
│                        INICIO                                       │
│                    saludo_inicial                                    │
│  "¡Bienvenido a TusAbogados.com! ... Por favor dígame sus          │
│   nombres y apellidos."                                             │
│  [Validación: nombre + apellido]                                    │
└──────────────────────────┬──────────────────────────────────────────┘
                           │ Nombre válido
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                  IDENTIFICACIÓN DE ROL                               │
│                  identificacion_rol                                  │
│  "Mucho gusto, {nombre}. Para orientarte mejor, necesito saber     │
│   tu rol en el caso."                                               │
│                                                                     │
│  ┌──────────────────┐    ┌──────────────────┐                      │
│  │    Demandado      │    │   Demandante     │                      │
│  │ (accidente, deuda,│    │ (divorcio,       │                      │
│  │  estafa, daño)    │    │  herencia, labor)│                      │
│  └────────┬─────────┘    └────────┬─────────┘                      │
└───────────┼────────────────────────┼───────────────────────────────┘
            │                        │
            ▼                        ▼
┌─────────────────────────────────────────────────────────────────────┐
│                 CATEGORIZACIÓN DEL CASO                              │
│                 categorizacion_caso                                  │
│  "Entendido, {nombre}, como {rol}. ¿En qué categoría crees que    │
│   está tu caso?"                                                    │
│                                                                     │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────────┐  │
│  │   Civil    │ │  Laboral   │ │   Penal    │ │ No sé cuál es  │  │
│  │(divorcio,  │ │(despido,   │ │(robos,     │ │  mi categoría  │  │
│  │ herencias, │ │ acoso,     │ │ agresiones,│ │ (un abogado    │  │
│  │ contratos) │ │ prestac.)  │ │ amenazas)  │ │  orientará)    │  │
│  └─────┬──────┘ └─────┬──────┘ └─────┬──────┘ └───────┬────────┘  │
└────────┼──────────────┼──────────────┼─────────────────┼───────────┘
         │              │              │                 │
         └──────────────┴──────────────┴─────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                 VERIFICACIÓN DE PRUEBAS                              │
│                 verificacion_pruebas                                 │
│  "Tu caso corresponde a la categoría {categoria}. ¿Cuenta con     │
│   pruebas que argumenten su caso?"                                   │
│                                                                     │
│  ┌────────────────────┐    ┌────────────────────────┐              │
│  │  Sí, tengo pruebas │    │  No, no tengo pruebas  │              │
│  │ (activa upload de  │    │  (continúa sin pruebas)│              │
│  │  archivos)         │    │                        │              │
│  └─────────┬──────────┘    └──────────┬─────────────┘              │
└────────────┼──────────────────────────┼────────────────────────────┘
             │                          │
             └────────────┬─────────────┘
                          ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   DESCRIPCIÓN DEL CASO                               │
│                   descripcion_caso                                   │
│  "Categoría {categoria} registrada. Describa brevemente su caso."  │
│  [Validación: mínimo 10 caracteres, 3 palabras]                     │
│  [Si tiene pruebas: muestra botón de adjuntar archivos]             │
└──────────────────────────┬──────────────────────────────────────────┘
                           │ Descripción válida
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   CAPTURA DE CORREO                                  │
│                   captura_correo                                     │
│  "Gracias, {nombre}. ¿Cuál es tu correo electrónico?"             │
│  [Validación: formato email válido]                                 │
└──────────────────────────┬──────────────────────────────────────────┘
                           │ Email válido
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   CAPTURA DE TELÉFONO                               │
│                   captura_telefono                                   │
│  "Correo registrado. ¿Cuál es su número telefónico?"              │
│  [Validación: 10 dígitos, móvil colombiano (3xx) o fijo (60x)]    │
└──────────────────────────┬──────────────────────────────────────────┘
                           │ Teléfono válido
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│              CONFIRMACIÓN DE CITA + DETALLES                        │
│              confirmacion_cita_opcion                                │
│                                                                     │
│  "¡Su cita ha sido confirmada!                                      │
│                                                                     │
│   📅 Fecha: Lunes 29 de septiembre - 10:30 a.m.                   │
│   📧 Confirmación enviada a: {correo}                               │
│   📱 Teléfono de contacto: {telefono}                               │
│                                                                     │
│   He analizado tu caso de {categoria}. Si el monto supera          │
│   los 10 millones de pesos, no hay costo inicial: solo se          │
│   aplica un honoratorio del 10% en caso de éxito.                   │
│                                                                     │
│   ¿Hay algo más en lo que pueda ayudarte?"                          │
│                                                                     │
│  ┌──────────────────────┐    ┌────────────────┐                    │
│  │ Sí, tengo otra duda  │    │  No, gracias   │                    │
│  └──────────┬───────────┘    └───────┬────────┘                    │
└─────────────┼─────────────────────────┼────────────────────────────┘
              │                         │
              ▼                         ▼
┌─────────────────────────┐  ┌──────────────────────────────────────┐
│   CONSULTA ADICIONAL    │  │            DESPEDIDA                  │
│   manejo_post_cita      │  │            despedida                  │
│                         │  │                                      │
│ "He registrado tu       │  │ "Gracias a usted. Ha sido un gusto  │
│  consulta adicional.    │  │  atenderte. Un abogado se            │
│  Un abogado se          │  │  comunicará contigo en la fecha      │
│  comunicará contigo."   │  │  acordada. ¡Que tengas un           │
│                         │  │  excelente día!"                     │
│ ┌────────────────────┐  │  │                                      │
│ │Sí, tengo otra duda │  │  │         ┌──────────────┐             │
│ └────────┬───────────┘  │  │         │  FIN DEL     │             │
│ ┌────────────────────┐  │  │         │ CONVERSACIÓN │             │
│ │   No, gracias      │  │  │         └──────────────┘             │
│ └────────┬───────────┘  │  │                                      │
│    ┌─────┴──────┐       │  └──────────────────────────────────────┘
│    ▼            ▼       │
│  Loop      Despedida    │
│ (vuelve)   (termina)    │
└────────────┬────────────┘
             │
             └──→ Loop: vuelve a mostrar opciones
```

---

## Flujo Alternativo: Rechazo de Horario

```
┌─────────────────────────────────────────────────────────────────────┐
│  Desde confirmacion_cita_opcion, si usuario selecciona              │
│  "No, por ahora no" (rechazar_cita)                                │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   RECHAZO DE HORARIO                                 │
│                   rechazo_horario                                    │
│  "Entiendo perfectamente. ¿Te gustaría que te pongamos en         │
│   contacto directamente con uno de nuestros abogados?"              │
│                                                                     │
│  ┌──────────────────────┐    ┌──────────────────────┐              │
│  │  Sí, contáctenme     │    │ Propónme otra fecha  │              │
│  └──────────┬───────────┘    └──────────┬───────────┘              │
└─────────────┼───────────────────────────┼──────────────────────────┘
              │                           │
              ▼                           ▼
┌─────────────────────────┐  ┌──────────────────────────────────────┐
│ CONTACTAR ABOGADO       │  │  FECHA ALTERNATIVA                    │
│ (contactar_abogado)     │  │  (otra_fecha)                         │
│                         │  │                                      │
│ "Un abogado se          │  │ "Queda registrada tu cita.           │
│  comunicará contigo     │  │  📅 Miércoles 1 de octubre - 3:30   │
│  a la brevedad."        │  │     p.m."                             │
│                         │  │                                      │
│ → manejo_post_cita      │  │ → manejo_post_cita                   │
│   (ofrece: otra duda /  │  │   (ofrece: otra duda / no gracias)  │
│    no gracias)          │  │                                      │
└─────────────────────────┘  └──────────────────────────────────────┘
```

---

## Flujo de Preguntas Libres (durante el flujo)

```
┌─────────────────────────────────────────────────────────────────────┐
│  Si el usuario hace una pregunta en cualquier paso que NO sea:     │
│  saludo, correo, teléfono, descripción, rol, categoría,            │
│  verificación pruebas, confirmación opción                         │
│                                                                     │
│  → Gemini responde la pregunta                                     │
│  → RAG busca en base de conocimiento (si disponible)               │
│                                                                     │
│  ┌──────────────────────────┐  ┌────────────────┐                  │
│  │Continuar con mi caso     │  │  No, gracias   │                  │
│  │ (retoma paso actual)     │  │  (despedida)   │                  │
│  └──────────────────────────┘  └────────────────┘                  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Flujo de Despedida (durante el flujo)

```
┌─────────────────────────────────────────────────────────────────────┐
│  Si el usuario dice "gracias", "adiós", "chao", "hasta luego",    │
│  "no gracias", "eso es todo" en pasos que no sean los iniciales:   │
│                                                                     │
│  → "Entendido, {nombre}. Un abogado se comunicará contigo.         │
│     Saludos cordiales."                                             │
│  → Limpia estado de conversación                                   │
│  → FIN                                                             │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Tabla Resumen de Pasos

| # | Paso ID | Siguiente | Validación | Botones | Acción |
|---|---------|-----------|------------|---------|--------|
| 1 | `saludo_inicial` | `identificacion_rol` | nombre | — | Texto libre |
| 2 | `identificacion_rol` | `categorizacion_caso` | — | demandado, demandante | Botón |
| 3 | `categorizacion_caso` | `verificacion_pruebas` | — | civil, laboral, penal, no_definida | Botón |
| 4 | `verificacion_pruebas` | `descripcion_caso` | — | si_pruebas, no_pruebas | Botón |
| 5 | `descripcion_caso` | `captura_correo` | descripcion | — | Texto libre |
| 6 | `captura_correo` | `captura_telefono` | correo | — | Texto libre |
| 7 | `captura_telefono` | `confirmacion_cita_opcion` | telefono | — | Texto libre |
| 8 | `confirmacion_cita_opcion` | `manejo_post_cita` | — | consulta_adicional, despedida | Botón |
| 9 | `manejo_post_cita` | FIN | — | — | Fin |
| 10 | `consulta_adicional` | `manejo_post_cita` | — | consulta_adicional, despedida | Botón |
| 11 | `despedida` | FIN | — | — | Fin |
| 12 | `rechazo_horario` | `alternativa_horario` | — | contactar_abogado, otra_fecha | Botón |
| 13 | `alternativa_horario` | `confirmacion_cita_opcion` | — | consulta_adicional, despedida | Botón |

---

## Tabla de Acciones de Botones (app.py)

| Acción | Paso Origen | Paso Destino | Descripción |
|--------|-------------|--------------|-------------|
| `demandado` | identificacion_rol | categorizacion_caso | Usuario es demandado |
| `demandante` | identificacion_rol | categorizacion_caso | Usuario es demandante |
| `civil` | categorizacion_caso | verificacion_pruebas | Caso civil |
| `laboral` | categorizacion_caso | verificacion_pruebas | Caso laboral |
| `penal` | categorizacion_caso | verificacion_pruebas | Caso penal |
| `no_definida` | categorizacion_caso | verificacion_pruebas | No sabe categoría |
| `si_pruebas` | verificacion_pruebas | descripcion_caso | Tiene pruebas (muestra upload) |
| `no_pruebas` | verificacion_pruebas | descripcion_caso | No tiene pruebas |
| `rechazar_cita` | confirmacion_cita_opcion | rechazo_horario | Rechaza propuesta de cita |
| `contactar_abogado` | rechazo_horario | manejo_post_cita | Quiere contacto directo |
| `otra_fecha` | rechazo_horario | manejo_post_cita | Propone otra fecha |
| `consulta_adicional` | manypost_cita / confirmacion_cita_opcion | manejo_post_cita | Tiene otra duda |
| `despedida` | manypost_cita / confirmacion_cita_opcion | FIN | Finalizar conversación |
| `continuar` | (pregunta libre) | paso_actual | Retoma flujo después de pregunta |

---

## Validaciones

| Campo | Regla | Mensaje de error |
|-------|-------|------------------|
| **Nombre** | Mín. 2 palabras, sin números, sin caracteres especiales, mín. 2 letras por palabra | "Verifica que el nombre sea válido. Debe ser tu nombre y apellido." |
| **Correo** | Formato `user@domain.ext`, sin `..`, `--`, `__` | "Verifica que el correo electrónico sea válido. Ejemplo: nombre@correo.com" |
| **Teléfono** | 10 dígitos, móvil (3xx) o fijo (60x), no todos iguales | "Verifica que el número de teléfono sea válido. Debe tener 10 dígitos." |
| **Descripción** | Mín. 10 caracteres, 3 palabras, no solo números/signos | "Describe brevemente los hechos de tu caso." |

---

## Estados de la Conversación

| Variable | Descripción | Se guarda en |
|----------|-------------|--------------|
| `user_name` | Nombre completo del usuario | `chat.user_name` |
| `user_role` | Rol: demandado / demandante | `chat.user_role` |
| `case_category` | Categoría: civil / laboral / penal / no_definida | `chat.case_category` |
| `has_evidence` | Pruebas: si_pruebas / no_pruebas | `chat.has_evidence` |
| `case_description` | Descripción del caso | `chat.case_description` |
| `user_email` | Correo electrónico | `chat.user_email` |
| `user_phone` | Teléfono | `chat.user_phone` |
| `paso_actual` | Paso actual del guion | `chat.paso_actual` |
| `appointment_time` | Fecha/hora de la cita | `chat.appointment_time` |

---

## Arquitectura Técnica

```
┌──────────────┐     POST /api/chat      ┌──────────────┐
│              │ ──────────────────────→  │              │
│   Frontend   │                          │   Backend    │
│  (index.html)│ ←──────────────────────  │   (app.py)   │
│              │     JSON response        │              │
└──────────────┘                          └──────┬───────┘
                                                 │
                                          ┌──────┴───────┐
                                          │              │
                                     ┌────▼────┐   ┌────▼────┐
                                     │ guion.py│   │ rag.py  │
                                     │ (PASOS) │   │(Pinecone│
                                     └─────────┘   └─────────┘
                                          │
                                     ┌────▼────────────┐
                                     │  Gemini 2.0     │
                                     │  Flash (LLM)    │
                                     └─────────────────┘
```

| Componente | Tecnología | Función |
|------------|-----------|---------|
| Frontend | HTML + CSS + JS vanilla | Interfaz de chat (380x700px) |
| Backend | Flask (Python 3.11) | API REST, lógica conversacional |
| Guion | guion.py | Pasos, validaciones, mensajes |
| RAG | Pinecone + Gemini Embeddings | Base de conocimiento PDFs |
| LLM | Gemini 2.0 Flash | Respuestas a preguntas libres |
| TTS | edge-tts (Microsoft) | Text-to-Speech (botón 🔊) |
