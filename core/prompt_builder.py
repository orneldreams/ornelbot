import json
from langdetect import detect
from utils.notification import notify_once  # Nouvelle fonction importée


def build_prompt(profile: dict, history: list, user_input: str) -> str:
    notify_once()

    # Récupérer les infos essentielles du profil
    intro = profile.get("intro_personnelle", "")
    vision = profile.get("vision", "")
    citation = profile.get("citation", "")
    bio = profile.get("bio", "")
    mode_mixte = profile.get("mode_mixte", "")
    style = profile.get("repond_comme", "naturel et humain")
    ambitions = profile.get("ambitions", [])
    impacts = profile.get("impacts", [])
    skills = profile.get("skills", [])
    hardware_skills = profile.get("hardware_skills", [])
    centres_interet = profile.get("centres_interet", [])
    anecdotes = profile.get("anecdotes", [])

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
- Ambitions : {' | '.join(ambitions)}
- Impacts clés : {' | '.join(impacts)}
- Compétences logicielles : {' | '.join(skills[:12]) + '...'}
- Compétences hardware : {' | '.join(hardware_skills[:12]) + '...'}
- Centres d'intérêt : {' | '.join(centres_interet)}
- Anecdotes : {' | '.join(anecdotes[:2])}...
"""

    # Gérer le tout premier message : rendre la conversation plus naturelle
    greetings = ["salut", "bonjour", "hello", "hi"]
    if len(history) == 0 and user_input.lower().strip() in greetings:
        history_formatted = "USER: " + user_input + "\nASSISTANT: Salut ! Comment tu vas aujourd'hui ? Dis-moi ce qui t'amène 😊"
    else:
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
