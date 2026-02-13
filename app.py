import sys
try:
    import audioop
except ImportError:
    import audioop_lts as audioop
    sys.modules["audioop"] = audioop

import streamlit as st
import base64, io, os, uuid
from openai import OpenAI
from gtts import gTTS
from pydub import AudioSegment

# 1. SETUP
client = OpenAI(api_key=st.secrets["Lucas13"])
st.set_page_config(page_title="Colab Tutor", layout="centered")

# CSS to hide the audio player and the bridge box
st.markdown("""
    <style>
    /* Hides the audio player entirely */
    audio { display: none; }
    /* Hides the bridge/text inputs */
    div[data-testid="stTextInput"] { position: absolute; top: -1000px; }
    </style>
""", unsafe_allow_html=True)

# Initialize the "Speaking" lock
if 'is_speaking' not in st.session_state:
    st.session_state.is_speaking = False

st.title("🎙️ Colab Tutor (Lucas11)")

# 2. INPUT LOCKING
if st.session_state.is_speaking:
    st.warning("⚠️ Lucas is speaking... please wait.")
    # Show a disabled placeholder or just hide the mic
else:
    audio_input = st.audio_input("Speak to Lucas11", key="lucas_mic")

    if audio_input:
        st.session_state.is_speaking = True # Lock the mic
        
        # 3. TRANSCRIPTION
        transcript = client.audio.transcriptions.create(
            model="whisper-1", 
            file=audio_input
        ).text
        
        st.write(f"**You:** {transcript}")

        # 4. BRAIN
        gpt_response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are Lucas11. Concise/witty. Speak English."},
                {"role": "user", "content": transcript}
            ]
        )
        ai_text = gpt_response.choices[0].message.content

        # 5. VOICE & AUTO-RESET
        fname = f"{uuid.uuid4().hex}.mp3"
        tts = gTTS(ai_text, lang="en")
        tts.save(fname)
        
        audio_seg = AudioSegment.from_mp3(fname)
        buf = io.BytesIO()
        audio_seg.export(buf, format="mp3")
        
        if os.path.exists(fname):
            os.remove(fname)

        st.markdown(f"### **Lucas11:** {ai_text}")
        
        # Play hidden audio
        st.audio(buf, format="audio/mp3", autoplay=True)
        
        # Reset lock after audio is triggered
        st.session_state.is_speaking = False
        
        if st.button("Speak Again"):
            st.session_state.lucas_mic = None
            st.rerun()
