from twilio.rest import Client
import requests
import certifi

# Test conexión a Twilio (URL real y certificados actualizados)
response = requests.get('https://api.twilio.com', verify=certifi.where())
print("Status code de prueba:", response.status_code)
              

client = Client(account_sid, auth_token)

def hacer_llamada(texto):
    """Envía una llamada real al número de destino con el mensaje."""
    try:
        llamada = client.calls.create(
            twiml=f'<Response><Say voice="alice" language="es-ES">{texto}</Say></Response>',
            to=numero_destino,
            from_=numero_origen
        )
        print("✅ Llamada iniciada. SID:", llamada.sid)
    except Exception as e:
        print("❌ Error al hacer la llamada:", e)

hacer_llamada("Hola, esto es una prueba de llamada con Twilio.")
