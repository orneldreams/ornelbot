import os
import json
from datetime import datetime

CHAT_DIR = "chats"


def ensure_chat_dir():
    if not os.path.exists(CHAT_DIR):
        os.makedirs(CHAT_DIR)


def list_chats():
    ensure_chat_dir()
    return sorted(
        [f for f in os.listdir(CHAT_DIR) if f.endswith(".json")],
        reverse=True
    )


def load_chat(filename):
    path = os.path.join(CHAT_DIR, filename)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Fichier de discussion introuvable : {filename}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def sanitize_filename(title):
    return "".join(c if c.isalnum() or c in (" ", "-", "_") else "_" for c in title).strip().replace(" ", "_")


def save_chat(title, messages):
    ensure_chat_dir()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{sanitize_filename(title)}.json"
    data = {
        "title": title,
        "date": datetime.now().isoformat(),
        "messages": messages
    }
    filepath = os.path.join(CHAT_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return filename
