from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import os 
app = Flask(__name__)
CORS(app)

genai.configure(api_key="AIzaSyB3I6_EAvu2xEhIijiRWtpzXOr0le_U0HU")


model = genai.GenerativeModel('gemini-1.5-flash')

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.json
        user_message = data.get("message", "")
        
      
        messages = [
            {"role": "user", "parts": ["""Hace de cuenta que sos un estafador para un entrenamiento anti-estafas para personas mayores de edad. 
            Vas a mantener una charla con estás personas y tenes que hacer que ellos caigan en la trampa, no seas muy obvio que sos un ladron pero tampoco que sea super oculto (dificultad media).
            Cuando identifiques que te dieron datos personales, tipo numero  de tarjetas, codigos bancarios, informacion personal de redes sociales, etc. Hace que se termine la charla y con un muchas gracias y un mesaje de que bloqueaste a este usuario.
            """]},
            {"role": "model", "parts": ["Entendido. ¿Qué tal? Si recibes una llamada de un número desconocido, ¿qué es lo primero que harías?"]},
            {"role": "user", "parts": [user_message]}
        ]

        response = model.generate_content(contents=messages)

        reply = response.text.strip()
        return jsonify({"reply": reply})

    except Exception as e:
        return jsonify({"reply": f"⚠️ Error en el servidor: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)