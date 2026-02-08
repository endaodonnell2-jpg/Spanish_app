import streamlit as st
from openai import OpenAI
from gtts import gTTS
from streamlit_mic_recorder import mic_recorder
import io, unicodedata, string

# --- 1. STYLE & SETUP ---
st.set_page_config(page_title="Colab Tutor", page_icon="🎙️")

st.markdown("""
    <style>
    .st-emotion-cache-1kyx7g1 { display: flex; justify-content: center; }
    button[data-testid="stBaseButton-secondary"] {
        border-radius: 50% !important;
        width: 250px !important;
        height: 250px !important;
        font-weight: bold !important;
        background-color: #28a745 !important;
        color: white !important;
        border: 10px solid #ffffff !important;
    }
    button[data-testid="stBaseButton-secondary"]:active {
        background-color: #ff0000 !important;
    }
    </style>
    """, unsafe_allow_html=True)

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# --- 2. DATA ---
if "step" not in st.session_state: st.session_state.step = 0
if "verbs" not in st.session_state:
    st.session_state.verbs = [
        ("I walk to the park", "Yo camino al parque"),
        ("I speak chinese", "Yo hablo chino"),
        ("You drink water", "Tú bebes agua")
    ]
if "announced" not in st.session_state: st.session_state.announced = -1
if "feedback" not in st.session_state: st.session_state.feedback = None

# --- 3. HELPERS ---
def play_audio(text, lang='es'):
    tts = gTTS(text, lang=lang)
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    st.audio(fp, format="audio/mp3", autoplay=True)

def normalize(s):
    s = s.lower()
    s = ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')
    return s.translate(str.maketrans('', '', string.punctuation)).strip()

# --- 4. APP LOGIC ---
st.title("Colab Tutor")

if st.session_state.step < len(st.session_state.verbs):
    en, es = st.session_state.verbs[st.session_state.step]

    # Tutor asks the question
    if st.session_state.announced != st.session_state.step:
        st.write(f"### Translate: {en}")
        play_audio(f"How do you say: {en}", lang='en')
        st.session_state.announced = st.session_state.step
    else:
        st.write(f"### Translate: {en}")

    # --- THE MIC BUTTON ---
    # We only show the mic if there is no feedback currently showing
    if st.session_state.feedback is None:
        audio = mic_recorder(
            start_prompt="HOLD TO SPEAK",
            stop_prompt="PROCESING...", 
            key=f"mic_{st.session_state.step}",
            just_once=True
        )

        if audio:
            with st.spinner("Checking..."):
                try:
                    audio_file = io.BytesIO(audio['bytes'])
                    audio_file.name = "audio.webm"
                    transcript = client.audio.transcriptions.create(
                        model="whisper-1", file=audio_file, language="es"
                    ).text
                    
                    # Store feedback in state instead of acting immediately
                    if normalize(transcript) == normalize(es):
                        st.session_state.feedback = {"type": "success", "msg": f"¡Correcto! {es}", "said": transcript}
                    else:
                        st.session_state.feedback = {"type": "error", "msg": f"Incorrecto. Es {es}", "said": transcript}
                    st.rerun() # Force refresh to show the feedback
                except Exception:
                    st.error("Hold the button longer!")

    # --- SHOW FEEDBACK & AUDIO ---
    if st.session_state.feedback:
        fb = st.session_state.feedback
        if fb["type"] == "success":
            st.success(fb["msg"])
        else:
            st.error(f"{fb['msg']} (You said: {fb['said']})")
        
        # Play the tutor's correction
        play_audio(fb["msg"])

        # Manual button to move to next question
        if st.button("Next Verb ➡️"):
            st.session_state.step += 1
            st.session_state.feedback = None # Clear feedback for next round
            st.rerun()

else:
    st.success("Session Complete!")
    if st.button("Restart"):
        st.session_state.step = 0
        st.session_state.announced = -1
        st.session_state.feedback = None
        st.rerun()
