import streamlit as st
import json
import os
import base64
from datetime import datetime, date, timedelta
from PIL import Image
import re
from core.prompt_builder import build_prompt
from core.groq_client import generate_response
from core.chat_manager import list_chats, load_chat, save_chat, delete_chat, rename_chat

# === Fonctions utilitaires ===
def load_profile():
    with open("profile.json", "r", encoding="utf-8") as f:
        return json.load(f)

def inject_css():
    with open("style/style.css", "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def get_base64_image(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def get_first_user_message(chat_history):
    for msg in chat_history:
        if msg["role"] == "user":
            return msg["content"]
    return "Nouvelle discussion"

def extract_keywords_for_title(text):
    words = text.replace("\n", " ").strip().split()
    return "_".join(words[:6]) if words else "Discussion"

def clean_user_input(text):
    text = text.strip()
    text = re.sub(r"\s+", " ", text)
    if not text:
        return text
    if not text.endswith(('.', '!', '?')):
        text += '.'
    text = text[0].upper() + text[1:]
    text = text.replace("cest", "C'est").replace("Cest", "C'est")
    return text

def format_date_label(d):
    today = date.today()
    if d == today:
        return "Aujourd’hui"
    elif d == today - timedelta(days=1):
        return "Hier"
    elif d >= today - timedelta(days=7):
        return "7 jours précédents"
    else:
        return d.strftime("%d %B %Y")

def insert_date_separator():
    if "last_displayed_date" not in st.session_state:
        st.session_state.last_displayed_date = None
    today = date.today()
    if st.session_state.last_displayed_date != today:
        st.session_state.last_displayed_date = today
        st.markdown(f"""
        <div style='text-align: center; color: gray; margin: 1em 0;'>
            🗓️ Aujourd'hui – {today.strftime('%d/%m/%Y')}
        </div>
        """, unsafe_allow_html=True)

# === Initialisation ===
st.set_page_config(page_title="OrnelBot", page_icon="🤖", layout="centered")
inject_css()
profile = load_profile()

# === Chargement des avatars ===
bot_avatar_path = "assets/avatar.png"
user_avatar_path = "assets/user_avatar.png"

bot_avatar = f"data:image/png;base64,{get_base64_image(bot_avatar_path)}" if os.path.exists(bot_avatar_path) else None
user_avatar = f"data:image/png;base64,{get_base64_image(user_avatar_path)}" if os.path.exists(user_avatar_path) else None

# === Session state ===
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "last_input" not in st.session_state:
    st.session_state.last_input = ""
if "greeted" not in st.session_state:
    st.session_state.greeted = False
if "current_chat_filename" not in st.session_state:
    st.session_state.current_chat_filename = None
if "chat_saved" not in st.session_state:
    st.session_state.chat_saved = False

# === Sidebar façon ChatGPT ===
st.sidebar.header("💬 Discussions")
chat_files = list_chats()

# Group chats by date
grouped_chats = {}
for chat in chat_files:
    date_obj = chat["date"].date() if isinstance(chat["date"], datetime) else date.today()
    label = format_date_label(date_obj)
    grouped_chats.setdefault(label, []).append(chat)

for label in grouped_chats:
    st.sidebar.markdown(f"**{label}**")
    for chat in grouped_chats[label]:
        col1, col2, col3 = st.sidebar.columns([6, 2, 2], gap="small")
        if col1.button(chat["title"], key=f"load_{chat['filename']}"):
            data = load_chat(chat["filename"])
            st.session_state.chat_history = data["messages"]
            st.session_state.greeted = True
            st.session_state.current_chat_filename = chat["filename"]
            st.session_state.chat_saved = True
        if col2.button("✏️", key=f"rename_{chat['filename']}"):
            new_title = st.text_input("Renommer la discussion :", key=f"new_title_{chat['filename']}")
            if new_title:
                new_filename = rename_chat(chat["filename"], new_title)
                if new_filename:
                    st.session_state.current_chat_filename = new_filename
                    st.rerun()
        if col3.button("🗑️", key=f"delete_{chat['filename']}"):
            delete_chat(chat["filename"])
            st.rerun()

if st.sidebar.button("➕ Nouvelle discussion"):
    st.session_state.chat_history = []
    st.session_state.last_input = ""
    st.session_state.greeted = False
    st.session_state.current_chat_filename = None
    st.session_state.chat_saved = False

# === Header fixe avec avatar et réseaux ===
if bot_avatar:
    st.markdown(f"""
    <div class="header-fixed">
        <img src="{bot_avatar}" alt="Avatar">
        <h1>OrnelBot</h1>
        <div class="social-links">
            <a href="https://github.com/tititaya" target="_blank" style="margin-right: 10px;">
                <img src="https://img.icons8.com/ios-glyphs/30/ffffff/github.png"/>
            </a>
            <a href="https://www.linkedin.com/in/ornel-rony-d-01737b267/" target="_blank">
                <img src="https://img.icons8.com/ios-filled/30/ffffff/linkedin.png"/>
            </a>
        </div>
    </div>
    <div style='height: 160px;'></div>
    """, unsafe_allow_html=True)
else:
    st.warning("Avatar du bot manquant.")

# === Message d'accueil une seule fois ===
if not st.session_state.greeted and bot_avatar:
    welcome_message = "Salut ! Je suis OrnelBot. Pose-moi n'importe quelle question sur mes projets, mes compétences ou des sujets généraux."
    st.session_state.chat_history.append({"role": "assistant", "content": welcome_message})
    st.session_state.greeted = True

# === Affichage historique avec date ===
insert_date_separator()
for message in st.session_state.chat_history:
    avatar = bot_avatar if message["role"] == "assistant" else user_avatar
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# === Champ de saisie natif avec vérification ===
user_input = st.chat_input("Tape ton message ici...")

if user_input and user_input.strip() and user_input != st.session_state.last_input:
    cleaned_input = clean_user_input(user_input)
    st.session_state.chat_history.append({"role": "user", "content": cleaned_input})

    prompt = build_prompt(profile, st.session_state.chat_history, cleaned_input)
    response = generate_response(prompt)

    st.session_state.chat_history.append({"role": "assistant", "content": response})
    st.session_state.last_input = user_input

    with st.chat_message("user", avatar=user_avatar):
        st.markdown(cleaned_input)
    with st.chat_message("assistant", avatar=bot_avatar):
        st.markdown(response)

    if not st.session_state.chat_saved:
        first_msg = get_first_user_message(st.session_state.chat_history)
        title = extract_keywords_for_title(first_msg)
        filename = save_chat(title, st.session_state.chat_history)
        st.session_state.current_chat_filename = filename
        st.session_state.chat_saved = True
    else:
        path = os.path.join("chats", st.session_state.current_chat_filename)
        if os.path.exists(path):
            with open(path, "r+", encoding="utf-8") as f:
                data = json.load(f)
                data["messages"] = st.session_state.chat_history
                f.seek(0)
                json.dump(data, f, ensure_ascii=False, indent=2)
                f.truncate()

# === Footer ===
st.markdown("""
<footer style='position: fixed; bottom: 0; width: 100%; background: transparent; text-align: center;'>
<hr style='margin-top: 10px;' />
<p style='color: #888888; font-size: 0.85em;'>
    ©2025 OrnelBot – On est ce qu’on veut.
</p>
</footer>
""", unsafe_allow_html=True)

# === Scroll auto intelligent + bouton flottant ===
st.markdown("""
<style>
.scroll-down-btn {
    position: fixed;
    bottom: 90px;
    right: 20px;
    background-color: #4CAF50;
    border: none;
    color: white;
    padding: 12px;
    border-radius: 50%;
    box-shadow: 0px 2px 6px rgba(0,0,0,0.3);
    cursor: pointer;
    z-index: 9999;
    display: none;
    transition: transform 0.2s ease-in-out;
}
.scroll-down-btn:hover {
    background-color: #388e3c;
    transform: scale(1.1);
}
</style>

<button class="scroll-down-btn" id="scroll-down-btn" title="Voir les derniers messages">⬇️</button>

<script>
let container = null;
const scrollBtn = document.getElementById("scroll-down-btn");
let userAtBottom = true;

function findScrollable() {
    const sections = document.querySelectorAll("section");
    for (let sec of sections) {
        if (sec.scrollHeight > sec.clientHeight + 50) return sec;
    }
    return null;
}

function scrollToBottom() {
    container = findScrollable();
    if (container) {
        container.scrollTo({ top: container.scrollHeight, behavior: 'smooth' });
    }
}

function toggleScrollButton() {
    container = findScrollable();
    if (!container) return;
    const isAtBottom = container.scrollHeight - container.scrollTop <= container.clientHeight + 100;
    scrollBtn.style.display = isAtBottom ? "none" : "block";
    userAtBottom = isAtBottom;
}

scrollBtn.addEventListener("click", scrollToBottom);

const observer = new MutationObserver(() => {
    container = findScrollable();
    if (userAtBottom) scrollToBottom();
    toggleScrollButton();
});
observer.observe(document.body, { childList: true, subtree: true });

window.addEventListener("scroll", toggleScrollButton);
</script>
""", unsafe_allow_html=True)
