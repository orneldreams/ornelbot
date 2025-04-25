import speech_recognition as sr
import pyttsx3
import streamlit as st

def listen_microphone():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("Parle maintenant... 🎙️")
        audio = recognizer.listen(source, timeout=5)
    try:
        text = recognizer.recognize_google(audio, language="fr-FR")
        return text
    except sr.UnknownValueError:
        return "Désolé, je n'ai pas compris."

def speak_response(text):
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)
    engine.setProperty('volume', 1)
    engine.say(text)
    engine.runAndWait()
