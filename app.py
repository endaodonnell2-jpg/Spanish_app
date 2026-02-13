import sys
try:
    import audioop
except ImportError:
    import audioop_lts as audioop
    sys.modules["audioop"] = audioop

# NOW you can keep the rest of your imports...
import streamlit as st
from pydub import AudioSegment

import streamlit as st
import base64, io, os, uuid
from openai import OpenAI
from gtts import gTTS
from pydub import AudioSegment

# 1. SETUP
# This pulls the key from your Advanced Settings > Secrets
client = OpenAI(api_key=st.secrets["Lucas13"])

st.title("🎙️ Colab Tutor (Lucas11)")

# 2. INPUT
# Native Streamlit microphone component
audio_input = st.audio_input("Speak to Lucas11")

if audio_input:
    # 3. TRANSCRIPTION (Whisper API)
    transcript = client.audio.transcriptions.create(
        model="whisper-1", 
        file=audio_input
    ).text
    
    st.write(f"**You said:** {transcript}")

    # 4. LOGIC & AUDIO GENERATION
    def play_combined(texts):
        combined = AudioSegment.empty()
        
        for text, lang in texts:
            # Create a unique temp file for this segment
            fname = f"{uuid.uuid4().hex}.mp3"
            tts = gTTS(text, lang=lang)
            tts.save(fname)
            
            # Add to the mix with a small silence gap
            combined += AudioSegment.from_mp3(fname) + AudioSegment.silent(duration=400)
            
            # Cleanup temp file
            if os.path.exists(fname):
                os.remove(fname)
        
        # Prepare the combined audio for Streamlit playback
        buf = io.BytesIO()
        combined.export(buf, format="mp3")
        
        # Display the text and the audio player
        st.markdown(f"### **Lucas11:** {texts[0][0]}")
        st.audio(buf, format="audio/mp3")

    # This is where you put your translation/tutor logic
    # Currently, it just repeats what you said back to you
    play_combined([(transcript, "en"), ("I heard you clearly.", "en")])
