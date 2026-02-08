import streamlit as st
from openai import OpenAI
from gtts import gTTS
from streamlit_mic_recorder import mic_recorder
import io

# --- 1. SETUP ---
st.set_page_config(page_title="Colab Tutor", layout="centered")

if "OPENAI_API_KEY" in st.secrets:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
else:
    st.error("Missing API Key!")
    st.stop()

# --- 2. SIDEBAR MENU ---
mode = st.sidebar.selectbox("Choose a mode:", ["Translation Drill", "Pronunciation Practice"])

# --- 3. DATA ---
verbs = [
    ("I speak Chinese", "Yo hablo chino"),
    ("You walk to the park", "Tú caminas al parque")
]

# --- 4. AUDIO PLAYER ---
def play_audio(text):
    tts = gTTS(text, lang='es')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    st.audio(fp, autoplay=True)

# --- 5. MODE: TRANSLATION ---
if mode == "Translation Drill":
    st.title("✍️ Translation Practice")
    if "t_step" not in st.session_state: st.session_state.t_step = 0
    
    if st.session_state.t_step < len(verbs):
        en, es = verbs[st.session_state.t_step]
        st.subheader(f"How do you say: '{en}'?")
        user_input = st.text_input("Type here:", key=f"t_{st.session_state.t_step}")
        
        if st.button("Check Answer"):
            if user_input.lower().strip() == es.lower().strip():
                st.success("Correct!")
                play_audio(es)
                st.session_state.t_step += 1
                st.rerun()
            else:
                st.error(f"Incorrect. It's: {es}")
                play_audio(es)
    else:
        st.write("Done!")
        if st.button("Restart"): 
            st.session_state.t_step = 0
            st.rerun()

# --- 6. MODE: PRONUNCIATION ---
elif mode == "Pronunciation Practice":
    st.title("🎤 Pronunciation Practice")
    if "p_step" not in st.session_state: st.session_state.p_step = 0
    
    en, es = verbs[st.session_state.p_step % len(verbs)]
    st.subheader(f"Repeat after me: '{es}'")
    if st.button("Listen to Example"):
        play_audio(es)
    
    st.write("Click 'Start' to record, then 'Stop' when finished:")
    audio = mic_recorder(start_prompt="🔴 Start Recording", stop_prompt="⏹️ Stop", key='recorder')

    if audio:
        st.audio(audio['bytes'])
        # Here we would add the AI feedback logic next!
        st.info("Audio received! (AI Analysis coming in the next update)")
