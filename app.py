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

st.title("🎙️ Colab Tutor (Lucas11)")

# Initialize Session State
if 'processing' not in st.session_state:
    st.session_state.processing = False

# 2. THE PROMPT (The Mic)
# We keep the mic visible as the default state
if not st.session_state.processing:
    audio_input = st.audio_input("Speak to Lucas11 now:", key="lucas_mic")
    
    if audio_input:
        st.session_state.processing = True
        st.rerun()

# 3. THE PROGRAM (Runs only after you speak)
if st.session_state.processing and st.session_state.get('lucas_mic'):
    try:
        # A. Transcribe
        with st.status("Listening to your voice...", expanded=False):
            transcript = client.audio.transcriptions.create(
                model="whisper-1", 
                file=st.session_state.lucas_mic
            ).text
        
        st.write(f"**You:** {transcript}")

        # B. AI Brain
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are Lucas11. Concise/witty. Max 12 words."},
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

        # D. Speak & Auto-Unlock with Progress Bar
        st.markdown(f"### **Lucas11:** {ai_text}")
        st.audio(buf, format="audio/mp3", autoplay=True)
        
        # This bar prevents the user from speaking until Lucas is done
        st.write("✨ Lucas11 is speaking...")
        bar = st.progress(0)
        steps = 20
        for i in range(steps + 1):
            time.sleep(duration / steps)
            bar.progress(i / steps)
        
        # E. RESET FOR NEXT ROUND
        st.session_state.processing = False
        st.session_state.lucas_mic = None # Clear the recording
        st.rerun()

    except Exception as e:
        st.error(f"Error: {e}")
        st.session_state.processing = False
        st.session_state.lucas_mic = None
        st.button("Try Again")

    except Exception as e:
        st.error(f"Error: {e}")
        st.session_state.processing = False
        st.rerun()
