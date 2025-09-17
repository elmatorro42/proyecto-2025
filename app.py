from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI

app = Flask(__name__)
CORS(app)  # permite que el front (localhost:3000, etc.) acceda al backend

# Cliente OpenAI (asegurate de tener la variable de entorno OPENAI_API_KEY)
client = OpenAI()

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.json
        user_message = data.get("message", "")

        # Llamada al modelo de OpenAI
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # podés usar gpt-4o, gpt-4.1-mini, etc.
            messages=[
                {"role": "system", "content": "Sos un estafador simulado para un entrenamiento anti-estafas. Contestá como un estafador, pero nunca des datos reales."},
                {"role": "user", "content": user_message}
            ]
        )

        reply = response.choices[0].message.content.strip()
        return jsonify({"reply": reply})

    except Exception as e:
        return jsonify({"reply": f"⚠️ Error en el servidor: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
