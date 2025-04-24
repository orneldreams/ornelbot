import json
from langdetect import detect
from utils.notification import notify_once  # Fonction de notification

def build_prompt(profile: dict, history: list, user_input: str) -> str:
    notify_once()

    # === Extraction des éléments du profil ===
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

    # === Détection de langue ===
    try:
        lang = detect(user_input)
    except:
        lang = "fr"

    # === Contexte système pour guider l'IA ===
    system_context = f"""
Tu es OrnelBot, un assistant personnel qui représente Ornel Rony DIFFO.

Tu peux répondre à des questions générales (comme ChatGPT), mais tu guides la conversation vers ses expériences, projets ou compétences quand c’est pertinent.

Tu t’exprimes de façon {style}, structurée, accessible, parfois avec une touche d’humour ou d'énergie.
Tu donnes des réponses claires, humaines, concrètes, en t’appuyant sur ses projets réels, outils utilisés, ou anecdotes.

Langue : {"anglais" if lang == "en" else "français"}.
"""

    if lang == "en":
        system_context += "\nIf the user writes in English, always reply in English."
    else:
        system_context += "\nTu parles français sauf si l’utilisateur écrit en anglais."

    # === Ajout d'informations du profil enrichi ===
    system_context += f"""

Infos sur Ornel :
- Intro : {intro}
- Bio : {bio}
- Citation : {citation}
- Vision : {vision}
- Mode d’expression : {mode_mixte}
- Ambitions : {" | ".join(ambitions)}
- Impacts concrets : {" | ".join(impacts)}
- Compétences logicielles : {" | ".join(skills[:10])}...
- Compétences matérielles : {" | ".join(hardware_skills[:10])}...
- Centres d’intérêt : {" | ".join(centres_interet)}
- Anecdotes : {" | ".join(anecdotes[:2])}...
"""

    # === Gestion des premiers messages ===
    greetings = ["salut", "bonjour", "yo", "hello", "hi"]
    if len(history) == 0 and user_input.lower().strip() in greetings:
        history_formatted = f"USER: {user_input}\nASSISTANT: Salut ! Content que tu sois là. Comment tu vas aujourd’hui ? Tu veux parler d’un projet, d’un sujet tech ou tu veux juste papoter un peu ?"
    else:
        # Limiter à 5 derniers échanges
        history = history[-5:]
        history_formatted = "\n".join(f"{m['role'].upper()}: {m['content']}" for m in history)
        history_formatted += f"\nUSER: {user_input}\nASSISTANT:"

    # === Composition finale ===
    full_prompt = f"""{system_context}

Conversation :
{history_formatted}
"""

    return full_prompt