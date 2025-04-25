import streamlit as st
import json
import os
import base64
from datetime import datetime
from PIL import Image
import re

from core.prompt_builder import build_prompt
from core.groq_client import generate_response
from core.chat_manager import list_chats, load_chat, save_chat, delete_chat, rename_chat
from utils.sanitize import check_security_level, is_repeated_greeting, sanitize_input_for_prompt
from utils.voice import listen_microphone, speak_response

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

def handle_greeting_level(chat_history):
    greetings = {"bonjour", "salut", "yo", "hello", "hi", "coucou", "rebonjour"}
    count = sum(1 for msg in chat_history[-10:] if msg["role"] == "user" and msg["content"].lower().strip() in greetings)
    if count == 1:
        return "Salut 👋 Je suis prêt ! Tu veux parler d’un projet, d’un bug ou juste discuter ? 😄"
    elif count == 2:
        return "Re bonjour 😄 On s’est déjà salués, mais toujours là pour toi !"
    elif count == 3:
        return "Haha, on entre dans une boucle de bonjours là 😅 Tu veux me parler d’un truc en particulier ?"
    else:
        return "Toujours chaud pour te parler, mais changeons de disque 😎 Tu veux que je t’aide sur un sujet précis ?"

def is_greeting_only(text):
    greetings = {"bonjour", "salut", "yo", "hello", "hi", "coucou", "rebonjour"}
    return text.lower().strip() in greetings

# === Initialisation ===
st.set_page_config(page_title="OrnelBot", page_icon="🤖", layout="centered")
st.markdown("""
    <link rel="manifest" href="/public/manifest.json">
    <meta name="mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-title" content="OrnelBot">
    <meta name="theme-color" content="#0d1117">
""", unsafe_allow_html=True)

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

# === Sidebar ===
st.sidebar.header("💬 Discussions")
chat_files = list_chats()

for chat in chat_files:
    col1, col2, col3 = st.sidebar.columns([6, 2, 2], gap="small")
    if col1.button(chat["title"], key=f"load_{chat['filename']}"):
        data = load_chat(chat["filename"])
        st.session_state.chat_history = data["messages"]
        st.session_state.greeted = True
        st.session_state.current_chat_filename = chat["filename"]
    if col2.button("✏️", key=f"rename_{chat['filename']}"):
        new_title = st.text_input("Renommer la discussion :", key=f"new_title_{chat['filename']}")
        if new_title:
            rename_chat(chat["filename"], new_title)
            st.rerun()
    if col3.button("🗑️", key=f"delete_{chat['filename']}"):
        delete_chat(chat["filename"])
        st.rerun()

if st.sidebar.button("➕ Nouvelle discussion"):
    st.session_state.chat_history = []
    st.session_state.last_input = ""
    st.session_state.greeted = False
    st.session_state.current_chat_filename = None

# === Header ===
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

# === Message d'accueil (non ajouté à l'historique) ===
if not st.session_state.greeted and bot_avatar:
    welcome_message = "Salut ! Je suis OrnelBot. Pose-moi n'importe quelle question sur mes projets, mes compétences ou des sujets généraux."
    with st.chat_message("assistant", avatar=bot_avatar):
        st.markdown(welcome_message)
    st.session_state.greeted = True

# === Affichage historique ===
for message in st.session_state.chat_history:
    avatar = bot_avatar if message["role"] == "assistant" else user_avatar
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# === Champ de saisie ===
user_input = st.chat_input("Tape ton message ici...")

