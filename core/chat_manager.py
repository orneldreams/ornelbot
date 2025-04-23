import os
import json
from datetime import datetime

CHAT_DIR = "chats"

def list_chats():
    """
    Retourne une liste de dictionnaires contenant :
    - filename
    - title
    - date (datetime)
    """
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
    """
    Charge le contenu d'un chat depuis un fichier JSON.
    """
    path = os.path.join(CHAT_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_chat(title, messages):
    """
    Sauvegarde un chat avec un nom basé sur l'heure et le titre.
    """
    if not os.path.exists(CHAT_DIR):
        os.makedirs(CHAT_DIR)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_title = title.replace(" ", "_").replace("/", "-")[:30]
    filename = f"{timestamp}_{safe_title}.json"
    data = {
        "title": title,
        "date": datetime.now().isoformat(),
        "messages": messages
    }
    with open(os.path.join(CHAT_DIR, filename), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)



def list_chats():
    if not os.path.exists(CHAT_DIR):
        os.makedirs(CHAT_DIR)
    files = [f for f in os.listdir(CHAT_DIR) if f.endswith(".json")]
    chats = []
    for f in sorted(files, reverse=True):
        path = os.path.join(CHAT_DIR, f)
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)
            chats.append({
                "filename": f,
                "title": data.get("title", f[:-5]),
                "date": data.get("date", "")
            })
    return chats

def load_chat(filename):
    path = os.path.join(CHAT_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_chat(title, messages):
    if not os.path.exists(CHAT_DIR):
        os.makedirs(CHAT_DIR)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{title.replace(' ', '_')}.json"
    data = {
        "title": title,
        "date": datetime.now().isoformat(),
        "messages": messages
    }
    with open(os.path.join(CHAT_DIR, filename), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def delete_chat(filename):
    path = os.path.join(CHAT_DIR, filename)
    if os.path.exists(path):
        os.remove(path)

def rename_chat(filename, new_title):
    old_path = os.path.join(CHAT_DIR, filename)
    new_filename = filename.split("_")[0] + "_" + new_title.replace(" ", "_") + ".json"
    new_path = os.path.join(CHAT_DIR, new_filename)
    if os.path.exists(old_path):
        with open(old_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        data["title"] = new_title
        with open(new_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.remove(old_path)
