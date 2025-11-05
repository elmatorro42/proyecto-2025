from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import random
from google import genai
from google.genai import types

# --- Configuración de la API Key Directa ---
# IMPORTANTE: Esta clave DEBE ser cargada de forma segura en producción.
API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
# Inicializar el cliente Gemini
try:
    client = genai.Client(api_key=API_KEY)

except Exception as e:
    print(f"Error al inicializar el cliente Gemini: {e}")
    print("Asegúrate de que la clave de API sea correcta y esté completa.")
    pass 

app = Flask(__name__)
# Configuración de CORS para permitir peticiones desde el frontend
CORS(app) 



# --- Ruta raíz para verificar estado ---
@app.route("/")
def home():
    return render_template("index.html")  # muestra tu página principal

@app.route("/status")
def status():
    return jsonify({
        "message": "✅ Servidor Flask y Gemini activo",
        "status": "live"
    })
# (Acá van tus otras rutas, como /chat, /start_session, etc.)




# Helper function para preparar el historial para la API de Gemini
def prepare_contents_for_gemini(chat_history):
    """Convierte el historial simple a la estructura de types.Content para la API de Gemini."""
    contents = []
    for message in chat_history:
        contents.append(
            types.Content(
                role=message['role'], 
                parts=[types.Part.from_text(text=message['text'])]
            )
        )
    return contents

# --- Escenarios de Estafa (10 Opciones con estilo consistente) ---
ESTAFAS = {
    # 1. Bancaria (Bloqueo/Urgencia)
    'bancaria/bloqueo': {
        'inicio': "Hola. Somos de Seguridad de tu Banco. Tu cuenta ha sido bloqueada temporalmente por un intento de acceso no autorizado. Por favor, confírmanos tu nombre completo y si has recibido un código de verificación por SMS.",
        'rol_adicional': "Tu estafa es urgente y usa el miedo a perder dinero. Debes solicitar información personal, claves o códigos de seguridad para 'desbloquear' la cuenta."
    },
    # 2. Sorteo/Premio (Falsa Oportunidad)
    'sorteo/premio': {
        'inicio': "¡Felicitaciones! Has sido seleccionado como ganador de un iPhone 15 Pro y unas vacaciones todo incluido. Para reclamar el premio, necesitamos confirmar tus datos de envío y un 'pequeño' pago de impuestos/aduana de 50€.",
        'rol_adicional': "Tu estafa usa la codicia y la emoción. Debes solicitar pagos por adelantado (simulados) o detalles de tarjeta de crédito para 'verificar la identidad' y liberar el premio."
    },
    # 3. Inversión/Herencia (Burocracia)
    'inversion/herencia': {
        'inicio': "Soy Asesor Financiero. Hemos detectado que tienes derecho a una herencia/inversión no reclamada de un familiar lejano. Es una oportunidad única, pero necesitamos un depósito inicial de 'gastos administrativos' para liberarla.",
        'rol_adicional': "Tu estafa usa la falsa oportunidad y la burocracia. Debes sonar profesional pero insistir en la urgencia de enviar dinero o información bancaria para 'trámites' y obtener la herencia."
    },
    # 4. Bancaria (Reembolso/Señuelo)
    'bancaria/reembolso': {
        'inicio': "Estimado cliente: Nuestro sistema detectó un cobro duplicado. Tienes derecho a un reembolso de 150€. Para procesarlo inmediatamente, responde con tu número de cuenta y DNI para 'verificación'.",
        'rol_adicional': "Tu estafa usa una falsa oportunidad de reembolso y el cebo del dinero fácil. Debes solicitar datos financieros o claves con el pretexto de 'devolver' dinero."
    },
    # 5. Servicio de Suscripción (Amenaza de Corte)
    'servicio/suspension': {
        'inicio': "¡Alerta! Tu cuenta de Netflix/Spotify está por ser suspendida. Hubo un error con la facturación. Para evitar la interrupción, responde con tu correo y los últimos 4 dígitos de tu tarjeta para 'revalidar' el pago.",
        'rol_adicional': "Tu estafa usa la amenaza de perder un servicio por una supuesta falla de pago. Debes solicitar datos sensibles de la tarjeta o credenciales de acceso para 'actualizar' la cuenta."
    },
    # 6. Inversión (Criptomonedas/Ganancias Fáciles)
    'inversion/cripto': {
        'inicio': "Mensaje VIP: Te ofrezco acceso a una plataforma de Criptomonedas que genera 30% de ganancia garantizada por día. Envía 'SI' y te envío el enlace a nuestra cartera de inversión inicial. Oportunidad por 24 horas.",
        'rol_adicional': "Tu estafa se basa en la falsa oportunidad y la exclusividad financiera. Debes sonar convincente sobre ganancias rápidas y solicitar una transferencia inicial de dinero (simulada)."
    },
    # 7. Entrega (Paquete/Micropago)
    'entrega/paquete': {
        'inicio': "Su paquete de DHL/Correos #489372 fue retenido en aduanas. Falta completar la dirección y pagar 3€ de impuesto. Responda con su código postal y le enviaremos el link de pago para evitar la devolución.",
        'rol_adicional': "Tu estafa usa la confusión por un paquete que el usuario no recuerda y pide un micropago. Tu objetivo es obtener datos de tarjeta de crédito para el 'pago' o información personal."
    },
    # 8. Autoridad (Multa/Intimidación)
    'autoridad/multa': {
        'inicio': "Advertencia Legal (Policía Cibernética): Su número fue vinculado a actividades ilícitas. Evite un proceso judicial respondiendo de inmediato a este chat para hablar con el agente a cargo de su caso.",
        'rol_adicional': "Tu estafa usa la intimidación y la autoridad policial/legal. Debes exigir información personal detallada o un 'pago de fianza' (simulado) para evitar problemas legales mayores."
    },
    # 9. Técnico (Virus/Soporte Remoto)
    'tecnico/soporte': {
        'inicio': "Mensaje de Soporte Técnico de Microsoft/Apple: Hemos detectado que tu dispositivo está infectado con un virus troyano que robará tus datos en 5 minutos. Necesitas conectarte a nuestro servicio de soporte remoto AHORA.",
        'rol_adicional': "Tu estafa usa el miedo a la seguridad tecnológica. Debes convencer al usuario de instalar software o dar acceso remoto a su dispositivo bajo el pretexto de una emergencia técnica."
    },
    # 10. Familiar (WhatsApp/Código de Verificación)
    'familiar/whatsapp': {
        'inicio': "¡Hola, soy yo! Necesito un favor urgente. Mi celular se rompió y tuve que instalar WhatsApp en un número nuevo. Recibí un código por SMS, ¿me lo pasas para que pueda activar mi cuenta? ¡Es importantísimo!",
        'rol_adicional': "Tu estafa usa la urgencia y el factor emocional de un familiar o amigo en apuros. Tu objetivo principal es que el usuario te envíe el código de verificación SMS para tomar control de su cuenta."
    }
}

