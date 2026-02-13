import sys
import time
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

# CSS to hide the audio player bar
st.markdown("<style>audio { display: none !important; }</style>", unsafe_allow_html=True)

st.title("🎙️ Colab Tutor (Lucas11)")

# Initialize the locking state
if 'lock' not in st.session_state:
    st.session_state.lock = False

# 2. THE MICROPHONE (Always prompts unless Lucas is talking)
if not st.session_state.lock:
    audio_input = st.audio_input("Click the circle to speak to Lucas11", key="lucas_mic")
    
    if audio_input:
        st.session_state.lock = True
        st.rerun()

# 3. THE PROGRAM (Runs after you speak)
if st.session_state.lock:
    try:
        # Check if we actually have audio data
        if st.session_state.lucas_mic is not None:
            # A. Transcription
            transcript = client.audio.transcriptions.create(
                model="whisper-1", 
                file=st.session_state.lucas_mic
            ).text
            st.write(f"**You:** {transcript}")

            # B. AI Brain
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are Lucas11. Concise. Max 10 words."},
                    {"role": "user", "content": transcript}
                ]
            )
            ai_text = response.choices[0].message.content

            # C. Voice Generation
            fname = f"{uuid.uuid4().hex}.mp3"
            gTTS(ai_text, lang="en").save(fname)
            audio_seg = AudioSegment.from_mp3(fname)
            duration = len(audio_seg) / 1000.0
            
            buf = io.BytesIO()
            audio_seg.export(buf, format="mp3")
            if os.path.exists(fname): os.remove(fname)

            # D. Output & Auto-Unlock
            st.markdown(f"### **Lucas11:** {ai_text}")
            st.audio(buf, format="audio/mp3", autoplay=True)
            
            # Progress bar shows she is talking
            bar = st.progress(0, text="Lucas11 is speaking...")
            for i in range(101):
                time.sleep(duration / 100)
                bar.progress(i)
            
            # E. RESET
            st.session_state.lock = False
            st.rerun()

    except Exception as e:
        st.error(f"Error: {e}")
        st.session_state.lock = False
        if st.button("Click to fix Microphone"):
            st.rerun()

# Emergency Reset Button (Always visible at the bottom)
if st.sidebar.button("Reset Microphone"):
    st.session_state.lock = False
    st.rerun()
