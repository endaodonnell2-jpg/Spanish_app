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

st.title("🎙️ Colab Tutor (Lucas11)")

# 2. INPUT
# We use a key "my_mic" so we can clear it later
audio_input = st.audio_input("Speak to Lucas11", key="my_mic")

if audio_input:
    # 3. TRANSCRIPTION (Whisper API)
    with st.spinner("Lucas is listening..."):
        transcript = client.audio.transcriptions.create(
            model="whisper-1", 
            file=audio_input
        ).text
    
    st.write(f"**You said:** {transcript}")

    # 4. LOGIC & AUDIO GENERATION
    def play_combined(texts):
        combined = AudioSegment.empty()
        
        for text, lang in texts:
            # Create a unique temp file
            fname = f"{uuid.uuid4().hex}.mp3"
            tts = gTTS(text, lang=lang)
            tts.save(fname)
            
            # Add to the mix
            combined += AudioSegment.from_mp3(fname) + AudioSegment.silent(duration=400)
            
            # Cleanup temp file
            if os.path.exists(fname):
                os.remove(fname)
        
        # Prepare for playback
        buf = io.BytesIO()
        combined.export(buf, format="mp3")
        
        # Display output
        st.markdown(f"### **Lucas11:** {texts[0][0]}")
        st.audio(buf, format="audio/mp3", autoplay=True) # Added autoplay so he talks back immediately

    # Run the AI response
    play_combined([(transcript, "en"), ("I heard you clearly.", "en")])

    # 5. THE "DELETE" TRICK
    # This clears the microphone input so it doesn't loop or stay on screen
    if st.button("Clear Conversation"):
        st.session_state.my_mic = None
        st.rerun()
