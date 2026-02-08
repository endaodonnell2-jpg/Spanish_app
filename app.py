import streamlit as st
from openai import OpenAI
from gtts import gTTS
import base64
import io

# --- 1. SETUP ---
st.set_page_config(page_title="Colab Tutor", layout="centered")
st.title("Colab Tutor: Test Mode 🚀")

# This is how Streamlit handles your OpenAI Key safely
if "OPENAI_API_KEY" in st.secrets:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
else:
    st.error("Missing OpenAI API Key in Streamlit Secrets!")
    st.stop()

# --- 2. DATA & STATE ---
if "step" not in st.session_state:
    st.session_state.step = 0
if "wrong_answers" not in st.session_state:
    st.session_state.wrong_answers = []

verbs = [
    ("I speak Chinese", "Yo hablo chino"),
    ("You walk to the park", "Tú caminas al parque")
]

# --- 3. HELPER FUNCTIONS ---
def play_audio(text, lang='es'):
    tts = gTTS(text, lang=lang)
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    st.audio(fp)

# --- 4. THE TEST FUNCTION (Translation) ---
def translation_test():
    if st.session_state.step < len(verbs):
        en, es = verbs[st.session_state.step]
        st.subheader(f"Translate: '{en}'")
        
        user_input = st.text_input("Type in Spanish:", key=f"input_{st.session_state.step}")
        
        if st.button("Check Answer"):
            if user_input.lower().strip() == es.lower().strip():
                st.success("¡Correcto!")
                play_audio(es)
                st.session_state.step += 1
                st.rerun()
            else:
                st.error(f"Incorrecto. It is: {es}")
                st.session_state.wrong_answers.append(verbs[st.session_state.step])
                play_audio(es)
    else:
        st.balloons()
        st.write("Test Complete!")
        if st.button("Restart"):
            st.session_state.step = 0
            st.rerun()

translation_test()
