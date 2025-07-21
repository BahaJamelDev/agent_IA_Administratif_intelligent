from twilio.rest import Client
import os 
from dotenv import load_dotenv

load_dotenv()
# Charger les variables d'environnement

def send_whatsapp_via_twilio(message, recipient_whatsapp_number):
    ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
    AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
    TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")

    client = Client(ACCOUNT_SID, AUTH_TOKEN)

    try:
        message = client.messages.create(
            body=message,
            from_=TWILIO_WHATSAPP_NUMBER,
            to=f"whatsapp:{recipient_whatsapp_number}"  
        )
        print(f"✅ Message WhatsApp envoyé ! ID: {message.sid}")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de l'envoi: {e}")
        return False

