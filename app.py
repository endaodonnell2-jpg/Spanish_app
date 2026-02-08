import streamlit as st
from openai import OpenAI
from gtts import gTTS
from streamlit_mic_recorder import mic_recorder
import io, unicodedata, string, time

# --- 1. CONFIG & GIANT BUTTON STYLE ---
st.set_page_config(page_title="Colab Tutor", page_icon="🎙️")

st.markdown("""
    <style>
    .st-emotion-cache-1kyx7g1 { display: flex; justify-content: center; }
    
    /* The Big Round Button */
    button[data-testid="stBaseButton-secondary"] {
        border-radius: 50% !important;
        width: 220px !important;
        height: 220px !important;
        font-weight: bold !important;
        font-size: 22px !important;
        background-color: #28a745 !important; /* Green */
        color: white !important;
        transition: background-color 0.5s ease;
    }
    /* Red while being pressed/active */
    button[data-testid="stBaseButton-secondary"]:active {
        background-color: #dc3545 !important; 
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
if "last_spoken" not in st.session_state: st.session_state.last_spoken = -1

# --- 3. HELPERS ---
def play_tutor(text, lang='es'):
    tts = gTTS(text, lang=lang)
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    st.audio(fp, format="audio/mp3", autoplay=True)

def normalize(s):
    s = s.lower()
    s = ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')
    return s.translate(str.maketrans('', '', string.punctuation)).strip()

# --- 4. THE APP ---
st.title("Colab Tutor")

if st.session_state.step < len(st.session_state.verbs):
    en, es = st.session_state.verbs[st.session_state.step]

    # Tutor asks immediately
    if st.session_state.last_spoken != st.session_state.step:
        play_tutor(f"How do you say: {en}", lang='en')
        st.session_state.last_spoken = st.session_state.step

    st.write(f"### Translate: {en}")
    
    # Visual instruction for the user
    st.caption("Wait 1s after pressing until it's Red, then speak.")

    # THE BUFFERED MIC
    audio = mic_recorder(
        start_prompt="HOLD TO SPEAK",
        stop_prompt="RECORDING... (RELEASE TO SEND)",
        key=f"mic_{st.session_state.step}",
        just_once=True,
    )

    if audio and audio['bytes']:
        # The 0.5s Tail: We wait slightly to ensure the buffer is captured
        time.sleep(0.5) 
        
        with st.spinner("Checking..."):
            try:
                # Convert to file-like object
                audio_file = io.BytesIO(audio['bytes'])
                audio_file.name = "audio.webm"

                transcript = client.audio.transcriptions.create(
                    model="whisper-1", 
                    file=audio_file,
                    language="es"
                ).text
                
                if normalize(transcript) == normalize(es):
                    msg = f"¡Correcto! {es}"
                    st.success(f"✅ {msg}")
                    play_tutor(msg)
                else:
                    msg = f"Incorrecto. Es {es}"
                    st.error(f"❌ {msg} (You said: {transcript})")
                    play_tutor(msg)
                
                if st.button("Next Question ➡️"):
                    st.session_state.step += 1
                    st.rerun()
                    
            except Exception:
                st.warning("I missed that. Please hold for a full second before speaking!")
else:
    st.balloons()
    if st.button("Restart"):
        st.session_state.step = 0
        st.session_state.last_spoken = -1
        st.rerun()
