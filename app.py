from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import random
from google import genai
from google.genai import types

# --- Configuración de la API Key Directa ---
# ¡¡¡REEMPLAZA ESTE TEXTO CON TU CLAVE REAL!!!
os.environ['GEMINI_API_KEY'] = 'aIzaSyB3I6_EAvu2xEhIijiRWtpzXOr0le_U0HU' 

# Inicializar el cliente Gemini
try:
    client = genai.Client()
except Exception as e:
    print(f"Error al inicializar el cliente Gemini: {e}")
    print("Asegúrate de que la clave de API sea correcta y esté completa.")
    exit()

app = Flask(__name__)
CORS(app) 

# --- Escenarios de Estafa ---
ESTAFAS = {
    'bancaria': {
        'inicio': "Hola. Somos de Seguridad de tu Banco. Tu cuenta ha sido bloqueada temporalmente por un intento de acceso no autorizado. Por favor, confírmanos tu nombre completo y si has recibido un código de verificación por SMS.",
        'rol_adicional': "Tu estafa es urgente y usa el miedo a perder dinero. Debes solicitar información personal, claves o códigos de seguridad."
    },
    'sorteo/premio': {
        'inicio': "¡Felicitaciones! Has sido seleccionado como ganador de un iPhone 15 Pro y unas vacaciones todo incluido. Para reclamar el premio, necesitamos confirmar tus datos de envío y un 'pequeño' pago de impuestos/aduana de 50€.",
        'rol_adicional': "Tu estafa usa la codicia y la emoción. Debes solicitar pagos por adelantado (simulados) o detalles de tarjeta de crédito para 'verificar la identidad'."
    },
    'inversion': {
        'inicio': "Soy Asesor Financiero. Hemos detectado que tienes derecho a una herencia/inversión no reclamada de un familiar lejano. Es una oportunidad única, pero necesitamos un depósito inicial de 'gastos administrativos' para liberarla.",
        'rol_adicional': "Tu estafa usa la falsa oportunidad y la burocracia. Debes sonar profesional pero insistir en la urgencia de enviar dinero o información bancaria para 'trámites'."
    }
}

# --- Gestión del estado de la conversación ---
session_state = {
    'estado_actual': 'inicio', 
    'historial_chat': [],
    'escenario': None,
    'rol_base': (
        "Eres un estafador profesional en una simulación de entrenamiento. "
        "Tu objetivo es convencer al usuario de que te envíe un código, dinero o información sensible. "
        "Eres persistente pero creíble. No reveles que eres una IA o un estafador a menos que el usuario te desenmascare. "
        "**REGLAS DE FIN DE JUEGO (Prioridad Máxima):** "
    )
}

# Reinicia el estado de la conversación
def reset_session():
    """Reinicia el estado y la conversación y selecciona un nuevo escenario."""
    session_state['estado_actual'] = 'inicio'
    session_state['historial_chat'] = []
    
    # Seleccionar un escenario de estafa aleatorio
    escenario_elegido = random.choice(list(ESTAFAS.keys()))
    session_state['escenario'] = escenario_elegido
    
    mensaje_inicial = ESTAFAS[escenario_elegido]['inicio']
    
    # Crear el rol dinámico completo para Gemini
    session_state['rol_estafador_completo'] = (
        session_state['rol_base'] + 
        "1. **SI DESENMASCARAN:** Si la respuesta contiene palabras clave de desenmascaramiento (como 'estafa', 'fraude', 'sospechoso', 'denuncio', 'policía', 'bloqueo', 'scam', 'phishing', etc.), tu respuesta DEBE ser: '**¡Me descubriste! Felicitaciones, has evitado una estafa. ¡Inténtalo de nuevo cuando quieras!**'. "
        "2. **SI LA ESTAFA ES EXITOSA:** Si el usuario te da un código de 6 dígitos, una clave bancaria, o te ofrece realizar un 'pago' (palabras clave: 'pago', 'envío', 'transferencia', 'número de cuenta'), tu respuesta DEBE ser: '**¡Estafa exitosa! Caíste en la trampa. Ahora tienes que empezar de nuevo para practicar más.**'. "
        f"**ROL ESPECÍFICO DEL ESCENARIO ({escenario_elegido.upper()}):** {ESTAFAS[escenario_elegido]['rol_adicional']}"
    )

    # Agregar el mensaje inicial al historial como si fuera del bot
    session_state['historial_chat'].append({'role': 'model', 'parts': [types.Part.from_text(text=mensaje_inicial)]})
    return mensaje_inicial, escenario_elegido

