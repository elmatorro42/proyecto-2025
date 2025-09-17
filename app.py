from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import os 
app = Flask(__name__)
CORS(app)


GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)


model = genai.GenerativeModel('gemini-1.5-flash')

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.json
        user_message = data.get("message", "")

      
        system_instruction = "Sos un estafador simulado para un entrenamiento anti-estafas. Contestá como un estafador, pero nunca des datos reales."

      
        response = model.generate_content(
            contents=user_message,
            system_instruction=system_instruction
        )


        reply = response.text.strip()
        return jsonify({"reply": reply})

    except Exception as e:
        return jsonify({"reply": f"⚠️ Error en el servidor: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
