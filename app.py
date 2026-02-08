import streamlit as st
from openai import OpenAI
from gtts import gTTS
from streamlit_mic_recorder import mic_recorder
import io, unicodedata, string

# --- 1. SETUP ---
st.set_page_config(page_title="Colab Tutor", page_icon="🚀")
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# --- 2. DATA ---
if "verbs" not in st.session_state:
    st.session_state.verbs = [
        ("I speak chinese", "Yo hablo chino"),
        ("You speak chinese", "Tú hablas chino"),
        ("He speaks chinese", "Él habla chino"),
        ("I walk to the park", "Yo camino al parque"),
        ("You walk to the park", "Tú caminas al parque")
    ]

# Initialize state variables
if "step" not in st.session_state: st.session_state.step = 0
if "feedback_text" not in st.session_state: st.session_state.feedback_text = ""
if "show_next" not in st.session_state: st.session_state.show_next = False

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

# --- 4. THE UI ---
st.title("Colab Tutor")

if st.session_state.step < len(st.session_state.verbs):
    en, es = st.session_state.verbs[st.session_state.step]
    
    st.write(f"### How do you say: '{en}'?")
    
    # Only show mic if we aren't waiting for the user to click "Next"
    if not st.session_state.show_next:
        audio = mic_recorder(start_prompt="🔴 Hold to Speak", stop_prompt="⏹️ Stop", key=f'mic_{st.session_state.step}')

        if audio:
            audio_bio = io.BytesIO(audio['bytes'])
            audio_bio.name = "audio.webm"
            
            with st.spinner("Checking..."):
                transcript = client.audio.transcriptions.create(
                    model="whisper-1", file=audio_bio, language="es"
                ).text
                
                if normalize(transcript) == normalize(es):
                    st.session_state.feedback_text = f"✅ ¡Correcto! You said: {transcript}"
                    st.session_state.current_audio = f"¡Correcto! {es}"
                else:
                    st.session_state.feedback_text = f"❌ Incorrecto. You said: {transcript}. It is: {es}"
                    st.session_state.current_audio = f"Incorrecto. Es {es}"
                
                st.session_state.show_next = True
                st.rerun()

    # Show Feedback and "Next" button
    if st.session_state.show_next:
        st.write(st.session_state.feedback_text)
        play_audio(st.session_state.current_audio)
        
        if st.button("Next Question ➡️"):
            st.session_state.step += 1
            st.session_state.show_next = False
            st.session_state.feedback_text = ""
            st.rerun()

else:
    st.success("All done! Great session.")
    if st.button("Restart"):
        st.session_state.step = 0
        st.rerun()
