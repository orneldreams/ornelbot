# utils/notification.py
import os
from dotenv import load_dotenv
from twilio.rest import Client

load_dotenv()

TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")
RECIPIENT_WHATSAPP_NUMBER = os.getenv("RECIPIENT_WHATSAPP_NUMBER")

def notify_once():
    if "already_notified" not in globals():
        globals()["already_notified"] = True
        try:
            client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)
            client.messages.create(
                body="👋 Une personne vient d'ouvrir OrnelBot !",
                from_=TWILIO_WHATSAPP_NUMBER,
                to=RECIPIENT_WHATSAPP_NUMBER
            )
        except Exception as e:
            print(f"[Erreur Twilio] {e}")
