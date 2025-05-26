import ollama

# Elegí el modelo: puede ser 'mistral', 'llama2', etc.
modelo = "mistral"

def iniciar_chat():
    print("Estafador (IA Local): ¡Felicidades! Usted ganó un premio increíble.")

    historial = []

    while True:
        user_input = input("\nTu respuesta: ").strip()

        if "cortar" in user_input.lower():
            print("Estafador (IA Local): ¡Qué lástima! Perdió una gran oportunidad...")
            break

        historial.append({'role': 'user', 'content': user_input})

        response = ollama.chat(
            model=modelo,
            messages=[
                {'role': 'system', 'content': (
                    "Sos un estafador telefónico ficticio que simula estafas para entrenar usuarios. "
                    "Tu objetivo es sonar convincente, insistente si el usuario duda, y nunca decir que es una simulación. "
                    "Solo salí del personaje si la palabra clave de salida es 'cortar'."
                )},
                *historial
            ]
        )

        respuesta_texto = response['message']['content']
        print(f"\nEstafador (IA Local): {respuesta_texto}")
        historial.append({'role': 'assistant', 'content': respuesta_texto})

if __name__ == "__main__":
    iniciar_chat()
import ollama

modelo = "mistral"

def iniciar_chat():
    print("Estafador (IA Local): ¡Felicidades! Usted ganó un premio increíble.")

    historial = []
    insistencia_nivel = 0  # 0: simpático, 1: insistente, 2: agresivo

    while True:
        user_input = input("\nTu respuesta: ").strip().lower()

        if "cortar" in user_input:
            print("Estafador (IA Local): ¡Qué lástima! Perdió una gran oportunidad...")
            break

        # Detectar dudas o negativas
        if any(palabra in user_input for palabra in ["no", "dudo", "sospecho", "mentira", "imposible", "nunca"]):
            insistencia_nivel = min(insistencia_nivel + 1, 2)

        # Definir personalidad según nivel
        if insistencia_nivel == 0:
            personalidad = (
                "Sos un estafador telefónico muy simpático y amable. "
                "Elogiás a la víctima, hablás con tono amigable y tratás de ganarte su confianza."
            )
        elif insistencia_nivel == 1:
            personalidad = (
                "Sos un estafador telefónico más frío y calculador. "
                "Te ponés insistente si el usuario duda, presionás suavemente para que acepte, "
                "y tratás de convencerlo con lógica."
            )
        else:
            personalidad = (
                "Sos un estafador telefónico agresivo y amenazante. "
                "Si el usuario sigue negándose, lo intimidás, lo apurás, "
                "y lo presionás fuerte para que acepte la estafa."
            )

        historial.append({'role': 'user', 'content': user_input})

        response = ollama.chat(
            model=modelo,
            messages=[
                {'role': 'system', 'content': (
                    personalidad + " Nunca digas que sos una IA. "
                    "Solo salí del personaje si la palabra clave es 'cortar'."
                )},
                *historial
            ]
        )

        respuesta_texto = response['message']['content']
        print(f"\nEstafador (IA Local): {respuesta_texto}")
        historial.append({'role': 'assistant', 'content': respuesta_texto})

if __name__ == "__main__":
    iniciar_chat()
