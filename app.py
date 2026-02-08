import streamlit as st
from openai import OpenAI
from gtts import gTTS
from streamlit_mic_recorder import mic_recorder
import io, unicodedata, string

# --- 1. SETUP & STYLING ---
st.set_page_config(page_title="Colab Tutor", page_icon="🎙️")

# Custom CSS to make the button giant and handle the "Feel"
st.markdown("""
    <style>
    div[data-testid="stVerticalBlock"] div[data-testid="element-container"] .stButton button {
        height: 150px;
        width: 150px;
        border-radius: 50%;
        font-size: 20px;
    }
    .main { background-color: #f5f7f9; }
    </style>
    """, unsafe_allow_html=True)

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# --- 2. SESSION STATE ---
if "verbs" not in st.session_state:
    st.session_state.verbs = [
        ("I speak chinese", "Yo hablo chino"),
        ("You speak chinese", "Tú hablas chino"),
        ("He speaks chinese", "Él habla chino"),
        ("I walk to the park", "Yo camino al parque"),
        ("You walk to the park", "Tú caminas al parque")
    ]

if "step" not in st.session_state: st.session_state.step = 0
if "last_announced" not in st.session_state: st.session_state.last_announced = -1
if "feedback" not in st.session_state: st.session_state.feedback = None

# --- 3. HELPERS ---
def normalize(s: str) -> str:
    s = s.lower()
    s = ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')
    s = ''.join(ch for ch in s if ch not in string.punctuation)
    return ' '.join(s.split())

def play_audio(text):
    tts = gTTS(text, lang='es')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    st.audio(fp, format="audio/mp3", autoplay=True)

# --- 4. THE APP ---
st.title("Colab Tutor")

if st.session_state.step < len(st.session_state.verbs):
    en, es = st.session_state.verbs[st.session_state.step]
    
    # TUTOR SPEAKS QUESTION IMMEDIATELY
    if st.session_state.last_announced != st.session_state.step:
        st.write(f"### Question {st.session_state.step + 1}")
        play_audio(f"How do you say: {en}")
        st.session_state.last_announced = st.session_state.step

    st.subheader(f"🗣️ '{en}'")

    # THE MIC BUTTON
    # 'just_once=True' ensures it processes immediately after you release
    audio = mic_recorder(
        start_prompt="HOLD TO SPEAK (RED)",
        stop_prompt="RELEASE TO CHECK (GREEN)",
        key=f'mic_{st.session_state.step}',
        use_container_width=True
    )

    if audio:
        audio_bio = io.BytesIO(audio['bytes'])
        audio_bio.name = "audio.webm"
        
        with st.spinner("Checking your accent..."):
            transcript = client.audio.transcriptions.create(
                model="whisper-1", file=audio_bio, language="es"
            ).text
            
            if normalize(transcript) == normalize(es):
                msg = f"Correcto! {es}"
                st.success(f"✅ {msg}")
                play_audio(msg)
                st.session_state.feedback = "correct"
            else:
                msg = f"Incorrecto, it is {es}"
                st.error(f"❌ {msg} (You said: {transcript})")
                play_audio(msg)
                st.session_state.feedback = "incorrect"
        
        # Short pause to let audio play, then move to next
        st.session_state.step += 1
        st.button("Continue to Next Question")

else:
    st.balloons()
    st.success("Session Complete!")
    if st.button("Restart"):
        st.session_state.step = 0
        st.session_state.last_announced = -1
        st.rerun()
