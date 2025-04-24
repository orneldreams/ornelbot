import os
import json
import re
from datetime import datetime

CHAT_DIR = "chats"

def extract_title_from_history(history):
    """
    Extrait un titre simple à partir des 3 premiers messages du chat.
    """
    text = " ".join(m["content"] for m in history[:3] if "content" in m).lower()
    keywords = re.findall(r'\b\w+\b', text)
    stopwords = {"le", "la", "les", "de", "des", "un", "une", "en", "et", "avec", "je", "tu", "il", "elle", "on", "que"}
    filtered = [w for w in keywords if w not in stopwords]
    title = "_".join(filtered[:6]) if filtered else "discussion"
    return title.capitalize()

def list_chats():
    if not os.path.exists(CHAT_DIR):
        os.makedirs(CHAT_DIR)

    chats = []
    for filename in sorted(os.listdir(CHAT_DIR), reverse=True):
        if filename.endswith(".json"):
            path = os.path.join(CHAT_DIR, filename)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    title = data.get("title", filename)
                    date_str = data.get("date", "")
                    try:
                        date = datetime.fromisoformat(date_str)
                    except ValueError:
                        date = datetime.fromtimestamp(os.path.getctime(path))
                    chats.append({
                        "filename": filename,
                        "title": title.strip(),
                        "date": date
                    })
            except Exception as e:
                print(f"[WARN] Impossible de lire {filename} : {e}")
    return chats

def load_chat(filename):
    path = os.path.join(CHAT_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_chat(title, messages):
    """
    Sauvegarde un chat. Si aucun titre n'est donné, génère un titre depuis l'historique.
    Retourne le nom de fichier utilisé.
    """
    if not os.path.exists(CHAT_DIR):
        os.makedirs(CHAT_DIR)

    if not title:
        title = extract_title_from_history(messages)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_title = title.replace(" ", "_").replace("/", "-")[:30]
    base_filename = f"{timestamp}_{safe_title}"
    filename = f"{base_filename}.json"
    i = 1
    while os.path.exists(os.path.join(CHAT_DIR, filename)):
        filename = f"{base_filename}_{i}.json"
        i += 1

    data = {
        "title": title,
        "date": datetime.now().isoformat(),
        "messages": messages
    }
    with open(os.path.join(CHAT_DIR, filename), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return filename

def delete_chat(filename):
    path = os.path.join(CHAT_DIR, filename)
    if os.path.exists(path):
        os.remove(path)

def rename_chat(filename, new_title):
    old_path = os.path.join(CHAT_DIR, filename)
    if not os.path.exists(old_path):
        return None

    try:
        with open(old_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        data["title"] = new_title

        prefix = filename.split("_")[0]
        new_filename = f"{prefix}_{new_title.replace(' ', '_')}.json"
        new_path = os.path.join(CHAT_DIR, new_filename)

        with open(new_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        os.remove(old_path)
        return new_filename
    except Exception as e:
        print(f"[ERROR] Échec du renommage : {e}")
        return None
