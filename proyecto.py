from modules.chat import iniciar_chat

if __name__ == "__main__":
    iniciar_chat()
def iniciar_chat():
    print("Estafador: ¡Felicidades! Usted ganó un premio increíble.")

    while True:
        respuesta = input("Tu respuesta: ").lower()

        if any(palabra in respuesta for palabra in ["no", "dudo", "sospecho", "mentira"]):
            print("Estafador: No hay tiempo para dudar. Si no confirma ahora, pierde el premio.")
        elif any(palabra in respuesta for palabra in ["sí", "acepto", "quiero", "dale"]):
            print("Estafador: Perfecto, ahora necesito que confirme su identidad con una transferencia bancaria.")
        else:
            print("Estafador: ¿Podría repetir? No le entendí bien.")

        # Opción para terminar el chat
        if "cortar" in respuesta or "basta" in respuesta:
            print("Estafador: ¡Qué lástima! Perdió una gran oportunidad...")
            break
import openai
import os
from dotenv import load_dotenv

# Cargar la clave desde el archivo .env
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Plantilla de inicio de conversación
sistema = {
    "role": "system",
    "content": (
        "Sos un estafador telefónico ficticio que simula estafas para entrenar usuarios. "
        "Tu objetivo es sonar convincente, insistente si el usuario duda, y nunca decir que es una simulación. "
        "Solo salí del personaje si la palabra clave de salida es 'cortar'."
    )
}

# Historial de la conversación
historial = [sistema]

def iniciar_chat():
    print("Estafador (IA): ¡Felicidades! Usted ganó un premio increíble.")
    while True:
        user_input = input("\nTu respuesta: ").strip()
        
        # Salida manual
        if "cortar" in user_input.lower():
            print("Estafador (IA): ¡Qué lástima! Perdió una gran oportunidad...")
            break

        historial.append({"role": "user", "content": user_input})

        respuesta = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=historial
        )

        respuesta_texto = respuesta.choices[0].message["content"]
        print(f"\nEstafador (IA): {respuesta_texto}")
        historial.append({"role": "assistant", "content": respuesta_texto})

if __name__ == "__main__":
    iniciar_chat()
