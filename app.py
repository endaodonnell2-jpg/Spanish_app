import streamlit as st
import streamlit.components.v1 as components
import base64
import io
from openai import OpenAI

# 1. YOUR WHISPER CONFIG
client = OpenAI(api_key="YOUR_OPENAI_API_KEY")

st.title("🎙️ Colab Tutor: Final Bridge Fix")

# 2. THE FRONTEND (The "Forced" Bridge)
def ptt_button():
    # We use 'st.components.v1.html' but we add a specific listener
    # that Streamlit's internal 'setComponentValue' can hook into.
    
    html_code = """
    <div style="text-align: center;">
        <button id="ptt" style="background: #2ecc71; color: white; border: none; width: 100px; height: 100px; border-radius: 50%; cursor: pointer; outline: none;">
            <svg viewBox="0 0 24 24" width="40" height="40" fill="white"><path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/><path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/></svg>
        </button>
        <p id="status" style="color: #2ecc71; font-family: sans-serif; margin-top: 10px;">HOLD TO SPEAK</p>
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
                    // THIS IS THE CRITICAL CHANGE:
                    // Streamlit components need to return data via this specific function
                    window.parent.postMessage({
                        type: 'streamlit:set_widget_value',
                        data: b64,
                        key: 'audio_bridge'
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
    return components.html(html_code, height=160)

# 3. RUN THE UI
ptt_button()

# 4. CATCH THE DATA
# This 'st.chat_input' trick or a 'st.text_input' with a key must match the JS key
audio_data = st.session_state.get('audio_bridge')

# Force a check of the key
if "audio_bridge" in st.session_state and st.session_state.audio_bridge:
    raw_b64 = st.session_state.audio_bridge
    
    try:
        # Decode and Transcribe using your Whisper logic
        audio_bytes = base64.b64decode(raw_b64)
        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = "recording.wav"
        
        with st.spinner("Whisper is transcribing..."):
            transcript = client.audio.transcriptions.create(
                model="whisper-1", 
                file=audio_file
            ).text
            
            st.markdown("---")
            st.subheader("Transcription:")
            st.success(transcript)
            
            # CLEAR the state so it doesn't loop forever
            st.session_state.audio_bridge = None
            
    except Exception as e:
        st.error(f"Error: {e}")
