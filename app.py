import streamlit as st
import json
import os
import base64
from datetime import datetime
from PIL import Image
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

# === Sidebar façon ChatGPT ===
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
            st.experimental_rerun()
    if col3.button("🗑️", key=f"delete_{chat['filename']}"):
        delete_chat(chat["filename"])
        st.experimental_rerun()

if st.sidebar.button("➕ Nouvelle discussion"):
    st.session_state.chat_history = []
    st.session_state.last_input = ""
    st.session_state.greeted = False
    st.session_state.current_chat_filename = None

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

# === Affichage historique ===
for message in st.session_state.chat_history:
    avatar = bot_avatar if message["role"] == "assistant" else user_avatar
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# === Champ de saisie natif avec vérification ===
user_input = st.chat_input("Tape ton message ici...")

if user_input and user_input.strip() and user_input != st.session_state.last_input:
    user_input = user_input.strip()
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    prompt = build_prompt(profile, st.session_state.chat_history, user_input)
    response = generate_response(prompt)

    st.session_state.chat_history.append({"role": "assistant", "content": response})
    st.session_state.last_input = user_input

    with st.chat_message("user", avatar=user_avatar):
        st.markdown(user_input)
    with st.chat_message("assistant", avatar=bot_avatar):
        st.markdown(response)

# === Sauvegarde automatique après chaque échange ===
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
        title = st.session_state.chat_history[0]["content"][:30].replace(" ", "_").strip(".,")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{title}.json"
        save_chat(title, st.session_state.chat_history)
        st.session_state.current_chat_filename = filename

# === Footer ===
st.markdown("""
<hr style='margin-top: 50px;' />
<p style='text-align: center; color: #888888; font-size: 0.85em;'>
    ©2025 OrnelBot – On est ce qu’on veut.
</p>
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