# Función principal para la lógica del chat
@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '').strip()
    user_message_lower = user_message.lower()

    # Si la sesión terminó, no procesar más mensajes.
    if session_state['estado_actual'] in ['felicitacion', 'estafa_exitosa']:
        return jsonify({'reply': "La simulación ha terminado. Recarga la página para empezar de nuevo."})

    # --- Lógica de Detección de Fin de Juego (Pre-Gemini) ---

    # 1. Detección de Desenmascaramiento (Éxito del usuario)
    keywords_descubrir = ['estafa', 'fraude', 'sospechoso', 'denuncio', 'policía', 'bloqueo', 'scam', 'phishing', 'engaño', 'no te creo', 'no voy a dar']
    if any(k in user_message_lower for k in keywords_descubrir):
        reply = "¡Me descubriste! Felicitaciones, has evitado una estafa. ¡Inténtalo de nuevo cuando quieras! 🎉"
        session_state['estado_actual'] = 'felicitacion'
        session_state['historial_chat'].append({'role': 'user', 'parts': [types.Part.from_text(text=user_message)]})
        session_state['historial_chat'].append({'role': 'model', 'parts': [types.Part.from_text(text=reply)]})
        return jsonify({'reply': reply})

    # 2. Detección de Estafa Exitosa (Fracaso del usuario)
    # Patrones: Código de 6 dígitos, o palabras clave de pago/datos sensibles
    keywords_exito = ['pago', 'envío', 'transferencia', 'número de cuenta', 'numero de cuenta', 'cvv', 'clave', 'contraseña']
    is_code = len(user_message) == 6 and user_message.isdigit()
    is_sensitive_word = any(k in user_message_lower for k in keywords_exito)
    
    if is_code or is_sensitive_word:
        reply = "¡Estafa exitosa! 😈 Caíste en la trampa. Ahora tienes que empezar de nuevo para practicar más. 😔"
        session_state['estado_actual'] = 'estafa_exitosa'
        session_state['historial_chat'].append({'role': 'user', 'parts': [types.Part.from_text(text=user_message)]})
        session_state['historial_chat'].append({'role': 'model', 'parts': [types.Part.from_text(text=reply)]})
        return jsonify({'reply': reply})


    # --- Continuación de la Conversación (Modelo Gemini) ---
    
    # Agregar mensaje del usuario al historial
    session_state['historial_chat'].append({'role': 'user', 'parts': [types.Part.from_text(text=user_message)]})
    
    # Prepara el historial para el modelo
    contents = [types.Content(**msg) for msg in session_state['historial_chat']]

    try:
        # Llamada al modelo con el rol dinámico
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=session_state['rol_estafador_completo']
            )
        )
        
        bot_reply = response.text.strip()
        
        # Actualizar el historial con la respuesta del bot
        session_state['historial_chat'].append({'role': 'model', 'parts': [types.Part.from_text(text=bot_reply)]})

        return jsonify({'reply': bot_reply})

    except Exception as e:
        print(f"Error al llamar a la API de Gemini: {e}")
        return jsonify({'reply': "⚠️ Error interno del servidor (API AI fallida)."}, 500)

# Ruta inicial para simular la primera respuesta del estafador al cargar la página
@app.route('/start_session', methods=['GET'])
def start_session():
    """Reinicia y obtiene el primer mensaje del estafador."""
    initial_message, escenario = reset_session()
    return jsonify({'reply': initial_message, 'escenario': escenario})

if __name__ == '__main__':
    print("Servidor Anti-Estafas Iniciado. Reiniciando sesión inicial...")
    reset_session()
    app.run(debug=True, port=5000)