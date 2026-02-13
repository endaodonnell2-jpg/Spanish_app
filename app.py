import streamlit as st
import streamlit.components.v1 as components
import base64
import os
import io
from openai import OpenAI

# 1. SETUP - Use your 'Lucas11' key here
client = OpenAI(api_key="YOUR_OPENAI_API_KEY") 

st.set_page_config(page_title="Colab Tutor", layout="centered")
st.title("🎙️ Colab Tutor: Whisper Mode")

# 2. THE FRONTEND - Your exact "Hold to Speak" logic
st_bridge_js = """
<div style="display: flex; flex-direction: column; align-items: center;">
    <button id="ptt" style="background: #2ecc71; color: white; border: none; padding: 20px; border-radius: 50%; cursor: pointer; width: 100px; height: 100px; outline: none; user-select: none; transition: 0.2s;">
        <svg viewBox="0 0 24 24" width="40" height="40" fill="white"><path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/><path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/></svg>
    </button>
    <p id="status" style="margin-top: 10px; font-weight: bold; color: #2ecc71;">READY</p>
</div>

<script>
    const btn = document.getElementById('ptt');
    const status = document.getElementById('status');
    let mediaRecorder, chunks = [];

    btn.onmousedown = async () => {
        chunks = [];
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
        mediaRecorder.ondataavailable = e => chunks.push(e.data);
        mediaRecorder.onstop = () => {
            const blob = new Blob(chunks, { type: 'audio/wav' });
            const reader = new FileReader();
            reader.readAsDataURL(blob);
            reader.onloadend = () => {
                const b64 = reader.result.split(',')[1];
                // STREAMLIT BRIDGE: This sends data to the 'audio_hex' widget
                window.parent.postMessage({type: 'streamlit:set_widget_value', data: b64, key: 'audio_hex'}, '*');
            };
        };
        mediaRecorder.start();
        btn.style.background = '#e74c3c';
        status.innerText = 'LISTENING...';
    };

    btn.onmouseup = () => {
        if(mediaRecorder) {
            mediaRecorder.stop();
            btn.style.background = '#2ecc71';
            status.innerText = 'PROCESSING...';
        }
    };
</script>
"""

components.html(st_bridge_js, height=180)

# 3. THE BACKEND - Your Colab Whisper Logic
# This hidden input catches the data from the JS button
audio_b64 = st.text_input("audio_bridge", key="audio_hex", label_visibility="collapsed")

if audio_b64:
    try:
        # A. Decode the audio
        audio_bytes = base64.b64decode(audio_b64)
        
        # B. Save to a temporary file (Whisper needs a file-like object with a name)
        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = "input.wav" 
        
        # C. Transcribe using Whisper-1 (Your exact Colab logic)
        with st.spinner("Whisper is thinking..."):
            transcript = client.audio.transcriptions.create(
                model="whisper-1", 
                file=audio_file
            ).text
            
            # D. Output result
            st.markdown("### You said:")
            st.success(transcript)
            
    except Exception as e:
        st.error(f"Transcription Error: {e}")

# Option to reset
if st.button("Clear"):
    st.rerun()
