import streamlit as st
import streamlit.components.v1 as components
import base64
import io
from openai import OpenAI

# 1. Setup API Key
client = OpenAI(api_key="YOUR_OPENAI_API_KEY")

st.title("🎙️ Colab Tutor: Whisper Fix")

# 2. JavaScript with a "Trigger" signal
st_bridge_js = """
<div style="text-align: center;">
    <button id="ptt" style="background: #2ecc71; color: white; border: none; width: 100px; height: 100px; border-radius: 50%; cursor: pointer;">
        <svg viewBox="0 0 24 24" width="40" height="40" fill="white"><path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/><path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/></svg>
    </button>
    <p id="status" style="color: #2ecc71; font-weight: bold; margin-top: 10px;">READY</p>
</div>

<script>
    const btn = document.getElementById('ptt');
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
                // Update the value AND trigger a change event
                window.parent.postMessage({
                    type: 'streamlit:set_widget_value',
                    data: b64,
                    key: 'audio_input_data'
                }, '*');
            };
        };
        mediaRecorder.start();
        btn.style.background = '#e74c3c';
        document.getElementById('status').innerText = 'LISTENING...';
    };

    btn.onmouseup = () => {
        if(mediaRecorder) {
            mediaRecorder.stop();
            btn.style.background = '#2ecc71';
            document.getElementById('status').innerText = 'THINKING...';
        }
    };
</script>
"""

components.html(st_bridge_js, height=160)

# 3. The Backend "Listener"
# If this key 'audio_input_data' changes, Streamlit reruns the script
audio_b64 = st.text_input("Bridge", key="audio_input_data", label_visibility="collapsed")

if audio_b64:
    # Immediately show that we received SOMETHING
    st.write("✅ Audio received, transcribing...")
    
    try:
        audio_bytes = base64.b64decode(audio_b64)
        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = "recording.wav"
        
        # Use Whisper-1 (Your Colab logic)
        transcript = client.audio.transcriptions.create(
            model="whisper-1", 
            file=audio_file
        ).text
        
        st.subheader("You said:")
        st.info(transcript)
        
    except Exception as e:
        st.error(f"Error: {e}")
