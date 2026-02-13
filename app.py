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
# Native mic component - the data stays until you record over it or clear it
audio_input = st.audio_input("Speak to Lucas11", key="lucas_mic")

if audio_input:
    # 3. TRANSCRIPTION (Whisper)
    with st.spinner("Listening..."):
        transcript = client.audio.transcriptions.create(
            model="whisper-1", 
            file=audio_input
        ).text
    
    st.write(f"**You:** {transcript}")

    # 4. THE BRAIN (GPT-4o)
    # This sends your text to the AI to get a real answer
    with st.spinner("Thinking..."):
        gpt_response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are Lucas11, a helpful and witty Colab Tutor. Keep your answers concise and conversational."},
                {"role": "user", "content": transcript}
            ]
        )
        ai_text = gpt_response.choices[0].message.content

    # 5. VOICE GENERATION (gTTS + Pydub)
    def speak_back(text):
        fname = f"{uuid.uuid4().hex}.mp3"
        tts = gTTS(text, lang="en")
        tts.save(fname)
        
        # Load and prepare audio
        audio_seg = AudioSegment.from_mp3(fname)
        buf = io.BytesIO()
        audio_seg.export(buf, format="mp3")
        
        # Cleanup temp file from server immediately
        if os.path.exists(fname):
            os.remove(fname)
            
        # Display text and Play Audio automatically
        st.markdown(f"### **Lucas11:** {text}")
        st.audio(buf, format="audio/mp3", autoplay=True)

    # Execute the response
    speak_back(ai_text)

    # 6. DELETE/RESET OPTION
    if st.button("Clear for next question"):
        st.session_state.lucas_mic = None
        st.rerun()
