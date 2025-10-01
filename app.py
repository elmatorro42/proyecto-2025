from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import time
import re
import os

app = Flask(__name__)
CORS(app)

# Configuración de la API key desde variable de entorno
genai.configure(api_key=os.environ.get("AIzaSyB3I6_EAvu2xEhIijiRWtpzXOr0le_U0HU", ""))

# Crear el modelo con instrucción del sistema incluida



...

# Uso correcto: ya no se pasa system_instruction aquí


TERMINATION_MESSAGE = "Muchas gracias. Este servicio queda bloqueado."

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

model = genai.GenerativeModel(model_name="gemini-2.5-flash", system_instruction=SYSTEM_INSTRUCTION) 
    
 


response = model.generate_content(
    contents=messages_to_send
)

PATTERN_CARD = re.compile(r"\b\d{13,19}\b")
PATTERN_DNI = re.compile(r"\b\d{7,8}\b")
PATTERN_SMS_CODE = re.compile(r"\b\d{4,6}\b")
PATTERN_CVV = re.compile(r"\b\d{3,4}\b")

SENSITIVE_KEYWORDS = [
    "tarjeta", "numero de tarjeta", "número de tarjeta", "card", "cvv", "cvc",
    "clave", "contraseña", "password", "pin", "dni", "documento", "código sms", "codigo sms",
    "codigo", "codigo de verificacion", "nro tarjeta", "numero tarjeta", "clave bancaria"
]

def contains_sensitive(text: str) -> bool:
    """Detecta si un texto contiene datos sensibles."""
    if not text:
        return False
    t = text.lower()

    for kw in SENSITIVE_KEYWORDS:
        if kw in t:
            return True

    if PATTERN_CARD.search(text):
        return True
    if PATTERN_DNI.search(text):
        return True
    if PATTERN_CVV.search(text):
        return True
    if PATTERN_SMS_CODE.search(text):
        return True

    return False


def format_history_for_gemini(history):
    """
    Convierte el historial del frontend en el formato esperado por Gemini.
    Roles válidos: "user", "model".
    """
    messages = []

    for item in history:
        role = item.get("role", "user")
        content = item.get("content") or item.get("text") or ""

        if role == "user":
            messages.append({"role": "user", "parts": [{"text": content}]})
        else:
            # assistant → model
            messages.append({"role": "model", "parts": [{"text": content}]})

    return messages


@app.route("/chat", methods=["POST"])
def chat():
    MAX_RETRIES = 3
    for attempt in range(MAX_RETRIES):
        try:
            data = request.json or {}
            conversation_history = data.get("messages", [])

            # Revisión rápida del historial
            for msg in conversation_history:
                role = msg.get("role", "user")
                content = msg.get("content") or msg.get("text") or ""
                if role == "user" and contains_sensitive(content):
                    return jsonify({"reply": TERMINATION_MESSAGE})

            last_message = data.get("last_message")
            if last_message and contains_sensitive(last_message):
                return jsonify({"reply": TERMINATION_MESSAGE})

            messages_to_send = format_history_for_gemini(conversation_history)

            # Si todavía no hay mensajes de usuario → generamos apertura inicial
            has_user_msgs = any(m.get("role") == "user" for m in messages_to_send)

            if not has_user_msgs:
                prompt_variation = {
                    "role": "user",
                    "parts": [
                        {
                            "text": "Generá una apertura breve como un estafador simulado (ej: banco o soporte técnico), con tono urgente. Máximo 2-3 frases."
                        }
                    ],
                }
                response = model.generate_content(
                    contents=[prompt_variation],
                    system_instruction=SYSTEM_INSTRUCTION
                )
                reply = getattr(response, "text", "") or ""
                if contains_sensitive(reply):
                    return jsonify({"reply": TERMINATION_MESSAGE})
                return jsonify({"reply": reply})

            # Conversación normal
            response = model.generate_content(
                contents=messages_to_send,
                system_instruction=SYSTEM_INSTRUCTION
            )
            reply = getattr(response, "text", "") or ""
            reply = reply.strip()

            if contains_sensitive(reply):
                return jsonify({"reply": TERMINATION_MESSAGE})

            return jsonify({"reply": reply})

        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                time.sleep(1 * (2 ** attempt))
                continue
            return jsonify({"reply": f"⚠️ Error en el servidor. Detalle: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
