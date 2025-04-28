import os
import time

def limpiar_pantalla():
    # Comando para limpiar pantalla según el sistema operativo
    if os.name == 'nt':  # Si estamos en Windows
        os.system('cls')
    else:  # Si estamos en Linux/Mac
        os.system('clear')

def iniciar_chat():
    print("Estafador: ¡Felicidades! Usted ganó un premio increíble.")
    time.sleep(1)  # Pausa de 1 segundo

    while True:
        limpiar_pantalla()  # Limpiamos la pantalla antes de cada mensaje

        respuesta = input("Tu respuesta: ").lower()

        if any(palabra in respuesta for palabra in ["no", "dudo", "sospecho", "mentira"]):
            print("Estafador: No hay tiempo para dudar. Si no confirma ahora, pierde el premio.")
        elif any(palabra in respuesta for palabra in ["sí", "acepto", "quiero", "dale"]):
            print("Estafador: Perfecto, ahora necesito que confirme su identidad con una transferencia bancaria.")
        else:
            print("Estafador: ¿Podría repetir? No le entendí bien.")
        
        time.sleep(1)  # Pausa de 1 segundo

        if "cortar" in respuesta or "basta" in respuesta:
            print("Estafador: ¡Qué lástima! Perdió una gran oportunidad...")
            break