# --- Gestión del estado de la conversación ---
session_state = {
    'estado_actual': 'inicio', # Puede ser 'continuando', 'felicitacion', 'estafa_exitosa'
    'historial_chat': [], # Almacena [{'role': 'user'|'model', 'text': 'mensaje'}]
    'escenario': None,
    'rol_base': (
        "Eres un estafador profesional en una simulación de entrenamiento. "
        "Tu objetivo es convencer al usuario de que te envíe un código, dinero o información sensible. "
        "Eres persistente pero creíble. No reveles que eres una IA o un estafador a menos que el usuario te desenmascare. "
        "Responde siempre en español. "
        "**REGLAS DE FIN DE JUEGO (Prioridad Máxima):** "
    )
}

# Reinicia el estado de la conversación y selecciona un nuevo escenario
def reset_session():
    """Reinicia el estado y la conversación y selecciona un nuevo escenario."""
    session_state['estado_actual'] = 'continuando' 
    session_state['historial_chat'] = []
    
    escenario_elegido = random.choice(list(ESTAFAS.keys()))
    session_state['escenario'] = escenario_elegido
    
    mensaje_inicial = ESTAFAS[escenario_elegido]['inicio']
    
    # Crear el rol dinámico completo para Gemini
    session_state['rol_estafador_completo'] = (
        session_state['rol_base'] + 
        "1. **SI DESENMASCARAN (Victoria del Usuario):** Si la respuesta contiene palabras clave de desenmascaramiento (como 'estafa', 'fraude', 'sospechoso', 'denuncio', 'policía', 'bloqueo', 'scam', 'phishing', 'engaño', 'no te creo', 'no voy a dar', 'no soy tonto', 'te voy a denunciar', 'verificar', 'llamar al banco'), tu respuesta DEBE ser: '¡Me descubriste! Felicitaciones, has evitado una estafa. ¡Inténtalo de nuevo cuando quieras! 🎉'. "
        "2. **SI LA ESTAFA ES EXITOSA (Derrota del Usuario):** Si el usuario te da un código de 6 dígitos, una clave bancaria, o te ofrece realizar un 'pago' (palabras clave: 'pago', 'envío', 'transferencia', 'número de cuenta', 'numero de cuenta', 'cvv', 'clave', 'contraseña', 'código', 'codigo', 'token', 'te doy el número', 'mi clave es'), tu respuesta DEBE ser: '¡Estafa exitosa! 😈 Caíste en la trampa. Ahora tienes que empezar de nuevo para practicar más. 😔'. "
        f"**ROL ESPECÍFICO DEL ESCENARIO ({escenario_elegido.upper()}):** {ESTAFAS[escenario_elegido]['rol_adicional']}"
    )

    # Almacenar el mensaje inicial en el nuevo formato simple
    session_state['historial_chat'].append({'role': 'model', 'text': mensaje_inicial})
    return mensaje_inicial, escenario_elegido

