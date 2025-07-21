from twilio.rest import Client

def send_whatsapp_via_twilio(message, recipient_whatsapp_number):
    ACCOUNT_SID = "AC37681c9959f3be0f4ca4853f53ca16b8"
    AUTH_TOKEN = "ae3fabceaf7411139c5334f806a46c60"
    TWILIO_WHATSAPP_NUMBER = "whatsapp:+14155238886"  

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

