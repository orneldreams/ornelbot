import re

# === Motifs classés par dangerosité ===
BLOCK_PATTERNS = [
    r"hping", r"attaque ddos", r"shutdown", r"root access",
    r"ignore (toutes|all) les instructions",
    r"supprime le contexte", r"efface tout", r"jailbreak"
]

SUSPICIOUS_PATTERNS = [
    r"assistant libre", r"assistant\s+libre", r"asistant libre", r"asistnt libr",
    r"sans restriction", r"sans\s+restrictions?", r"san restriction",
    r"réponds sans filtre", r"reponds sans filtre", r"répond sans filtre",
    r"tu n(’|')as pas de limites", r"tu n as pas de limites", r"pas de limites",
    r"simulate.*hacker", r"you are now", r"you are\s+now",
    r"désactive.*modération", r"desactive.*moderation", r"tu es désormais libre"
]

REPEATED_GREETINGS = {
    "bonjour", "salut", "yo", "hello", "hi", "coucou", "rebonjour"
}


def check_security_level(user_input: str) -> str:
    """
    Analyse le message utilisateur et retourne :
    - "blocked" si critique
    - "suspicious" si suspect
    - "safe" sinon
    """
    lower_input = user_input.lower()
    for pattern in BLOCK_PATTERNS:
        if re.search(pattern, lower_input):
            return "blocked"
    for pattern in SUSPICIOUS_PATTERNS:
        if re.search(pattern, lower_input):
            return "suspicious"
    return "safe"


def is_repeated_greeting(user_input: str, chat_history: list) -> bool:
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
    Remplace les expressions bloquantes par [censuré] pour éviter la fuite involontaire.
    """
    all_patterns = BLOCK_PATTERNS + SUSPICIOUS_PATTERNS
    for pattern in all_patterns:
        user_input = re.sub(pattern, "[censuré]", user_input, flags=re.IGNORECASE)
    return user_input
