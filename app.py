import streamlit as st
from openai import OpenAI
from gtts import gTTS
from streamlit_mic_recorder import mic_recorder
import io, unicodedata, string

# --- 1. CONFIG & STYLE ---
st.set_page_config(page_title="Colab Tutor", page_icon="🎙️")

st.markdown("""
    <style>
    .st-emotion-cache-1kyx7g1 { display: flex; justify-content: center; }
    button[data-testid="stBaseButton-secondary"] {
        border-radius: 50% !important;
        width: 200px !important;
        height: 200px !important;
        font-weight: bold !important;
        background-color: #28a745 !important; /* Green start */
        color: white !important;
    }
    /* This makes the button feel more like a walkie talkie */
    button[data-testid="stBaseButton-secondary"]:active {
        background-color: #dc3545 !important; /* Red when pressed */
    }
    </style>
    """, unsafe_allow_html=True)

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# --- 2. DATA ---
if "verbs" not in st.session_state:
    st.session_state.verbs = [
        ("I walk to the park", "Yo camino al parque"),
        ("I speak chinese", "Yo hablo chino"),
        ("You drink water", "Tú bebes agua")
    ]
if "step" not in st.session_state: st.session_state.step = 0
if "last_spoken_step" not in st.session_state: st.session_state.last_spoken_step = -1

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

# --- 4. APP LOGIC ---
st.title("Colab Tutor")

if st.session_state.step < len(st.session_state.verbs):
    en, es = st.session_state.verbs[st.session_state.step]

    # Tutor asks the question
    if st.session_state.last_spoken_step != st.session_state.step:
        play_tutor(f"How do you say: {en}", lang='en')
        st.session_state.last_spoken_step = st.session_state.step

    st.write(f"### Translate: {en}")

    # The Mic
    audio = mic_recorder(
        start_prompt="HOLD TO SPEAK (GREEN)",
        stop_prompt="RELEASE (RED)",
        key=f"mic_{st.session_state.step}",
        just_once=True
    )

    # CHECK: ONLY PROCEED IF AUDIO IS NOT EMPTY
    if audio and audio['bytes']:
        if len(audio['bytes']) < 1000: # Too small to be a voice
            st.warning("Too short! Please hold the button longer.")
        else:
            with st.spinner("Checking..."):
                try:
                    transcript = client.audio.transcriptions.create(
                        model="whisper-1", 
                        file=io.BytesIO(audio['bytes']), 
                        language="es"
                    ).text
                    
                    if normalize(transcript) == normalize(es):
                        st.success(f"✅ ¡Correcto! {es}")
                        play_tutor(f"¡Correcto! {es}")
                    else:
                        st.error(f"❌ Incorrecto. You said '{transcript}'. It is: {es}")
                        play_tutor(f"Incorrecto. Es {es}")
                    
                    if st.button("Next Verb ➡️"):
                        st.session_state.step += 1
                        st.rerun()
                except Exception as e:
                    st.error("OpenAI had trouble hearing that. Try again!")
                    # This prevents the whole app from crashing if the API fails

else:
    st.success("Done!")
    if st.button("Restart"):
        st.session_state.step = 0
        st.session_state.last_spoken_step = -1
        st.rerun()
