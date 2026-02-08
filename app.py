import streamlit as st
from openai import OpenAI
from gtts import gTTS
from streamlit_mic_recorder import mic_recorder
import io
import unicodedata
import string

# --- 1. SETUP ---
st.set_page_config(page_title="Colab Tutor", page_icon="🚀")

# This looks for the secret you saved in the Streamlit "Vault"
if "OPENAI_API_KEY" in st.secrets:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
else:
    st.error("Missing API Key in Streamlit Secrets!")
    st.stop()

# --- 2. DATA (Your Full List) ---
if "jugar_verbs" not in st.session_state:
    st.session_state.jugar_verbs = [
        ("I speak chinese", "Yo hablo chino"), ("You speak chinese", "Tú hablas chino"),
        ("He speaks chinese", "Él habla chino"), ("She speaks chinese", "Ella habla chino"),
        ("I walk to the park", "Yo camino al parque"), ("You walk to the park", "Tú caminas al parque"),
        ("He walks to the park", "Él camina al parque"), ("She walks to the park", "Ella camina al parque"),
        ("I watch television", "Yo miro televisión"), ("You watch television", "Tú miras televisión"),
        ("He watches television", "Él mira televisión"), ("She watches television", "Ella mira televisión"),
        ("I teach Maths", "Yo enseño matemáticas"), ("You teach Maths", "Tú enseññas matemáticas"),
        ("He teaches Maths", "Él enseña matemáticas"), ("She teaches Maths", "Ella enseña matemáticas")
    ]

if "step" not in st.session_state: st.session_state.step = 0
if "wrong_drills" not in st.session_state: st.session_state.wrong_drills = []

# --- 3. HELPERS ---
def normalize(s: str) -> str:
    s = s.lower()
    s = ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')
    s = ''.join(ch for ch in s if ch not in string.punctuation)
    return ' '.join(s.split())

def play_audio(text):
    tts = gTTS(text, lang='es', tld='es')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    # The 'autoplay' ensures it plays once as soon as the UI updates
    st.audio(fp, format="audio/mp3", autoplay=True)

# --- 4. THE FLOW ---
st.title("Colab Tutor: Air Practice")

if st.session_state.step < len(st.session_state.jugar_verbs):
    en, es = st.session_state.jugar_verbs[st.session_state.step]
    
    st.write(f"**Question {st.session_state.step + 1}:**")
    st.subheader(f"How do you say: '{en}'?")
    
    # Microphone component
    audio = mic_recorder(start_prompt="🔴 Tap to Speak", stop_prompt="⏹️ Stop & Check", key='mic')

    if audio:
        # Convert audio to file for Whisper
        audio_bio = io.BytesIO(audio['bytes'])
        audio_bio.name = "audio.webm"
        
        with st.spinner("Teacher is checking..."):
            transcript = client.audio.transcriptions.create(
                model="whisper-1", file=audio_bio, language="es"
            ).text
            
            user_norm = normalize(transcript)
            expected_norm = normalize(es)
            
            if user_norm == expected_norm:
                st.success(f"¡Correcto! You said: {transcript}")
                play_audio(f"¡Correcto! {es}")
                if st.button("Next ➡️"):
                    st.session_state.step += 1
                    st.rerun()
            else:
                st.error(f"¡Incorrecto! You said: {transcript}")
                st.info(f"The answer is: {es}")
                st.session_state.wrong_drills.append(st.session_state.jugar_verbs[st.session_state.step])
                play_audio(f"Incorrecto. Es {es}")
                if st.button("Continue ➡️"):
                    st.session_state.step += 1
                    st.rerun()
else:
    # Review Logic
    if st.session_state.wrong_drills:
        st.warning(f"Drills finished, but let's review the {len(st.session_state.wrong_drills)} you missed!")
        if st.button("Start Review"):
            st.session_state.jugar_verbs = st.session_state.wrong_drills.copy()
            st.session_state.wrong_drills = []
            st.session_state.step = 0
            st.rerun()
    else:
        st.balloons()
        st.success("Perfect score! All verbs mastered.")
        if st.button("Restart All"):
            st.session_state.step = 0
            st.rerun()
