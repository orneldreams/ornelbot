import os
import json
from datetime import datetime

CHAT_DIR = "chats"

def ensure_chat_dir():
    if not os.path.exists(CHAT_DIR):
        os.makedirs(CHAT_DIR)

def list_chats():
    """Liste les fichiers de discussion triés par date (récente en premier)."""
    ensure_chat_dir()
    chats = []
    for f in os.listdir(CHAT_DIR):
        if f.endswith(".json"):
            with open(os.path.join(CHAT_DIR, f), "r", encoding="utf-8") as file:
                data = json.load(file)
                chats.append({
                    "filename": f,
                    "title": data.get("title", f),
                    "date": data.get("date", "")
                })
    return sorted(chats, key=lambda x: x["date"], reverse=True)

def load_chat(filename):
    """Charge une discussion à partir du nom de fichier."""
    path = os.path.join(CHAT_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_chat(title, messages):
    """Crée et sauvegarde automatiquement une nouvelle discussion."""
    ensure_chat_dir()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_title = title.replace(" ", "_").replace("/", "_")
    filename = f"{timestamp}_{safe_title}.json"
    data = {
        "title": title,
        "date": datetime.now().isoformat(),
        "messages": messages
    }
    with open(os.path.join(CHAT_DIR, filename), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return filename  # retourne le nom du fichier pour chargement immédiat
