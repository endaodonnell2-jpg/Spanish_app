import streamlit as st
from openai import OpenAI
from gtts import gTTS
from streamlit_mic_recorder import mic_recorder
import io, unicodedata, string

# --- 1. SETTINGS & STYLE ---
st.set_page_config(page_title="Colab Tutor", page_icon="🎙️")

# Custom CSS for the "Giant Action Button" and layout
st.markdown("""
    <style>
    /* Make the mic button container centered and large */
    .st-emotion-cache-1kyx7g1 { 
        display: flex; 
        justify-content: center; 
    }
    /* Style the actual mic button */
    button[data-testid="stBaseButton-secondary"] {
        border-radius: 50% !important;
        width: 200px !important;
        height: 200px !important;
        background-color: #ff4b4b !important;
        color: white !important;
        font-weight: bold !important;
        font-size: 20px !important;
        border: 5px solid white !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2) !important;
    }
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
if "announced" not in st.session_state: st.session_state.announced = -1
if "processing" not in st.session_state: st.session_state.processing = False

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

# --- 4. THE APP FLOW ---
st.title("Colab Tutor")

if st.session_state.step < len(st.session_state.verbs):
    en, es = st.session_state.verbs[st.session_state.step]
    
    # STEP A: TEACHER ASKS THE QUESTION IMMEDIATELY
    if st.session_state.announced != st.session_state.step:
        st.write(f"### Question {st.session_state.step + 1}")
        play_audio(f"How do you say: {en}")
        st.session_state.announced = st.session_state.step

    st.subheader(f"🗣️ Translate: '{en}'")

    # STEP B: THE MIC (Visual Feedback via Prompts)
    # This component handles the 'Red when recording' internally
    audio = mic_recorder(
        start_prompt="TAP TO START",
        stop_prompt="TAP TO CHECK",
        key=f'mic_{st.session_state.step}'
    )

    if audio and not st.session_state.processing:
        st.session_state.processing = True
        audio_bio = io.BytesIO(audio['bytes'])
        audio_bio.name = "audio.webm"
        
        with st.spinner("Tutor is listening..."):
            transcript = client.audio.transcriptions.create(
                model="whisper-1", file=audio_bio, language="es"
            ).text
            
            # STEP C: FEEDBACK
            if normalize(transcript) == normalize(es):
                feedback_msg = f"Correcto! {es}"
                st.success(f"✅ {feedback_msg}")
                play_audio(feedback_msg)
            else:
                feedback_msg = f"Incorrecto, it is {es}"
                st.error(f"❌ {feedback_msg} (You said: {transcript})")
                play_audio(feedback_msg)
        
        # Move forward automatically after feedback
        if st.button("Move to Next Verb ➡️"):
            st.session_state.step += 1
            st.session_state.processing = False
            st.rerun()

else:
    st.balloons()
    st.success("You've finished the list!")
    if st.button("Start Over"):
        st.session_state.step = 0
        st.session_state.announced = -1
        st.rerun()
