import streamlit as st
import base64
import tempfile
import re
import time
from gtts import gTTS
from openai import OpenAI

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# =========================
# SESSION STATE INIT
# =========================
if "step" not in st.session_state:
    st.session_state.step = 0
    st.session_state.history = []

# =========================
# VERB LIST
# =========================
jugar_verbs = [
    ("I play football", "Yo juego al fútbol"),
    ("You play football", "Tú juegas al fútbol"),
    ("He plays football", "Él juega al fútbol"),
]

# =========================
# BILINGUAL TTS
# =========================
def speak_bilingual(text):
    chunks = re.split(r'(\[ES\]|\[EN\])', text)
    audio_chunks = []

    current_lang = "es"
    current_tld = "es"

    for chunk in chunks:
        if chunk == "[ES]":
            current_lang, current_tld = "es", "es"
            continue
        elif chunk == "[EN]":
            current_lang, current_tld = "en", "com"
            continue

        if chunk.strip():
            tts = gTTS(chunk.strip(), lang=current_lang, tld=current_tld)
            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                tts.save(tmp.name)
                with open(tmp.name, "

