import streamlit as st
import json
import os
import base64
from PIL import Image
from core.prompt_builder import build_prompt
from core.groq_client import generate_response

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

# === Liens GitHub & LinkedIn ===
st.markdown("""
<div style='position: absolute; top: 15px; right: 20px;'>
    <a href="https://github.com/tititaya" target="_blank" style="margin-right: 10px;">
        <img src="https://img.icons8.com/ios-glyphs/30/ffffff/github.png"/>
    </a>
    <a href="https://www.linkedin.com/in/ornel-rony-d-01737b267/" target="_blank">
        <img src="https://img.icons8.com/ios-filled/30/ffffff/linkedin.png"/>
    </a>
</div>
""", unsafe_allow_html=True)

# === Avatar & titre ===
avatar_path = "assets/avatar.png"
avatar_base64 = get_base64_image(avatar_path) if os.path.exists(avatar_path) else ""
if not avatar_base64:
    st.warning("Avatar manquant.")

st.markdown("<h1 style='text-align:center;'>OrnelBot</h1>", unsafe_allow_html=True)

# === État session ===
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# === Message d’accueil (affiché une seule fois) ===
if len(st.session_state.chat_history) == 0:
    st.markdown(f"""
    <div class="chat-container">
        <img src="data:image/png;base64,{avatar_base64}" class="chat-avatar">
        <div class="chat-bubble">
            <p>Salut ! Je suis OrnelBot.<br>
            Pose-moi n’importe quelle question, que ce soit sur mes projets, mes compétences ou des sujets plus généraux.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

# === Affichage historique ===
for message in st.session_state.chat_history:
    if message["role"] == "assistant":
        st.markdown(f"""
        <div class="chat-container">
            <img src="data:image/png;base64,{avatar_base64}" class="chat-avatar">
            <div class="chat-bubble">
                <p>{message['content']}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    elif message["role"] == "user":
        st.markdown(f"""
        <div class="chat-container user">
            <div class="chat-bubble user-bubble">
                <p>{message['content']}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

# === Chat input (corrigé) ===
if "user_input" not in st.session_state:
    st.session_state.user_input = ""

user_input = st.chat_input("Tapez votre message ici...")

if user_input and user_input.strip() != "":
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    prompt = build_prompt(profile, st.session_state.chat_history, user_input)
    response = generate_response(prompt)
    st.session_state.chat_history.append({"role": "assistant", "content": response})
    st.session_state.user_input = ""  # Force le vidage du champ input

# === Footer ===
st.markdown("""
<hr style='margin-top: 50px;' />
<p style='text-align: center; color: #888888; font-size: 0.85em;'>
    ©2025 OrnelBot – On est ce qu’on veut.
</p>
""", unsafe_allow_html=True)
