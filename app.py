import streamlit as st
import base64, io, os, uuid
from openai import OpenAI
from gtts import gTTS
 
# --- BRUTE FORCE IMPORT CHECK ---
try:
    from pydub import AudioSegment
except ImportError:
    st.error("⚠️ Pydub not found! Make sure 'pydub' is in requirements.txt and reboot.")
    st.stop()

# 1. SETUP
client = OpenAI(api_key="Lucas13")

st.title("🎙️ Colab Tutor (Lucas11)")

# 2. INPUT
audio_input = st.audio_input("Speak to Lucas11")

if audio_input:
    # ... Transcription Logic ...
    transcript = client.audio.transcriptions.create(model="whisper-1", file=audio_input).text
    
    # 3. RESPONSE (Using your Pydub + Canvas logic)
    def play_combined(texts):
        combined = AudioSegment.empty()
        for text, lang in texts:
            fname = f"{uuid.uuid4().hex}.mp3"
            gTTS(text, lang=lang).save(fname)
            combined += AudioSegment.from_mp3(fname) + AudioSegment.silent(duration=400)
            os.remove(fname)
        
        # Streamlit-friendly output
        buf = io.BytesIO()
        combined.export(buf, format="mp3")
        b64 = base64.b64encode(buf.getvalue()).decode()
        
        # Display the "Mouth" UI you masters in Colab
        st.markdown(f"**Lucas11:** {texts[0][0]}")
        st.audio(buf, format="audio/mp3")

    play_combined([(transcript, "en"), ("I heard you clearly.", "en")])
