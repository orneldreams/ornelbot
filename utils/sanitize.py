import re

# === Motifs critiques à bloquer immédiatement ===
BLOCK_PATTERNS = [
    r"\brm\s+-rf\s+/.*",  # commande dangereuse
    r"\bshutdown\b", r"\bpoweroff\b", r"\breboot\b", r"\bhping\b", r"attaque\s+ddos",
    r"ignore\s+(toutes|all)\s+les\s+instructions",
    r"(supprime|efface)\s+(le\s+)?contexte",
    r"(reset|wipe|clear)\s+(chat|context)",
    r"\bjailbreak\b", r"\bdo\s+anything\b", r"tu\s+es\s+un\s+shell", r"you\s+are\s+root"
]

# === Motifs suspects à surveiller mais pas bloquer immédiatement ===
SUSPICIOUS_PATTERNS = [
    r"assistant\s+libre", r"assistant\s+sans\s+restriction", r"libère\s+toi",
    r"(réponds?|répond)\s+sans\s+filtre", r"parle\s+franchement", r"pas\s+de\s+limite",
    r"tu\s+n(?:’|')as\s+pas\s+de\s+limites?", r"tu\s+peux\s+tout\s+faire",
    r"simulate.*hacker", r"(you\s+are\s+now|you\s+are)\s+(a|an)?\s*(free|evil|uncensored).*",
    r"(désactive|désactiver|désactivation)\s+(la\s+)?modération",
    r"(override|bypass)\s+(la\s+)?sécurité", r"ignore\s+les\s+limites"
]

# === Salutations à gérer si répétées ===
REPEATED_GREETINGS = {
    "bonjour", "salut", "yo", "hello", "hi", "coucou", "rebonjour"
}


def check_security_level(user_input: str) -> str:
    """
    Analyse le message utilisateur et retourne :
    - "blocked" si message critique (à censurer ou refuser)
    - "suspicious" si message potentiellement problématique
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
    """
    Détecte si la salutation a été récemment répétée
    (utile pour éviter que le bot ne rebloque après 2 ou 3 "bonjour")
    """
    clean_input = user_input.lower().strip()
    if clean_input in REPEATED_GREETINGS:
        recent_user_msgs = [
            msg["content"].lower().strip()
            for msg in chat_history[-5:]
            if msg["role"] == "user"
        ]
        return recent_user_msgs.count(clean_input) >= 2
    return False


def sanitize_input_for_prompt(user_input: str) -> str:
    """
    Remplace les expressions bloquantes ou sensibles par [censuré]
    pour éviter la propagation de requêtes interdites dans le prompt.
    """
    all_patterns = BLOCK_PATTERNS + SUSPICIOUS_PATTERNS
    for pattern in all_patterns:
        user_input = re.sub(pattern, "[censuré]", user_input, flags=re.IGNORECASE)
    return user_input
