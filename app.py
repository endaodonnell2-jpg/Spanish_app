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

# CSS to hide the audio player and style the progress bar
st.markdown("""
    <style>
    audio { display: none !important; }
    .stProgress > div > div > div > div {
        background-color: #00a884;
    }
    </style>
""", unsafe_allow_html=True)

if 'processing' not in st.session_state:
    st.session_state.processing = False

st.title("🎙️ Colab Tutor (Lucas11)")

# 2. THE LOCK
if st.session_state.processing:
    st.write("✨ **Lucas11 is speaking...**")
    progress_bar = st.progress(0)
else:
    audio_input = st.audio_input("Talk to Lucas11", key="lucas_mic")
    
    if audio_input:
        st.session_state.processing = True
        st.rerun()

# 3. THE ACTION
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
                {"role": "system", "content": "You are Lucas11. Concise/witty. Max 15 words."},
                {"role": "user", "content": transcript}
            ]
        )
        ai_text = response.choices[0].message.content

        # C. Speak & Measure
        fname = f"{uuid.uuid4().hex}.mp3"
        gTTS(ai_text, lang="en").save(fname)
        
        audio_seg = AudioSegment.from_mp3(fname)
        duration_seconds = len(audio_seg) / 1000.0
        
        buf = io.BytesIO()
        audio_seg.export(buf, format="mp3")
        
        if os.path.exists(fname): os.remove(fname)

        st.markdown(f"### **Lucas11:** {ai_text}")
        st.audio(buf, format="audio/mp3", autoplay=True)

        # D. PROGRESS BAR TIMER (Visual Auto-Unlock)
        # Updates the bar in increments so it looks smooth
        steps = 20
        for i in range(steps + 1):
            time.sleep(duration_seconds / steps)
            progress_bar.progress(i / steps)
        
        # Reset and Rerun
        st.session_state.processing = False
        st.session_state.lucas_mic = None
        st.rerun()

    except Exception as e:
        st.error(f"Error: {e}")
        st.session_state.processing = False
        st.rerun()
