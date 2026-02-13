import streamlit as st
import base64
import io
from openai import OpenAI

# 1. SETUP - Use your 'Lucas11' key
client = OpenAI(api_key="YOUR_OPENAI_API_KEY")

st.title("🎙️ Colab Tutor: Manual Test")

# 2. MANUAL UPLOAD (To test if Whisper works here)
uploaded_file = st.file_uploader("Upload a voice clip to test Whisper", type=['wav', 'mp3', 'm4a'])

if uploaded_file is not None:
    try:
        with st.spinner("Whisper is transcribing..."):
            # We pass the file directly to OpenAI
            transcript = client.audio.transcriptions.create(
                model="whisper-1", 
                file=uploaded_file
            ).text
            
            st.markdown("---")
            st.subheader("What Whisper Heard:")
            st.success(transcript)
            
    except Exception as e:
        st.error(f"Whisper Error: {e}")

st.divider()
st.info("If this works, your OpenAI connection is fine. The issue is strictly the JavaScript button's permission.")
