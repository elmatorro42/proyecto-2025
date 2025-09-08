import ollama
import pyttsx3
from ollama import chat
from ollama import ChatResponse

modelo = "mistral"
engine = pyttsx3.init()

def llamada_estafador(texto):
    print(f"[Llamada] Estafador dice: {texto}")
    engine.say(texto)  # Usar el texto que llega a la función
    engine.runAndWait()


def iniciar_chat():
    print("Estafador (IA Local): ¡Felicidades! Usted ganó un premio increíble.")
    
    historial = []
    insistencia_nivel = 0  # 0: simpático, 1: insistente, 2: agresivo

    while True:
        user_input = input("\nTu respuesta: ").strip().lower()

        if "cortar" in user_input:
            llamada_estafador("Qué lástima. Perdió una gran oportunidad...")
            break

        # Detectar dudas o negativas
        if any(palabra in user_input for palabra in ["no", "dudo", "sospecho", "mentira", "imposible", "nunca"]):
            insistencia_nivel = min(insistencia_nivel + 1, 2)

        """
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
        """

        """ TESTEANDO LA IA
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
        llamada_estafador(respuesta_texto)
        historial.append({'role': 'assistant', 'content': respuesta_texto})

        """

        response: ChatResponse = chat(model="gemma3", messages=[
            
        ])


if __name__ == "__main__":
    iniciar_chat()
