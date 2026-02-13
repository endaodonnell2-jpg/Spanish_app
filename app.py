import sys
try:
    import audioop
except ImportError:
    import audioop_lts as audioop
    sys.modules["audioop"] = audioop

import streamlit as st
import io, os, uuid
from openai import OpenAI
from gtts import gTTS
from pydub import AudioSegment

# 1. SETUP
client = OpenAI(api_key=st.secrets["Lucas13"])

# CSS to hide the audio bar and the 'Stop' button during recording
st.markdown("""
    <style>
    audio { display: none !important; }
    /* This hides the native 'Stop' button to prevent interruption */
    button[title="Stop Recording"] { display: none !important; }
    </style>
""", unsafe_allow_html=True)

# Initialize Session States
if 'processing' not in st.session_state:
    st.session_state.processing = False

st.title("🎙️ Colab Tutor (Lucas11)")

# 2. LOGIC GATE
if st.session_state.processing:
    # While processing, we show a spinner instead of the mic
    st.info("⏳ Lucas11 is thinking... Microphone locked.")
else:
    # Mic is only visible when NOT processing
    audio_input = st.audio_input("Talk to Lucas11", key="lucas_mic")

    if audio_input:
        st.session_state.processing = True
        st.rerun() # Force immediate lockout

# 3. THE ACTION (Only runs if processing is True)
if st.session_state.processing and st.session_state.get('lucas_mic'):
    try:
        # A. Transcribe
        transcript = client.audio.transcriptions.create(
            model="whisper-1", 
            file=st.session_state.lucas_mic
        ).text
        st.write(f"**You:** {transcript}")

        # B. Brain
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are Lucas11. Very short, witty answers."},
                {"role": "user", "content": transcript}
            ]
        )
        ai_text = response.choices[0].message.content

        # C. Speak (gTTS + Pydub)
        fname = f"{uuid.uuid4().hex}.mp3"
        gTTS(ai_text, lang="en").save(fname)
        
        audio_seg = AudioSegment.from_mp3(fname)
        buf = io.BytesIO()
        audio_seg.export(buf, format="mp3")
        
        if os.path.exists(fname): os.remove(fname)

        st.markdown(f"### **Lucas11:** {ai_text}")
        st.audio(buf, format="audio/mp3", autoplay=True)

    except Exception as e:
        st.error(f"Error: {e}")
    
    # D. UNLOCK
    if st.button("Finished? Click to unlock mic"):
        st.session_state.processing = False
        st.session_state.lucas_mic = None
        st.rerun()
