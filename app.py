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

# CSS to hide audio bar
st.markdown("<style>audio { display: none !important; }</style>", unsafe_allow_html=True)

st.title("🎙️ Colab Tutor (Lucas11)")

# Initialize state
if 'lock' not in st.session_state:
    st.session_state.lock = False

# 2. THE MICROPHONE
if not st.session_state.lock:
    # We use a unique key every time to prevent the "Error occurred" loop
    audio_key = f"ms_{st.session_state.get('counter', 0)}"
    audio_input = st.audio_input("Speak to Lucas11", key=audio_key)
    
    if audio_input is not None:
        st.session_state.temp_audio = audio_input
        st.session_state.lock = True
        st.session_state.counter = st.session_state.get('counter', 0) + 1
        st.rerun()

# 3. THE PROGRAM
if st.session_state.lock and st.session_state.get('temp_audio'):
    try:
        # A. Transcribe
        with st.spinner("Decoding..."):
            transcript = client.audio.transcriptions.create(
                model="whisper-1", 
                file=st.session_state.temp_audio
            ).text
        
        st.write(f"**You:** {transcript}")

        # B. AI Brain
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are Lucas11. Very short, witty answers. Max 10 words."},
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

        # D. Output
        st.markdown(f"### **Lucas11:** {ai_text}")
        st.audio(buf, format="audio/mp3", autoplay=True)
        
        # Progress bar
        bar = st.progress(0, text="Lucas11 is speaking...")
        for i in range(101):
            time.sleep(duration / 100)
            bar.progress(i)
        
        # E. CLEAN RESET
        st.session_state.lock = False
        st.session_state.temp_audio = None
        st.rerun()

    except Exception as e:
        # If an error happens, we reset so the user can try again
        st.session_state.lock = False
        st.session_state.temp_audio = None
        st.rerun()
