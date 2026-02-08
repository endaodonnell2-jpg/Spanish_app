import streamlit as st
from openai import OpenAI
from gtts import gTTS
from streamlit_mic_recorder import mic_recorder
import io, unicodedata, string

# --- 1. THE STYLE (Force the Visuals) ---
st.set_page_config(page_title="Colab Tutor", page_icon="🎙️")

st.markdown("""
    <style>
    .st-emotion-cache-1kyx7g1 { display: flex; justify-content: center; }
    
    /* The button - Big and Green by default */
    button[data-testid="stBaseButton-secondary"] {
        border-radius: 50% !important;
        width: 250px !important;
        height: 250px !important;
        font-weight: bold !important;
        font-size: 24px !important;
        background-color: #28a745 !important;
        color: white !important;
        border: 10px solid #ffffff !important;
    }
    
    /* The button - Turns Bright Red the MOMENT it is pressed */
    button[data-testid="stBaseButton-secondary"]:active {
        background-color: #ff0000 !important;
        transform: scale(0.95);
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
        play_audio(f"How do you say: {en}", lang='en')
        st.session_state.announced = st.session_state.step

    st.write(f"### Translate: {en}")
    
    # --- THE TRUE HOLD BUTTON ---
    # By setting just_once=True, it stops the recording the moment 
    # the browser detects the 'mouseup' or 'touchend' event.
    audio = mic_recorder(
        start_prompt="HOLD TO SPEAK",
        stop_prompt="CHECKING...", 
        key=f"mic_{st.session_state.step}",
        just_once=True
    )

    if audio:
        with st.spinner("Analyzing..."):
            try:
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
                    play_audio(msg)
                else:
                    msg = f"Incorrecto. Es {es}"
                    st.error(f"❌ {msg} (You said: {transcript})")
                    play_audio(msg)
                
                # Auto-advance button
                if st.button("Next Verb ➡️"):
                    st.session_state.step += 1
                    st.rerun()
                    
            except Exception:
                st.error("Hold the button a bit longer while speaking!")
else:
    st.success("Session Complete!")
    if st.button("Restart"):
        st.session_state.step = 0
        st.session_state.announced = -1
        st.rerun()
