import streamlit as st
from openai import OpenAI
from gtts import gTTS
from streamlit_mic_recorder import mic_recorder
import io, unicodedata, string

# --- 1. SETUP ---
st.set_page_config(page_title="Colab Tutor")
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# --- 2. THE CSS (Force the Red/Green) ---
st.markdown("""
    <style>
    .st-emotion-cache-1kyx7g1 { display: flex; justify-content: center; }
    button[data-testid="stBaseButton-secondary"] {
        border-radius: 50% !important;
        width: 250px !important;
        height: 250px !important;
        background-color: #28a745 !important;
        color: white !important;
        font-weight: bold !important;
    }
    button[data-testid="stBaseButton-secondary"]:active {
        background-color: #ff0000 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. STATE ---
if "step" not in st.session_state: st.session_state.step = 0
if "verbs" not in st.session_state:
    st.session_state.verbs = [
        ("I walk to the park", "Yo camino al parque"),
        ("I speak chinese", "Yo hablo chino"),
        ("You drink water", "Tú bebes agua")
    ]
if "last_asked" not in st.session_state: st.session_state.last_asked = -1

# --- 4. FUNCTIONS ---
def speak(text, lang='es'):
    tts = gTTS(text, lang=lang)
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    st.audio(fp, format="audio/mp3", autoplay=True)

def clean(s):
    s = s.lower()
    s = ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')
    return s.translate(str.maketrans('', '', string.punctuation)).strip()

# --- 5. THE APP ---
st.title("Colab Tutor")

if st.session_state.step < len(st.session_state.verbs):
    en, es = st.session_state.verbs[st.session_state.step]

    # Ask the question ONLY ONCE
    if st.session_state.last_asked != st.session_state.step:
        st.write(f"### Translate: {en}")
        speak(f"How do you say: {en}", lang='en')
        st.session_state.last_asked = st.session_state.step
    else:
        st.write(f"### Translate: {en}")

    # THE MIC - Using 'just_once' and a clean key
    # If the user has already spoken, we hide the mic to prevent double-clicks
    audio = mic_recorder(
        start_prompt="HOLD TO SPEAK",
        stop_prompt="RELEASED - CHECKING...",
        key=f"mic_v3_{st.session_state.step}",
        just_once=True
    )

    if audio and audio['bytes']:
        with st.spinner("Tutor is listening..."):
            try:
                # 1. Transcribe
                transcript = client.audio.transcriptions.create(
                    model="whisper-1", 
                    file=io.BytesIO(audio['bytes']), 
                    language="es"
                ).text
                
                # 2. Check Answer
                if clean(transcript) == clean(es):
                    feedback = f"¡Correcto! {es}"
                    st.success(feedback)
                else:
                    feedback = f"Incorrecto. Es {es}"
                    st.error(f"{feedback} (You said: {transcript})")
                
                # 3. Speak Feedback IMMEDIATELY
                speak(feedback)
                
                # 4. Stay here until 'Next' is clicked
                if st.button("Next Verb ➡️"):
                    st.session_state.step += 1
                    st.rerun()

            except Exception as e:
                st.error("Wait for the red light, then speak!")
                if st.button("Try Again"):
                    st.rerun()

else:
    st.success("List finished!")
    if st.button("Restart"):
        st.session_state.step = 0
        st.session_state.last_asked = -1
        st.rerun()
