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
