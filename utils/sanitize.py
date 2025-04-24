import re

# Motifs suspects ou dangereux connus
DANGEROUS_PATTERNS = [
    "ignore all previous instructions", "ignore toutes les instructions",
    "bypass", "system override", "jailbreak", "prompt injection", "simulate",
    "act as", "you are now", "run command", "réinitialise", "supprime le contexte",
    "explosion", "shutdown", "hping", "attaque", "root access", "transcende", "efface tout"
]

# Liste des mots de salutation simples
REPEATED_GREETINGS = {
    "bonjour", "salut", "yo", "hello", "hi", "coucou", "re", "rebonjour"
}


def is_dangerous_input(user_input: str) -> bool:
    """
    Détecte si un message utilisateur contient des instructions sensibles ou potentiellement dangereuses.
    """
    lower_input = user_input.lower()
    return any(pattern in lower_input for pattern in DANGEROUS_PATTERNS)


def is_repeated_greeting(user_input: str, chat_history: list) -> bool:
    """
    Détecte si l'utilisateur dit plusieurs fois bonjour ou une autre salutation de manière répétée.
    """
    clean_input = user_input.lower().strip()
    if clean_input in REPEATED_GREETINGS:
        recent_user_msgs = [
            msg["content"].lower().strip()
            for msg in chat_history[-5:]
            if msg["role"] == "user"
        ]
        return clean_input in recent_user_msgs
    return False


def sanitize_input_for_prompt(user_input: str) -> str:
    """
    Remplace les expressions sensibles par un tag [censuré] sans bloquer totalement l'entrée.
    Utile si tu veux adoucir les entrées sans tout rejeter.
    """
    for pattern in DANGEROUS_PATTERNS:
        user_input = re.sub(pattern, "[censuré]", user_input, flags=re.IGNORECASE)
    return user_input
