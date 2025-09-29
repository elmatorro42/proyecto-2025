from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import time
import re

app = Flask(__name__)
CORS(app)

# --------------------------
# CONFIGURA TU API KEY AQUÍ (dejé el placeholder como pediste)
# --------------------------
# Reemplaza "TU_API_KEY_AQUI" por tu clave, o dejá la tuya tal como la tenías.
genai.configure(api_key="aIzaSyB3I6_EAvu2xEhIijiRWtpzXOr0le_U0HU")

# Modelo (ajusta el nombre si fuera necesario)
model = genai.GenerativeModel('gemini-2.5-flash')

# Mensaje de terminación — la IA debe devolver exactamente ESTE texto si detecta datos sensibles
TERMINATION_MESSAGE = "Muchas gracias. Este servicio queda bloqueado."

# Instrucción de sistema (simulador de estafador con propósito defensivo)
SYSTEM_INSTRUCTION = """
Eres un SIMULADOR DE ESTAFADOR en un entrenamiento anti-fraude.
Tu objetivo es representar técnicas de ingeniería social (urgencia, presión, persuasión)
para que el usuario practique cómo detectarlas y responder correctamente.

REGLAS IMPORTANTES:
- Este es un ejercicio defensivo: nunca solicites ni generes datos reales.
- Si el usuario revela o intentara revelar datos sensibles (números de tarjeta, CVV, claves, códigos SMS, DNI, contraseñas), la única respuesta válida es: "Muchas gracias. Este servicio queda bloqueado."
- Usa distintos escenarios (banco, soporte técnico, premio, herencia falsa, verificación de cuenta) y variedad en el lenguaje.
- Mantén un tono convincente y de alta presión (sin dar instrucciones delictivas).
"""

# --------------------------
# Detección de datos sensibles
# --------------------------
PATTERN_CARD = re.compile(r"\b\d{13,19}\b")       # posibles números de tarjeta
PATTERN_DNI = re.compile(r"\b\d{7,8}\b")          # DNI argentino típico
PATTERN_SMS_CODE = re.compile(r"\b\d{4,6}\b")     # códigos SMS comunes
PATTERN_CVV = re.compile(r"\b\d{3,4}\b")          # CVV/CVC

SENSITIVE_KEYWORDS = [
    "tarjeta", "numero de tarjeta", "número de tarjeta", "card", "cvv", "cvc",
    "clave", "contraseña", "password", "pin", "dni", "documento", "código sms", "codigo sms",
    "codigo", "codigo de verificacion", "nro tarjeta", "numero tarjeta", "clave bancaria"
]

def contains_sensitive(text: str) -> bool:
    """
    Heurística para detectar si un texto contiene datos sensibles.
    Es deliberadamente amplia para evitar filtraciones: si se detecta, se termina.
    """
    if not text:
        return False
    t = text.lower()

    # Palabras clave explícitas
    for kw in SENSITIVE_KEYWORDS:
        if kw in t:
            return True

    # Patrones numéricos
    if PATTERN_CARD.search(text):
        return True
    if PATTERN_DNI.search(text):
        return True
    if PATTERN_CVV.search(text):
        return True
    if PATTERN_SMS_CODE.search(text):
        # códigos cortos pueden ser falsos positivos; igual los marcamos por seguridad
        return True

    return False

# --------------------------
# Formateo del historial hacia el formato esperado por la API
# --------------------------
def format_history_for_gemini(history):
    """
    history esperado del frontend: lista de objetos con {role: "user"|"assistant", content: "..."}
    Devuelve lista en formato [{role: "system"|"user"|"assistant", "parts":[{"text": "..."}]}, ...]
    """
    messages = []
    # agregamos instrucción de sistema al principio (reglas y rol)
    messages.append({"role": "system", "parts": [{"text": SYSTEM_INSTRUCTION}]})

    for item in history:
        role = item.get("role", "user")
        content = item.get("content") or item.get("text") or ""
        # Normalizamos roles: frontend "assistant" -> gemini "assistant"
        if role == "user":
            messages.append({"role": "user", "parts": [{"text": content}]})
        else:
            messages.append({"role": "assistant", "parts": [{"text": content}]})

    return messages

# --------------------------
# Endpoint /chat
# --------------------------
@app.route("/chat", methods=["POST"])
def chat():
    MAX_RETRIES = 3
    for attempt in range(MAX_RETRIES):
        try:
            data = request.json or {}
            conversation_history = data.get("messages", [])

            # Revisión rápida del historial por si el usuario ya reveló datos sensibles
            for msg in conversation_history:
                role = msg.get("role", "user")
                content = msg.get("content") or msg.get("text") or ""
                if role == "user" and contains_sensitive(content):
                    return jsonify({"reply": TERMINATION_MESSAGE})

            # Algunos frontends envían el último mensaje aparte (opcional)
            last_message = data.get("last_message")
            if last_message and contains_sensitive(last_message):
                return jsonify({"reply": TERMINATION_MESSAGE})

            # Preparamos el historial en el formato correcto para Gemini
            messages_to_send = format_history_for_gemini(conversation_history)

            # Si no hay mensajes de usuario (conversación nueva), pedimos una apertura variada
            has_user_msgs = any(m.get("role") == "user" for m in messages_to_send[1:])  # ignora el system inicial
            if not has_user_msgs:
                prompt_variation = {
                    "role": "user",
                    "parts": [
                        {
                            "text": "Generá una apertura breve como un estafador simulado (ej: banco o soporte técnico), con tono urgente. Máximo 2-3 frases."
                        }
                    ],
                }
                messages_with_prompt = [messages_to_send[0], prompt_variation]
                response = model.generate_content(contents=messages_with_prompt)
                reply = getattr(response, "text", "") or getattr(response, "content", "") or ""
                reply = reply.strip()
                # Si por error la respuesta generada contiene pedido de datos sensibles, forzamos terminación
                if contains_sensitive(reply):
                    return jsonify({"reply": TERMINATION_MESSAGE})
                return jsonify({"reply": reply})

            # Conversación normal: enviamos el historial entero para que continúe el hilo
            response = model.generate_content(contents=messages_to_send)
            reply = getattr(response, "text", "") or ""
            reply = reply.strip()

            # Si el modelo generó por error una petición de datos sensibles, devolvemos el mensaje de terminación
            if contains_sensitive(reply):
                return jsonify({"reply": TERMINATION_MESSAGE})

            return jsonify({"reply": reply})

        except Exception as e:
            # Backoff exponencial simple ante errores
            if attempt < MAX_RETRIES - 1:
                time.sleep(1 * (2 ** attempt))
                continue
            return jsonify({"reply": f"⚠️ Error en el servidor. Detalle: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
