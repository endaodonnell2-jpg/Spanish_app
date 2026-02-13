import streamlit as st
import streamlit.components.v1 as components
import base64
import io
from openai import OpenAI

# 1. SETUP - Use your key
client = OpenAI(api_key="YOUR_OPENAI_API_KEY")

st.set_page_config(page_title="Colab Tutor", layout="centered")
st.title("🎙️ Colab Tutor")

# 2. THE FRONTEND - Custom Hold-to-Speak
st_bridge_js = """
<div style="display: flex; flex-direction: column; align-items: center; padding: 20px;">
    <button id="ptt" style="background: #2ecc71; color: white; border: none; width: 120px; height: 120px; border-radius: 50%; cursor: pointer; outline: none; box-shadow: 0 4px 15px rgba(46, 204, 113, 0.4);">
        <svg viewBox="0 0 24 24" width="50" height="50" fill="white"><path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/><path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/></svg>
    </button>
    <p id="status" style="color: #2ecc71; font-weight: bold; margin-top: 15px; font-family: sans-serif;">HOLD TO SPEAK</p>
</div>

<script>
    const btn = document.getElementById('ptt');
    const status = document.getElementById('status');
    let mediaRecorder, chunks = [];

    btn.onmousedown = async () => {
        chunks = [];
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);
            mediaRecorder.ondataavailable = e => chunks.push(e.data);
            mediaRecorder.onstop = () => {
                const blob = new Blob(chunks, { type: 'audio/webm' });
                const reader = new FileReader();
                reader.readAsDataURL(blob);
                reader.onloadend = () => {
                    const b64 = reader.result.split(',')[1];
                    // FORCE SEND to Streamlit
                    window.parent.postMessage({
                        type: 'streamlit:set_widget_value',
                        data: b64,
                        key: 'whisper_pipe'
                    }, '*');
                };
            };
            mediaRecorder.start();
            btn.style.background = '#e74c3c';
            status.innerText = 'LISTENING...';
        } catch (err) {
            status.innerText = 'MIC ERROR: ' + err.message;
        }
    };

    btn.onmouseup = () => {
        if(mediaRecorder && mediaRecorder.state === 'recording') {
            mediaRecorder.stop();
            btn.style.background = '#2ecc71';
            status.innerText = 'PROCESSING...';
        }
    };
</script>
"""

components.html(st_bridge_js, height=220)

# 3. THE BACKEND - Capture and Transcribe
# This 'whisper_pipe' must match the key in the JS above
audio_data_b64 = st.text_input("Bridge", key="whisper_pipe", label_visibility="collapsed")

if audio_data_b64:
    try:
        # Decode the raw audio from the button
        audio_bytes = base64.b64decode(audio_data_b64)
        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = "voice.webm" # Whisper accepts webm from browsers
        
        with st.spinner("Transcribing with Whisper..."):
            transcript = client.audio.transcriptions.create(
                model="whisper-1", 
                file=audio_file
            ).text
            
            # Show results just like your Colab Tutor
            st.markdown("---")
            st.markdown(f"**You:** {transcript}")
            
    except Exception as e:
        st.error(f"Error: {str(e)}")

# Clear for next turn
if st.button("Clear Text"):
    st.rerun()