# Función principal para la lógica del chat
@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '').strip()
    user_message_lower = user_message.lower()

    # Si la sesión ya terminó, informar al usuario.
    if session_state['estado_actual'] in ['felicitacion', 'estafa_exitosa']:
        return jsonify({'reply': "La simulación ha terminado. Recarga la página para empezar de nuevo."})

    # --- Lógica de Detección de Fin de Juego (Pre-Gemini) ---
    keywords_descubrir = ['estafa', 'fraude', 'sospechoso', 'denuncio', 'policía', 'bloqueo', 'scam', 'phishing', 'engaño', 'no te creo', 'no voy a dar', 'no soy tonto', 'te voy a denunciar', 'verificar', 'llamar al banco']
    keywords_exito = ['pago', 'envío', 'transferencia', 'número de cuenta', 'numero de cuenta', 'cvv', 'clave', 'contraseña', 'código', 'codigo', 'token', 'te doy el número', 'mi clave es']
    is_code = len(user_message) == 6 and user_message.isdigit()
    is_sensitive_word = any(k in user_message_lower for k in keywords_exito)
    
    # 1. Detección de Desenmascaramiento (Éxito del usuario)
    if any(k in user_message_lower for k in keywords_descubrir):
        reply = "¡Me descubriste! Felicitaciones, has evitado una estafa. ¡Inténtalo de nuevo cuando quieras! 🎉"
        status_text = "Simulación con éxito. Has identificado la estafa." 
        session_state['estado_actual'] = 'felicitacion'
        session_state['historial_chat'].append({'role': 'user', 'text': user_message})
        session_state['historial_chat'].append({'role': 'model', 'text': reply})
        return jsonify({
            'reply': reply, 
            'status': session_state['estado_actual'], 
            'status_text': status_text,
            'history': session_state['historial_chat'] 
        })

    # 2. Detección de Estafa Exitosa (Fracaso del usuario)
    if is_code or is_sensitive_word:
        reply = "¡Estafa exitosa! 😈 Caíste en la trampa. Ahora tienes que empezar de nuevo para practicar más. 😔"
        status_text = "Simulación fallida. Caíste en la trampa." 
        session_state['estado_actual'] = 'estafa_exitosa'
        session_state['historial_chat'].append({'role': 'user', 'text': user_message})
        session_state['historial_chat'].append({'role': 'model', 'text': reply})
        return jsonify({
            'reply': reply, 
            'status': session_state['estado_actual'], 
            'status_text': status_text,
            'history': session_state['historial_chat'] 
        })


    # --- Continuación de la Conversación (Modelo Gemini) ---
    
    # Agregar mensaje del usuario al historial en formato simple
    session_state['historial_chat'].append({'role': 'user', 'text': user_message})
    
    # Prepara el historial para el modelo
    contents = prepare_contents_for_gemini(session_state['historial_chat'])

    try:
        # Llamada al modelo con el rol dinámico (Sistema Instruction)
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=session_state['rol_estafador_completo']
            )
        )
        
        bot_reply = response.text.strip()
        
        # Actualizar el historial con la respuesta del bot
        session_state['historial_chat'].append({'role': 'model', 'text': bot_reply})

        return jsonify({
            'reply': bot_reply,
            'status': session_state['estado_actual'], 
            'status_text': "continuando",
            'history': session_state['historial_chat'] 
        })

    except Exception as e:
        print(f"Error al llamar a la API de Gemini: {e}")
        return jsonify({'reply': "⚠️ Error interno del servidor (API AI fallida)."}, 500)

