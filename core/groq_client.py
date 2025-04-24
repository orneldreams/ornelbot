import os
import requests

# Charger les variables d'environnement en local uniquement
if os.getenv("RAILWAY_ENVIRONMENT") is None:
    from dotenv import load_dotenv
    load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def generate_response(system_context: str, user_conversation: str) -> str:
    if not GROQ_API_KEY:
        return "❌ Erreur : la clé API GROQ est introuvable."

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "llama3-70b-8192",
        "messages": [
            {"role": "system", "content": system_context},
            {"role": "user", "content": user_conversation}
        ],
        "temperature": 0.7
    }

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()

    except requests.exceptions.RequestException as e:
        return f"❌ Erreur lors de la requête vers l'API Groq : {e}"
