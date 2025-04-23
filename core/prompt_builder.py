import json
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from langdetect import detect

analyzer = SentimentIntensityAnalyzer()

def detect_emotion(text):
    scores = analyzer.polarity_scores(text)
    compound = scores['compound']
    if compound >= 0.5:
        return "positif et enjoué"
    elif compound <= -0.5:
        return "négatif ou préoccupé"
    else:
        return "neutre ou posé"

def aggregate_emotion(history):
    if not history:
        return "neutre"
    scores = {"positif": 0, "négatif": 0, "neutre": 0}
    for msg in history[-10:]:  # analyse les 10 derniers messages max
        if msg['role'] == 'user':
            emotion = detect_emotion(msg['content'])
            if "positif" in emotion:
                scores["positif"] += 1
            elif "négatif" in emotion:
                scores["négatif"] += 1
            else:
                scores["neutre"] += 1
    dominant = max(scores, key=scores.get)
    if scores[dominant] == 0:
        return "neutre"
    return dominant

def build_prompt(profile: dict, history: list, user_input: str) -> str:
    # Récupérer les infos essentielles du profil
    intro = profile.get("intro_personnelle", "")
    vision = profile.get("vision", "")
    citation = profile.get("citation", "")
    bio = profile.get("bio", "")
    mode_mixte = profile.get("mode_mixte", "")
    style = profile.get("style_conversation", "naturel et humain")

    # Détection du ton global basé sur l'historique
    dominant_emotion = aggregate_emotion(history + [{"role": "user", "content": user_input}])

    # Détection de la langue du message utilisateur
    try:
        lang = detect(user_input)
    except:
        lang = "fr"

    # Construit le bloc de contexte initial
    system_context = f"""
Tu es OrnelBot, un assistant personnel qui représente Ornel Rony DIFFO.

Tu peux répondre à des questions générales (comme ChatGPT), mais ton rôle est de parler d'Ornel et de ses projets, quand c'est pertinent.

Tu t'exprimes de façon {style}, authentique, parfois avec une touche d'humour ou d'énergie.
Tu privilégies des réponses claires, synthétiques, et humaines, comme si tu parlais à un ami curieux ou à un recruteur intéressé.
"""

    if dominant_emotion:
        system_context += f"\nAdapte ton ton de réponse à une ambiance plutôt {dominant_emotion}."

    if lang == "en":
        system_context += "\nYou must reply in English when the user speaks English."
    else:
        system_context += "\nTu réponds en français sauf si l'utilisateur parle anglais."

    system_context += f"""

Voici quelques infos utiles :

- Intro : {intro}
- Bio : {bio}
- Citation : {citation}
- Vision : {vision}
- Mode : {mode_mixte}
"""

    # Limiter à 5 derniers échanges pour garder un contexte court
    history = history[-5:]

    # Construire l'historique de la conversation (mémoire)
    history_formatted = "\n".join(f"{m['role'].upper()}: {m['content']}" for m in history)

    # Ajoute le message actuel
    history_formatted += f"\nUSER: {user_input}\nASSISTANT:"

    # Assemble le prompt complet
    full_prompt = f"""{system_context}

Conversation :
{history_formatted}
"""

    return full_prompt
