import streamlit as st
from openai import OpenAI
from gtts import gTTS
from streamlit_mic_recorder import mic_recorder
import io, unicodedata, string

# --- 1. CONFIG & STYLE ---
st.set_page_config(page_title="Colab Tutor", page_icon="🎙️")

# CSS to make the button look like a big Walkie-Talkie
st.markdown("""
    <style>
    /* Center the microphone */
    .st-emotion-cache-1kyx7g1 { display: flex; justify-content: center; }
    
    /* Make the button circular and big */
    button[data-testid="stBaseButton-secondary"] {
        border-radius: 50% !important;
        width: 180px !important;
        height: 180px !important;
        font-weight: bold !important;
        border: 4px solid #eeeeee !important;
    }
    </style>
    """, unsafe_allow_html=True)

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# --- 2. DATA & SESSION STATE ---
if "verbs" not in st.session_state:
    st.session_state.verbs = [
        ("I walk to the park", "Yo camino al parque"),
        ("I speak chinese", "Yo hablo chino"),
        ("You drink water", "Tú bebes agua"),
        ("He eats an apple", "Él come una manzana"),
        ("We speak Spanish", "Nosotros hablamos español")
    ]

if "step" not in st.session_state: st.session_state.step = 0
if "last_spoken_step" not in st.session_state: st.session_state.last_spoken_step = -1

# --- 3. HELPERS ---
def play_tutor(text):
    tts = gTTS(text, lang='es')
    if "How do you say" in text:
        tts = gTTS(text, lang='en') # Ask in English
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

    # A. TUTOR ASKS QUESTION IMMEDIATELY
    if st.session_state.last_spoken_step != st.session_state.step:
        play_tutor(f"How do you say: {en}")
        st.session_state.last_spoken_step = st.session_state.step

    st.write(f"### Question {st.session_state.step + 1}")
    st.info(f"**Translate:** {en}")

    # B. THE HOLD-TO-SPEAK BUTTON
    # 'just_once=True' makes it process as soon as you release the button
    audio = mic_recorder(
        start_prompt="HOLD TO SPEAK (GREEN)",
        stop_prompt="RECORDING... RELEASE (RED)",
        key=f"mic_{st.session_state.step}",
        just_once=True
    )

    if audio:
        with st.spinner("Checking..."):
            transcript = client.audio.transcriptions.create(
                model="whisper-1", 
                file=io.BytesIO(audio['bytes']), 
                language="es"
            ).text
            
            user_said = normalize(transcript)
            correct_ans = normalize(es)

            if user_said == correct_ans:
                st.success(f"✅ Correcto! {es}")
                play_tutor(f"¡Correcto! {es}")
            else:
                st.error(f"❌ Incorrecto. You said '{transcript}'. It is: {es}")
                play_tutor(f"Incorrecto. Es {es}")
            
            # Button to move to next
            if st.button("Next Verb ➡️"):
                st.session_state.step += 1
                st.rerun()

else:
    st.balloons()
    st.success("Session finished!")
    if st.button("Restart"):
        st.session_state.step = 0
        st.session_state.last_spoken_step = -1
        st.rerun()