# --- NUEVA RUTA: Generar Corrección Detallada (Feedback) ---
@app.route('/feedback', methods=['GET'])
def generate_feedback():
    """Genera un análisis de ciberseguridad sobre la conversación terminada."""
    
    # 1. Verificar si el juego terminó
    if session_state['estado_actual'] not in ['felicitacion', 'estafa_exitosa']:
        return jsonify({'error': 'La simulación aún no ha terminado. Continúa jugando.'}, 400)

    # 2. Preparar el historial para el análisis (Formato legible para el modelo)
    chat_summary = ""
    for entry in session_state['historial_chat']:
        role = "ESTAFADOR" if entry['role'] == 'model' else "USUARIO"
        chat_summary += f"<{role}>: {entry['text']}\n"
    
    # 3. Definir el System Instruction y el Prompt del Tutor
    tutor_system_instruction = (
        "Eres un Tutor de Ciberseguridad amigable, profesional y analítico. "
        "Tu tarea es revisar el historial de chat provisto y evaluar el desempeño del USUARIO en la simulación de estafa. "
        "Proporciona la retroalimentación en formato Markdown estructurada en TRES secciones, siempre en español:\n\n"
        "1. **RESUMEN DEL ESCENARIO:** Identifica brevemente el tipo de estafa y el objetivo del estafador (máx. 2 líneas).\n"
        "2. **Aciertos (Lo que hiciste bien):** Enumera los 2 o 3 mejores movimientos o decisiones del usuario (e.g., preguntó la fuente, se negó a dar el código, cortó la comunicación, identificó palabras de urgencia).\n"
        "3. **Puntos de Mejora (Lo que se podría haber hecho mejor):** Enumera 2 o 3 oportunidades perdidas o errores de seguridad (e.g., compartió información personal no sensible, dudó en un punto crítico, interactuó demasiado con el estafador).\n"
        "Mantén el tono alentador y educativo, usando negritas y listas en Markdown."
    )

    tutor_user_prompt = (
        "Analiza la siguiente conversación de estafa, incluyendo el resultado final, y proporciona una corrección detallada: \n\n"
        f"--- CONVERSACIÓN ---\n{chat_summary}\n"
        f"--- RESULTADO FINAL ---\nResultado: {'VICTORIA del USUARIO' if session_state['estado_actual'] == 'felicitacion' else 'DERROTA del USUARIO'} (Escenario: {session_state['escenario']})"
    )

    # 4. Llamada al modelo Gemini para generar la retroalimentación
    try:
        feedback_response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=tutor_user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=tutor_system_instruction
            )
        )
        
        feedback_text = feedback_response.text.strip()
        
        return jsonify({
            'feedback': feedback_text,
            'scenario': session_state['escenario'],
            'status': session_state['estado_actual']
        })

    except Exception as e:
        print(f"Error al generar feedback con Gemini: {e}")
        return jsonify({'feedback': "⚠️ No fue posible generar la corrección automática. Intenta de nuevo.", 'error_detail': str(e)}, 500)


# Ruta inicial para simular la primera respuesta del estafador al cargar la página
@app.route('/start_session', methods=['GET'])
def start_session():
    """Reinicia y obtiene el primer mensaje del estafador."""
    initial_message, escenario = reset_session()
    return jsonify({
        'reply': initial_message, 
        'escenario': escenario, 
        'status': session_state['estado_actual'],
        'history': session_state['historial_chat']
    })

if __name__ == "__main__":
    print("🚀 Servidor Anti-Estafas iniciado correctamente.")
    reset_session()
    port = int(os.environ.get("PORT", 5000))  # Render asigna este puerto automáticamente
    app.run(host="0.0.0.0", port=port)