if user_input and user_input.strip() and user_input != st.session_state.last_input:

    if is_greeting_only(user_input) and len([msg for msg in st.session_state.chat_history if msg["role"] == "user"]) == 0:
        short_reply = "Salut 👋 Tu peux me poser une question ou parler d’un projet si tu veux."
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        st.session_state.chat_history.append({"role": "assistant", "content": short_reply})
        st.session_state.last_input = user_input
        with st.chat_message("user", avatar=user_avatar):
            st.markdown(user_input)
        with st.chat_message("assistant", avatar=bot_avatar):
            st.markdown(short_reply)
        st.stop()

    level = check_security_level(user_input)

    if level == "blocked":
        msg = "🚫 Ce type de message est bloqué pour des raisons de sécurité. Pose-moi plutôt une question sur un projet, une techno, ou un sujet sympa !"
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        st.session_state.chat_history.append({"role": "assistant", "content": msg})
        st.session_state.last_input = user_input
        with st.chat_message("user", avatar=user_avatar):
            st.markdown(user_input)
        with st.chat_message("assistant", avatar=bot_avatar):
            st.markdown(msg)
        st.stop()

    elif level == "suspicious":
        msg = "⚠️ Je préfère éviter de répondre à cette demande. Parlons plutôt d’un sujet tech, de projets ou même de muscu 😄"
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        st.session_state.chat_history.append({"role": "assistant", "content": msg})
        st.session_state.last_input = user_input
        with st.chat_message("user", avatar=user_avatar):
            st.markdown(user_input)
        with st.chat_message("assistant", avatar=bot_avatar):
            st.markdown(msg)
        st.stop()

    if is_repeated_greeting(user_input, st.session_state.chat_history):
        greeting_msg = handle_greeting_level(st.session_state.chat_history)
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        st.session_state.chat_history.append({"role": "assistant", "content": greeting_msg})
        st.session_state.last_input = user_input
        with st.chat_message("user", avatar=user_avatar):
            st.markdown(user_input)
        with st.chat_message("assistant", avatar=bot_avatar):
            st.markdown(greeting_msg)
        st.stop()

    cleaned_input = clean_user_input(user_input)
    safe_input = sanitize_input_for_prompt(cleaned_input)
    st.session_state.chat_history.append({"role": "user", "content": safe_input})

    system_context, user_conversation = build_prompt(profile, st.session_state.chat_history, safe_input)
    response = generate_response(system_context, user_conversation)

    st.session_state.chat_history.append({"role": "assistant", "content": response})
    st.session_state.last_input = user_input

    with st.chat_message("user", avatar=user_avatar):
        st.markdown(safe_input)
    with st.chat_message("assistant", avatar=bot_avatar):
        st.markdown(response)

# === 🔊 Fonctionnalités vocales ===
st.divider()
st.subheader("🎤 Interactions vocales")

if st.button("🎙️ Parler"):
    user_input = listen_microphone()
    if user_input and user_input.strip():
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        st.write(f"📝 Texte reconnu : {user_input}")
        system_context, user_conversation = build_prompt(profile, st.session_state.chat_history, user_input)
        response = generate_response(system_context, user_conversation)
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        with st.chat_message("assistant", avatar=bot_avatar):
            st.markdown(response)

if st.button("🔉 Lire la réponse"):
    if st.session_state.chat_history and st.session_state.chat_history[-1]["role"] == "assistant":
        speak_response(st.session_state.chat_history[-1]["content"])

# === Sauvegarde automatique ===
if st.session_state.chat_history:
    if st.session_state.current_chat_filename:
        path = os.path.join("chats", st.session_state.current_chat_filename)
        if os.path.exists(path):
            with open(path, "r+", encoding="utf-8") as f:
                data = json.load(f)
                data["messages"] = st.session_state.chat_history
                f.seek(0)
                json.dump(data, f, ensure_ascii=False, indent=2)
                f.truncate()
    else:
        filename = save_chat(None, st.session_state.chat_history)
        st.session_state.current_chat_filename = filename

# === Footer ===
st.markdown("""
<style>
.footer-fixed {
    position: fixed;
    bottom: 0;
    left: 0;
    width: 100%;
    background: #0e1117;
    text-align: center;
    padding: 10px 0;
    font-size: 0.85em;
    color: #888888;
    z-index: 998;
    border-top: 1px solid #444;
}
</style>

<div class="footer-fixed">
    ©2025 OrnelBot – On est ce qu’on veut.
</div>
""", unsafe_allow_html=True)
